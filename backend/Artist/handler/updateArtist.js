import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const { provider_id, ...updateData } = JSON.parse(event.body);
  const artistId = event.pathParameters.artistId;
  const token = event.headers?.Authorization;
  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: token_function,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token }),
  };

  try {
    const invokeResponse = await lambda.invoke(invokeParams).promise();
    const responsePayload = JSON.parse(invokeResponse.Payload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unauthorized access";
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: { error: "Unauthorized", message: errorMessage },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Authorization check failed", details: error.message },
    };
  }

  const updateExpression = Object.keys(updateData)
    .map((key, index) => `#key${index} = :value${index}`)
    .join(", ");

  const expressionAttributeNames = Object.keys(updateData).reduce(
    (acc, key, index) => {
      acc[`#key${index}`] = key;
      return acc;
    },
    {}
  );

  const expressionAttributeValues = Object.keys(updateData).reduce(
    (acc, key, index) => {
      acc[`:value${index}`] = updateData[key];
      return acc;
    },
    {}
  );

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
      body: {
        message: "Artista actualizado con éxito",
        artistId,
        updateData,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error al actualizar el artista",
        error: error.message,
      },
    };
  }
}
