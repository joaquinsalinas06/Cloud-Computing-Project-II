import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const GSI_NAME = process.env.GSI_NAME;

export async function handler(event) {
  const provider_id = event.query?.provider_id;
  const name = event.query?.name;

  console.log("provider_id:", provider_id);
  console.log("name:", name);

  const params = {
    TableName: TABLE_NAME,
    IndexName: GSI_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND #name = :name",
    ExpressionAttributeNames: {
      "#name": "name",
    },
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":name": name,
    },
  };

  try {
    const data = await dynamodb.query(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: data.Items,
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error al obtener los artistas por nombre",
        error: error.message,
      },
    };
  }
}
