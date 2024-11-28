import React, { useContext, useEffect, useState, useRef } from "react";
import ProviderContext from "../contexts/ProviderContext";
import ThemeWrapper from "../components/ThemeWrapper";
import { fetchPosts } from "../services/post";
import { Post } from "../types/post";
import PostComponent from "../components/Post";

const HomePage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [posts, setPosts] = useState<Post[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(1);
	const [hasMore, setHasMore] = useState<boolean>(true);
	const loaderRef = useRef<HTMLDivElement>(null);

	const fetchPage = async (page: number) => {
		if (loading || !hasMore) return;
		setLoading(true);
		const payload = {
			provider_id: provider,
			page,
			limit: 10,
		};
		try {
			const response = await fetchPosts(payload);
			if (response.body.items.length > 0) {
				setPosts((prevPosts) => [...prevPosts, ...response.body.items]);
				setHasMore(response.body.pagination.hasNextPage);
			}
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
		} catch (err) {
			setError("Error loading posts");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchPage(1);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider]);

	useEffect(() => {
		const handleScroll = () => {
			if (loaderRef.current) {
				const bottom = loaderRef.current.getBoundingClientRect().bottom;
				if (bottom <= window.innerHeight && !loading) {
					setCurrentPage((prev) => prev + 1);
				}
			}
		};

		window.addEventListener("scroll", handleScroll);
		return () => {
			window.removeEventListener("scroll", handleScroll);
		};
	}, [loading]);

	useEffect(() => {
		if (currentPage > 1) {
			fetchPage(currentPage);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [currentPage]);

	return (
		<ThemeWrapper>
			<div
				style={{
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					justifyContent: "center",
					height: "100%",
					width: "100%",
				}}
			>
				<div style={{ marginTop: "2rem", width: "100%" }}>
					{loading && <p>Loading posts...</p>}
					{error && <p>{error}</p>}
					{posts.length === 0 && !loading && !error && (
						<p>No posts available.</p>
					)}

					<div style={{ width: "100%" }}>
						{posts.map((post) => (
							<PostComponent key={post.post_id} post={post} />
						))}
					</div>

					{loading && (
						<div
							ref={loaderRef}
							style={{
								textAlign: "center",
								marginTop: "20px",
								padding: "10px",
								color: "#ccc",
							}}
						>
							Loading more posts...
						</div>
					)}
				</div>
			</div>
		</ThemeWrapper>
	);
};

export default HomePage;
