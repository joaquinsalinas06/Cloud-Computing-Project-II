import React, { useEffect, useState } from "react";
import { Post as PostType } from "../types/post";
import { UserResponse } from "../types/user";
import { fetchUser } from "../services/user";

interface PostProps {
	post: PostType;
}

const Post: React.FC<PostProps> = ({ post }) => {
	const [username, setUsername] = useState<string | null>(null);
	const [, setLoading] = useState<boolean>(false);
	const [, setError] = useState<string | null>(null);

	useEffect(() => {
		const loadUsername = async () => {
			if (!post.provider_id || !post.user_id) {
				setError("Provider ID or User ID is missing.");
				return;
			}

			setLoading(true);
			try {
				const userData: UserResponse = await fetchUser({
					provider_id: post.provider_id,
					user_id: post.user_id,
				});
				setUsername(userData.username);
				setError(null);
			} catch (err) {
				console.error("Error fetching username:", err);
				setError("Failed to load username.");
			} finally {
				setLoading(false);
			}
		};

		loadUsername();
	}, [post.provider_id, post.user_id]);

	return (
		<div
			style={{
				backgroundColor: "rgba(255, 255, 255, 0.1)",
				borderRadius: "8px",
				padding: "1rem",
				marginBottom: "1rem",
				boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
				maxWidth: "600px",
				width: "80%",
			}}
		>
			<h3 style={{ fontSize: "1.25rem", fontWeight: "bold" }}>
				{username}
			</h3>
			<p>{post.description}</p>
			<p>Created At: {post.created_at}</p>
		</div>
	);
};

export default Post;
