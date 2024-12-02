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
    Payload: JSON.stringify({ token, provider_id }),
  };

  try {
    const invokeResponse = await lambda.invoke(invokeParams).promise();
    const responsePayload = JSON.parse(invokeResponse.Payload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unauthorized access";
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Unauthorized", message: errorMessage }),
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Authorization check failed", details: error.message }),
    };
  }

  // Parámetros para la consulta a DynamoDB
  const params = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id and post_id = :post_id", // Solo por provider_id y post_id
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":post_id": parseInt(post_id, 10),  
    },
  };

  try {
    const data = await dynamoDb.query(params).promise();
    if (data.Items && data.Items.length > 0) {
      return {
        statusCode: 200,
        body: data.Items[0], 
      };
    } else {
      return {
        statusCode: 404,
        body: { message: "Post not found" },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: { error: "Could not retrieve post", details: error.message },
    };
  }
};
