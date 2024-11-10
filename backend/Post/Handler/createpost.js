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
    return {
      statusCode: 201,
      body: JSON.stringify({ message: "Post created successfully", post_id }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not create post", details: error.message }),
    };
  }
};
