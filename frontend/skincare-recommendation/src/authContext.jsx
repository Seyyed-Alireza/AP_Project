// import { createContext, useContext, useState, useEffect } from "react";

// const AuthContext = createContext();
// export const useAuth = () => useContext(AuthContext);

// export const AuthProvider = ({ children }) => {
//   const [user, setUser] = useState(null);
//   const [token, setToken] = useState(null);

//   useEffect(() => {
//     const savedToken = localStorage.getItem("token");
//     const savedUser = localStorage.getItem("user");
//     if (savedToken && savedUser) {
//       setToken(JSON.parse(savedToken));
//       setUser(JSON.parse(savedUser));
//     }
//   }, []);

//   const login = async (username, password) => {
//     const host = window.location.hostname;
//     const res = await fetch(`http://${host}:8000/accounts/api/login/`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ username, password }),
//     });

//     if (!res.ok) {
//       const errorData = await res.json().catch(() => ({}));
//       throw new Error(errorData.error || "نام کاربری یا رمز عبور اشتباه است");
//     }

//     const data = await res.json();

//     if (data.access) {
//       setToken({ access: data.access, refresh: data.refresh });
//       localStorage.setItem(
//         "token",
//         JSON.stringify({ access: data.access, refresh: data.refresh })
//       );

//       setUser(data.user);
//       localStorage.setItem("user", JSON.stringify(data.user));
//     } else {
//       throw new Error(data.error || "Login failed");
//     }
//   };

//   const logout = () => {
//     setUser(null);
//     setToken(null);
//     localStorage.removeItem("user");
//     localStorage.removeItem("token");
//   };

//   return (
//     <AuthContext.Provider value={{ user, token, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };







