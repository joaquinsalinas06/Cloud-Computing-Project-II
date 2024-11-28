import React, { useContext, useEffect, useState, useRef } from "react";
import ProviderContext from "../contexts/ProviderContext";
import { Album as AlbumType } from "../types/album";
import { fetchAlbums } from "../services/album";
import Album from "../components/Album";
import ThemeWrapper from "../components/ThemeWrapper";

const AlbumPage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [albums, setAlbums] = useState<AlbumType[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [hasMore, setHasMore] = useState<boolean>(true);
	const [exclusiveStartKey, setExclusiveStartKey] = useState<
		string | undefined
	>(undefined);
	const [error, setError] = useState<string | null>(null);
	const loaderRef = useRef<HTMLDivElement>(null);

	const loadAlbums = async () => {
		if (loading || !hasMore) return;
		setLoading(true);

		try {
			const data = await fetchAlbums({
				provider_id: provider,
				limit: 12,
				exclusiveStartKey,
			});

			if (Array.isArray(data.body.items)) {
				setAlbums((prevAlbums) => {
					const newAlbums = data.body.items.filter(
						(album) =>
							!prevAlbums.some(
								(prevAlbum) =>
									prevAlbum.album_id === album.album_id
							)
					);
					return [...prevAlbums, ...newAlbums];
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
			setError("Error loading albums");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadAlbums();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider]);

	const handleScroll = () => {
		if (loaderRef.current) {
			const bottom = loaderRef.current.getBoundingClientRect().bottom;
			if (bottom <= window.innerHeight && !loading && hasMore) {
				loadAlbums();
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
					{albums.length === 0 && !loading ? (
						<p style={{ textAlign: "center" }}>No albums found.</p>
					) : (
						albums.map((album) => (
							<Album key={album.album_id} album={album} />
						))
					)}
				</div>

				{loading && (
					<div style={{ textAlign: "center" }} ref={loaderRef}>
						<span>Loading more albums...</span>
					</div>
				)}

				{!hasMore && !loading && (
					<div style={{ textAlign: "center" }}>
						<span>No more albums to load.</span>
					</div>
				)}

				{hasMore && !loading && (
					<button
						onClick={() => loadAlbums()}
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

export default AlbumPage;
