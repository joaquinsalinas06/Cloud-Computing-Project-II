import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const album =
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  const provider_id = album.provider_id;

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
