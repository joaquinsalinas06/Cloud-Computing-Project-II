import { AlbumRequest, AlbumResponse, AlbumResponseById } from "../types/album";

const ALBUM_URL =
	"https://hil58kwcuk.execute-api.us-east-1.amazonaws.com/dev/album";

export const fetchAlbums = async (
	payload: AlbumRequest
): Promise<AlbumResponse> => {
	const { provider_id, limit = 3, exclusiveStartKey } = payload;
	const url = `${ALBUM_URL}/all/${provider_id}?limit=${limit}&exclusiveStartKey=${encodeURIComponent(
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
			throw new Error("Failed to fetch albums");
		}

		const data: AlbumResponse = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching albums:", error);
		throw new Error("Error fetching albums");
	}
};

export const fetchAlbumById = async (
	provider_id: string,
	album_id: number
): Promise<AlbumResponseById> => {
	const url = `${ALBUM_URL}/${provider_id}/${album_id}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});

		if (!response.ok) {
			throw new Error("Failed to fetch album");
		}

		const data: AlbumResponseById = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching album:", error);
		throw new Error("Error fetching album");
	}
};
