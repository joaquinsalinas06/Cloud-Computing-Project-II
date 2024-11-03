import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const song =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  const params = {
    TableName: TABLE_NAME,
    Item: song,
  };

  try {
    await dynamodb.put(params).promise();
    return {
      statusCode: 201,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Canción creada con éxito",
        song: song,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error al crear la canción",
        error: error.message,
      },
    };
  }
}
