import React, { useContext, useState, useEffect } from "react";
import { Song as SongType } from "../types/song";
import { useAudioContext } from "../contexts/AudioContext";
import ProviderContext from "../contexts/ProviderContext";
import { FaPlay, FaPause } from "react-icons/fa";

interface SongProps {
	song: SongType;
}

const Song: React.FC<SongProps> = ({ song }) => {
	const context = useContext(ProviderContext);
	const theme = context?.theme;
	const { playAudio, pauseAudio, playingTrack } = useAudioContext();
	const [isPlaying, setIsPlaying] = useState(false);

	useEffect(() => {
		setIsPlaying(playingTrack === song.preview_music_url);
	}, [playingTrack, song.preview_music_url]);

	const togglePlay = () => {
		if (isPlaying) {
			pauseAudio();
			setIsPlaying(false);
		} else {
			playAudio(song.preview_music_url);
			setIsPlaying(true);
		}
	};

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
					<strong>Released:</strong>{" "}
					{new Date(song.release_date).toLocaleDateString()}
				</p>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Duration:</strong> {song.duration}
				</p>
				<p className="text-sm text-gray-600 mb-3">
					<strong>Times Played:</strong> {song.times_played}
				</p>
				<a
					href={song.song_url}
					target="_blank"
					rel="noopener noreferrer"
					style={{
						color: theme?.primaryColor,
						marginRight: "1rem",
					}}
					className="text-sm font-medium hover:underline"
				>
					Listen on Spotify
				</a>

				<button
					onClick={togglePlay}
					style={{
						color: theme?.primaryColor,
					}}
					className="px-4 py-2 bg-blue-500 rounded hover:bg-blue-600"
				>
					{isPlaying ? <FaPause /> : <FaPlay />}
				</button>
			</div>
		</div>
	);
};

export default Song;
