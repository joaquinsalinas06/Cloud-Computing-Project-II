import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const providerId = event.path?.providerId;
  const songId = event.path?.songId
  
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
    await dynamodb.delete(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: { message: "Canción eliminada con éxito" },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { message: "Error al eliminar la canción", error: error.message },
    };
  }
}
