import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const songs = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  if (!Array.isArray(songs) || songs.length === 0) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Se requiere una lista de canciones válida",
      },
    };
  }

  let failedSongs = [];
  let createdSongs = [];

  for (let song of songs) {
    const providerId = song.providerId;
    let highestSongId = 0;

    try {
      const response = await dynamodb
        .query({
          TableName: TABLE_NAME,
          KeyConditionExpression: "providerId = :providerId",
          ExpressionAttributeValues: {
            ":providerId": providerId,
          },
          ScanIndexForward: false,
          Limit: 1,
        })
        .promise();

      if (response.Items.length > 0) {
        highestSongId = response.Items[0].songId;
      }
    } catch (error) {
      failedSongs.push({
        song,
        error: `Error al consultar el songId más alto: ${error.message}`,
      });
      continue;
    }

    song.songId = highestSongId + 1;

    const params = {
      TableName: TABLE_NAME,
      Item: song,
      ConditionExpression:
        "attribute_not_exists(providerId) AND attribute_not_exists(songId)",
    };

    try {
      await dynamodb.put(params).promise();
      createdSongs.push(song);
    } catch (error) {
      failedSongs.push({
        song,
        error: `Error al crear la canción: ${error.message}`,
      });
    }
  }

  return {
    statusCode: 201,
    headers: {
      "Content-Type": "application/json",
    },
    body: {
      message: "Proceso de creación completado",
      createdSongs,
      failedSongs,
    },
  };
}
