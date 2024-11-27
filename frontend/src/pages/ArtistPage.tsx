import React, { useEffect, useState, useContext, useRef } from "react";
import ProviderContext from "../contexts/ProviderContext";
import { Artist } from "../types/artist";
import { fetchArtists } from "../services/artist";
import ArtistComponent from "../components/Artist";

const ArtistPage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [artists, setArtists] = useState<Artist[]>([]);
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
				limit: 10,
				exclusiveStartKey,
			});

			setArtists((prevArtists) => [...prevArtists, ...data.items]);
			setExclusiveStartKey(data.lastEvaluatedKey);
			setHasMore(!!data.lastEvaluatedKey);
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
		<div
			className="flex flex-col items-center p-4 overflow-auto"
			style={{ maxHeight: "calc(100vh - 4rem)" }}
		>
			<h1 className="text-3xl font-semibold text-gray-800 mb-4">
				Artists
			</h1>

			{error && <p className="text-red-500">{error}</p>}

			<div className="flex flex-wrap justify-center">
				{artists.length === 0 && !loading ? (
					<p>No artists found.</p>
				) : (
					artists.map((artist) => (
						<ArtistComponent
							key={artist.artist_id}
							artist={artist}
						/>
					))
				)}
			</div>

			{loading && (
				<div className="mt-4 text-center" ref={loaderRef}>
					<span>Loading more artists...</span>
				</div>
			)}

			{!hasMore && !loading && (
				<div className="mt-4 text-center">
					<span>No more artists to load.</span>
				</div>
			)}
		</div>
	);
};

export default ArtistPage;
