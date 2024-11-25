import { Music, Video, Music2 } from "lucide-react";

interface ProviderSelectorProps {
	currentProvider: string;
	onProviderChange: (provider: string) => void;
}

export function ProviderSelector({
	currentProvider,
	onProviderChange,
}: ProviderSelectorProps) {
	return (
		<div className="flex flex-col items-center space-y-4 mb-8">
			<h2 className="text-xl font-semibold">
				Choose your music provider
			</h2>
			<div className="flex gap-4">
				<button
					className={`w-32 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition ${
						currentProvider === "Spotify"
							? "bg-[#1DB954] text-white"
							: "bg-white text-black border border-gray-300"
					}`}
					onClick={() => onProviderChange("Spotify")}
				>
					<Music className="h-4 w-4" />
					Spotify
				</button>
				<button
					className={`w-32 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition ${
						currentProvider === "YouTubeMusic"
							? "bg-[#FF0000] text-white"
							: "bg-white text-black border border-gray-300"
					}`}
					onClick={() => onProviderChange("YouTubeMusic")}
				>
					<Video className="h-4 w-4" />
					YouTube
				</button>
				<button
					className={`w-32 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition ${
						currentProvider === "AppleMusic"
							? "bg-[#FA2C55] text-white"
							: "bg-white text-black border border-gray-300"
					}`}
					onClick={() => onProviderChange("AppleMusic")}
				>
					<Music2 className="h-4 w-4" />
					Apple
				</button>
			</div>
		</div>
	);
}
