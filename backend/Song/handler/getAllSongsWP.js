import "dotenv/config";
import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const providerId = event.query?.providerId;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query.exclusiveStartKey))
    : null;

  if (!providerId) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "The 'providerId' parameter is required.",
      },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "providerId = :providerId",
    ExpressionAttributeValues: {
      ":providerId": providerId,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey ? exclusiveStartKey : undefined,
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
          message: "No songs found",
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
        message: "Error retrieving songs",
        error: error.message,
      },
    };
  }
}
