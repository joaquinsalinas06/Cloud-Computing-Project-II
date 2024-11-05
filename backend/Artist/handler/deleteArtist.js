const AWS = require("aws-sdk");

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = "artist-api-table";

module.exports.handler = async (event) => {
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
    await dynamodb.delete(params).promise();
    return {
      statusCode: 204,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Artista eliminado con éxito",
        artistId,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al eliminar el artista",
        error: error.message,
      }),
    };
  }
}
