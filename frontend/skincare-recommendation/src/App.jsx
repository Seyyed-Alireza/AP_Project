import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Login from './pages/login';
import Header from "./components/Header";
import Nav from './components/Nav';
import Main from './components/Main';
import Footer from './components/Footer';

function App() {
  const [user, setUser] = useState(null);

  // گرفتن user فعلی از سرور
  useEffect(() => {
    fetch("http://127.0.0.1:8000/accounts/api/get_user/")
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <Router>
      <Routes>
        <Route path='/' element={<MainLayout user={user} />}>
          <Route index element={<Home />} />
        </Route>
        <Route path='/login' element={<Login setUser={setUser} />} />
      </Routes>
    </Router>
  );
}

export default App;
