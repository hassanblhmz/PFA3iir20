/**
 * Page de connexion
 */
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { ShoppingCart, Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [showPwd, setShowPwd] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form)
      toast.success('Connexion réussie !')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Identifiants incorrects')
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = (email) => {
    setForm({ email, password: email === 'admin@pfa.ma' ? 'admin123' : 'test123' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 backdrop-blur rounded-2xl mb-4">
            <ShoppingCart size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">GestAchats</h1>
          <p className="text-blue-200 mt-1">Gestion des Achats & Approvisionnements</p>
          <p className="text-blue-300 text-sm mt-1">Projet de Fin d'Année — EMSI 2024</p>
        </div>

        {/* Formulaire */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Connexion</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email" className="input" placeholder="votre@email.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Mot de passe</label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'}
                  className="input pr-10" placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3">
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          {/* Comptes de démonstration */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-xs text-gray-500 text-center mb-3 font-medium uppercase tracking-wide">
              Comptes de démonstration
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { email: 'admin@pfa.ma', label: 'Admin', color: 'bg-purple-50 text-purple-700 border-purple-200' },
                { email: 'demandeur@pfa.ma', label: 'Demandeur', color: 'bg-blue-50 text-blue-700 border-blue-200' },
                { email: 'validateur@pfa.ma', label: 'Validateur', color: 'bg-green-50 text-green-700 border-green-200' },
                { email: 'acheteur@pfa.ma', label: 'Acheteur', color: 'bg-orange-50 text-orange-700 border-orange-200' },
              ].map(acc => (
                <button key={acc.email} onClick={() => quickLogin(acc.email)}
                  className={`text-xs py-1.5 px-3 rounded-lg border font-medium transition-colors hover:opacity-80 ${acc.color}`}>
                  {acc.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
