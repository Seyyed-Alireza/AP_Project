import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../authUser";
import '../assets/fonts/font.css';
import '../styles/login/style/style.css';

function Login({ setUser }) {  // اگر میخوای بعد از ورود user تو App ذخیره بشه
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [next, setNext] = useState("/"); // مسیر بعد از لاگین
  const { login } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    const root = document.getElementById("root");
    root.classList.add("page-login");
    return () => {
      root.classList.remove("page-login");
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    try {
      const res = await fetch("http://127.0.0.1:8000/accounts/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        login(data)
        navigate(next);
      } else {
        setError(data.error || "خطایی رخ داد");
      }
    } catch (err) {
      console.error(err);
      setError("ارتباط با سرور برقرار نشد");
    }
  };

  return (
      <form className="form-box" onSubmit={handleSubmit} noValidate>
        {error && <p className="login-p" style={{ color: "red" }}>{error}</p>}

        <input type="hidden" name="next" value={next} />

        <div className="form-field">
          <label htmlFor="username">نام کاربری</label>
          <input
            className="login-form-input"
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="off"
          />
        </div>

        <div className="form-field">
          <label htmlFor="password">رمز عبور</label>
          <input
            className="login-form-input"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="page-button">ورود</button>

        <div className="login-link">
          <span>حساب کاربری ندارید؟</span> <Link to="/register">ثبت نام کنید</Link>
        </div>
      </form>
  );
}

export default Login;
