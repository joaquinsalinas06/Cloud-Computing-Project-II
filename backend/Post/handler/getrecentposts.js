const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

export async function handler(event) {
  const { provider_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
    },
    ScanIndexForward: false, 
    Limit: 10
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
      body: JSON.stringify({ error: "Could not retrieve recent posts", details: error.message }),
    };
  }
}
