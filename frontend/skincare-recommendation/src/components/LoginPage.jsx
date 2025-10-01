import { useState } from "react";
import "../assets/fonts/font.css"

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // برای نگه‌داری سشن Django
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Login successful:", data);
        window.location.href = "/"; // بعد از لاگین بفرست به صفحه اصلی
      } else {
        setError("نام کاربری یا رمز عبور اشتباه است.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("مشکلی پیش آمد. دوباره تلاش کنید.");
    }
  };

  return (
    <div className="form-box">
      <form onSubmit={handleSubmit} noValidate>
        <input type="hidden" name="next" value="/" />

        <div className="form-field">
          <label htmlFor="username">نام کاربری</label>
          <input
            id="username"
            type="text"
            name="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="form-field">
          <label htmlFor="password">رمز عبور</label>
          <input
            id="password"
            type="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button type="submit">ورود</button>

        <div className="login-link">
          <span>حساب کاربری ندارید؟</span>
          <a href="/register">ثبت نام کنید</a>
        </div>
      </form>
    </div>
  );
}
