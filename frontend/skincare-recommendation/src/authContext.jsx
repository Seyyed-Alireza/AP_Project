import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken && savedUser) {
      setToken(JSON.parse(savedToken));
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = async (username, password) => {
    const host = window.location.hostname;
    const res = await fetch(`http://${host}:8000/accounts/api/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.error || "نام کاربری یا رمز عبور اشتباه است");
    }

    const data = await res.json();

    if (data.access) {
      setToken({ access: data.access, refresh: data.refresh });
      localStorage.setItem(
        "token",
        JSON.stringify({ access: data.access, refresh: data.refresh })
      );

      setUser(data.user);
      localStorage.setItem("user", JSON.stringify(data.user));
    } else {
      throw new Error(data.error || "Login failed");
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
