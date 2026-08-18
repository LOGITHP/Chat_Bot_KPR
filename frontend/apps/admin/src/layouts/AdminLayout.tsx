import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import { LayoutDashboard, FileText, Building2, Users, Bus, Info, FolderTree, Settings, LogOut } from "lucide-react"
import { cn } from "../lib/utils"
import { clearAdminSession, getAdminName } from "../pages/Login"

export default function AdminLayout() {
  const location = useLocation()
  const navigate  = useNavigate()
  const adminName = getAdminName() || "Admin"

  function handleLogout() {
    clearAdminSession()
    navigate("/login", { replace: true })
  }

  const navGroups = [
    {
      title: "Dashboard",
      items: [
        { name: "Overview", path: "/dashboard", icon: LayoutDashboard }
      ]
    },
    {
      title: "Content",
      items: [
        { name: "Documents", path: "/documents", icon: FileText },
        { name: "Departments", path: "/departments", icon: Building2 },
        { name: "Clubs", path: "/clubs", icon: Users },
        { name: "Transport", path: "/transport", icon: Bus },
        { name: "Campus Data", path: "/campus", icon: Info },
        { name: "Categories", path: "/categories", icon: FolderTree },
      ]
    },
    {
      title: "Administration",
      items: [
        { name: "Users", path: "/users", icon: Users }
      ]
    },
    {
      title: "System",
      items: [
        { name: "Settings", path: "/settings", icon: Settings }
      ]
    }
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-sidebar border-r border-border flex flex-col hidden md:flex">
        <div className="h-14 flex items-center px-4 border-b border-border bg-sidebar text-sidebar-foreground">
          <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
            <img src="/kpr_logo.png" alt="KPRIET" className="h-8 w-8 rounded-md bg-white object-contain p-0.5" />
            <span>CampusAI Admin</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
          {navGroups.map((group, idx) => (
            <div key={idx}>
              {group.title !== "Dashboard" && (
                <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  {group.title}
                </div>
              )}
              <div className="space-y-1">
                {group.items.map(item => {
                  const isActive = location.pathname.startsWith(item.path)
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                        isActive 
                          ? "bg-primary text-primary-foreground" 
                          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-50"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-border/20">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-slate-400 hover:bg-red-900/20 hover:text-red-400 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 flex items-center justify-between px-4 md:px-6 border-b border-border bg-white dark:bg-gray-900">
          <div className="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-200 md:hidden">
            <img src="/kpr_logo.png" alt="KPRIET" className="h-8 w-8 rounded-md bg-white object-contain p-0.5" />
            <span>CampusAI Admin</span>
          </div>
          <div className="flex items-center gap-3 ml-auto">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 hidden sm:block">{adminName}</div>
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold text-xs shadow">
              {adminName.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-gray-50 dark:bg-gray-950">
          <div className="max-w-7xl mx-auto w-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
