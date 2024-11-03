import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const { providerId, songId } =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  if (!providerId || !songId) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "Faltan parámetros: providerId o songId" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    Key: {
      providerId,
      songId: parseInt(songId, 10),
    },
  };

  try {
    const data = await dynamodb.get(params).promise();
    if (data.Item) {
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: data.Item,
      };
    } else {
      return {
        statusCode: 404,
        headers: { "Content-Type": "application/json" },
        body: { message: "Canción no encontrada" },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { message: "Error al buscar la canción", error: error.message },
    };
  }
}
