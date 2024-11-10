const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const { provider_id, song_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    IndexName: process.env.INDEXGSI1_TABLE1_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND song_id = :song_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":song_id": song_id,
    },
  };

  try {
    const result = await dynamoDb.query(params).promise();
    return {
      statusCode: 200,
      body: JSON.stringify(result.Items),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Could not retrieve post by song_id", details: error.message }),
    };
  }
}
