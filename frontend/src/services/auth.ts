import axios from "axios";
import {
	LoginRequest,
	LoginResponse,
	LogoutRequest,
	RegisterRequest,
	RegisterResponse,
} from "../types/auth";

const AUTH_URL =
	"https://cleiktxro5.execute-api.us-east-1.amazonaws.com/dev/user";
export const login = async (payload: LoginRequest): Promise<LoginResponse> => {
	try {
		const response = await axios.post<LoginResponse>(
			`${AUTH_URL}/login`,
			payload,
			{
				headers: {
					"Content-Type": "application/json",
				},
			}
		);
		const { data } = response;
		if (data?.body?.data?.token) {
			localStorage.setItem("token", data.body.data.token);
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
			`${AUTH_URL}/register`,
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

export const logout = async (payload: LogoutRequest): Promise<void> => {
	try {
		await axios.post(`${AUTH_URL}/logout`, payload, {
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});
		localStorage.removeItem("token");
		localStorage.removeItem("provider");
		localStorage.removeItem("user_id");
		console.log("Logout exitoso");
	} catch (error) {
		console.error("Logout fallido:", error);
		throw new Error("No se pudo completar el logout");
	}
};
