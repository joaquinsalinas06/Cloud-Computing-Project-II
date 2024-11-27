import { ArtistRequest, ArtistResponse } from "../types/artist";

const ARTIST_URL =
	"https://740z32b6v4.execute-api.us-east-1.amazonaws.com/dev/artist";

export const fetchArtists = async (
	payload: ArtistRequest
): Promise<ArtistResponse> => {
	const { provider_id, limit = 10, exclusiveStartKey } = payload;
	const url = `${ARTIST_URL}/allWP?provider_id=${provider_id}&limit=${limit}&exclusiveStartKey=${encodeURIComponent(
		exclusiveStartKey || ""
	)}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
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
