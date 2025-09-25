import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../authUser";
import defaultUserPic from "../assets/images/default-user-pic.svg";

const Header = () => {
  const { user, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const [menuLeft, setMenuLeft] = useState("0px");

  const navigate = useNavigate();

  // ریف‌ها برای تشخیص کلیک بیرون
  const btnRef = useRef(null);
  const menuRef = useRef(null);
  const containerRef = useRef(null);

  // منطق محاسبه موقعیت منو
  const setLeft = () => {
    if (!containerRef.current) return;
    const vw = window.innerWidth;
    const cw = containerRef.current.getBoundingClientRect().width;

    if (vw > cw) {
      setMenuLeft(`${(vw - cw) / 2}px`);
    }
    if (vw < cw) {
      setMenuLeft("10px");
    }
    if (vw < 576) {
      setMenuLeft("5px");
    }
  };

  // اجرای setLeft روی resize
  useEffect(() => {
    setLeft();
    window.addEventListener("resize", setLeft);
    return () => window.removeEventListener("resize", setLeft);
  }, []);

  // بستن منو وقتی بیرون کلیک بشه
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        btnRef.current &&
        !btnRef.current.contains(event.target) &&
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setShowMenu(false);
      }
    };

    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, []);

  const toggleMenu = () => {
    setShowMenu((prev) => !prev);
    setLeft();
  };

  return (
    <header>
      <div className="header_container" ref={containerRef}>
        <div className="logo_name">
          <div className="logo">لوگو سایت</div>
          <div className="name">اسم سایت</div>
        </div>

        {user ? (
          <>
            <button
              id="user_name"
              type="button"
              ref={btnRef}
              onClick={toggleMenu}
            >
              {user.username}
              {user.userprofile?.profile_picture ? (
                <img
                  className="prof_pic"
                  src={user.userprofile.profile_picture}
                  alt="عکس پروفایل"
                  width={40}
                  height={40}
                />
              ) : (
                <img
                  className="prof_pic_default"
                  src={defaultUserPic}
                  alt="عکس کاربر"
                  width={40}
                />
              )}
            </button>

            {showMenu && (
              <div
                id="user_box"
                ref={menuRef}
                style={{ left: menuLeft, position: "absolute", zIndex: 5 }}
              >
                <p>نام: {user.username}</p>
                <p onClick={() => navigate("/")}>صفحه اصلی</p>
                <p onClick={() => navigate("/profile")}>صفحه شخصی</p>
                <p onClick={() => navigate("/editprofile")}>ویرایش اطلاعات</p>
                <button className="button-to-link"
                  onClick={() => {
                    logout();
                    navigate("/");
                  }}
                >
                  خروج
                </button>
              </div>
            )}
          </>
        ) : (
          <button onClick={() => navigate("/login")}>ورود/ ثبت نام</button>
        )}
      </div>
    </header>
  );
};

export default Header;
