import { useState } from "react";

const Header = ({ user }) => {
  const [showMenu, setShowMenu] = useState(false);

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
                <p className="box_name">
                  <span style={{ fontSize: "15px" }}>نام:</span> {user.username}
                </p>

                <p onClick={() => (window.location.href = "/")}>
                  صفحه اصلی
                </p>

                <p onClick={() => (window.location.href = "/profile")}>
                  صفحه شخصی
                </p>

                <p onClick={() => (window.location.href = "/editprofile")}>
                  ویرایش اطلاعات
                </p>

                <button
                  type="button"
                  className="signout"
                  onClick={() => {
                    window.location.href = "/logout";
                  }}
                >
                  خروج
                </button>
              </div>
            )}
          </>
        ) : (
          <button
            id="register-login-button"
            type="button"
            onClick={() => (window.location.href = "/login")}
          >
            ورود/ ثبت نام
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
