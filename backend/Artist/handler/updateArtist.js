import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = "artist-api-table";

export async function handler(event) {
  const { provider_id, ...updateData } = JSON.parse(event.body);
  const artistId = event.pathParameters.artistId;

  const updateExpression = Object.keys(updateData)
    .map((key, index) => `#key${index} = :value${index}`)
    .join(", ");

  const expressionAttributeNames = Object.keys(updateData).reduce((acc, key, index) => {
    acc[`#key${index}`] = key;
    return acc;
  }, {});

  const expressionAttributeValues = Object.keys(updateData).reduce((acc, key, index) => {
    acc[`:value${index}`] = updateData[key];
    return acc;
  }, {});

  const params = {
    TableName: TABLE_NAME,
    Key: { provider_id, artistId },
    UpdateExpression: `SET ${updateExpression}`,
    ExpressionAttributeNames: expressionAttributeNames,
    ExpressionAttributeValues: expressionAttributeValues,
  };

  try {
    await dynamodb.update(params).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Artista actualizado con éxito",
        artistId,
        updateData,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al actualizar el artista",
        error: error.message,
      }),
    };
  }
}
