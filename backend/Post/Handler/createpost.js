const AWS = require("aws-sdk");
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = async function (event) {
  const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
  const { provider_id, user_id, song_id, album_id, titulo, descripcion } = body;
  const token = event.headers?.Authorization;

  if (!provider_id || !user_id || !token) {
    return {
      statusCode: 400,
      body: { error: "Missing parameters or token" }
    };
  }

  let highestPostId = 0;
  try{
    const response =  await dynamoDb.query({
      TableName: process.env.TABLE_NAME,
      KeyConditionExpression: "provider_id = :provider_id",
      ExpressionAttributeValues: {
        ":provider_id": provider_id
      },
      ScanIndexForward: false,
      Limit: 1
    })
    .promise();
    if (response.Items.length > 0) {
      highestPostId = response.Items[0].post_id;
    }

  }catch (error) {
    return {
      statusCode: 500,
      message: { error: "Error querying highest post_id", 
      details: error.message }
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

    console.log("Response Payload:", responsePayload);

    if (!responsePayload.statusCode || responsePayload.statusCode !== 200) {
      const errorMessage = responsePayload.body?.error || "Unknown error";
      return {
        statusCode: 401,
        body: { error: "Unauthorized", message: errorMessage }
      };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: { error: "Authorization check failed", details: error.message }
    };
  }
  function getFormattedDate() {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); 
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
  
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

  const post_id =  highestPostId + 1;
  const params = {
    TableName: process.env.TABLE_NAME,
    Item: {
      provider_id,
      post_id,
      user_id,
      song_id,
      album_id,
      titulo,
      descripcion,
      created_at: getFormattedDate() 
    }
  };

  try {
    await dynamoDb.put(params).promise();
    return {
      statusCode: 201,
      body: { message: "Post created successfully", post_id }
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: { error: "Could not create post", details: error.message }
    };
  }
};
