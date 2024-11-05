import "dotenv/config";
import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  console.log("Received event:", JSON.stringify(event, null, 2));

  const providerId = event.query?.providerId;
  const limit = event.query?.limit || 10;
  const exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query.exclusiveStartKey))
    : null;

    console.log("providerId:", providerId);
    console.log("limit:", limit);
    console.log("exclusiveStartKey:", exclusiveStartKey);
    console.log("TABLE_NAME:", TABLE_NAME);

  if (!providerId) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "The 'providerId' parameter is required.",
      }),
    };
  }

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "providerId = :providerId",
    ExpressionAttributeValues: {
      ":providerId": providerId,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey,
  };

  try {
    const response = await dynamodb.query(params).promise();
    console.log(response)
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: response.Items,
        lastEvaluatedKey: response.LastEvaluatedKey
          ? encodeURIComponent(JSON.stringify(response.LastEvaluatedKey))
          : null,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error retrieving songs",
        error: error.message,
      }),
    };
  }
}
