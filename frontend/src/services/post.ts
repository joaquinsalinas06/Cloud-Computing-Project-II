import { PostRequest, PostResponse } from "../types/post";

const POST_URL = "https://b2gtwjio0g.execute-api.us-east-1.amazonaws.com/dev";
export const fetchPosts = async (
	payload: PostRequest
): Promise<PostResponse> => {
	console.log("Fetching posts:", payload);
	const url = `${POST_URL}/posts/${payload.provider_id}?page=${payload.page}&limit=${payload.limit}`;

	const response = await fetch(url, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `${localStorage.getItem("token")}`,
		},
	});
	console.log("Response:", response);
	if (!response.ok) {
		throw new Error("Failed to fetch posts");
	}

	const data: PostResponse = await response.json();
	return data;
};

import { PostById } from "../types/post";

export const fetchPost = async (
	provider_id: string,
	post_id: number
): Promise<PostById> => {
	const url = `${POST_URL}/post/${provider_id}/${post_id}`;

	const response = await fetch(url, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `${localStorage.getItem("token")}`,
		},
	});

	if (!response.ok) {
		throw new Error("Failed to fetch post");
	}

	const post: PostById = await response.json();
	return post;
};
