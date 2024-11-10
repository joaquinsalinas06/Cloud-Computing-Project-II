const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

export async function handler(event) {
  const { provider_id, post_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    Key: { provider_id, post_id }
  };

  try {
    const result = await dynamoDb.get(params).promise();
    if (result.Item) {
      return {
        statusCode: 200,
        body: JSON.stringify(result.Item),
      };
    } else {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: "Post not found" }),
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not retrieve post", details: error.message }),
    };
  }
}
