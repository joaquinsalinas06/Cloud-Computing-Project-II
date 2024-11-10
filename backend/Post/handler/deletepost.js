const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

export async function handler(event) {
  const { provider_id, post_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    Key: { provider_id, post_id }
  };

  try {
    await dynamoDb.delete(params).promise();
    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Post deleted successfully" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not delete post", details: error.message }),
    };
  }
}
