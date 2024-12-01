import React, { useContext, useEffect, useState } from "react";
import ProviderContext from "../contexts/ProviderContext";
import { fetchPosts } from "../services/post";
import { Post as PostType } from "../types/post";
import Post from "../components/Post";
import ThemeWrapper from "../components/ThemeWrapper";

const HomePage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const [posts, setPosts] = useState<PostType[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(1);
	const [hasMore, setHasMore] = useState<boolean>(true);

	const fetchPage = async (page: number) => {
		if (loading || !hasMore) return;
		setLoading(true);

		const payload = {
			provider_id: provider,
			page,
			limit: 3,
		};

		try {
			const response = await fetchPosts(payload);
			const newPosts = response.body.items;

			if (newPosts.length > 0) {
				setPosts((prevPosts) => {
					const updatedPosts = [...prevPosts, ...newPosts];
					return updatedPosts.filter(
						(post, index, self) =>
							index ===
							self.findIndex((p) => p.post_id === post.post_id)
					);
				});
				setHasMore(response.body.pagination.hasNextPage);
			} else {
				setHasMore(false);
			}
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
		} catch (err) {
			setError("Error loading posts");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		setPosts([]);
		setCurrentPage(1);
		setHasMore(true);
		fetchPage(1);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider]);

	useEffect(() => {
		const handleScroll = () => {
			const scrollHeight = document.documentElement.scrollHeight;
			const scrollTop = document.documentElement.scrollTop;
			const clientHeight = document.documentElement.clientHeight;

			if (
				scrollTop + clientHeight >= scrollHeight - 10 &&
				hasMore &&
				!loading
			) {
				setCurrentPage((prev) => prev + 1);
			}
		};

		window.addEventListener("scroll", handleScroll);

		return () => {
			window.removeEventListener("scroll", handleScroll);
		};
	}, [loading, hasMore]);

	useEffect(() => {
		if (currentPage > 1 && hasMore) {
			fetchPage(currentPage);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [currentPage, hasMore]);

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
				{posts.length === 0 && !loading && !error && (
					<p style={{ textAlign: "center" }}>No posts available.</p>
				)}

				<div
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(3, 1fr)",
						gap: "20",
						width: "80%",
						padding: "20px",
						boxSizing: "border-box",
					}}
				>
					{posts.map((post) => (
						<Post key={post.post_id} post={post} />
					))}
				</div>

				{error && (
					<p style={{ color: "red", textAlign: "center" }}>{error}</p>
				)}
				<button
					onClick={() => setCurrentPage((prev) => prev + 1)}
					disabled={!hasMore || loading}
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
					{loading ? "Cargando..." : "Cargar más"}
				</button>
			</div>
		</ThemeWrapper>
	);
};

export default HomePage;
