import React from "react";
import { Song as SongType } from "../types/song";

interface SongProps {
	song: SongType;
}

const Song: React.FC<SongProps> = ({ song }) => {
	const releaseDate = new Date(song.release_date).toLocaleDateString();

	return (
		<div
			style={{
				backgroundColor: "rgba(255, 255, 255, 0.1)",
				borderRadius: "8px",
				padding: "1rem",
				marginBottom: "1rem",
				width: "100%",
				height: "100%",
				boxSizing: "border-box",
				overflow: "hidden",
				boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
			}}
		>
			<div
				className="relative bg-gray-200"
				style={{
					height: "300px",
					width: "100%",
					borderRadius: "8px",
					overflow: "hidden",
				}}
			>
				<img
					src={song.cover_image_url}
					alt={song.title}
					style={{
						objectFit: "cover",
						width: "100%",
						height: "100%",
					}}
				/>
			</div>

			<div className="p-4 text-left">
				<h2 className="text-xl font-semibold text-gray-800 mb-2">
					{song.title}
				</h2>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Genre:</strong> {song.genre}
				</p>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Released:</strong> {releaseDate}
				</p>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Duration:</strong> {song.duration}
				</p>
				<p className="text-sm text-gray-600 mb-3">
					<strong>Times Played:</strong> {song.times_played}
				</p>

				<div className="flex space-x-4">
					<a
						href={song.song_url}
						target="_blank"
						rel="noopener noreferrer"
						className="text-blue-500 text-sm font-medium hover:underline"
					>
						Listen to Song
					</a>
					{song.preview_music_url && (
						<a
							href={song.preview_music_url}
							target="_blank"
							rel="noopener noreferrer"
							className="text-blue-500 text-sm font-medium hover:underline"
						>
							Preview Song
						</a>
					)}
				</div>
			</div>
		</div>
	);
};

export default Song;
