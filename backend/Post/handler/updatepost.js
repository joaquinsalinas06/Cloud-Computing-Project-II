const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

export async function handler(event) {
  const { provider_id, post_id } = event.pathParameters;
  const { titulo, descripcion } = JSON.parse(event.body);

  const params = {
    TableName: process.env.TABLE_NAME,
    Key: { provider_id, post_id },
    UpdateExpression: "SET titulo = :titulo, descripcion = :descripcion",
    ExpressionAttributeValues: {
      ":titulo": titulo,
      ":descripcion": descripcion,
    },
    ReturnValues: "ALL_NEW",
  };

  try {
    const result = await dynamoDb.update(params).promise();
    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Post updated successfully", post: result.Attributes }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not update post", details: error.message }),
    };
  }
}
