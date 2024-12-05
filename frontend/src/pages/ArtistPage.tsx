import React, { useContext, useEffect, useState, useRef } from "react";
import ProviderContext from "../contexts/ProviderContext";
import { Artist as ArtistType } from "../types/artist";
import { fetchArtists } from "../services/artist";
import Artist from "../components/Artist";
import ThemeWrapper from "../components/ThemeWrapper";

const ArtistPage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [artists, setArtists] = useState<ArtistType[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [hasMore, setHasMore] = useState<boolean>(true);
	const [exclusiveStartKey, setExclusiveStartKey] = useState<
		string | undefined
	>(undefined);
	const [error, setError] = useState<string | null>(null);
	const loaderRef = useRef<HTMLDivElement>(null);

	const loadArtists = async () => {
		if (loading || !hasMore) return;
		setLoading(true);
		try {
			const data = await fetchArtists({
				provider_id: provider,
				limit: 3,
				exclusiveStartKey,
			});

			if (Array.isArray(data.body.items)) {
				setArtists((prevArtists) => {
					const newArtists = data.body.items.filter(
						(artist) =>
							!prevArtists.some(
								(prevArtist) =>
									prevArtist.artist_id === artist.artist_id
							)
					);
					return [...prevArtists, ...newArtists];
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
			setError("Error loading artists");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadArtists();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider]);

	const handleScroll = () => {
		if (loaderRef.current) {
			const bottom = loaderRef.current.getBoundingClientRect().bottom;
			if (bottom <= window.innerHeight && !loading && hasMore) {
				loadArtists();
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
					{artists.length === 0 && !loading ? (
						<p style={{ textAlign: "center" }}>No artists found.</p>
					) : (
						artists.map((artist) => (
							<Artist key={artist.artist_id} artist={artist} />
						))
					)}
				</div>

				{loading && (
					<div style={{ textAlign: "center" }} ref={loaderRef}>
						<span>Loading more artists...</span>
					</div>
				)}

				{!hasMore && !loading && (
					<div style={{ textAlign: "center" }}>
						<span>No more artists to load.</span>
					</div>
				)}

				{hasMore && !loading && (
					<button
						onClick={() => loadArtists()}
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

export default ArtistPage;
