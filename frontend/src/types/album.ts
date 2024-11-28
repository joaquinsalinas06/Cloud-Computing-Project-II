export interface Album {
	provider_id: string;
	album_id: number;
	title: string;
	release_date: string;
	songs_count: number;
	cover_image_url: string;
	spotify_url: string;
	artist_id: number;
	song_ids: number[];
}

export interface AlbumRequest {
	provider_id: string;
	limit?: number;
	exclusiveStartKey?: string;
}

export interface AlbumResponse {
	body: {
		items: Album[];
		lastEvaluatedKey?: string;
	};
}

export interface AlbumResponseById {
	album: Album;
}
