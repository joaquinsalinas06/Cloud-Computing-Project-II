import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../services/auth";
import ProviderContext from "../contexts/ProviderContext";
import ThemeWrapper from "../components/ThemeWrapper";
import { ProviderSelector } from "../components/ProviderSelector";

const RegisterPage: React.FC = () => {
	const [step, setStep] = useState<number>(1);
	const [email, setEmail] = useState<string>("");
	const [password, setPassword] = useState<string>("");
	const [confirmPassword, setConfirmPassword] = useState<string>("");
	const [username, setUsername] = useState<string>("");
	const [name, setName] = useState<string>("");
	const [lastname, setLastname] = useState<string>("");
	const [phoneNumber, setPhoneNumber] = useState<string>("");
	const [birthDate, setBirthDate] = useState<string>("");
	const [gender, setGender] = useState<string>("M");
	const [age, setAge] = useState<number>(0);

	const { provider, switchProvider } = useContext(ProviderContext)!;
	const navigate = useNavigate();

	const handleNextStep = (event: React.FormEvent) => {
		event.preventDefault();
		if (step === 1) {
			if (!email || !password || !confirmPassword || !username) {
				alert("Please fill in all required fields");
				return;
			}
			if (password !== confirmPassword) {
				alert("Passwords do not match");
				return;
			}
			setStep(2);
		}
	};

	const handleRegister = async (event: React.FormEvent) => {
		event.preventDefault();
		try {
			const payload = {
				provider_id: provider,
				password,
				email,
				username,
				name,
				last_name: lastname,
				phone_number: phoneNumber,
				date_birth: birthDate,
				genre: gender,
				age,
				active: true,
				date_created: new Date()
					.toISOString()
					.replace("T", " ")
					.split(".")[0],
			};

			const response = await register(payload);
			alert(response.body.message);
			navigate("/login");
		} catch (error) {
			console.error(error);
			alert("An error occurred during registration");
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
					onSubmit={step === 1 ? handleNextStep : handleRegister}
					className="bg-white p-8 rounded shadow-md w-full max-w-md"
				>
					<h1 className="text-2xl font-bold mb-6 text-center">
						{`Register to ${provider}`}
					</h1>
					<h2 className="text-xl font-semibold mb-4">
						{step === 1
							? "Step 1: Basic Information"
							: "Step 2: Additional Details"}
					</h2>

					{step === 1 && (
						<>
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
							<input
								type="password"
								placeholder="Confirm Password"
								value={confirmPassword}
								onChange={(e) =>
									setConfirmPassword(e.target.value)
								}
								className="block w-full p-3 border rounded mb-4"
							/>
							<input
								type="text"
								placeholder="Username"
								value={username}
								onChange={(e) => setUsername(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							/>
							<button
								type="submit"
								className="bg-blue-500 text-white px-4 py-2 rounded w-full"
							>
								Next
							</button>
						</>
					)}

					{step === 2 && (
						<>
							<input
								type="text"
								placeholder="First Name"
								value={name}
								onChange={(e) => setName(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							/>
							<input
								type="text"
								placeholder="Last Name"
								value={lastname}
								onChange={(e) => setLastname(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							/>
							<input
								type="text"
								placeholder="Phone Number"
								value={phoneNumber}
								onChange={(e) => setPhoneNumber(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							/>
							<input
								type="date"
								placeholder="Date of Birth"
								value={birthDate}
								onChange={(e) => setBirthDate(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							/>
							<select
								value={gender}
								onChange={(e) => setGender(e.target.value)}
								className="block w-full p-3 border rounded mb-4"
							>
								<option value="M">Male</option>
								<option value="F">Female</option>
							</select>
							<input
								type="number"
								placeholder="Age"
								value={age}
								onChange={(e) => setAge(Number(e.target.value))}
								className="block w-full p-3 border rounded mb-4"
							/>
							<button
								type="submit"
								className="bg-green-500 text-white px-4 py-2 rounded w-full"
							>
								Register
							</button>
							<button
								type="button"
								onClick={() => setStep(1)}
								className="bg-gray-500 text-white px-4 py-2 rounded w-full mt-4"
							>
								Back
							</button>
						</>
					)}
				</form>
			</div>
		</ThemeWrapper>
	);
};

export default RegisterPage;
