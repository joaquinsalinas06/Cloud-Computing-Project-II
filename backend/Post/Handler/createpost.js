const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require("uuid");

module.exports.handler = async function (event) {
  const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const { provider_id, user_id, song_id, playlist_id, titulo, descripcion } = body;
  const token = event.headers?.Authorization;

  if (!provider_id || !user_id || !token) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Missing parameters or token" })
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

    console.log("Response Payload:", responsePayload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unknown error";
      return {
        statusCode: 401,
        body: JSON.stringify({ error: "Unauthorized", message: errorMessage })
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Authorization check failed", details: error.message })
    };
  }

  const post_id = uuidv4();
  const params = {
    TableName: process.env.TABLE_NAME,
    Item: {
      provider_id,
      post_id,
      user_id,
      song_id,
      playlist_id,
      titulo,
      descripcion,
      created_at: new Date().toISOString()
    }
  };

  try {
    await dynamoDb.put(params).promise();
    return {
      statusCode: 201,
      body: JSON.stringify({ message: "Post created successfully", post_id })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not create post", details: error.message })
    };
  }
};
