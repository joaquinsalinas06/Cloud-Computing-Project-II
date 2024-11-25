import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
  const provider_id = event.query?.provider_id;

  if (!provider_id) {
    return {
      statusCode: 400,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "The 'providerId' parameter is required.",
      },
    };
  }

  const params = {
    TableName: TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
    },
  };

  try {
    let items = [];
    let lastEvaluatedKey;

    do {
      const response = await dynamodb.query(params).promise();
      items = items.concat(response.Items);
      lastEvaluatedKey = response.LastEvaluatedKey;
      params.ExclusiveStartKey = lastEvaluatedKey;
    } while (lastEvaluatedKey);

    console.log("Total items retrieved:", items.length);

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: { items },
    };
  } catch (error) {
    console.error("Error querying DynamoDB:", error);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        message: "Error retrieving songs",
        error: error.message,
      },
    };
  }
}
