const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  
  const provider_id  = event.path?.provider_id;
  const post_id = event.path?.post_id;
  if (!provider_id || !post_id) {
    return {
      statusCode: 400,
      Headers: { "Content-Type": "application/json" },
      body: { error: "Missing provider_id or post_id" },
    };
  }
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
