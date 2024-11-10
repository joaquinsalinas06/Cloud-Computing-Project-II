const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;
  const post_id = event.path?.post_id;
  const token = event.headers?.Authorization;

  if (!provider_id || !post_id || !token) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { error: "Missing required parameters or token" },
    };
  }

  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: process.env.LAMBDA_FUNCTION_NAME,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token })
  };

  try {
    const invokeResponse = await lambda.invoke(invokeParams).promise();
    const responsePayload = JSON.parse(invokeResponse.Payload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unauthorized access";
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: { error: "Unauthorized", message: errorMessage },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Authorization check failed", details: error.message },
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
