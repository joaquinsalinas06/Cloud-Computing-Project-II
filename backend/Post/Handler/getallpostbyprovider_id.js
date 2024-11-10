const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event){
  const provider_id = event.path?.provider_id;

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
      body: result.Items,
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: { error: "Could not retrieve posts", details: error.message },
    };
  }
}
