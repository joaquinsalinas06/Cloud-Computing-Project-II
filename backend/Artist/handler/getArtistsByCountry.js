const AWS = require("aws-sdk");

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = "artist-api-table";
const LSI_NAME = "CountryIndex"; 

export async function handler(event) {
  const { provider_id, country } = JSON.parse(event.body);

  const params = {
    TableName: TABLE_NAME,
    IndexName: LSI_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND country = :country",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":country": country,
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data.Items), 
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al obtener los artistas por país",
        error: error.message,
      }),
    };
  }
}
