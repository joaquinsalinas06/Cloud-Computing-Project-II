import React from "react";
import { Post as PostType } from "../types/post";

interface PostProps {
	post: PostType;
}

const Post: React.FC<PostProps> = ({ post }) => {
	return (
		<div
			style={{
				backgroundColor: "rgba(255, 255, 255, 0.1)",
				borderRadius: "8px",
				padding: "1rem",
				marginBottom: "1rem",
				boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
				maxWidth: "600px",
				width: "100%",
			}}
		>
			<h3 style={{ fontSize: "1.25rem", fontWeight: "bold" }}>
				Post ID: {post.post_id} - {post.description}
			</h3>
			<p>Provider: {post.provider_id}</p>
			<p>
				Song ID: {post.song_id} | Album ID: {post.album_id}
			</p>
			<p>Created At: {post.created_at}</p>
		</div>
	);
};

export default Post;
