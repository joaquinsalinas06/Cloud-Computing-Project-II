const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;

  const page = parseInt(event.query?.page) || 1;
  const pageSize = parseInt(event.query?.limit) || 10;
  if (!provider_id) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Missing provider_id" }),
    };
  }

  if (page < 1 || pageSize < 1) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Page and pageSize must be greater than 0" }),
    };
  }

  const params = {
    TableName: process.env.TABLE_NAME,
    KeyConditionExpression: "provider_id = :provider_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
    },
    Limit: pageSize,
  };

  let items = [];
  let currentPage = 1;
  let lastEvaluatedKey = null;

  try {
    while (currentPage < page) {
      const result = await dynamoDb.query({ ...params, ExclusiveStartKey: lastEvaluatedKey }).promise();
      lastEvaluatedKey = result.LastEvaluatedKey;

      if (!lastEvaluatedKey) {
        return {
          statusCode: 200,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            items: [], 
            pagination: {
              currentPage: page,
              pageSize: pageSize,
              totalItems: 0,
              totalPages: currentPage - 1,
              hasNextPage: false,
              hasPreviousPage: page > 1
            }
          }),
        };
      }
      currentPage++;
    }

    const result = await dynamoDb.query({ ...params, ExclusiveStartKey: lastEvaluatedKey }).promise();
    items = result.Items;
    lastEvaluatedKey = result.LastEvaluatedKey;

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: {
        items: items,
        pagination: {
          currentPage: page,
          pageSize: pageSize,
          hasNextPage: !!lastEvaluatedKey,
          hasPreviousPage: page > 1,
          lastEvaluatedKey: lastEvaluatedKey ?lastEvaluatedKey : null
        }
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: { error: "Could not retrieve posts", details: error.message },
    };
  }
};
