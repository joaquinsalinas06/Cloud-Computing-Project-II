import React, { useEffect, useState, useContext } from "react";
import { fetchArtistById } from "../services/artist";
import { Album as AlbumType } from "../types/album";
import { ArtistResponseById } from "../types/artist";
import ProviderContext from "../contexts/ProviderContext";

interface AlbumProps {
	album: AlbumType;
}

const Album: React.FC<AlbumProps> = ({ album }) => {
	const [artistName, setArtistName] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const context = useContext(ProviderContext);
	const theme = context?.theme;
	const releaseDate = new Date(album.release_date).toLocaleDateString();

	useEffect(() => {
		const loadArtistName = async () => {
			if (!album.artist_id) {
				setError("Artist ID is missing.");
				return;
			}

			setLoading(true);
			try {
				const artistData: ArtistResponseById = await fetchArtistById({
					provider_id: localStorage.getItem("provider") || "",
					artist_id: album.artist_id,
				});
				setArtistName(artistData.body.name);
				setError(null);
				// eslint-disable-next-line @typescript-eslint/no-unused-vars
			} catch (err) {
				setError("Failed to load artist name.");
			} finally {
				setLoading(false);
			}
		};

		loadArtistName();
	}, [album.artist_id]);

	return (
		<div
			style={{
				backgroundColor: "rgba(255, 255, 255, 0.1)",
				borderRadius: "8px",
				padding: "1rem",
				marginBottom: "1rem",
				width: "100%",
				height: "100%",
				boxSizing: "border-box",
			}}
		>
			<div
				style={{
					height: "300px",
					width: "100%",
				}}
			>
				<img
					src={album.cover_image_url}
					alt={album.title}
					style={{
						objectFit: "cover",
						width: "100%",
						height: "100%",
						borderRadius: "8px",
					}}
				/>
			</div>

			<div style={{ padding: "1rem 0", textAlign: "left" }}>
				<h2
					style={{
						fontSize: "1.25rem",
						fontWeight: "bold",
						color: "#f8f8f8",
						marginBottom: "0.5rem",
					}}
				>
					{album.title}
				</h2>
				<p
					style={{
						fontSize: "0.875rem",
						color: "#ccc",
						marginBottom: "0.5rem",
					}}
				>
					<strong>Artist:</strong>{" "}
					{loading
						? "Loading..."
						: error
						? "Error loading artist"
						: artistName || "Unknown Artist"}
				</p>
				<p
					style={{
						fontSize: "0.875rem",
						color: "#ccc",
						marginBottom: "0.5rem",
					}}
				>
					<strong>Release Date:</strong> {releaseDate}
				</p>
				<p
					style={{
						fontSize: "0.875rem",
						color: "#ccc",
						marginBottom: "0.5rem",
					}}
				>
					<strong>Songs:</strong> {album.songs_count}
				</p>
				<a
					href={album.spotify_url}
					target="_blank"
					rel="noopener noreferrer"
					style={{
						color: theme?.primaryColor,
						fontSize: "0.875rem",
						textDecoration: "none",
						marginTop: "1rem",
						display: "inline-block",
					}}
				>
					Listen on Spotify
				</a>
			</div>
		</div>
	);
};

export default Album;
