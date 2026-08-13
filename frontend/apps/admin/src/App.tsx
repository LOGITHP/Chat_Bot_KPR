import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import AdminLayout  from "./layouts/AdminLayout"
import Dashboard    from "./pages/Dashboard"
import Documents    from "./pages/Documents"
import Departments  from "./pages/Departments"
import Clubs        from "./pages/Clubs"
import Transport    from "./pages/Transport"
import CampusData   from "./pages/CampusData"
import Users        from "./pages/Users"
import Categories   from "./pages/Categories"
import Settings     from "./pages/Settings"
import AdminLogin, { getAdminToken } from "./pages/Login"

function AdminGuard({ children }: { children: React.ReactNode }) {
  return getAdminToken() ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<AdminLogin />} />

        <Route
          path="/"
          element={<AdminGuard><AdminLayout /></AdminGuard>}
        >
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard"   element={<Dashboard />} />
          <Route path="documents"   element={<Documents />} />
          <Route path="departments" element={<Departments />} />
          <Route path="clubs"       element={<Clubs />} />
          <Route path="transport"   element={<Transport />} />
          <Route path="campus"      element={<CampusData />} />
          <Route path="users"       element={<Users />} />
          <Route path="categories"  element={<Categories />} />
          <Route path="settings"    element={<Settings />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App
