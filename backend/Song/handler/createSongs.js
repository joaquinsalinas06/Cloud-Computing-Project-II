import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const songs =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  if (!Array.isArray(songs) || songs.length === 0) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "A list of songs is required",
      },
    };
  }

  let failedSongs = [];
  let createdSongs = [];

  for (let song of songs) {
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
      failedSongs.push({
        song,
        error: `Error al consultar el songId más alto: ${error.message}`,
      });
      continue;
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
      createdSongs.push(song);
    } catch (error) {
      failedSongs.push({
        song,
        error: `Error creating the song: ${error.message}`,
      });
    }
  }

  return {
    statusCode: 201,
    headers: {
      "Content-Type": "application/json",
    },
    body: {
      message: "Process completed",
      createdSongs,
      failedSongs,
    },
  };
}
