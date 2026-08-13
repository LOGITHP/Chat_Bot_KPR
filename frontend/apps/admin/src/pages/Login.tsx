import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Shield, Eye, EyeOff, Mail, Lock, AlertCircle } from "lucide-react"

export const ADMIN_TOKEN_KEY = "campus_admin_token"
export const ADMIN_NAME_KEY  = "campus_admin_name"

export function saveAdminSession(token: string, name: string) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
  localStorage.setItem(ADMIN_NAME_KEY, name)
}

export function clearAdminSession() {
  localStorage.removeItem(ADMIN_TOKEN_KEY)
  localStorage.removeItem(ADMIN_NAME_KEY)
}

export function getAdminToken() { return localStorage.getItem(ADMIN_TOKEN_KEY) }
export function getAdminName()  { return localStorage.getItem(ADMIN_NAME_KEY) }

export default function AdminLogin() {
  const navigate   = useNavigate()
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [showPwd,  setShowPwd]  = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || !password.trim()) { setError("Please fill in all fields."); return }
    setError("")
    setLoading(true)
    try {
      const res  = await fetch("/api/v1/auth/login", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ identifier: email.trim(), password }),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || "Login failed."); return }
      if (data.role !== "admin") {
        setError("Access denied. This portal is for administrators only.")
        return
      }
      saveAdminSession(data.access_token, data.name || "Admin")
      navigate("/dashboard", { replace: true })
    } catch {
      setError("Unable to reach the server. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Dark bg blobs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-900/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-violet-900/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div
          className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl"
          style={{ boxShadow: "0 0 80px rgba(99,102,241,0.15)" }}
        >
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="relative mb-4">
              <div className="w-20 h-20 rounded-2xl overflow-hidden shadow-xl ring-4 ring-indigo-500/20 bg-white flex items-center justify-center">
                <img src="/kpr_logo.png" alt="KPRIET Logo" className="w-full h-full object-contain p-1" />
              </div>
              <div className="absolute -bottom-2 -right-2 w-7 h-7 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md">
                <Shield className="w-3.5 h-3.5 text-white" />
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white">Admin Portal</h1>
            <p className="text-slate-400 text-sm mt-1">CampusAI — KPRIET</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="flex items-start gap-2 p-3 rounded-xl bg-red-950/60 border border-red-800/50 text-red-300 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            {/* Email */}
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Admin Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="principal@kpriet.ac.in"
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-slate-800/60 border border-slate-700 text-white text-sm placeholder:text-slate-500 outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type={showPwd ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-10 py-2.5 rounded-xl bg-slate-800/60 border border-slate-700 text-white text-sm placeholder:text-slate-500 outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {loading ? "Authenticating…" : "Sign In to Admin"}
            </button>
          </form>

          <p className="text-center text-[11px] text-slate-600 mt-6">
            Student portal access → use the user application instead.
          </p>
        </div>
      </div>
    </div>
  )
}
