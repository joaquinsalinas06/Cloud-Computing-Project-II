import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const INDEX_NAME = process.env.INDEX_NAME;

export async function handler(event) {
  const title = event.query?.title;
  const limit = event.query?.limit || 10;
  let exclusiveStartKey = event.query?.exclusiveStartKey
    ? JSON.parse(decodeURIComponent(event.query.exclusiveStartKey))
    : null;

  console.log(event);

  if (!title) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: {
        message: "The parameter: title is missing",
      },
    };
  }
  const params = {
    TableName: TABLE_NAME,
    IndexName: INDEX_NAME,
    KeyConditionExpression: "title = :title",
    ExpressionAttributeValues: {
      ":title": title,
    },
    Limit: limit,
    ExclusiveStartKey: exclusiveStartKey ? exclusiveStartKey : undefined,
  };

  try {
    const response = await dynamodb.query(params).promise();
    console.log("DynamoDB response:", response);

    if (response.Count === 0) {
      return {
        statusCode: 404,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          message: "No albums found",
        },
      };
    } else {
      return {
        statusCode: 200,
        headers: {
          "Content-Type": "application/json",
        },
        body: {
          items: response.Items,
          lastEvaluatedKey: response.LastEvaluatedKey
            ? encodeURIComponent(JSON.stringify(response.LastEvaluatedKey))
            : null,
        },
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "An error occurred while getting the album by title",
        error: error.message,
      },
    };
  }
}
