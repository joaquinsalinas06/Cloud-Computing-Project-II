import { PostRequest, PostResponse } from "../types/post";

const POST_URL =
	"https://igs2w5en0l.execute-api.us-east-1.amazonaws.com/dev/posts";
export const fetchPosts = async (
	payload: PostRequest
): Promise<PostResponse> => {
	console.log("Fetching posts:", payload);
	const url = `${POST_URL}/${payload.provider_id}?page=${payload.page}&limit=${payload.limit}`;

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
