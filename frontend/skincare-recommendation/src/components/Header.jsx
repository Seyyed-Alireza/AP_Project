const Header = ({ user }) => {
  return (
    <header>
      <div className="header_container">
        <div className="logo_name">
          <div className="logo">لوگو سایت</div>
          <div className="name">اسم سایت</div>
        </div>

        {user ? (
          <>
            <button id="user_name" type="button">
              {user.username}
              {user.userprofile?.profile_picture ? (
                <img
                  className="prof_pic"
                  src={user.userprofile.profile_picture}
                  alt="عکس پروفایل"
                  width={120}
                  height={120}
                />
              ) : (
                <img
                  className="prof_pic_default"
                  src="/static/images/default.svg"
                  alt="عکس پیش‌فرض"
                  width={120}
                />
              )}
            </button>

            <div id="user_box">
              <p className="box_name">
                <span style={{ fontSize: "15px" }}>نام:</span> {user.username}
              </p>

              <p onClick={() => (window.location.href = "/mainpage")}>
                {/* SVG صفحه اصلی */}
                صفحه اصلی
              </p>

              <p onClick={() => (window.location.href = "/profile")}>
                {/* SVG صفحه شخصی */}
                صفحه شخصی
              </p>

              <p onClick={() => (window.location.href = "/editprofile")}>
                {/* SVG ویرایش اطلاعات */}
                ویرایش اطلاعات
              </p>

              <button
                type="button"
                className="signout"
                onClick={() => {
                  // برای logout می‌تونی fetch/post بزنی و بعد redirect کنی
                  window.location.href = "/logout";
                }}
              >
                {/* SVG خروج */}
                خروج
              </button>
            </div>
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
