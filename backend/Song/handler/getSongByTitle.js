import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const INDEX_NAME = process.env.INDEX_NAME;

export async function handler(event) {
  const { title } =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  if (!title) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "Falta el parámetro: title" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    IndexName: INDEX_NAME,
    KeyConditionExpression: "title = :title",
    ExpressionAttributeValues: {
      ":title": title,
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: data.Items,
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "Error al buscar la canción por título",
        error: error.message,
      },
    };
  }
}
