import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
	const { provider_id } = JSON.parse(event.body);
  const artistId = event.pathParameters.artistId;

  const params = {
    TableName: TABLE_NAME,
    Key: {
      provider_id,
      artistId,
    },
  };

  try {
    const data = await dynamodb.get(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data.Item),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al obtener el artista",
        error: error.message,
      }),
    };
  }
}
