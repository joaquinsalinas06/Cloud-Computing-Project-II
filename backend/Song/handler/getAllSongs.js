import "dotenv/config";
import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function getAllSongs(event) {
    const { providerId, limit, lastEvaluatedKey } = JSON.parse(event.body);

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "#providerId = :providerId",
    ExpressionAttributeNames: {
      "#providerId": "providerId",
    },
    ExpressionAttributeValues: {
      ":providerId": providerId,
    },
    Limit: limit,
    ExclusiveStartKey: lastEvaluatedKey,
  };

  try {
    const result = await dynamodb.query(params).promise();
    return {
      items: result.Items,
      lastEvaluatedKey: result.LastEvaluatedKey,
    };
  } catch (error) {
    console.error(error);
    return null;
  }
}