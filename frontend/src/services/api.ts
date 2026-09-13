/**
 * NETRYX EVIDENCE — API Service
 * Axios client with JWT interceptors and auto-refresh.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ── Request Interceptor: Attach JWT ─────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response Interceptor: Auto-refresh on 401 ───────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        localStorage.setItem('access_token', data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// ── Auth API ─────────────────────────────────────────────────
export const authAPI = {
  register: (data: { name: string; email: string; password: string; role?: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  mfaSetup: () => api.post('/auth/mfa/setup'),

  mfaVerify: (data: { code: string; mfa_token?: string }) =>
    api.post('/auth/mfa/verify', data),

  me: () => api.get('/auth/me'),
}

// ── Cases API ────────────────────────────────────────────────
export const casesAPI = {
  list: (params?: { page?: number; status?: string; priority?: string; search?: string }) =>
    api.get('/cases', { params }),

  get: (id: number) => api.get(`/cases/${id}`),

  create: (data: { title: string; description?: string; priority?: string; tags?: string[] }) =>
    api.post('/cases', data),

  update: (id: number, data: Record<string, unknown>) =>
    api.put(`/cases/${id}`, data),

  delete: (id: number) => api.delete(`/cases/${id}`),
}

// ── Evidence API ─────────────────────────────────────────────
export const evidenceAPI = {
  list: (params?: { case_id?: number; type?: string; status?: string; page?: number }) =>
    api.get('/evidence', { params }),

  get: (id: string) => api.get(`/evidence/${id}`),

  upload: (caseId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('case_id', caseId.toString())
    return api.post('/evidence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) console.log(`Upload: ${Math.round((e.loaded / e.total) * 100)}%`)
      },
    })
  },

  getAnalysis: (id: string) => api.get(`/evidence/${id}/analysis`),

  reanalyze: (id: string) => api.post(`/evidence/${id}/reanalyze`),
}

// ── Graph API ────────────────────────────────────────────────
export const graphAPI = {
  getCaseGraph: (caseId: number) => api.get(`/graph/case/${caseId}`),
}

export default api
