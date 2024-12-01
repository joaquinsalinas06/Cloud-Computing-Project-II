import { UserRequest, UserResponse } from "../types/user";

const USER_URL =
	"https://ifge4t3dxd.execute-api.us-east-1.amazonaws.com/dev/user";

export const fetchUser = async (
	request: UserRequest
): Promise<UserResponse> => {
	const { provider_id, user_id } = request;
	const url = `${USER_URL}/${provider_id}/${user_id}`;

	try {
		const response = await fetch(url, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `${localStorage.getItem("token")}`,
			},
		});

		if (!response.ok) {
			throw new Error(
				`Failed to fetch user: ${response.status} ${response.statusText}`
			);
		}

		const data = await response.json();
		const user = data.body as UserResponse;
		return user;
	} catch (error) {
		console.error("Error fetching user:", error);
		throw error;
	}
};
