import { useState } from "react"
import { Settings as SettingsIcon, Moon, Sun, Bell, Shield, LogOut } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { clearSession } from "./Login"

export default function Settings() {
  const [notifications, setNotifications] = useState(true)
  const navigate = useNavigate()

  function handleLogout() {
    clearSession()
    navigate("/login", { replace: true })
  }

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto w-full space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <SettingsIcon className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          Preferences & Settings
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Manage your account notification preferences and campus assistant settings.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-gray-100 dark:border-slate-800 shadow-sm space-y-6">
        <div className="divide-y divide-gray-100 dark:divide-slate-800 text-xs">
          <div className="py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell className="w-4 h-4 text-indigo-500" />
              <div>
                <span className="font-bold text-gray-900 dark:text-white">Campus Circular Notifications</span>
                <p className="text-gray-400">Receive alerts when new college announcements or exam schedules are posted.</p>
              </div>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              className={`w-11 h-6 rounded-full transition-colors relative ${notifications ? "bg-indigo-600" : "bg-gray-200 dark:bg-slate-700"}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${notifications ? "left-6" : "left-1"}`} />
            </button>
          </div>

          <div className="py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-emerald-500" />
              <div>
                <span className="font-bold text-gray-900 dark:text-white">Role-based Access Filtering</span>
                <p className="text-gray-400">Restricts knowledge search to authorized department and year curriculum documents.</p>
              </div>
            </div>
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">
              Active
            </span>
          </div>

          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="font-bold text-red-600 dark:text-red-400">Sign Out</span>
              <p className="text-gray-400">End your current session on this device.</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-3.5 py-1.5 rounded-xl border border-red-200 dark:border-red-800 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 font-semibold transition flex items-center gap-1.5"
            >
              <LogOut className="w-3.5 h-3.5" /> Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
