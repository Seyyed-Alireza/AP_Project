import Header from "../components/Header";
import Nav from "../components/Nav";
import Footer from "../components/Footer";
import { Outlet } from "react-router-dom";
import '../styles/mainpage/style/main.css';

function MainLayout({ user }) {
  return (
    <>
      <Header user={user}/>
      <Nav />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  );
}

export default MainLayout;
