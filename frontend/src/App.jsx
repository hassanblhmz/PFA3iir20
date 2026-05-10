/**
 * Application principale - Routing React
 */
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'

// Pages
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import SuppliersPage from './pages/suppliers/SuppliersPage'
import SupplierFormPage from './pages/suppliers/SupplierFormPage'
import ProductsPage from './pages/products/ProductsPage'
import ProductFormPage from './pages/products/ProductFormPage'
import PurchaseRequestsPage from './pages/purchases/PurchaseRequestsPage'
import PurchaseRequestFormPage from './pages/purchases/PurchaseRequestFormPage'
import PurchaseRequestDetailPage from './pages/purchases/PurchaseRequestDetailPage'
import PurchaseOrdersPage from './pages/purchases/PurchaseOrdersPage'
import PurchaseOrderDetailPage from './pages/purchases/PurchaseOrderDetailPage'
import StockPage from './pages/stock/StockPage'
import UsersPage from './pages/users/UsersPage'

// Route protégée
function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen">Chargement...</div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />

      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardPage />} />

        {/* Fournisseurs - Admin, Acheteur */}
        <Route path="suppliers" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <SuppliersPage />
          </ProtectedRoute>
        } />
        <Route path="suppliers/new" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <SupplierFormPage />
          </ProtectedRoute>
        } />
        <Route path="suppliers/:id/edit" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <SupplierFormPage />
          </ProtectedRoute>
        } />

        {/* Articles - Admin, Acheteur */}
        <Route path="products" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <ProductsPage />
          </ProtectedRoute>
        } />
        <Route path="products/new" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <ProductFormPage />
          </ProtectedRoute>
        } />
        <Route path="products/:id/edit" element={
          <ProtectedRoute roles={['admin', 'acheteur']}>
            <ProductFormPage />
          </ProtectedRoute>
        } />

        {/* Demandes d'achat - Tous sauf magasinier */}
        <Route path="purchases/requests" element={
          <ProtectedRoute roles={['admin', 'demandeur', 'validateur', 'acheteur']}>
            <PurchaseRequestsPage />
          </ProtectedRoute>
        } />
        <Route path="purchases/requests/new" element={
          <ProtectedRoute roles={['admin', 'demandeur']}>
            <PurchaseRequestFormPage />
          </ProtectedRoute>
        } />
        <Route path="purchases/requests/:id" element={
          <ProtectedRoute roles={['admin', 'demandeur', 'validateur', 'acheteur']}>
            <PurchaseRequestDetailPage />
          </ProtectedRoute>
        } />

        {/* Commandes - Admin, Acheteur, Validateur */}
        <Route path="purchases/orders" element={
          <ProtectedRoute roles={['admin', 'acheteur', 'validateur']}>
            <PurchaseOrdersPage />
          </ProtectedRoute>
        } />
        <Route path="purchases/orders/:id" element={
          <ProtectedRoute roles={['admin', 'acheteur', 'validateur', 'magasinier']}>
            <PurchaseOrderDetailPage />
          </ProtectedRoute>
        } />

        {/* Stock - Admin, Magasinier */}
        <Route path="stock" element={
          <ProtectedRoute roles={['admin', 'magasinier']}>
            <StockPage />
          </ProtectedRoute>
        } />

        {/* Utilisateurs - Admin seulement */}
        <Route path="users" element={
          <ProtectedRoute roles={['admin']}>
            <UsersPage />
          </ProtectedRoute>
        } />
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="top-right" toastOptions={{
          duration: 4000,
          style: { borderRadius: '10px', background: '#333', color: '#fff' },
        }} />
      </BrowserRouter>
    </AuthProvider>
  )
}
