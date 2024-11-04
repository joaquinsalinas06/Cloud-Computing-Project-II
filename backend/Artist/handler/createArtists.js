import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const { provider_id, artists } = 
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  try {
    const putRequests = artists.map((artist) => ({
      PutRequest: {
        Item: { ...artist, provider_id },
      },
    }));

    const params = {
      RequestItems: {
        [TABLE_NAME]: putRequests,
      },
    };

    await dynamodb.batchWrite(params).promise();

    return {
      statusCode: 201,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: `${artists.length} artista(s) creado(s) con éxito`,
        artists,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al crear los artistas",
        error: error.message,
      }),
    };
  }
}
