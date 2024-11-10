import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const LSI_NAME = process.env.LSI_NAME_2;

export async function handler(event) {
  const provider_id = event.query?.provider_id;
  const genre = event.query?.genre;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query?.exclusiveStartKey))
    : null;

  if (!provider_id || !genre) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "The 'provider_id' and 'genre' parameters are required.",
      },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    IndexName: LSI_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND genre = :genre",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":genre": genre,
    },
  };
  try {
    const response = await dynamodb.query(params).promise();
    console.log("DynamoDB response:", response);

    if (response.Count === 0) {
      return {
        statusCode: 404,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          message: "No items found",
        },
      };
    } else {
      return {
        statusCode: 200,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          items: response.Items,
          lastEvaluatedKey: response.LastEvaluatedKey
            ? encodeURIComponent(JSON.stringify(response.LastEvaluatedKey))
            : null,
        },
      };
    }
  } catch (error) {
    console.error("Error querying DynamoDB:", error);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error retrieving items",
        error: error.message,
      },
    };
  }
}
