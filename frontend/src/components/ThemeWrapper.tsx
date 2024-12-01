import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "../services/auth";
import ProviderContext from "../contexts/ProviderContext";
import UserContext from "../contexts/UserContext";

interface ThemeWrapperProps {
	children: React.ReactNode;
}

const ThemeWrapper: React.FC<ThemeWrapperProps> = ({ children }) => {
	const { theme, provider } = useContext(ProviderContext)!;
	const { user_id } = useContext(UserContext)!;

	const navigate = useNavigate();

	const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
		!!localStorage.getItem("token")
	);

	const handleAlbumPage = () => {
		navigate("/albums");
	};

	const handleArtistPage = () => {
		navigate("/artists");
	};

	const handleSongPage = () => {
		navigate("/songs");
	};

	const handleProfilePage = () => {
		navigate("/profile");
	};

	const handleLogout = () => {
		const payload = {
			provider_id: provider,
			user_id,
		};
		logout(payload);
		setIsAuthenticated(false);
		navigate("/login");
	};

	useEffect(() => {
		// Verificar si el token existe al cargar el componente
		setIsAuthenticated(!!localStorage.getItem("token"));
	}, []);

	return (
		<div
			style={{
				backgroundColor: theme.backgroundColor,
				color: theme.textColor,
				height: "100vh",
				width: "100vw",
				display: "flex",
				flexDirection: "column",
				alignItems: "center",
				justifyContent: "flex-start",
				margin: "0",
				padding: "0",
				overflow: "hidden",
			}}
		>
			<header
				style={{
					backgroundColor: theme.primaryColor,
					color: theme.textColor,
					padding: "0.01rem",
					width: "100%",
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					position: "relative",
					boxShadow: `0px 4px 6px rgba(0, 0, 0, 0.2)`,
				}}
			>
				<button
					onClick={handleArtistPage}
					style={{ position: "absolute", left: "2rem" }}
				>
					Artists
				</button>
				<button
					onClick={handleAlbumPage}
					style={{ position: "absolute", left: "8.5rem" }}
				>
					Albums
				</button>

				<button
					onClick={handleSongPage}
					style={{ position: "absolute", left: "15.2rem" }}
				>
					Songs
				</button>

				<button
					onClick={() => navigate("/home")}
					style={{
						fontSize: "1.5rem",
						fontWeight: "bold",
						backgroundColor: "transparent",
					}}
				>
					{theme.name}
				</button>
				{isAuthenticated && (
					<button
						onClick={handleProfilePage}
						style={{ position: "absolute", right: "8.5rem" }}
					>
						Profile
					</button>
				)}
				{isAuthenticated && (
					<button
						onClick={handleLogout}
						style={{
							position: "absolute",
							right: "1.5rem",
							border: "none",
							cursor: "pointer",
							color: theme.textColor,
						}}
						aria-label="Logout"
					>
						Logout
					</button>
				)}
			</header>

			<div
				style={{
					flex: 1,
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					width: "100%",
				}}
			>
				{children}
			</div>
		</div>
	);
};

export default ThemeWrapper;
