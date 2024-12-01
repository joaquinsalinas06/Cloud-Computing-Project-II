import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/auth";
import ProviderContext from "../contexts/ProviderContext";
import UserContext from "../contexts/UserContext";
import ThemeWrapper from "../components/ThemeWrapper";
import { ProviderSelector } from "../components/ProviderSelector";

const LoginPage: React.FC = () => {
	const [email, setEmail] = useState<string>("");
	const [password, setPassword] = useState<string>("");
	const { provider, switchProvider } = useContext(ProviderContext)!;
	const { setUser } = useContext(UserContext)!;

	const navigate = useNavigate();

	const handleLogin = async (event: React.FormEvent) => {
		event.preventDefault();
		try {
			const payload = {
				provider_id: provider,
				email,
				password,
			};
			const response = await login(payload);
			switchProvider(provider);
			setUser(response.body.data?.user_id ?? 0);
			navigate("/home");
		} catch (error) {
			console.error(error);
			alert("Invalid credentials");
		}
	};

	return (
		<ThemeWrapper>
			<div className="flex flex-col items-center justify-center min-h-screen px-4">
				<ProviderSelector
					currentProvider={provider}
					onProviderChange={switchProvider}
				/>
				<form
					onSubmit={handleLogin}
					className="bg-white p-8 rounded shadow-md w-full max-w-md"
				>
					<h1 className="text-2xl font-bold mb-6 text-center">
						Login to {provider}
					</h1>
					<input
						type="email"
						placeholder="Email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						className="block w-full p-3 border rounded mb-4"
					/>
					<input
						type="password"
						placeholder="Password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="block w-full p-3 border rounded mb-4"
					/>
					<button
						type="submit"
						className="bg-blue-500 text-white px-4 py-2 rounded w-full"
					>
						Login
					</button>
					<p className="text-sm mt-4 text-center">
						Don't have an account?{" "}
						<span
							className="text-blue-500 cursor-pointer"
							onClick={() => navigate("/register")}
						>
							Register
						</span>
					</p>
				</form>
			</div>
		</ThemeWrapper>
	);
};

export default LoginPage;
