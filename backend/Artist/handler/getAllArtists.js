import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const { provider_id } = JSON.parse(event.body);

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data.Items),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al obtener los artistas",
        error: error.message,
      }),
    };
  }
}
