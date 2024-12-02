import { Pagination } from "./pagination";

export interface Post {
	provider_id: string;
	post_id: number;
	user_id: number;
	song_id: number;
	album_id: number;
	description: string;
	created_at: string;
}

export interface PostById {
	statusCode: number;
	body: Post;
}

export interface PostRequest {
	provider_id: string;
	page: number;
	limit: number;
}

export interface PostResponse {
	statusCode: number;
	body: {
		items: Post[];
		pagination: Pagination;
	};
}
