import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const providerId = event.queryStringParameters.providerId;
  const limit = event.queryStringParameters.limit || 10;
  const exclusiveStartKey = event.queryStringParameters.exclusiveStartKey
    ? JSON.parse(
        decodeURIComponent(event.queryStringParameters.exclusiveStartKey)
      )
    : null;

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "providerId = :providerId",
    ExpressionAttributeValues: {
      ":providerId": providerId,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey,
  };

  try {
    const response = await dynamodb.query(params).promise();
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
        message: "Error al recuperar las canciones",
        error: error.message,
      }),
    };
  }
}
