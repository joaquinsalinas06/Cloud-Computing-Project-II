import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const GSI_NAME = process.env.GSI;

export async function handler(event) {
  const genre = event.query?.genre;
  const min_duration = event.query?.min_duration;
  const max_duration = event.query?.max_duration;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query.exclusiveStartKey))
    : null;
  const token = event.headers?.Authorization;
  const provider_id = event.path?.provider_id;

  if (!token) {
    return {
      statusCode: 401,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        error: "Unauthorized",
        message: "Token is required",
      },
    };
  }

  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  if (!genre || !duration) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "The parameters: genre and duration are required",
      },
    };
  }

  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: token_function,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token, provider_id }),
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
    IndexName: GSI_NAME,
    KeyConditionExpression:
      "genre = :genre AND duration BETWEEN :min_duration AND :max_duration",
    ExpressionAttributeValues: {
      ":genre": genre,
      ":min_duration": min_duration,
      ":max_duration": max_duration,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey,
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: error.message }),
    };
  }
}

