import React, { useContext } from "react";
import ProviderContext from "../contexts/ProviderContext";
import ThemeWrapper from "../components/ThemeWrapper";

const HomePage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;

	return (
		<ThemeWrapper>
			<div
				style={{
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					justifyContent: "center",
					height: "100%",
					width: "100%",
				}}
			>
				<div
					style={{
						backgroundColor: "rgba(0, 0, 0, 0.7)",
						color: "#FFFFFF",
						padding: "2rem",
						borderRadius: "8px",
						textAlign: "center",
						maxWidth: "400px",
						width: "100%",
						boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
					}}
				>
					<h2
						style={{
							fontSize: "1.5rem",
							fontWeight: "bold",
						}}
					>
						Welcome to {provider}
					</h2>
					<p
						style={{
							marginTop: "1rem",
							fontSize: "1rem",
						}}
					>
						Enjoy a personalized experience with {provider}.
					</p>
				</div>
			</div>
		</ThemeWrapper>
	);
};

export default HomePage;
