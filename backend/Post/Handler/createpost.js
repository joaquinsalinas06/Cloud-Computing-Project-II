const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require("uuid");

module.exports.handler = async function (event) {
  const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const { provider_id, user_id, song_id, playlist_id, titulo, descripcion } = body;
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
    const response = {
      statusCode: 201,
      body: { message: "Post created successfully", post_id }
    };
    response.body = JSON.stringify(response.body);
    return response;
  } catch (error) {
    const errorResponse = {
      statusCode: 500,
      body: { error: "Could not create post", details: error.message }
    };
    errorResponse.body = JSON.stringify(errorResponse.body); 
    return errorResponse;
  }
};
