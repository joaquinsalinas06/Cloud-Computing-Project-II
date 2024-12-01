import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const songs =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const provider_id = event.path?.provider_id;
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

  if (!Array.isArray(songs) || songs.length === 0) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "A list of songs is required",
      },
    };
  }

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

  let failedSongs = [];
  let createdSongs = [];

  for (let song of songs) {
    const provider_id = song.provider_id;
    let highestSongId = 0;

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
        highestSongId = response.Items[0].song_id;
      }
    } catch (error) {
      failedSongs.push({
        song,
        error: `Error al consultar el songId más alto: ${error.message}`,
      });
      continue;
    }

    song.song_id = highestSongId + 1;

    const params = {
      TableName: TABLE_NAME,
      Item: song,
      ConditionExpression:
        "attribute_not_exists(provider_id) AND attribute_not_exists(song_id)",
    };

    try {
      await dynamodb.put(params).promise();
      createdSongs.push(song);
    } catch (error) {
      failedSongs.push({
        song,
        error: `Error creating the song: ${error.message}`,
      });
    }
  }

  return {
    statusCode: 201,
    headers: {
      "Content-Type": "application/json",
    },
    body: {
      message: "Process completed",
      createdSongs,
      failedSongs,
    },
  };
}
