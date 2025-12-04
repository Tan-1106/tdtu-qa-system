import { useState, useEffect } from 'react';
import { getCurrentUser, logoutUser } from '../api/userApi';
import { getAccessToken } from '../axiosInstance'; 

const useUserAuth = () => {
    const [user, setUser] = useState(null); 
    const [isLoadingUser, setIsLoadingUser] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = getAccessToken();

        if (!token) {
            setIsLoadingUser(false);
            setIsAuthenticated(false);
            return;
        }

        const fetchUser = async () => {
            try {
                const userData = await getCurrentUser();

                setUser({
                    name: userData.name,
                    studentId: userData.sub, 
                    department: userData.faculty, 
                    avatar: userData.name.charAt(0).toUpperCase(),
                    role: userData.role, 
                });
                setIsAuthenticated(true);
            } catch (error) {
                console.error("Authentication failed, user data not loaded:", error);
                setIsAuthenticated(false);
                setUser(null);
            } finally {
                setIsLoadingUser(false);
            }
        };

        fetchUser();
    }, []);

    const handleLogout = () => {
        logoutUser();
        setUser(null);
        setIsAuthenticated(false);
    };

    return { user, isLoadingUser, isAuthenticated, handleLogout };
};

export default useUserAuth;