const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const provider_id = event.path?.provider_id;
  const album_id = event.path?.album_id;
  const token = event.headers?.Authorization;
  const page = parseInt(event.query?.page) || 1;
  const pageSize = parseInt(event.query?.limit) || 10;
  if (!provider_id  || !album_id || !token) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { error: "Missing required parameters or token" },
    };
  }
  const lambda = new AWS.Lambda();
  const invokeParams = {
    FunctionName: process.env.LAMBDA_FUNCTION_NAME,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ token })
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


  if (page < 1 || pageSize < 1) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: { error: "Page and pageSize must be greater than 0" },
    };
  }


  const params = {
    TableName: process.env.TABLE_NAME,
    IndexName: process.env.INDEXGSI2_TABLE1_NAME,
    KeyConditionExpression: "provider_id = :provider_id AND album_id = :album_id",
    ExpressionAttributeValues: {
      ":provider_id": provider_id,
      ":album_id": album_id,
    },
    Limit: pageSize,
    ScanIndexForward: true, 
  };
  let items = [];
  let currentPage = 1;
  let lastEvaluatedKey = null;
  try {
    while (currentPage < page) {
      const result = await dynamoDb.query({ ...params, ExclusiveStartKey: lastEvaluatedKey }).promise();
      lastEvaluatedKey = result.LastEvaluatedKey;

      if (!lastEvaluatedKey) {
        break;
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
        items: items.length > 0 ? items : [{ message: "No more items" }],  
        pagination: {
          currentPage: page,
          pageSize: pageSize,
          hasNextPage: !!lastEvaluatedKey,
          hasPreviousPage: page > 1,
          lastEvaluatedKey: lastEvaluatedKey || null
        }
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      pagination: {
        currentPage: page,
        pageSize: pageSize,
        hasNextPage: false,
        hasPreviousPage: page > 1,
        lastEvaluatedKey: lastEvaluatedKey || null
      },
      headers: { "Content-Type": "application/json" },
      body: { error: "Could not retrieve posts", details: error.message },
    };
  }
};
