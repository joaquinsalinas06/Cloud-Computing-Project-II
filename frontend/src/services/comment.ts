import { CommentRequest, CommentResponse } from "../types/comment";

const COMMENT_URL =
	"https://99xdh4cl89.execute-api.us-east-1.amazonaws.com/dev/comments";

export const fetchComments = async (
	payload: CommentRequest
): Promise<CommentResponse> => {
	const { provider_id, post_id, page = 1, pageSize = 10 } = payload;
	console.log("Fetching comments for post:", payload);
	const url = `${COMMENT_URL}/post/${provider_id}/${post_id}?page=${page}&pageSize=${pageSize}`;

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
