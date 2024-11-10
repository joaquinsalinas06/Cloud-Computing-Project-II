import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.path?.provider_id;
  const song_id = event.path?.song_id;

  if (!provider_id || !song_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "The parameters: provider_id or song_id are missing" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    Key: {
      provider_id,
      song_id: parseInt(song_id, 10),
    },
  };

  try {
    await dynamodb.delete(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: { message: "Song was deleted successfully" },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "An error occurred while deleting the song ",
        error: error.message,
      },
    };
  }
}
