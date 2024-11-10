import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const INDEX_NAME = process.env.INDEX_NAME;

export async function handler(event) {
  const title = event.query?.title;

  if (!title) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { message: "The parameter: title is missing" },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    IndexName: INDEX_NAME,
    KeyConditionExpression: "title = :title",
    ExpressionAttributeValues: {
      ":title": title,
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: data.Items,
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "An error occurred while creating the album by title",
        error: error.message,
      },
    };
  }
}
