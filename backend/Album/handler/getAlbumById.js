import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.path?.provider_id;
  const album_id = event.path?.album_id;

  if (!provider_id || !album_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "The parameters: provider_id or album_id are missing" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    Key: {
      provider_id,
      album_id: parseInt(album_id, 10),
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
        body: { message: "Album not found" },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "An error occurred while getting the album",
        error: error.message,
      },
    };
  }
}
