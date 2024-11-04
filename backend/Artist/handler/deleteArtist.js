import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const { provider_id } = JSON.parse(event.body);
  const artistId = event.pathParameters.artistId;

  const params = {
    TableName: TABLE_NAME,
    Key: {
      provider_id,
      artistId,
    },
  };

  try {
    await dynamodb.delete(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Artista eliminado con éxito",
        artistId,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al eliminar el artista",
        error: error.message,
      }),
    };
  }
}
