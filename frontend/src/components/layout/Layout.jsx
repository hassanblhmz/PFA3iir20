/**
 * Layout principal — Sidebar + Navbar + Contenu
 */
import React, { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  LayoutDashboard, Users, Package, ShoppingCart, ClipboardList,
  Truck, Warehouse, ChevronDown, ChevronRight, LogOut, Menu, X,
  Bell, User, Building2, AlertTriangle
} from 'lucide-react'

const NAV_ITEMS = [
  { path: '/', icon: LayoutDashboard, label: 'Tableau de bord', exact: true },
  { path: '/suppliers', icon: Building2, label: 'Fournisseurs', roles: ['admin', 'acheteur'] },
  { path: '/products', icon: Package, label: 'Articles', roles: ['admin', 'acheteur'] },
  {
    label: 'Achats',
    icon: ShoppingCart,
    roles: ['admin', 'demandeur', 'validateur', 'acheteur'],
    children: [
      { path: '/purchases/requests', label: 'Demandes d\'achat', icon: ClipboardList, roles: ['admin', 'demandeur', 'validateur', 'acheteur'] },
      { path: '/purchases/orders', label: 'Commandes', icon: Truck, roles: ['admin', 'acheteur', 'validateur'] },
    ]
  },
  { path: '/stock', icon: Warehouse, label: 'Stock', roles: ['admin', 'magasinier'] },
  { path: '/users', icon: Users, label: 'Utilisateurs', roles: ['admin'] },
]

const ROLE_LABELS = {
  admin: 'Administrateur',
  demandeur: 'Demandeur',
  validateur: 'Validateur',
  acheteur: 'Acheteur',
  magasinier: 'Magasinier',
}

const ROLE_COLORS = {
  admin: 'bg-purple-100 text-purple-700',
  demandeur: 'bg-blue-100 text-blue-700',
  validateur: 'bg-green-100 text-green-700',
  acheteur: 'bg-orange-100 text-orange-700',
  magasinier: 'bg-teal-100 text-teal-700',
}

function NavItem({ item, onClose }) {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)

  if (item.roles && !item.roles.includes(user?.role)) return null

  if (item.children) {
    return (
      <div>
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <item.icon size={18} />
          <span className="flex-1 text-left">{item.label}</span>
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        {open && (
          <div className="ml-4 mt-1 space-y-1">
            {item.children.map(child => (
              <NavItem key={child.path} item={child} onClose={onClose} />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <NavLink
      to={item.path}
      end={item.exact}
      onClick={onClose}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-2.5 text-sm rounded-lg transition-colors ${
          isActive
            ? 'bg-blue-50 text-blue-700 font-medium'
            : 'text-gray-600 hover:bg-gray-100'
        }`
      }
    >
      <item.icon size={18} />
      {item.label}
    </NavLink>
  )
}

function Sidebar({ onClose }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <ShoppingCart size={16} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-gray-900 text-sm">GestAchats</div>
            <div className="text-xs text-gray-500">PFA 2026</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.path || item.label} item={item} onClose={onClose} />
        ))}
      </nav>

      {/* User profile */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <User size={16} className="text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-gray-900 truncate">
              {user?.full_name || user?.email}
            </div>
            <span className={`badge text-xs ${ROLE_COLORS[user?.role]}`}>
              {ROLE_LABELS[user?.role]}
            </span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut size={16} />
          Déconnexion
        </button>
      </div>
    </div>
  )
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar Desktop */}
      <div className="hidden lg:flex lg:w-64 lg:flex-shrink-0">
        <Sidebar />
      </div>

      {/* Sidebar Mobile Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-gray-900/50" onClick={() => setSidebarOpen(false)} />
          <div className="relative w-64 h-full">
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Navbar */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <Menu size={20} />
          </button>
          <div className="flex-1" />
          <button className="relative p-2 rounded-lg hover:bg-gray-100">
            <Bell size={20} className="text-gray-600" />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
