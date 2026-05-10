/**
 * Composants UI réutilisables
 */
import React from 'react'
import { X, AlertTriangle, CheckCircle, XCircle, Clock, Package } from 'lucide-react'

// ---- Badge de statut ----
const STATUS_CONFIG = {
  // Demandes
  brouillon:     { label: 'Brouillon',    color: 'bg-gray-100 text-gray-600' },
  soumis:        { label: 'Soumis',       color: 'bg-blue-100 text-blue-700' },
  en_validation: { label: 'En validation',color: 'bg-yellow-100 text-yellow-700' },
  valide:        { label: 'Validé',       color: 'bg-green-100 text-green-700' },
  rejete:        { label: 'Rejeté',       color: 'bg-red-100 text-red-700' },
  commande:      { label: 'Commandé',     color: 'bg-purple-100 text-purple-700' },
  // Commandes
  envoyee:          { label: 'Envoyée',         color: 'bg-blue-100 text-blue-700' },
  confirmee:        { label: 'Confirmée',       color: 'bg-indigo-100 text-indigo-700' },
  recue_partielle:  { label: 'Partielle',       color: 'bg-orange-100 text-orange-700' },
  recue:            { label: 'Reçue',           color: 'bg-green-100 text-green-700' },
  cloturee:         { label: 'Clôturée',        color: 'bg-gray-100 text-gray-600' },
  annulee:          { label: 'Annulée',         color: 'bg-red-100 text-red-700' },
  // Stock
  normal:   { label: 'Normal',   color: 'bg-green-100 text-green-700' },
  faible:   { label: 'Faible',   color: 'bg-yellow-100 text-yellow-700' },
  critique: { label: 'Critique', color: 'bg-orange-100 text-orange-700' },
  rupture:  { label: 'Rupture',  color: 'bg-red-100 text-red-700' },
  // Fournisseurs
  actif:    { label: 'Actif',    color: 'bg-green-100 text-green-700' },
  inactif:  { label: 'Inactif',  color: 'bg-gray-100 text-gray-600' },
  suspendu: { label: 'Suspendu', color: 'bg-red-100 text-red-700' },
}

export function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, color: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`badge ${config.color}`}>{config.label}</span>
  )
}

// ---- Priorité badge ----
const PRIORITY_CONFIG = {
  normale:  { label: 'Normale',  color: 'bg-gray-100 text-gray-600' },
  urgente:  { label: 'Urgente',  color: 'bg-orange-100 text-orange-700' },
  critique: { label: 'Critique', color: 'bg-red-100 text-red-700' },
}

export function PriorityBadge({ priority }) {
  const config = PRIORITY_CONFIG[priority] || { label: priority, color: 'bg-gray-100 text-gray-600' }
  return <span className={`badge ${config.color}`}>{config.label}</span>
}

// ---- Modal ----
export function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  if (!isOpen) return null
  const sizes = { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' }
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gray-900/50" onClick={onClose} />
      <div className={`relative bg-white rounded-xl shadow-xl w-full ${sizes[size]} max-h-[90vh] flex flex-col`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={18} />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 px-6 py-4">{children}</div>
      </div>
    </div>
  )
}

// ---- Table ----
export function Table({ columns, data, loading, emptyMessage = 'Aucune donnée' }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map((col) => (
              <th key={col.key} className="text-left py-3 px-4 font-medium text-gray-500 text-xs uppercase tracking-wide">
                {col.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="text-center py-16 text-gray-400">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={row.id || i} className="table-row">
                {columns.map((col) => (
                  <td key={col.key} className="py-3 px-4 text-gray-700">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

// ---- Stat Card ----
export function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colors = {
    blue:   { bg: 'bg-blue-50',   icon: 'bg-blue-500',   text: 'text-blue-600' },
    green:  { bg: 'bg-green-50',  icon: 'bg-green-500',  text: 'text-green-600' },
    orange: { bg: 'bg-orange-50', icon: 'bg-orange-500', text: 'text-orange-600' },
    red:    { bg: 'bg-red-50',    icon: 'bg-red-500',    text: 'text-red-600' },
    purple: { bg: 'bg-purple-50', icon: 'bg-purple-500', text: 'text-purple-600' },
  }
  const c = colors[color]
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 ${c.icon} rounded-xl flex items-center justify-center`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  )
}

// ---- Page Header ----
export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  )
}

// ---- Empty State ----
export function EmptyState({ icon: Icon = Package, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <Icon size={28} className="text-gray-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      {description && <p className="text-gray-500 mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

// ---- Loading Spinner ----
export function Spinner({ size = 'md' }) {
  const sizes = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' }
  return (
    <div className="flex justify-center py-8">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizes[size]}`} />
    </div>
  )
}

// ---- Confirm Dialog ----
export function ConfirmDialog({ isOpen, onClose, onConfirm, title, message, danger }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-gray-600 mb-6">{message}</p>
      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="btn-secondary">Annuler</button>
        <button
          onClick={() => { onConfirm(); onClose() }}
          className={danger ? 'btn-danger' : 'btn-primary'}
        >
          Confirmer
        </button>
      </div>
    </Modal>
  )
}
