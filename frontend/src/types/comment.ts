export interface CommentRequest {
	provider_id: string;
	post_id: number;
	page?: number;
	pageSize?: number;
	start_date?: string;
	end_date?: string;
}

export interface CommentResponse {
	comments: Array<{
		Comment: Comment;
	}>;
	pagination: {
		currentPage: number;
		pageSize: number;
		totalItems: number;
		totalPages: number;
		hasNextPage: boolean;
		hasPreviousPage: boolean;
	};
}

export interface Comment {
	provider_id: string;
	comment_id: number;
	post_id: number;
	user_id: number;
	text: string;
	date: string;
}
