import React, {
	createContext,
	useState,
	useContext,
	useRef,
	useEffect,
} from "react";

interface AudioContextProps {
	currentAudio: HTMLAudioElement | null;
	playingTrack: string | null;
	playAudio: (url: string) => void;
	pauseAudio: () => void;
	volume: number;
}

const AudioContext = createContext<AudioContextProps | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useAudioContext = () => {
	const context = useContext(AudioContext);
	if (!context) {
		throw new Error("useAudioContext must be used within an AudioProvider");
	}
	return context;
};

export const AudioProvider: React.FC<{ children: React.ReactNode }> = ({
	children,
}) => {
	const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(
		null
	);
	const [playingTrack, setPlayingTrack] = useState<string | null>(null);
	const [volume] = useState<number>(0.5);

	const audioRef = useRef<HTMLAudioElement | null>(null);

	const playAudio = (url: string) => {
		if (playingTrack === url && audioRef.current) {
			audioRef.current.play();
			return;
		}

		if (audioRef.current) {
			audioRef.current.pause();
		}

		const audio = new Audio(url);
		audio.volume = volume;
		audio.play();

		audioRef.current = audio;
		setCurrentAudio(audio);
		setPlayingTrack(url);

		audio.addEventListener("ended", () => {
			setPlayingTrack(null);
			setCurrentAudio(null);
		});

		audio.addEventListener("error", (e) => {
			console.error("Error playing audio:", e);
		});
	};

	const pauseAudio = () => {
		if (audioRef.current) {
			audioRef.current.pause();
		}
	};

	useEffect(() => {
		return () => {
			if (audioRef.current) {
				audioRef.current.pause();
			}
		};
	}, []);

	return (
		<AudioContext.Provider
			value={{
				currentAudio,
				playingTrack,
				playAudio,
				pauseAudio,
				volume,
			}}
		>
			{children}
		</AudioContext.Provider>
	);
};
