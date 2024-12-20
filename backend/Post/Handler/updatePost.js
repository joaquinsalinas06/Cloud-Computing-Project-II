const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;  
  const post_id = event.path?.post_id;          
  const token = event.headers?.Authorization;

  const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const { titulo, descripcion } = body;

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

  const parsedPostId = parseInt(post_id, 10);

  if (isNaN(parsedPostId)) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { error: "Invalid post_id format, must be an integer" },
    };
  }

  let updateExpression = "SET";
  const expressionAttributeValues = {};

  if (titulo) {
    updateExpression += " titulo = :titulo,";
    expressionAttributeValues[":titulo"] = titulo;
  }
  if (descripcion) {
    updateExpression += " descripcion = :descripcion,";
    expressionAttributeValues[":descripcion"] = descripcion;
  }

  updateExpression = updateExpression.slice(0, -1);

  if (Object.keys(expressionAttributeValues).length === 0) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { error: "No fields provided to update" },
    };
  }

  const params = {
    TableName: process.env.TABLE_NAME,
    Key: { provider_id, post_id: parsedPostId }, 
    UpdateExpression: updateExpression,
    ExpressionAttributeValues: expressionAttributeValues,
    ReturnValues: "ALL_NEW",
  };

  try {
    const result = await dynamoDb.update(params).promise();
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: { message: "Post updated successfully", post: result.Attributes },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Could not update post", details: error.message },
    };
  }
};
