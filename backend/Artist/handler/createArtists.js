import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const artists =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const token = event.headers?.Authorization;
  const token_function = process.env.LAMBDA_FUNCTION_NAME;

  if (!Array.isArray(artists) || artists.length === 0) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "A list of artists is required",
      },
    };
  }

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


  let failedArtists = [];
  let createdArtists = [];

  for (let artist of artists) {
    const provider_id = artist.provider_id;
    let highestArtistId = 0;

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
        highestArtistId = response.Items[0].artist_id;
      }
    } catch (error) {
      failedArtists.push({
        artist,
        error: `Error querying the highest artistId: ${error.message}`,
      });
      continue;
    }

    artist.artist_id = highestArtistId + 1;

    const params = {
      TableName: TABLE_NAME,
      Item: artist,
      ConditionExpression:
        "attribute_not_exists(provider_id) AND attribute_not_exists(artist_id)",
    };

    try {
      await dynamodb.put(params).promise();
      createdArtists.push(artist);
    } catch (error) {
      failedArtists.push({
        artist,
        error: `Error creating the artist: ${error.message}`,
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
      createdArtists,
      failedArtists,
    },
  };
}
