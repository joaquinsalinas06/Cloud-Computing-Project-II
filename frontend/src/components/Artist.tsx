import React from "react";
import { Artist as ArtistType } from "../types/artist";

interface ArtistProps {
	artist: ArtistType;
}

const Artist: React.FC<ArtistProps> = ({ artist }) => {
	const birthDate = new Date(artist.birth_date).toLocaleDateString();

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
			}}
		>
			<div
				className="relative bg-gray-200"
				style={{
					height: "300px",
					width: "100%",
				}}
			>
				<img
					src={artist.cover_image_url}
					alt={artist.name}
					style={{
						objectFit: "cover",
						width: "100%",
						height: "100%",
						borderRadius: "8px",
					}}
				/>
			</div>

			<div className="p-4 text-left">
				<h2 className="text-xl font-semibold text-gray-800 mb-2">
					{artist.name}
				</h2>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Genre:</strong> {artist.genre}
				</p>
				<p className="text-sm text-gray-600 mb-1">
					<strong>Country:</strong> {artist.country}
				</p>
				<p className="text-sm text-gray-600 mb-3">
					<strong>Born:</strong> {birthDate}
				</p>
				<p className="text-sm text-gray-600">
					<strong>Status:</strong>{" "}
					{artist.status ? "Active" : "Inactive"}
				</p>
			</div>
		</div>
	);
};

export default Artist;
