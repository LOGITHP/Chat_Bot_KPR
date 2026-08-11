const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiService {
  getToken() {
    return localStorage.getItem('access_token');
  }

  setAuth(data) {
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
    }
    if (data.username) {
      localStorage.setItem('username', data.username);
    }
    if (data.role) {
      localStorage.setItem('role', data.role);
    }
    if (data.student_id) {
      localStorage.setItem('student_id', data.student_id);
    }
  }

  clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    localStorage.removeItem('student_id');
  }

  getHeaders(isMultipart = false) {
    const headers = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = this.getHeaders(options.isMultipart);

    const config = {
      method: options.method || 'GET',
      headers: { ...headers, ...options.headers },
      body: options.body
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `Request failed with status ${response.status}`);
      }
      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  // --- AUTH ENDPOINTS ---
  async register(username, password, role = 'student', studentId = null) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, role, student_id: studentId })
    });
    this.setAuth(data);
    return data;
  }

  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setAuth(data);
    return data;
  }

  async guestLogin(guestName = null) {
    const data = await this.request('/auth/guest-login', {
      method: 'POST',
      body: JSON.stringify({ guest_name: guestName })
    });
    this.setAuth(data);
    return data;
  }

  async getProfile() {
    return await this.request('/auth/me');
  }

  // --- ADMIN PDF & DOCUMENT ENDPOINTS ---
  async uploadPdf(file, category = 'General') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    return await this.request('/admin/upload-pdf', {
      method: 'POST',
      isMultipart: true,
      body: formData
    });
  }

  async getDocuments(category = null, search = null) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    const queryStr = params.toString() ? `?${params.toString()}` : '';

    return await this.request(`/admin/documents${queryStr}`);
  }

  async deleteDocument(docId) {
    return await this.request(`/admin/documents/${docId}`, {
      method: 'DELETE'
    });
  }

  async reindexDocuments() {
    return await this.request('/admin/reindex', {
      method: 'POST'
    });
  }

  // --- CHAT ENDPOINTS ---
  async queryChat(question, sessionId = null, category = null) {
    return await this.request('/chat/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        session_id: sessionId,
        category
      })
    });
  }

  async getChatHistory() {
    return await this.request('/chat/history');
  }

  async getSessionDetails(sessionId) {
    return await this.request(`/chat/history/${sessionId}`);
  }

  async deleteSession(sessionId) {
    return await this.request(`/chat/history/${sessionId}`, {
      method: 'DELETE'
    });
  }
}

export const api = new ApiService();
