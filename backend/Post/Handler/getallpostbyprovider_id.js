const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event){
  const { provider_id } = event.pathParameters;

  const params = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
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
      body: JSON.stringify({ error: "Could not retrieve posts", details: error.message }),
    };
  }
}
