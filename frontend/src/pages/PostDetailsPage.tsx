import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPost } from "../services/post";
import { fetchComments } from "../services/comment";
import { Post } from "../types/post";
import { CommentResponse } from "../types/comment";
import ProviderContext from "../contexts/ProviderContext";

const PostDetailsPage: React.FC = () => {
	const { post_id } = useParams<{
		post_id: string;
	}>();
	const [post, setPost] = useState<Post | null>(null);
	const { provider } = useContext(ProviderContext)!;
	const [comments, setComments] = useState<CommentResponse | null>(null);
	const [loadingPost, setLoadingPost] = useState<boolean>(true);
	const [loadingComments, setLoadingComments] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const loadPost = async () => {
			try {
				const postData = await fetchPost(provider, parseInt(post_id!));
				setPost(postData);
			} catch (err) {
				console.error("Error fetching post:", err);
				setError("Failed to load post details.");
			} finally {
				setLoadingPost(false);
			}
		};

		const loadComments = async () => {
			try {
				const response = await fetchComments({
					provider_id: provider,
					post_id: parseInt(post_id!),
					page: 1,
					pageSize: 10,
				});
				setComments(response);
			} catch (err) {
				console.error("Error fetching comments:", err);
				setError("Failed to load comments.");
			} finally {
				setLoadingComments(false);
			}
		};

		loadPost();
		loadComments();
	}, [provider, post_id]);

	if (loadingPost || loadingComments) return <p>Loading...</p>;
	if (error) return <p className="text-red-500">{error}</p>;

	return (
		<div className="p-6 bg-gray-100 min-h-screen">
			<div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-4 mb-8">
				<h1 className="text-2xl font-bold">{post?.description}</h1>
				<p>
					Song ID: {post?.song_id} | Album ID: {post?.album_id}
				</p>
				<p className="text-sm text-gray-500">
					Created At: {post?.created_at}
				</p>
			</div>

			<div className="max-w-3xl mx-auto">
				<h2 className="text-xl font-bold mb-4">Comments</h2>
				{comments?.comments.map((comment) => (
					<div
						key={comment.Comment.comment_id}
						className="bg-gray-100 p-4 mb-4 rounded-lg"
					>
						<p className="font-semibold">
							User ID: {comment.Comment.user_id}
						</p>
						<p className="mt-2">{comment.Comment.text}</p>
						<p className="mt-2 text-sm text-gray-500">
							{comment.Comment.date}
						</p>
					</div>
				))}
			</div>
		</div>
	);
};

export default PostDetailsPage;
