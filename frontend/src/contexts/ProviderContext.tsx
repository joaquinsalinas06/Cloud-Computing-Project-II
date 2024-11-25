import React, { createContext, useState, ReactNode, useEffect } from "react";
import {
	spotifyTheme,
	youtubeMusicTheme,
	appleMusicTheme,
} from "../themes/theme-config";
import { Theme } from "../types/theme";

interface ProviderContextProps {
	provider: string;
	theme: Theme;
	switchProvider: (newProvider: string) => void;
	resetProvider: () => void;
}

const ProviderContext = createContext<ProviderContextProps | undefined>(
	undefined
);

const themes: Record<string, Theme> = {
	Spotify: spotifyTheme,
	YouTubeMusic: youtubeMusicTheme,
	AppleMusic: appleMusicTheme,
};

interface ProviderProviderProps {
	children: ReactNode;
}

export const ProviderProvider: React.FC<ProviderProviderProps> = ({
	children,
}) => {
	const [provider, setProvider] = useState<string>(
		() => localStorage.getItem("provider") || "Spotify"
	);
	const [theme, setTheme] = useState<Theme>(
		() => themes[localStorage.getItem("provider") || "Spotify"]
	);

	const switchProvider = (newProvider: string) => {
		setProvider(newProvider);
		setTheme(themes[newProvider]);
		localStorage.setItem("provider", newProvider);
	};

	const resetProvider = () => {
		setProvider("Spotify");
		setTheme(themes["Spotify"]);
	};

	useEffect(() => {
		setTheme(themes[provider]);
	}, [provider]);

	return (
		<ProviderContext.Provider
			value={{ provider, theme, switchProvider, resetProvider }}
		>
			{children}
		</ProviderContext.Provider>
	);
};

export default ProviderContext;
