import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../authUser";

const Header = () => {
  const { user, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  const toggleMenu = () => {
    setShowMenu((prev) => !prev);
  };

  return (
    <header>
      <div className="header_container">
        <div className="logo_name">
          <div className="logo">لوگو سایت</div>
          <div className="name">اسم سایت</div>
        </div>

        {user ? (
          <>
            <button id="user_name" type="button" onClick={toggleMenu}>
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
                  src="/static/images/default.svg"
                  alt="عکس پیش‌فرض"
                  width={40}
                />
              )}
            </button>

            {/* منوی کاربر فقط وقتی state فعال باشه نشون داده میشه */}
            {showMenu && (
              <div id="user_box">
                <p>نام: {user.username}</p>
                <p onClick={() => navigate("/")}>صفحه اصلی</p>
                <p onClick={() => navigate("/profile")}>صفحه شخصی</p>
                <p onClick={() => navigate("/editprofile")}>ویرایش اطلاعات</p>
                <button onClick={() => { logout(); navigate("/"); }}>خروج</button>
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
