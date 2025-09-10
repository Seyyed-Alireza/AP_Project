import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
// import './App.css'
import './styles/main.css';
import Header from "./components/Header";
import Nav from './components/Nav';
import Main from './components/Main';
import Footer from './components/Footer';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("/api/get_user/")
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => console.error(err));
  }, []);
  return (
    <div className="App">
      <header>
        <Header user={user}/>
      </header>
      <nav>
        <Nav />
      </nav>
      <main>
        <Main />
      </main>
      <Footer />
    </div>
  )
}


export default App
