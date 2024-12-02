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
				  className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md mx-auto"
				>
				  <h1 className="text-3xl font-bold mb-8 text-center">
					Login to {provider}
				  </h1>
				 	<div className="space-y-10">
						<div className="p-10">
							<input
								type="email"
								placeholder="Email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								className="block w-full p-6 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
						</div>
						<div className="p-4">
							<input
								type="password"
								placeholder="Password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								className="block w-full p-6 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>
					</div>
				  <button
					type="submit"
					className="bg-blue-500 text-white px-4 py-3 rounded-lg w-full font-semibold hover:bg-blue-600 transition duration-300 mt-6"
				  >
					Login
				  </button>
				  <p className="text-sm mt-6 text-center">
					Don't have an account?{" "}
					<span
					  className="text-blue-500 cursor-pointer hover:underline"
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
