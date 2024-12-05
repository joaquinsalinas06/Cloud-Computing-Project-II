import { SongRequest, SongResponse, SongResponseById } from "../types/song";

const SONG_URL =
	"https://gc4irka306.execute-api.us-east-1.amazonaws.com/dev/song";

export const fetchSongs = async (
	payload: SongRequest
): Promise<SongResponse> => {
	const { provider_id, limit = 6, exclusiveStartKey } = payload;
	const url = `${SONG_URL}/all/${provider_id}?limit=${limit}&exclusiveStartKey=${encodeURIComponent(
		exclusiveStartKey || ""
	)}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});

		if (!response.ok) {
			throw new Error("Failed to fetch songs");
		}

		const data: SongResponse = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching songs:", error);
		throw new Error("Error fetching songs");
	}
};

export const fetchSongById = async (
	provider_id: string,
	song_id: number
): Promise<SongResponseById> => {
	const url = `${SONG_URL}/${provider_id}/${song_id}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});

		if (!response.ok) {
			throw new Error("Failed to fetch song");
		}

		const data: SongResponseById = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching song:", error);
		throw new Error("Error fetching song");
	}
};
