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

  console.log("Deleting artist with params: ", params);

  try {
    const result = await dynamodb.delete(params).promise();

    console.log("Result: ", result);

    return {
      statusCode: 204,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Song was deleted successfully",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "An error occurred while deleting the artist",
        error: error.message,
      },
    };
  }
}