import { createContext, useContext, useState, useEffect, useCallback } from "react";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [refreshTimeout, setRefreshTimeout] = useState(null);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    if (refreshTimeout) clearTimeout(refreshTimeout);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  }, [refreshTimeout]);

  const refreshToken = useCallback(async () => {
    if (!token?.refresh) return;

    try {
      const host = window.location.hostname;
      const res = await fetch(`http://${host}:8000/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: token.refresh }),
      });

      if (!res.ok) throw new Error("Refresh token failed");

      const data = await res.json();
      if (data.access) {
        const newToken = { access: data.access, refresh: token.refresh };
        setToken(newToken);
        localStorage.setItem("token", JSON.stringify(newToken));

        // تایمر را دوباره ست کن
        scheduleTokenRefresh(newToken);
      }
    } catch (err) {
      console.error("Refresh error:", err);
      logout();
    }
  }, [token, logout]);

  const scheduleTokenRefresh = useCallback((currentToken) => {
    if (!currentToken?.access) return;

    const payload = JSON.parse(atob(currentToken.access.split(".")[1]));
    const exp = payload.exp * 1000;
    const now = Date.now();
    const timeout = exp - now - 60 * 1000;

    if (timeout > 0) {
      if (refreshTimeout) clearTimeout(refreshTimeout);
      const t = setTimeout(refreshToken, timeout);
      setRefreshTimeout(t);
    }
  }, [refreshTimeout, refreshToken]);

  // --- فقط یک بار load کن بدون dependency که loop نشه ---
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken && savedUser) {
      const parsedToken = JSON.parse(savedToken);
      setToken(parsedToken);
      setUser(JSON.parse(savedUser));
      // برنامه‌ریزی refresh بدون اینکه dependency باعث loop شود
      const payload = JSON.parse(atob(parsedToken.access.split(".")[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();
      const timeout = exp - now - 60 * 1000;
      if (timeout > 0) {
        const t = setTimeout(() => refreshToken(), timeout);
        setRefreshTimeout(t);
      }
    }
  }, []); // ← خالی! فقط یک بار اجرا می‌شود

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
    if (data.access && data.refresh) {
      const newToken = { access: data.access, refresh: data.refresh };
      setToken(newToken);
      localStorage.setItem("token", JSON.stringify(newToken));

      setUser(data.user);
      localStorage.setItem("user", JSON.stringify(data.user));

      // بعد از login refresh برنامه‌ریزی می‌شود
      const payload = JSON.parse(atob(newToken.access.split(".")[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();
      const timeout = exp - now - 60 * 1000;
      if (timeout > 0) {
        const t = setTimeout(() => refreshToken(), timeout);
        setRefreshTimeout(t);
      }
    } else {
      throw new Error(data.error || "Login failed");
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (!token?.access) return;

      const payload = JSON.parse(atob(token.access.split(".")[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();

      // اگر کمتر از 1 دقیقه مونده refresh کن
      if (exp - now < 60 * 1000) {
        refreshToken();
      }
    }, 40000); // هر 30 ثانیه چک می‌کنه

    return () => clearInterval(interval);
  }, [token, refreshToken]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};










// import { createContext, useContext, useState, useEffect, useCallback } from "react";

// const AuthContext = createContext();
// export const useAuth = () => useContext(AuthContext);

// export const AuthProvider = ({ children }) => {
//   const [user, setUser] = useState(null);
//   const [token, setToken] = useState(null);
//   const [refreshTimeout, setRefreshTimeout] = useState(null);

//   const logout = useCallback(() => {
//     setUser(null);
//     setToken(null);
//     if (refreshTimeout) clearTimeout(refreshTimeout);
//     localStorage.removeItem("user");
//     localStorage.removeItem("token");
//   }, []);

//   const refreshToken = useCallback(async () => {
//     if (!token?.refresh) return;

//     try {
//       const host = window.location.hostname;
//       const res = await fetch(`http://${host}:8000/api/token/refresh/`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ refresh: token.refresh }),
//       });

//       if (!res.ok) throw new Error("Refresh token failed");

//       const data = await res.json();
//       if (data.access) {
//         const newToken = { access: data.access, refresh: token.refresh };
//         setToken(newToken);
//         localStorage.setItem("token", JSON.stringify(newToken));

//         // تایمر را دوباره ست کن
//         scheduleTokenRefresh(newToken);
//       }
//     } catch (err) {
//       console.error("Refresh error:", err);
//       logout();
//     }
//   }, [token, logout]);

//   const login = async (username, password) => {
//     const host = window.location.hostname;
//     const res = await fetch(`http://${host}:8000/accounts/api/login/`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ username, password }),
//     });

//     if (!res.ok) {
//       const errorData = await res.json().catch(() => ({}));
//       throw new Error(errorData.error || "نام کاربری یا رمز عبور اشتباه است");
//     }

//     const data = await res.json();
//     if (data.access && data.refresh) {
//       const newToken = { access: data.access, refresh: data.refresh };
//       setToken(newToken);
//       localStorage.setItem("token", JSON.stringify(newToken));

//       setUser(data.user);
//       localStorage.setItem("user", JSON.stringify(data.user));

//     } else {
//       throw new Error(data.error || "Login failed");
//     }
//   };

// //   const scheduleTokenRefresh = useCallback((currentToken) => {
// //     if (!currentToken?.access) return;

// //     const payload = JSON.parse(atob(currentToken.access.split(".")[1]));
// //     const exp = payload.exp * 1000;
// //     const now = Date.now();
// //     const timeout = exp - now - 60 * 1000;

// //     if (timeout > 0) {
// //       if (refreshTimeout) clearTimeout(refreshTimeout);
// //       const t = setTimeout(refreshToken, timeout);
// //       setRefreshTimeout(t);
// //     }
// //   }, [refreshTimeout, refreshToken]);

//   // --- فقط یک بار load کن بدون dependency که loop نشه ---
//   useEffect(() => {
//     const savedToken = localStorage.getItem("token");
//     const savedUser = localStorage.getItem("user");
//     if (savedToken && savedUser) {
//       setToken(JSON.parse(savedToken));
//       setUser(JSON.parse(savedUser));
//     }
//   }, []);

  
//   useEffect(() => {
//     const interval = setInterval(() => {
//       if (!token?.access) return;

//       const payload = JSON.parse(atob(token.access.split(".")[1]));
//       const exp = payload.exp * 1000;
//       const now = Date.now();

//       // اگر کمتر از 1 دقیقه تا انقضا مونده refresh کن
//       if (exp - now < 60 * 1000) {
//         refreshToken();
//       }
//     }, 30000); // هر 30 ثانیه چک می‌کنه

//     return () => clearInterval(interval);
//   }, [token, refreshToken]);

//   return (
//     <AuthContext.Provider value={{ user, token, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };
