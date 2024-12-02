import React from "react";
import { useNavigate } from "react-router-dom";
import { Post as PostType } from "../types/post";

interface PostProps {
	post: PostType;
}

const Post: React.FC<PostProps> = ({ post }) => {
	const navigate = useNavigate();

	const handleClick = () => {
		navigate(`/post/${post.post_id}`);
	};

	return (
		<div
			onClick={handleClick}
			className="cursor-pointer bg-gray-100 rounded-lg p-4 mb-4 shadow-md hover:bg-gray-200"
		>
			<h3 className="text-xl font-bold">{post.description}</h3>
			<p className="text-sm text-gray-500">
				Created At: {post.created_at}
			</p>
		</div>
	);
};

export default Post;
