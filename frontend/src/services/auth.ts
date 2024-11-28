import axios from "axios";
import {
	LoginRequest,
	LoginResponse,
	RegisterRequest,
	RegisterResponse,
} from "../types/auth";

const USER_URL =
	"https://sni78nehca.execute-api.us-east-1.amazonaws.com/dev/user";
export const login = async (payload: LoginRequest): Promise<LoginResponse> => {
	try {
		console.log(payload);
		const response = await axios.post<LoginResponse>(
			`${USER_URL}/login`,
			payload,
			{
				headers: {
					"Content-Type": "application/json",
				},
			}
		);
		console.log(response);
		const { data } = response;
		if (data?.data?.token) {
			localStorage.setItem("token", data.data.token);
		}
		return data;
	} catch (error) {
		console.error("Login failed:", error);
		throw new Error("Invalid credentials");
	}
};

export const register = async (
	payload: RegisterRequest
): Promise<RegisterResponse> => {
	try {
		console.log("payload", payload);
		const response = await axios.post<RegisterResponse>(
			`${USER_URL}/register`,
			payload,
			{
				headers: {
					"Content-Type": "application/json",
				},
			}
		);
		return response.data;
	} catch (error) {
		console.error("Registration failed:", error);
		throw new Error("An error occurred during registration");
	}
};

export const logout = (): void => {
	localStorage.removeItem("token");
	localStorage.removeItem("provider");
};
