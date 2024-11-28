export interface Song {
	provider_id: string;
	song_id: number;
	title: string;
	genre: string;
	release_date: string;
	duration: string;
	cover_image_url: string;
	times_played: number;
	song_url: string;
	preview_music_url: string;
	album_id: number;
	artist_id: number;
}

export interface SongRequest {
	provider_id: string;
	limit?: number;
	exclusiveStartKey?: string;
}

export interface SongResponse {
	body: {
		items: Song[];
		lastEvaluatedKey?: string;
	};
}

export interface SongResponseById {
	song: Song;
}
