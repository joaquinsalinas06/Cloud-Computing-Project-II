import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.path?.provider_id;
  const album_id = event.path?.album_id;
  const token = event.headers?.Authorization;
  const token_function = process.env.LAMBDA_FUNCTION_NAME; 

  if (!provider_id || !album_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "The parameters: provider_id or album_id are missing" },
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
    KeyConditionExpression: "provider_id = :provider_id and album_id = :album_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":album_id": parseInt(album_id, 10),
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    if (data.Items && data.Items.length > 0) {
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: data.Itemm[0],
      };
    } else {
      return {
        statusCode: 404,
        headers: { "Content-Type": "application/json" },
        body: { message: "Album not found" },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "An error occurred while getting the album",
        error: error.message,
      },
    };
  }
}
