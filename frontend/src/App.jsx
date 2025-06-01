import './App.css'
import HomePage from "./pages/home.jsx";
import ProPage from "./pages/pro.jsx";
import TestPage from "./pages/test.jsx";
import {Route, Routes} from "react-router-dom";

function App() {

  return (
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pro" element={<ProPage />} />
        <Route path="/test" element={<TestPage />} />
      </Routes>
  )
}

export default App
