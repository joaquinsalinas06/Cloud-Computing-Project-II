import React, { useContext, useEffect, useState, useRef } from "react";
import ProviderContext from "../contexts/ProviderContext";
import { Song as SongType } from "../types/song";
import { fetchSongs } from "../services/song";
import Song from "../components/Song";
import ThemeWrapper from "../components/ThemeWrapper";

const SongPage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [songs, setSongs] = useState<SongType[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [hasMore, setHasMore] = useState<boolean>(true);
	const [exclusiveStartKey, setExclusiveStartKey] = useState<
		string | undefined
	>(undefined);
	const [error, setError] = useState<string | null>(null);
	const loaderRef = useRef<HTMLDivElement>(null);

	const loadSongs = async () => {
		if (loading || !hasMore) return;
		setLoading(true);

		try {
			const data = await fetchSongs({
				provider_id: provider,
				limit: 12,
				exclusiveStartKey,
			});

			if (Array.isArray(data.body.items)) {
				setSongs((prevSongs) => {
					const newSongs = data.body.items.filter(
						(song) =>
							!prevSongs.some(
								(prevSong) => prevSong.song_id === song.song_id
							)
					);
					return [...prevSongs, ...newSongs];
				});
			} else {
				console.error(
					"Expected 'items' to be an array, but got:",
					data.body.items
				);
			}

			setExclusiveStartKey(data.body.lastEvaluatedKey);
			setHasMore(!!data.body.lastEvaluatedKey);
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
		} catch (error) {
			setError("Error loading songs");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadSongs();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider]);

	const handleScroll = () => {
		if (loaderRef.current) {
			const bottom = loaderRef.current.getBoundingClientRect().bottom;
			if (bottom <= window.innerHeight && !loading && hasMore) {
				loadSongs();
			}
		}
	};

	useEffect(() => {
		window.addEventListener("scroll", handleScroll);
		return () => {
			window.removeEventListener("scroll", handleScroll);
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [loading, hasMore]);

	return (
		<ThemeWrapper>
			<div
				style={{
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					justifyContent: "flex-start",
					height: "calc(100vh - 80px)",
					width: "100%",
					backgroundColor: "#121212",
					color: "#fff",
					overflow: "auto",
				}}
			>
				{error && (
					<p style={{ color: "red", textAlign: "center" }}>{error}</p>
				)}

				<div
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(3, 1fr)",
						gap: "40px",
						width: "60%",
						padding: "20px",
						boxSizing: "border-box",
					}}
				>
					{songs.length === 0 && !loading ? (
						<p style={{ textAlign: "center" }}>No songs found.</p>
					) : (
						songs.map((song) => (
							<Song key={song.song_id} song={song} />
						))
					)}
				</div>

				{loading && (
					<div style={{ textAlign: "center" }} ref={loaderRef}>
						<span>Loading more songs...</span>
					</div>
				)}

				{!hasMore && !loading && (
					<div style={{ textAlign: "center" }}>
						<span>No more songs to load.</span>
					</div>
				)}

				{hasMore && !loading && (
					<button
						onClick={() => loadSongs()}
						style={{
							backgroundColor: "#FFFFFF",
							color: "black",
							padding: "12px 24px",
							border: "none",
							borderRadius: "4px",
							cursor: "pointer",
							marginBottom: "20px",
							fontSize: "16px",
						}}
					>
						{loading ? "Loading..." : "Load More"}
					</button>
				)}
			</div>
		</ThemeWrapper>
	);
};

export default SongPage;
