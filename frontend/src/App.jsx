import './css/App.css'
import Editor from './pages/Editor.jsx'
import Home from './pages/Home.jsx'
import { Route, Routes } from 'react-router-dom'

function App() {
    return (
        <main>
            <Routes>
                <Route path="/" element={<Home/>} />
                <Route path="/edit" element={<Editor/>} />
            </Routes>
        </main>
    )
}

export default App