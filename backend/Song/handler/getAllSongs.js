import "dotenv/config";
import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const providerId = event.query?.providerId;

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
  };

  try {
    let items = [];
    let lastEvaluatedKey;

    do {
      const response = await dynamodb.query(params).promise();
      items = items.concat(response.Items);
      lastEvaluatedKey = response.LastEvaluatedKey;
      params.ExclusiveStartKey = lastEvaluatedKey;
    } while (lastEvaluatedKey);

    console.log("Total items retrieved:", items.length);

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: { items },
    };
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
