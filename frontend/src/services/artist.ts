import { ArtistRequest, ArtistResponse } from "../types/artist";
import { ArtistRequestById, ArtistResponseById } from "../types/artist";

const ARTIST_URL =
	"https://f5ta3qzwfi.execute-api.us-east-1.amazonaws.com/dev/artist";

export const fetchArtists = async (
	payload: ArtistRequest
): Promise<ArtistResponse> => {
	const { provider_id, limit = 3, exclusiveStartKey } = payload;
	const url = `${ARTIST_URL}/all/${provider_id}?limit=${limit}&exclusiveStartKey=${encodeURIComponent(
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
			throw new Error("Failed to fetch artists");
		}
		const data: ArtistResponse = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching artists:", error);
		throw new Error("Error fetching artists");
	}
};

export const fetchArtistById = async (
	payload: ArtistRequestById
): Promise<ArtistResponseById> => {
	const { provider_id, artist_id } = payload;
	const url = `${ARTIST_URL}/${provider_id}/${artist_id}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});
		console.log("fetchArtistById", response);

		if (!response.ok) {
			throw new Error("Failed to fetch artist");
		}

		const data: ArtistResponseById = await response.json();
		return data;
	} catch (error) {
		console.error("Error fetching artist:", error);
		throw new Error("Error fetching artist");
	}
};
