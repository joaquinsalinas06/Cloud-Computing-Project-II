const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;
  const post_id = event.path?.post_id;
  const token = event.headers?.Authorization;

  console.log("Received request:", { provider_id, post_id, token });

  if (!provider_id || !post_id || !token) {
    console.log("Missing required parameters or token");
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Missing required parameters or token" }),
    };
  }

  // Validación de post_id (asegurándonos de que sea un número)
  const parsedPostId = parseInt(post_id, 10);
  if (isNaN(parsedPostId)) {
    console.log("Invalid post_id:", post_id);
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Invalid post_id, it should be a number" }),
    };
  }

  // Autorización (verifica si el token es válido)
  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: process.env.LAMBDA_FUNCTION_NAME,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token, provider_id }),
  };

  try {
    console.log("Invoking authorization lambda function...");
    const invokeResponse = await lambda.invoke(invokeParams).promise();
    const responsePayload = JSON.parse(invokeResponse.Payload);
    console.log("Authorization response:", responsePayload);

    if (responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unauthorized access";
      console.log("Unauthorized access:", errorMessage);
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Unauthorized", message: errorMessage }),
      };
    }
  } catch (error) {
    console.log("Authorization check failed:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Authorization check failed", details: error.message }),
    };
  }

  // Parametros para la consulta DynamoDB
  const queryParams = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND post_id = :post_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":post_id": parsedPostId, // Asegurándonos que post_id sea un número
    },
  };

  console.log("Query parameters:", queryParams);

  try {
    // Realiza la consulta para ver si existe el post
    const result = await dynamoDb.query(queryParams).promise();
    console.log("Query result:", result);

    if (result.Items.length === 0) {
      console.log("Post not found");
      return {
        statusCode: 404,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Post not found" }),
      };
    }

    // Parametros para la eliminación
    const deleteParams = {
      TableName: process.env.TABLE_NAME,
      Key: { 
        provider_id: provider_id,  // provider_id es String
        post_id: parsedPostId,     // post_id es un número
      },
    };

    console.log("Delete parameters:", deleteParams);

    // Elimina el post
    await dynamoDb.delete(deleteParams).promise();
    console.log("Post deleted successfully");

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Post deleted successfully" }),
    };
  } catch (error) {
    console.log("Error deleting post:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Could not delete post", details: error.message }),
    };
  }
};
