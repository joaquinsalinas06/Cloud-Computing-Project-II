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
    await dynamodb.delete(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: { message: "Album was succesfuly created" },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "An error occurred while deleting the album",
        error: error.message,
      },
    };
  }
}
