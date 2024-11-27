import React from "react";
import {
	BrowserRouter as Router,
	Routes,
	Route,
	Navigate,
} from "react-router-dom";
import { ProviderProvider } from "./contexts/ProviderContext";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ArtistPage from "./pages/ArtistPage";

const App: React.FC = () => {
	return (
		<ProviderProvider>
			<Router>
				<Routes>
					<Route path="/" element={<Navigate to="/login" />} />
					<Route path="/login" element={<LoginPage />} />
					<Route path="/register" element={<RegisterPage />} />
					<Route path="/home" element={<HomePage />} />
					<Route path="/artists" element={<ArtistPage />} />
				</Routes>
			</Router>
		</ProviderProvider>
	);
};

export default App;
