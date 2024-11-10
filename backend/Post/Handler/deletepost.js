const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  // Verifica si pathParameters está definido
  if (!event.pathParameters || !event.pathParameters.provider_id || !event.pathParameters.post_id) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Missing required path parameters: provider_id and post_id" })
    };
  }

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
};
