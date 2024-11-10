const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;
  const post_id = event.path?.post_id;

  if (!provider_id || !post_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Missing provider_id or post_id" }),
    };
  }

  const queryParams = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND post_id = :post_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":post_id": post_id
    }
  };

  try {
    const result = await dynamoDb.query(queryParams).promise();

    if (result.Items.length === 0) {
      return {
        statusCode: 404,
        headers: { "Content-Type": "application/json" },
        body: { error: "Post not found" },
      };
    }

    const deleteParams = {
      TableName: process.env.TABLE_NAME,
      Key: { provider_id, post_id }
    };

    await dynamoDb.delete(deleteParams).promise();

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: { message: "Post deleted successfully" },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Could not delete post", details: error.message },
    };
  }
};
