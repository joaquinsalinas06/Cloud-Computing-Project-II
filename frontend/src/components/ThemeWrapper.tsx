import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "../services/auth";
import { LogOut } from "lucide-react";
import ProviderContext from "../contexts/ProviderContext";

interface ThemeWrapperProps {
	children: React.ReactNode;
}

const ThemeWrapper: React.FC<ThemeWrapperProps> = ({ children }) => {
	const { theme } = useContext(ProviderContext)!;
	const navigate = useNavigate();

	const handleLogout = () => {
		logout();
		navigate("/login");
	};

	const tokenExists = !!localStorage.getItem("token");

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
					padding: "1.5rem",
					width: "100%",
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					position: "relative",
					borderBottom: `4px solid ${theme.accentColor}`,
					boxShadow: `0px 4px 6px rgba(0, 0, 0, 0.2)`,
				}}
			>
				<h1
					style={{
						fontSize: "1.5rem",
						fontWeight: "bold",
					}}
				>
					{theme.name}
				</h1>
				{tokenExists && (
					<button
						onClick={handleLogout}
						style={{
							position: "absolute",
							right: "1.5rem",
							background: "none",
							border: "none",
							cursor: "pointer",
							color: theme.textColor,
						}}
						aria-label="Logout"
					>
						<LogOut size={24} />
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
