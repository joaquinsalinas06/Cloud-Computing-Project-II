import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const LSI_NAME = process.env.LSI_NAME_1;

export async function handler(event) {
  const provider_id = event.query?.provider_id;
  const country = event.query?.country;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query?.exclusiveStartKey))
    : null;
  const token = event.headers?.Authorization;
  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  if (!provider_id || !country) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "The 'provider_id' and 'country' parameters are required.",
      },
    };
  }

  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: token_function,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token }),
  };

  try {
    const invokeResponse = await lambda.invoke(invokeParams).promise();
    const responsePayload = JSON.parse(invokeResponse.Payload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unauthorized access";
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: { error: "Unauthorized", message: errorMessage },
      };
    } 
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Authorization check failed", details: error.message },
    };
  }


  const params = {
    TableName: TABLE_NAME,
    IndexName: LSI_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND country = :country",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":country": country,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey ? exclusiveStartKey : undefined,
  };

  try {
    const response = await dynamodb.query(params).promise();
    console.log("DynamoDB response:", response);

    if (response.Count === 0) {
      return {
        statusCode: 404,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          message: "No items found",
        },
      };
    } else {
      return {
        statusCode: 200,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          items: response.Items,
          lastEvaluatedKey: response.LastEvaluatedKey
            ? encodeURIComponent(JSON.stringify(response.LastEvaluatedKey))
            : null,
        },
      };
    }
  } catch (error) {
    console.error("Error querying DynamoDB:", error);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error retrieving items",
        error: error.message,
      },
    };
  }
}
