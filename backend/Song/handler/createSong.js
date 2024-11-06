import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const song =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  const provider_id = song.provider_id;

  let highestSongId = 0;
  try {
    const response = await dynamodb
      .query({
        TableName: TABLE_NAME,
        KeyConditionExpression: "provider_id = :provider_id",
        ExpressionAttributeValues: {
          ":provider_id": provider_id,
        },
        ScanIndexForward: false,
        Limit: 1,
      })
      .promise();

    if (response.Items.length > 0) {
      highestSongId = response.Items[0].song_id;
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error al consultar el songId más alto",
        error: error.message,
      },
    };
  }

  song.song_id = highestSongId + 1;

  const params = {
    TableName: TABLE_NAME,
    Item: song,
    ConditionExpression:
      "attribute_not_exists(provider_id) AND attribute_not_exists(song_id)",
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
