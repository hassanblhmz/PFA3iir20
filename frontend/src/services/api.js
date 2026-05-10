/**
 * Configuration Axios - Service HTTP centralisé
 * Gestion automatique des tokens JWT et refresh
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Intercepteur REQUEST — ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercepteur RESPONSE — gérer le refresh automatique
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post(`${API_URL}/auth/refresh/`, { refresh })
        localStorage.setItem('access_token', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        // Refresh échoué → déconnexion
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ---- Services métier ----

export const authService = {
  login: (credentials) => api.post('/auth/login/', credentials),
  getMe: () => api.get('/users/me/'),
  changePassword: (data) => api.put('/users/change_password/', data),
}

export const userService = {
  list: (params) => api.get('/users/', { params }),
  get: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/register/', data),
  update: (id, data) => api.patch(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
}

export const supplierService = {
  list: (params) => api.get('/suppliers/', { params }),
  get: (id) => api.get(`/suppliers/${id}/`),
  create: (data) => api.post('/suppliers/', data),
  update: (id, data) => api.patch(`/suppliers/${id}/`, data),
  delete: (id) => api.delete(`/suppliers/${id}/`),
  getOrders: (id) => api.get(`/suppliers/${id}/orders/`),
}

export const productService = {
  list: (params) => api.get('/products/', { params }),
  get: (id) => api.get(`/products/${id}/`),
  create: (data) => api.post('/products/', data),
  update: (id, data) => api.patch(`/products/${id}/`, data),
  delete: (id) => api.delete(`/products/${id}/`),
  getCritical: () => api.get('/products/critical/'),
  listCategories: () => api.get('/products/categories/'),
  createCategory: (data) => api.post('/products/categories/', data),
}

export const purchaseRequestService = {
  list: (params) => api.get('/purchases/requests/', { params }),
  get: (id) => api.get(`/purchases/requests/${id}/`),
  create: (data) => api.post('/purchases/requests/', data),
  update: (id, data) => api.patch(`/purchases/requests/${id}/`, data),
  delete: (id) => api.delete(`/purchases/requests/${id}/`),
  submit: (id) => api.post(`/purchases/requests/${id}/submit/`),
  validate: (id, data) => api.post(`/purchases/requests/${id}/validate/`, data),
  reject: (id, data) => api.post(`/purchases/requests/${id}/reject/`, data),
  createOrder: (id, data) => api.post(`/purchases/requests/${id}/create_order/`, data),
}

export const purchaseOrderService = {
  list: (params) => api.get('/purchases/orders/', { params }),
  get: (id) => api.get(`/purchases/orders/${id}/`),
  create: (data) => api.post('/purchases/orders/', data),
  update: (id, data) => api.patch(`/purchases/orders/${id}/`, data),
  send: (id) => api.post(`/purchases/orders/${id}/send/`),
}

export const receptionService = {
  list: (params) => api.get('/purchases/receptions/', { params }),
  get: (id) => api.get(`/purchases/receptions/${id}/`),
  create: (data) => api.post('/purchases/receptions/', data),
}

export const stockService = {
  listMovements: (params) => api.get('/stock/movements/', { params }),
  adjust: (data) => api.post('/stock/movements/adjust/', data),
  getCritical: () => api.get('/stock/movements/critical_products/'),
}

export const dashboardService = {
  getStats: () => api.get('/purchases/dashboard/'),
}
