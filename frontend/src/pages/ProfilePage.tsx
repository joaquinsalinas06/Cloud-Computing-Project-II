import React, { useContext, useEffect, useState } from "react";
import ThemeWrapper from "../components/ThemeWrapper";
import ProviderContext from "../contexts/ProviderContext";
import UserContext from "../contexts/UserContext";
import { fetchUser } from "../services/user";
import { UserResponse } from "../types/user";

const ProfilePage: React.FC = () => {
	const { provider } = useContext(ProviderContext)!;
	const { user_id } = useContext(UserContext)!;
	const [user, setUser] = useState<UserResponse | null>(null);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const loadUser = async () => {
			if (!provider || !user_id) {
				setError("Provider or user ID is missing.");
				return;
			}

			setLoading(true);
			try {
				const userData = await fetchUser({
					provider_id: provider,
					user_id,
				});
				console.log(userData);
				setUser(userData);
				setError(null);
			} catch (err) {
				setError("Failed to load user data.");
				console.error(err);
			} finally {
				setLoading(false);
			}
		};

		loadUser();
	}, [provider, user_id]);

	if (loading) {
		return (
			<ThemeWrapper>
				<div style={{ textAlign: "center", padding: "20px" }}>
					<p>Loading user data...</p>
				</div>
			</ThemeWrapper>
		);
	}

	if (error) {
		return (
			<ThemeWrapper>
				<div style={{ textAlign: "center", padding: "20px" }}>
					<p style={{ color: "red" }}>{error}</p>
				</div>
			</ThemeWrapper>
		);
	}

	if (!user) {
		return (
			<ThemeWrapper>
				<div style={{ textAlign: "center", padding: "20px" }}>
					<p>No user data available.</p>
				</div>
			</ThemeWrapper>
		);
	}

	return (
		<ThemeWrapper>
			<div
				style={{
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					justifyContent: "center",
					padding: "20px",
					height: "100vh",
				}}
			>
				<h1 style={{ fontSize: "2rem", marginBottom: "20px" }}>
					User Profile
				</h1>
				<div
					style={{
						backgroundColor: "rgba(255, 255, 255, 0.1)",
						padding: "20px",
						borderRadius: "8px",
						width: "100%",
						maxWidth: "400px",
						boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
					}}
				>
					<p>
						<strong>Username:</strong> {user.username}
					</p>
					<p>
						<strong>Name:</strong> {user.name} {user.last_name}
					</p>
					<p>
						<strong>Email:</strong> {user.email}
					</p>
					<p>
						<strong>Phone Number:</strong> {user.phone_number}
					</p>
					<p>
						<strong>Gender:</strong> {user.gender}
					</p>
					<p>
						<strong>Age:</strong> {user.age}
					</p>
					<p>
						<strong>Active:</strong> {user.active ? "Yes" : "No"}
					</p>
					<p>
						<strong>Created At:</strong>{" "}
						{new Date(user.created_at).toLocaleDateString()}
					</p>
				</div>
				<div style={{ padding: "40px" }}>
					<button>Create Post</button>
				</div>
			</div>
		</ThemeWrapper>
	);
};

export default ProfilePage;
