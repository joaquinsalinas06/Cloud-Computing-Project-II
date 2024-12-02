import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPost } from "../services/post";
import { fetchComments, createComment } from "../services/comment";
import { fetchUser } from "../services/user";
import { Post } from "../types/post";
import { Comment } from "../types/comment";
import ProviderContext from "../contexts/ProviderContext";
import UserContext from "../contexts/UserContext";

const PostDetailsPage: React.FC = () => {
	const { post_id } = useParams<{ post_id: string }>();
	const [post, setPost] = useState<Post | null>(null);
	const { provider } = useContext(ProviderContext)!;
	const { user_id } = useContext(UserContext)!;
	const [comments, setComments] = useState<Comment[]>([]);
	const [usernames, setUsernames] = useState<Record<string, string>>({});
	const [loadingPost, setLoadingPost] = useState<boolean>(true);
	const [setLoadingComments] = useState<boolean>(false);
	const [creatingComment, setCreatingComment] = useState<boolean>(false);
	const [newCommentText, setNewCommentText] = useState<string>("");
	const [error, setError] = useState<string | null>(null);

	// Existing useEffect and handlers remain the same
	useEffect(() => {
		const loadPost = async () => {
			try {
				const postData = await fetchPost(provider, parseInt(post_id!));
				setPost(postData.body);
				// eslint-disable-next-line @typescript-eslint/no-unused-vars
			} catch (err) {
				setError("Failed to load post details.");
			} finally {
				setLoadingPost(false);
			}
		};

		loadPost();
	}, [provider, post_id]);

	useEffect(() => {
		const loadComments = async () => {
			setLoadingComments(true);
			try {
				const response = await fetchComments({
					provider_id: provider,
					post_id: parseInt(post_id!),
					page: 1,
					pageSize: 100,
				});

				const uniqueUserIds = Array.from(
					new Set(response.comments.map((comment) => comment.user_id))
				);

				const fetchedUsernames = await Promise.all(
					uniqueUserIds.map(async (user_id) => {
						if (!usernames[user_id]) {
							try {
								const user = await fetchUser({
									provider_id: provider,
									user_id,
								});
								return { user_id, username: user.username };
							} catch {
								return { user_id, username: "Unknown User" };
							}
						}
						return { user_id, username: usernames[user_id] };
					})
				);

				const updatedUsernames = fetchedUsernames.reduce(
					(acc, { user_id, username }) => ({
						...acc,
						[user_id]: username,
					}),
					{}
				);

				setUsernames((prev) => ({ ...prev, ...updatedUsernames }));
				setComments(response.comments);
			} catch {
				setError("Failed to load comments.");
			} finally {
				setLoadingComments(false);
			}
		};

		loadComments();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [provider, post_id]);

	const handleCreateComment = async () => {
		if (!newCommentText.trim()) return;
		setCreatingComment(true);
		try {
			const response = await createComment({
				provider_id: provider,
				user_id: user_id!,
				post_id: parseInt(post_id!),
				text: newCommentText,
			});

			const user = await fetchUser({
				provider_id: provider,
				user_id: user_id!,
			});

			setComments((prev) => [
				{
					...response.comentario,
					user_id: response.comentario.user_id,
				},
				...prev,
			]);

			setUsernames((prev) => ({
				...prev,
				[response.comentario.user_id]: user.username || "You",
			}));

			setNewCommentText("");
		} catch {
			setError("Failed to create comment.");
		} finally {
			setCreatingComment(false);
		}
	};

	if (loadingPost) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-neutral-50">
				<div className="animate-pulse text-neutral-600">
					Loading post...
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-neutral-50">
				<div className="text-red-500">{error}</div>
			</div>
		);
	}

	return (
		<div className="bg-neutral-50 min-h-screen flex justify-center items-start">
			<div className="w-full max-w-2xl mx-auto px-4 py-8">
				{/* Post Header */}
				<article className="bg-white rounded-xl shadow-sm mb-8 p-6 text-center">
					<h1 className="text-2xl font-semibold text-neutral-900 mb-2">
						{post?.description}
					</h1>
					<time className="text-sm text-neutral-500 block">
						{new Date(post?.created_at || "").toLocaleDateString()}
					</time>
				</article>

				{/* Comments Section */}
				<section className="space-y-8">
					<h2 className="text-xl font-semibold text-neutral-900 text-center mb-4">
						Comments
					</h2>

					{/* Comment Form */}
					<div className="bg-white rounded-xl shadow-sm p-4">
						<textarea
							className="w-full min-h-[100px] p-3 border border-neutral-200 rounded-lg resize-none 
                       bg-neutral-50 focus:ring-2 focus:ring-neutral-500 focus:border-transparent
                       transition-all duration-200 ease-in-out text-neutral-900 placeholder-neutral-400"
							placeholder="Share your thoughts..."
							value={newCommentText}
							onChange={(e) => setNewCommentText(e.target.value)}
						/>
						<div className="mt-3 flex justify-center">
							<button
								onClick={handleCreateComment}
								disabled={
									creatingComment || !newCommentText.trim()
								}
								className="px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 
                         disabled:bg-neutral-300 disabled:cursor-not-allowed transition-colors
                         duration-200 ease-in-out w-full sm:w-auto"
							>
								{creatingComment
									? "Posting..."
									: "Post Comment"}
							</button>
						</div>
					</div>

					{/* Comments List */}
					<div className="space-y-4">
						{comments.map((comment) => (
							<article
								key={comment.comment_id}
								className="bg-white rounded-xl shadow-sm p-4 transition-all duration-200 ease-in-out
                         hover:shadow-md"
							>
								<header className="flex flex-col items-center mb-2">
									<h3 className="font-medium text-neutral-900">
										{usernames[comment.user_id] ||
											"Unknown User"}
									</h3>
									<time className="text-xs text-neutral-500">
										{new Date(
											comment.date || ""
										).toLocaleDateString()}
									</time>
								</header>
								<p className="text-neutral-700 leading-relaxed text-center">
									{comment.text}
								</p>
							</article>
						))}
					</div>
				</section>
			</div>
		</div>
	);
};

export default PostDetailsPage;
