import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const GSI_NAME = process.env.GSI;

export const handler = async (event) => {
  const user_id = event.path?.user_id;
  const start_created_at = event.query?.start_created_at;
  const end_created_at = event.query?.end_created_at;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query?.exclusiveStartKey))
    : null;

  const token = event.headers?.Authorization;
 
  if (!token) {
    return {
      statusCode: 401,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        error: "Unauthorized",
        message: "Token is required",
      }),
    };
  }

  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  if (!user_id) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "'user_id' parameter is required.",
      }),
    };
  }

  if (!start_created_at) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "'start_created_at' parameter is required.",
      }),
    };
  }

  if (!end_created_at) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "'end_created_at' parameter is required.",
      }),
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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          error: "Unauthorized",
          message: errorMessage,
        }),
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        error: "Internal Server Error",
        message: error.message,
      }),
    };
  }

  const params = {
    TableName: TABLE_NAME,
    IndexName: GSI_NAME,
    KeyConditionExpression:
      "#user_id = :user_id AND #createdAt BETWEEN :start_created_at AND :end_created_at",
    ExpressionAttributeNames: {
      "#user_id": "user_id",
      "#createdAt": "createdAt",
    },
    ExpressionAttributeValues: {
      ":user_id": user_id,
      ":start_created_at": start_created_at,
      ":end_created_at": end_created_at,
    },
    Limit: limit,
  };

  if (exclusiveStartKey) {
    params.ExclusiveStartKey = exclusiveStartKey;
  }

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        error: "Internal Server Error",
        message: error.message,
      }),
    };
  }
};
