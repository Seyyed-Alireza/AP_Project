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
            <button className="header-button"
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
                <p className="user-menu-info">
                  نام: {user.username}
                  </p>
                <p className="user-menu-choice" onClick={() => navigate("/")}>
                  <svg
                    width="24px"
                    height="24px"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="size-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
                    />
                  </svg>
                  صفحه اصلی
                  </p>
                <p className="user-menu-choice" onClick={() => navigate("/profile")}>
                  <svg
                    width="24px"
                    height="24px"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="size-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                    />
                  </svg>

                  صفحه شخصی
                  </p>
                <p className="user-menu-choice" onClick={() => navigate("/editprofile")}>
                  <svg
                    width="24px"
                    height="24px"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="size-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                    />
                  </svg>
                  ویرایش اطلاعات
                  </p>
                <button className="signout"
                  onClick={() => {
                    logout();
                    navigate("/");
                  }}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    xmlnsXlink="http://www.w3.org/1999/xlink"
                    version="1.1"
                    id="mdi-account-arrow-right-outline"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M19,21V19H15V17H19V15L22,18L19,21M13,18C13,18.71 13.15,19.39 13.42,20H2V17C2,14.79 5.58,13 10,13C11,13 11.96,13.09 12.85,13.26C13.68,13.42 14.44,13.64 15.11,13.92C13.83,14.83 13,16.32 13,18M4,17V18H11C11,16.96 11.23,15.97 11.64,15.08L10,15C6.69,15 4,15.9 4,17M10,4A4,4 0 0,1 14,8A4,4 0 0,1 10,12A4,4 0 0,1 6,8A4,4 0 0,1 10,4M10,6A2,2 0 0,0 8,8A2,2 0 0,0 10,10A2,2 0 0,0 12,8A2,2 0 0,0 10,6Z" />
                  </svg>
                  خروج
                </button>
              </div>
            )}
          </>
        ) : (
          <button className="header-button" onClick={() => navigate("/login")}>ورود/ ثبت نام</button>
        )}
      </div>
    </header>
  );
};

export default Header;
