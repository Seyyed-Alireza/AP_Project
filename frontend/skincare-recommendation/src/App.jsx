import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
// import './App.css'
import './styles/main.css';
import Header from "./components/Header";
import Nav from './components/Nav';
import Main from './components/Main';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <header>
        <Header />
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
