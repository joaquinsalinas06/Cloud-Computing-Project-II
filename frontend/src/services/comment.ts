import { CommentRequest, CommentResponse } from "../types/comment";

const COMMENT_URL =
	"https://vytaaq9yq0.execute-api.us-east-1.amazonaws.com/dev";

export const fetchComments = async (
	payload: CommentRequest
): Promise<CommentResponse> => {
	const { provider_id, post_id, page = 1, pageSize = 10 } = payload;
	console.log("Fetching comments for post:", payload);
	const url = `${COMMENT_URL}/comments/post/${provider_id}/${post_id}?page=${page}&pageSize=${pageSize}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});
		console.log("Response:", response);

		if (!response.ok) {
			throw new Error("Failed to fetch comments");
		}

		const data: CommentResponse = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching comments:", error);
		throw new Error("Error fetching comments");
	}
};

import { CommentRequestCreate, CommentResponseCreate } from "../types/comment";

export const createComment = async (
	payload: CommentRequestCreate
): Promise<CommentResponseCreate> => {
	const { provider_id, post_id, user_id, text } = payload;

	const url = `${COMMENT_URL}/comment/${provider_id}/${user_id}/${post_id}`;

	try {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
			body: JSON.stringify({ text }),
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData?.message || "Failed to create comment");
		}

		const data: CommentResponseCreate = await response.json();
		return data;
	} catch (error) {
		console.error("Error creating comment:", error);
		throw new Error("Error creating comment");
	}
};
