import React from "react";
import {
	BrowserRouter as Router,
	Routes,
	Route,
	Navigate,
} from "react-router-dom";
import { ProviderProvider } from "./contexts/ProviderContext";
import { UserProvider } from "./contexts/UserContext";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ArtistPage from "./pages/ArtistPage";
import AlbumPage from "./pages/AlbumPage";
import SongPage from "./pages/SongPage";
import ProfilePage from "./pages/ProfilePage";

const App: React.FC = () => {
	return (
		<ProviderProvider>
			<UserProvider>
				<Router>
					<Routes>
						<Route path="/" element={<Navigate to="/login" />} />
						<Route path="/login" element={<LoginPage />} />
						<Route path="/register" element={<RegisterPage />} />
						<Route path="/home" element={<HomePage />} />
						<Route path="/artists" element={<ArtistPage />} />
						<Route path="/albums" element={<AlbumPage />} />
						<Route path="/songs" element={<SongPage />} />
						<Route path="/profile" element={<ProfilePage />} />
					</Routes>
				</Router>
			</UserProvider>
		</ProviderProvider>
	);
};

export default App;
