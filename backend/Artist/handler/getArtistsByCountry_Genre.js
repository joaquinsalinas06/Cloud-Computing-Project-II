import AWS from "aws-sdk";

const { DynamoDB } = AWS;
const dynamodb = new DynamoDB.DocumentClient();
const TABLE_NAME = process.env.TABLE_NAME;
const GSI_NAME = process.env.GSI;

export const handler = async (event) => {
    const country = event.query?.country;
    const genre = event.query?.genre;
    const limit = event.query?.limit || 10;
    let exclusiveStartKey = event.query?.exclusiveStartKey
        ? JSON.parse(decodeURIComponent(event.query?.exclusiveStartKey))
        : null;

    const token = event.headers?.Authorization;

    if (!token) {
        return {
            statusCode: 401,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                error: "Unauthorized",
                message: "Token is required",
            }),
        };
    }

    const token_function = process.env.LAMBDA_FUNCTION_NAME;

    if (!country) {
        return {
            statusCode: 400,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: "'country' parameter is required.",
            }),
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
                body: JSON.stringify({ error: "Unauthorized", message: errorMessage }),
            };
        }
    } catch (error) {
        return {
            statusCode: 401,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                error: "Unauthorized",
                message: "Token is required",
            }),
        };
    }

    const params = {
        TableName: TABLE_NAME,
        IndexName: GSI_NAME,
        KeyConditionExpression: "#country = :country AND #genre = :genre",
        ExpressionAttributeNames: {
            "#country": "country",
            "#genre": "genre",
        },
        ExpressionAttributeValues: {
            ":country": country,
            ":genre": genre,
        },
        Limit: limit,
        ExclusiveStartKey: exclusiveStartKey,
    };
    
    try {
        const data = await dynamodb.query(params).promise();
        return {
            statusCode: 200,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: data.Items,
                exclusiveStartKey: data.LastEvaluatedKey
                    ? encodeURIComponent(JSON.stringify(data.LastEvaluatedKey))
                    : null,
            }),
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                error: "Internal Server Error",
                message: error.message,
            }),
        };
    }
};
