import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import AdminDashboard from './components/AdminDashboard';
import StudentPortal from './components/StudentPortal';
import GuestPortal from './components/GuestPortal';
import { ShieldCheck, GraduationCap, UserCheck, Sparkles, Lock, KeyRound, User } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('student'); // 'student', 'admin', 'guest'
  const [currentUser, setCurrentUser] = useState(null);
  
  // Auth Form state
  const [authMode, setAuthMode] = useState('login'); // 'login', 'register'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [studentIdInput, setStudentIdInput] = useState('');
  const [authError, setAuthError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check existing stored session
    const storedUsername = localStorage.getItem('username');
    const storedRole = localStorage.getItem('role');
    const storedStudentId = localStorage.getItem('student_id');

    if (storedUsername && storedRole) {
      setCurrentUser({
        username: storedUsername,
        role: storedRole,
        student_id: storedStudentId
      });
      setActiveTab(storedRole);
    }
  }, []);

  const handleLogout = () => {
    api.clearAuth();
    setCurrentUser(null);
    setUsername('');
    setPassword('');
    setStudentIdInput('');
  };

  const handleAdminAuth = async (e) => {
    e.preventDefault();
    setAuthError(null);
    setIsLoading(true);

    try {
      if (authMode === 'login') {
        const res = await api.login(username, password);
        if (res.role !== 'admin') {
          throw new Error('Account does not have Admin privileges.');
        }
        setCurrentUser(res);
      } else {
        const res = await api.register(username, password, 'admin');
        setCurrentUser(res);
      }
    } catch (err) {
      setAuthError(err.message || 'Admin authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStudentAuth = async (e) => {
    e.preventDefault();
    setAuthError(null);
    setIsLoading(true);

    try {
      if (authMode === 'login') {
        const res = await api.login(username, password);
        setCurrentUser(res);
      } else {
        const res = await api.register(username, password, 'student', studentIdInput || null);
        setCurrentUser(res);
      }
    } catch (err) {
      setAuthError(err.message || 'Student authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestAccess = async () => {
    setIsLoading(true);
    try {
      const res = await api.guestLogin(username || null);
      setCurrentUser(res);
      setActiveTab('guest');
    } catch (err) {
      setAuthError('Guest access failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header className="glass-panel" style={{ borderRadius: '0', padding: '0.85rem 2rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'var(--primary-gradient)', padding: '0.5rem', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center' }}>
            <Sparkles size={22} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'var(--primary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              College RAG Portal
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FastAPI • MinIO • MongoDB • Qdrant • Ollama</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: 'flex', background: 'rgba(0,0,0,0.3)', padding: '0.3rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--glass-border)', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveTab('student')} 
            className="btn-secondary" 
            style={{ 
              padding: '0.4rem 1rem', 
              fontSize: '0.85rem',
              background: activeTab === 'student' ? 'var(--primary-gradient)' : 'transparent',
              border: 'none',
              color: activeTab === 'student' ? 'white' : 'var(--text-muted)'
            }}
          >
            <GraduationCap size={16} /> Student Portal
          </button>

          <button 
            onClick={() => setActiveTab('guest')} 
            className="btn-secondary" 
            style={{ 
              padding: '0.4rem 1rem', 
              fontSize: '0.85rem',
              background: activeTab === 'guest' ? 'var(--secondary-gradient)' : 'transparent',
              border: 'none',
              color: activeTab === 'guest' ? 'white' : 'var(--text-muted)'
            }}
          >
            <UserCheck size={16} /> Guest Mode
          </button>

          <button 
            onClick={() => setActiveTab('admin')} 
            className="btn-secondary" 
            style={{ 
              padding: '0.4rem 1rem', 
              fontSize: '0.85rem',
              background: activeTab === 'admin' ? 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)' : 'transparent',
              border: 'none',
              color: activeTab === 'admin' ? 'white' : 'var(--text-muted)'
            }}
          >
            <ShieldCheck size={16} /> Admin Control
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1 }}>
        {/* Guest View */}
        {activeTab === 'guest' && (
          currentUser && currentUser.role === 'guest' ? (
            <GuestPortal user={currentUser} onLogout={handleLogout} />
          ) : (
            <div style={{ maxWidth: '420px', margin: '4rem auto', padding: '2rem' }} className="glass-panel">
              <h2 style={{ textAlign: 'center', marginBottom: '0.5rem', fontSize: '1.4rem' }}>Guest Fast Query Access</h2>
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Ask temporary questions without registering a student account.
              </p>
              <button onClick={handleGuestAccess} disabled={isLoading} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                {isLoading ? "Starting Guest Session..." : "Enter Guest Query Portal"}
              </button>
            </div>
          )
        )}

        {/* Student View */}
        {activeTab === 'student' && (
          currentUser && (currentUser.role === 'student' || currentUser.role === 'admin') ? (
            <StudentPortal user={currentUser} onLogout={handleLogout} />
          ) : (
            <div style={{ maxWidth: '420px', margin: '3rem auto', padding: '2rem' }} className="glass-panel">
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <GraduationCap size={44} color="#3b82f6" style={{ margin: '0 auto 0.5rem auto' }} />
                <h2 style={{ fontSize: '1.4rem' }}>Student Login</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Sign in with Student ID or credentials to access past chat histories
                </p>
              </div>

              {authError && (
                <div style={{ padding: '0.75rem', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', color: '#f87171', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', marginBottom: '1rem', textAlign: 'center' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleStudentAuth}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                    Username or Student ID
                  </label>
                  <div style={{ position: 'relative' }}>
                    <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
                    <input 
                      type="text" 
                      required 
                      placeholder="e.g. STU-10294 or student1" 
                      value={username} 
                      onChange={(e) => setUsername(e.target.value)} 
                      className="input-field" 
                      style={{ paddingLeft: '2.25rem' }} 
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                    Password
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
                    <input 
                      type="password" 
                      required 
                      placeholder="••••••••" 
                      value={password} 
                      onChange={(e) => setPassword(e.target.value)} 
                      className="input-field" 
                      style={{ paddingLeft: '2.25rem' }} 
                    />
                  </div>
                </div>

                {authMode === 'register' && (
                  <div style={{ marginBottom: '1.25rem' }}>
                    <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                      Student ID (Optional)
                    </label>
                    <input 
                      type="text" 
                      placeholder="STU-XXXXXX" 
                      value={studentIdInput} 
                      onChange={(e) => setStudentIdInput(e.target.value)} 
                      className="input-field" 
                    />
                  </div>
                )}

                <button type="submit" disabled={isLoading} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                  {isLoading ? "Authenticating..." : (authMode === 'login' ? "Student Sign In" : "Register Student Account")}
                </button>
              </form>

              <div style={{ textAlign: 'center', marginTop: '1.25rem' }}>
                <button 
                  onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                  style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '0.85rem', cursor: 'pointer' }}
                >
                  {authMode === 'login' ? "Need an account? Register as Student" : "Already have an account? Sign In"}
                </button>
              </div>
            </div>
          )
        )}

        {/* Admin View */}
        {activeTab === 'admin' && (
          currentUser && currentUser.role === 'admin' ? (
            <AdminDashboard onLogout={handleLogout} />
          ) : (
            <div style={{ maxWidth: '420px', margin: '3rem auto', padding: '2rem' }} className="glass-panel">
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <ShieldCheck size={44} color="#ef4444" style={{ margin: '0 auto 0.5rem auto' }} />
                <h2 style={{ fontSize: '1.4rem' }}>Admin Control Sign In</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Manage PDFs, upload documents to MinIO, and control Vector DB sync
                </p>
              </div>

              {authError && (
                <div style={{ padding: '0.75rem', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', color: '#f87171', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', marginBottom: '1rem', textAlign: 'center' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleAdminAuth}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>Admin Username</label>
                  <input type="text" required placeholder="admin" value={username} onChange={(e) => setUsername(e.target.value)} className="input-field" />
                </div>
                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>Admin Password</label>
                  <input type="password" required placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" />
                </div>
                <button type="submit" disabled={isLoading} className="btn-primary" style={{ width: '100%', justifyContent: 'center', background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)' }}>
                  {isLoading ? "Verifying Credentials..." : (authMode === 'login' ? "Admin Sign In" : "Register Admin")}
                </button>
              </form>

              <div style={{ textAlign: 'center', marginTop: '1.25rem' }}>
                <button 
                  onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                  style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '0.85rem', cursor: 'pointer' }}
                >
                  {authMode === 'login' ? "Create Admin Account" : "Sign In to Admin Account"}
                </button>
              </div>
            </div>
          )
        )}
      </main>
    </div>
  );
}
