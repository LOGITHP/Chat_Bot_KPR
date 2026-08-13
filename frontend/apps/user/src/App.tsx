import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import UserLayout from "./layouts/UserLayout"
import Dashboard from "./pages/Dashboard"
import Chat from "./pages/Chat"
import History from "./pages/History"
import Search from "./pages/Search"
import Campus from "./pages/Campus"
import Departments from "./pages/Departments"
import Clubs from "./pages/Clubs"
import Transport from "./pages/Transport"
import Documents from "./pages/Documents"
import Profile from "./pages/Profile"
import Settings from "./pages/Settings"
import Login from "./pages/Login"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/guest" element={<Navigate to="/chat" />} />
        
        {/* Main Application Layout */}
        <Route path="/" element={<UserLayout />}>
          <Route index element={<Navigate to="/chat" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="chat/:conversationId" element={<Chat />} />
          <Route path="history" element={<History />} />
          <Route path="search" element={<Search />} />
          <Route path="documents" element={<Documents />} />
          <Route path="departments" element={<Departments />} />
          <Route path="departments/:id" element={<Departments />} />
          <Route path="clubs" element={<Clubs />} />
          <Route path="clubs/:id" element={<Clubs />} />
          <Route path="transport" element={<Transport />} />
          <Route path="campus" element={<Campus />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
