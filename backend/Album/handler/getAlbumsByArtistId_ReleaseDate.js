import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const GSI_NAME = process.env.GSI;

export default async function handler(event) {
  const artist_id = event.path?.artist_id;
  const start_date = event.query?.start_date;
  const end_date = event.query?.end_date;
  const limit = parseInt(event.query?.limit, 10) || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query.exclusiveStartKey))
    : null;

  const token = event.headers?.Authorization;
  const token_function = process.env.LAMBDA_FUNCTION_NAME;

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

  if (!artist_id) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "'artist_id' parameter is required.",
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
        error: "Authorization check failed",
        details: error.message,
      }),
    };
  }

  const params = {
    TableName: TABLE_NAME,
    IndexName: GSI_NAME,
    KeyConditionExpression:
      "artist_id = :artist_id AND release_date BETWEEN :start_date AND :end_date",
    ExpressionAttributeValues: {
      ":artist_id": artist_id,
      ":start_date": start_date,
      ":end_date": end_date,
    },
    ScanIndexForward: false,
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey || undefined,
  };

  try {
    const response = await dynamodb.query(params).promise();

    if (!response.Items || response.Items.length === 0) {
      return {
        statusCode: 404,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: "No albums found for the given artist.",
        }),
      };
    }

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: response.Items,
        lastEvaluatedKey: response.LastEvaluatedKey
          ? encodeURIComponent(JSON.stringify(response.LastEvaluatedKey))
          : null,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error querying DynamoDB",
        error: error.message,
      }),
    };
  }
}
