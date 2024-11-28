import React, { createContext, useState, ReactNode, useEffect } from "react";

interface UserContextProps {
	user_id: number | null;
	setUser: (id: number) => void;
	resetUser: () => void;
}

const UserContext = createContext<UserContextProps | undefined>(undefined);

interface UserProviderProps {
	children: ReactNode;
}

const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
	const [user_id, setUserId] = useState<number | null>(() => {
		const storedId = localStorage.getItem("user_id");
		return storedId ? Number(storedId) : null;
	});

	const setUser = (id: number) => {
		setUserId(id);
		localStorage.setItem("user_id", id.toString());
	};

	const resetUser = () => {
		setUserId(null);
		localStorage.removeItem("user_id");
	};

	useEffect(() => {
		const storedId = localStorage.getItem("user_id");
		if (storedId) {
			setUserId(Number(storedId));
		}
	}, []);

	return (
		<UserContext.Provider value={{ user_id, setUser, resetUser }}>
			{children}
		</UserContext.Provider>
	);
};

export default UserContext;
export { UserProvider };
