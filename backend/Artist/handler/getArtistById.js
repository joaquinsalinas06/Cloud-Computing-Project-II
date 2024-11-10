import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.path?.provider_id;
  const artist_id = event.path?.artist_id;

  if (!provider_id || !artist_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "The parameters: provider_id or artist_id are missing" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    Key: {
      provider_id,
      artist_id: parseInt(artist_id, 10),
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
        body: { message: "Artist not found" },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "An error occurred while searching for the artist",
        error: error.message,
      },
    };
  }
}
