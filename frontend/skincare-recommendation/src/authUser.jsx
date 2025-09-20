import { createContext, useContext, useState, useEffect } from "react";

// ایجاد Context
const AuthContext = createContext();

// هوک کمکی برای دسترسی راحت به context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // وقتی اپ بالا میاد (mount) کاربر رو از localStorage بخونیم
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // تابع login → ذخیره کاربر و نگه داشتن تو localStorage
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  // تابع logout → پاک کردن user
  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
