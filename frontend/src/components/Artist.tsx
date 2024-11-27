import React from "react";
import { Artist as ArtistType } from "../types/artist";

interface ArtistProps {
	artist: ArtistType;
}

const Artist: React.FC<ArtistProps> = ({ artist }) => {
	const birthDate = new Date(artist.birth_date).toLocaleDateString();

	return (
		<div className="bg-white rounded-lg overflow-hidden shadow-lg w-full max-w-xs mx-4 my-2">
			<div className="relative w-full h-48 bg-gray-200">
				<img
					src={artist.cover_image_url}
					alt={artist.name}
					className="w-full h-full object-cover"
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

				<div className="flex items-center">
					<span
						className={`px-4 py-2 rounded-full text-white font-semibold ${
							artist.status ? "bg-green-500" : "bg-red-500"
						}`}
					>
						{artist.status ? "Active" : "Inactive"}
					</span>
				</div>
			</div>
		</div>
	);
};

export default Artist;
