const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

export async function handler(event) {
  const { provider_id, album_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    IndexName: process.env.INDEXGSI2_TABLE1_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND album_id = :album_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":album_id": album_id,
    },
  };

  try {
    const result = await dynamoDb.query(params).promise();
    return {
      statusCode: 200,
      body: JSON.stringify(result.Items),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not retrieve posts by album_id", details: error.message }),
    };
  }
}
