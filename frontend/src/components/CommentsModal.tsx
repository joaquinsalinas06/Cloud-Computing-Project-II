import React, { useEffect, useState } from "react";
import { fetchComments } from "../services/comment"; // Asegúrate de que fetchComments esté importado
import { CommentRequest, CommentResponse } from "../types/comment"; // Importa las interfaces correctas

interface CommentsModalProps {
	provider_id: string;
	post_id: number;
	isOpen: boolean;
	onClose: () => void;
}

const CommentsModal: React.FC<CommentsModalProps> = ({
	provider_id,
	post_id,
	isOpen,
	onClose,
}) => {
	const [comments, setComments] = useState<CommentResponse | null>(null);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(1);

	useEffect(() => {
		if (!isOpen) return; // No cargar comentarios si el modal está cerrado
		const loadComments = async () => {
			setLoading(true);
			setError(null);

			const requestPayload: CommentRequest = {
				provider_id,
				post_id,
				page: currentPage,
				pageSize: 10,
			};

			try {
				const response: CommentResponse = await fetchComments(
					requestPayload
				);
				setComments(response);
			} catch (err) {
				console.error("Error fetching comments:", err);
				setError("Failed to load comments.");
			} finally {
				setLoading(false);
			}
		};

		loadComments();
	}, [provider_id, post_id, isOpen, currentPage]);

	const handleNextPage = () => {
		if (comments && comments.pagination.hasNextPage) {
			setCurrentPage((prev) => prev + 1);
		}
	};

	const handlePreviousPage = () => {
		if (currentPage > 1) {
			setCurrentPage((prev) => prev - 1);
		}
	};

	if (!isOpen) return null;

	return (
		<div className="fixed top-0 left-0 w-full h-full bg-gray-800 bg-opacity-50 flex justify-center items-center z-50">
			<div className="bg-white p-6 rounded-lg max-w-xl w-full shadow-lg">
				<h2 className="text-xl font-bold mb-4">Comments</h2>
				{loading && <p>Loading comments...</p>}
				{error && <p className="text-red-500">{error}</p>}
				<div>
					{comments?.comments.map((comment) => (
						<div
							key={comment.Comment.comment_id}
							className="mb-4 p-4 bg-gray-100 rounded-lg shadow-sm"
						>
							<p className="font-semibold">
								User ID: {comment.Comment.user_id}
							</p>
							<p className="mt-2">{comment.Comment.comment_id}</p>
							<p className="mt-2 text-sm text-gray-500">
								{comment.Comment.text}
							</p>
						</div>
					))}
				</div>
				<div className="flex justify-between items-center mt-4">
					<button
						onClick={handlePreviousPage}
						disabled={currentPage === 1}
						className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-400"
					>
						Previous
					</button>
					<span>Page {currentPage}</span>
					<button
						onClick={handleNextPage}
						disabled={!comments?.pagination.hasNextPage}
						className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-400"
					>
						Next
					</button>
				</div>
				<button
					onClick={onClose}
					className="mt-4 w-full py-2 bg-red-500 text-white rounded-lg"
				>
					Close
				</button>
			</div>
		</div>
	);
};

export default CommentsModal;
