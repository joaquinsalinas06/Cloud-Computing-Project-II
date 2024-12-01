import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.path?.provider_id;
  const album =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  const token = event.headers?.Authorization;

  if (!token) {
    return {
      statusCode: 401,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        error: "Unauthorized",
        message: "Token is required",
      },
    };
  }

  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: token_function,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token, provider_id }),
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

  let highestAlbumId = 0;

  try {
    const response = await dynamodb
      .query({
        TableName: TABLE_NAME,
        KeyConditionExpression: "provider_id = :provider_id",
        ExpressionAttributeValues: {
          ":provider_id": provider_id,
        },
        ScanIndexForward: false,
        Limit: 1,
      })
      .promise();

    if (response.Items.length > 0) {
      highestAlbumId = response.Items[0].album_id;
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error getting highest album id",
        error: error.message,
      },
    };
  }

  album.album_id = highestAlbumId + 1;

  const params = {
    TableName: TABLE_NAME,
    Item: album,
    ConditionExpression:
      "attribute_not_exists(provider_id) AND attribute_not_exists(album_id)",
  };

  try {
    await dynamodb.put(params).promise();
    return {
      statusCode: 201,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Album was created successfully",
        album: album,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "An error occurred while creating the album",
        error: error.message,
      },
    };
  }
}
