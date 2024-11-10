const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;
  const post_id = event.path?.post_id;
  const params = {
    TableName: process.env.TABLE_NAME,
    Key: { provider_id, post_id }
  };

  try {
    const result = await dynamoDb.get(params).promise();
    if (result.Item) {
      return {
        statusCode: 200,
        body: result.Item,
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
      body: { error: "Could not retrieve post", details: error.message },
    };
  }
}
