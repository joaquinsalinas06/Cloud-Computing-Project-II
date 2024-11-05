import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;

export async function handler(event) {
	const { artists } = 
    typeof event.body === "string" ? JSON.parse(event.body) : event.body;

  try {
    const batches = [];
    for (let i = 0; i < artists.length; i += 25) {
      batches.push(artists.slice(i, i + 25));
    }

    const processBatch = async (batch) => {
      const putRequests = batch.map((artist) => ({
        PutRequest: {
          Item: artist,  
        },
      }));

      const params = {
        RequestItems: {
          [TABLE_NAME]: putRequests,
        },
      };

      const result = await dynamodb.batchWrite(params).promise();

      if (result.UnprocessedItems && Object.keys(result.UnprocessedItems).length > 0) {
        await processBatch(result.UnprocessedItems[TABLE_NAME].map((item) => item.PutRequest.Item));
      }
    };

    for (const batch of batches) {
      await processBatch(batch);
    }

    return {
      statusCode: 201,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: `${artists.length} artista(s) creado(s) con éxito`,
        artists,
      }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Error al crear los artistas",
        error: error.message,
      }),
    };
  }
}
