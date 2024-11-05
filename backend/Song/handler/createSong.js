import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

async function getNextSongId() {
  const params = {
    TableName: TABLE_NAME,
    Key: { pk: "songCounter" },
    UpdateExpression: "ADD #cnt :val",
    ExpressionAttributeNames: { "#cnt": "count" },
    ExpressionAttributeValues: { ":val": 1 },
    ReturnValues: "UPDATED_NEW",
  };

  console.log(params);

  const result = await dynamodb.update(params).promise();
  console.log(result);
  return result.Attributes.count;
}

export async function handler(event) {
  const song =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    console.log(song);

  try {
    const songId = await getNextSongId();
    song.songId = songId;
    console.log(song);
    console.log(songId);

    const params = {
      TableName: TABLE_NAME,
      Item: song,
    };

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
