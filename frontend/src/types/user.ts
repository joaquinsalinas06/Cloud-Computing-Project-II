export interface UserResponse {
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

export interface UserRequest {
	provider_id: string;
	user_id: number;
}
