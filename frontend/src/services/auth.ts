import axios from "axios";
import {
	LoginRequest,
	LoginResponse,
	RegisterRequest,
	RegisterResponse,
} from "../types/auth";

export const login = async (payload: LoginRequest): Promise<LoginResponse> => {
	try {
		const response = await axios.post<LoginResponse>(`/api/login`, payload);

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
		const response = await axios.post<RegisterResponse>(
			"/api/register",
			payload
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
