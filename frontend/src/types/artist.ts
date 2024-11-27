export interface ArtistRequest {
	provider_id: string;
	limit?: number;
	exclusiveStartKey?: string;
}

export interface ArtistResponse {
	items: Artist[];
	lastEvaluatedKey?: string;
}

export interface Artist {
	provider_id: string;
	artist_id: number;
	name: string;
	genre: string;
	status: boolean;
	birth_date: string;
	country: string;
	cover_image_url: string;
}
