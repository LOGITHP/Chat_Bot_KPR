import { Link, Outlet, useLocation } from "react-router-dom"
import { MessageSquarePlus, History, Search, Building2, Users, Bus, Info, FileText, User, Settings, LogOut, Menu, X } from "lucide-react"
import { useState } from "react"
import { cn } from "../lib/utils"

export default function UserLayout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { name: "Chat", path: "/chat", icon: MessageSquarePlus },
    { name: "History", path: "/history", icon: History },
    { name: "Search", path: "/search", icon: Search },
  ]

  const campusItems = [
    { name: "Departments", path: "/departments", icon: Building2 },
    { name: "Clubs", path: "/clubs", icon: Users },
    { name: "Transport", path: "/transport", icon: Bus },
    { name: "Campus Information", path: "/campus", icon: Info },
    { name: "Documents", path: "/documents", icon: FileText },
  ]

  const accountItems = [
    { name: "Profile", path: "/profile", icon: User },
    { name: "Settings", path: "/settings", icon: Settings },
  ]

  const NavLink = ({ item }: { item: any }) => {
    const isActive = location.pathname.startsWith(item.path)
    return (
      <Link
        to={item.path}
        className={cn(
          "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
          isActive 
            ? "bg-primary text-primary-foreground" 
            : "text-sidebar-foreground hover:bg-gray-100 dark:hover:bg-gray-800"
        )}
      >
        <item.icon className="h-4 w-4" />
        {item.name}
      </Link>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Menu Toggle */}
      <div className="md:hidden fixed top-0 left-0 w-full flex items-center justify-between px-4 h-14 border-b border-border bg-background z-50">
        <div className="font-semibold text-lg">CampusAI</div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={cn(
        "fixed md:static inset-y-0 left-0 z-40 w-64 bg-sidebar border-r border-border transform transition-transform duration-200 ease-in-out flex flex-col",
        isMobileMenuOpen ? "translate-x-0 pt-14 md:pt-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="p-4 hidden md:flex items-center">
          <div className="font-semibold text-xl">CampusAI</div>
        </div>

        <div className="p-4">
          <Link to="/chat" className="flex items-center gap-2 w-full justify-center px-4 py-2.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
            <MessageSquarePlus className="h-5 w-5" />
            New Chat
          </Link>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          <div className="space-y-1">
            {navItems.map(item => <NavLink key={item.path} item={item} />)}
          </div>

          <div>
            <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Campus</div>
            <div className="space-y-1">
              {campusItems.map(item => <NavLink key={item.path} item={item} />)}
            </div>
          </div>
        </div>

        <div className="p-3 border-t border-border space-y-1">
          {accountItems.map(item => <NavLink key={item.path} item={item} />)}
          <button className="flex w-full items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-sidebar-foreground hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400 transition-colors">
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 pt-14 md:pt-0">
        <Outlet />
      </main>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </div>
  )
}
