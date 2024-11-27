export interface LoginRequest {
	provider_id: string;
	email: string;
	password: string;
}

export interface LoginResponse {
	status: string;
	message: string;
	data?: {
		token: string;
		expiration: string;
		user_id: number;
	};
}

export interface RegisterRequest {
	provider_id: string;
	password: string;
	email: string;
	username: string;
	name: string;
	last_name: string;
	phone_number: string;
	birth_date: string;
	gender: string;
	age: number;
	active: boolean;
	created_at: string;
}

export interface RegisterResponse {
	statusCode: number;
	body: {
		message: string;
		user_id: number;
	};
}
