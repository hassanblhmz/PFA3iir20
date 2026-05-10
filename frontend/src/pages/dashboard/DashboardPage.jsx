/**
 * Dashboard — Statistiques et vue d'ensemble avec contenu spécifique aux rôles
 */
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardService } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { StatCard, StatusBadge, PriorityBadge, Spinner } from '../../components/ui'
import { ClipboardList, ShoppingCart, AlertTriangle, DollarSign, CheckCircle, Clock, Truck } from 'lucide-react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Doughnut, Bar } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardService.getStats()
      .then(r => setStats(r.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner size="lg" />

  const requestsChartData = {
    labels: ['En attente', 'Validées', 'Rejetées'],
    datasets: [{ data: [stats?.requests?.pending||0, stats?.requests?.validated||0, stats?.requests?.rejected||0], backgroundColor: ['#3b82f6','#22c55e','#ef4444'], borderWidth: 0 }],
  }
  const ordersChartData = {
    labels: ['Jan','Fév','Mar','Avr','Mai','Juin'],
    datasets: [{ label: 'Commandes', data: [3,7,5,9,4,8], backgroundColor: '#3b82f6', borderRadius: 6 }],
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="text-gray-500 text-sm mt-1">
          {user?.role === 'demandeur' && 'Gestion de vos demandes d\'achat'}
          {user?.role === 'validateur' && 'Validation des demandes d\'achat'}
          {user?.role === 'acheteur' && 'Gestion des commandes'}
          {user?.role === 'magasinier' && 'Gestion du stock et des réceptions'}
          {user?.role === 'admin' && 'Vue d\'ensemble de votre activité'}
        </p>
      </div>

      {/* DEMANDEUR Dashboard */}
      {user?.role === 'demandeur' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard title="Mes demandes" value={stats?.requests?.total||0} subtitle={`${stats?.requests?.pending||0} en attente`} icon={ClipboardList} color="blue" />
            <StatCard title="Validées" value={stats?.requests?.validated||0} subtitle="Prêtes à commander" icon={CheckCircle} color="green" />
            <StatCard title="Rejetées" value={stats?.requests?.rejected||0} subtitle="À revérifier" icon={AlertTriangle} color="red" />
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-gray-900">Vos demandes d'achat</h2>
              <Link to="/purchases/requests/new" className="text-sm text-blue-600 hover:underline">Nouvelle demande</Link>
            </div>
            {!stats?.recent_requests?.length ? (
              <p className="text-gray-400 text-sm text-center py-8">Aucune demande</p>
            ) : (
              <div className="space-y-2">
                {stats.recent_requests.map(req => (
                  <Link key={req.id} to={`/purchases/requests/${req.id}`} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition">
                    <div>
                      <p className="font-medium text-gray-900">{req.reference}</p>
                      <p className="text-sm text-gray-500">{req.title}</p>
                    </div>
                    <div className="flex gap-2"><PriorityBadge priority={req.priority} /><StatusBadge status={req.status} /></div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* VALIDATEUR Dashboard */}
      {user?.role === 'validateur' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard title="En attente" value={stats?.requests?.pending||0} subtitle="À valider" icon={Clock} color="orange" />
            <StatCard title="Validées" value={stats?.requests?.validated||0} subtitle="Ce mois" icon={CheckCircle} color="green" />
            <StatCard title="Rejetées" value={stats?.requests?.rejected||0} subtitle="Ce mois" icon={AlertTriangle} color="red" />
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-gray-900">Demandes en attente de validation</h2>
              <Link to="/purchases/requests" className="text-sm text-blue-600 hover:underline">Voir tout</Link>
            </div>
            {!stats?.recent_requests?.length ? (
              <p className="text-gray-400 text-sm text-center py-8">Aucune demande en attente</p>
            ) : (
              <div className="space-y-2">
                {stats.recent_requests.filter(r => r.status === 'soumis').map(req => (
                  <Link key={req.id} to={`/purchases/requests/${req.id}`} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition border-l-4 border-orange-400">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{req.reference} — {req.title}</p>
                      <p className="text-sm text-gray-500">De {req.requested_by_name}</p>
                    </div>
                    <PriorityBadge priority={req.priority} />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* ACHETEUR Dashboard */}
      {user?.role === 'acheteur' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Commandes" value={stats?.orders?.total||0} subtitle={`${stats?.orders?.pending||0} en cours`} icon={Truck} color="blue" />
            <StatCard title="Validées" value={stats?.requests?.validated||0} subtitle="À commander" icon={CheckCircle} color="green" />
            <StatCard title="Dépenses" value={`${(stats?.finance?.total_spent||0).toLocaleString('fr-MA')} MAD`} subtitle="Commandes reçues" icon={DollarSign} color="purple" />
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-gray-900">Demandes validées à commander</h2>
              <Link to="/purchases/requests" className="text-sm text-blue-600 hover:underline">Voir tout</Link>
            </div>
            {!stats?.recent_requests?.length ? (
              <p className="text-gray-400 text-sm text-center py-8">Aucune demande validée</p>
            ) : (
              <div className="space-y-2">
                {stats.recent_requests.filter(r => r.status === 'valide').map(req => (
                  <Link key={req.id} to={`/purchases/requests/${req.id}`} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{req.reference} — {req.title}</p>
                      <p className="text-sm text-gray-500">Montant: {parseFloat(req.total_amount||0).toLocaleString('fr-MA')} MAD</p>
                    </div>
                    <StatusBadge status={req.status} />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* MAGASINIER Dashboard */}
      {user?.role === 'magasinier' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard title="Stock critique" value={stats?.stock?.critical_count||0} subtitle="À réapprovisionner" icon={AlertTriangle} color="red" />
            <StatCard title="Commandes reçues" value={stats?.orders?.completed||0} subtitle="Ce mois" icon={Truck} color="blue" />
          </div>
          <div className="card">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Articles en stock faible</h2>
            <Link to="/stock" className="btn-primary">Gérer le stock</Link>
          </div>
        </>
      )}

      {/* ADMIN Dashboard */}
      {user?.role === 'admin' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Total demandes" value={stats?.requests?.total||0} subtitle={`${stats?.requests?.pending||0} en attente`} icon={ClipboardList} color="blue" />
            <StatCard title="Commandes actives" value={stats?.orders?.total||0} subtitle={`${stats?.orders?.pending||0} en cours`} icon={ShoppingCart} color="purple" />
            <StatCard title="Stock critique" value={stats?.stock?.critical_count||0} subtitle="Articles à réapprovisionner" icon={AlertTriangle} color="orange" />
            <StatCard title="Dépenses totales" value={`${(stats?.finance?.total_spent||0).toLocaleString('fr-MA')} MAD`} subtitle="Commandes reçues" icon={DollarSign} color="green" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h2 className="text-base font-semibold text-gray-900 mb-4">Statut des demandes</h2>
              <div className="h-56 flex items-center justify-center">
                <Doughnut data={requestsChartData} options={{ plugins: { legend: { position: 'bottom' } }, maintainAspectRatio: false }} />
              </div>
            </div>
            <div className="card">
              <h2 className="text-base font-semibold text-gray-900 mb-4">Commandes par mois</h2>
              <div className="h-56">
                <Bar data={ordersChartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-gray-900">Demandes récentes</h2>
              <Link to="/purchases/requests" className="text-sm text-blue-600 hover:underline">Voir tout</Link>
            </div>
            {!stats?.recent_requests?.length ? (
              <p className="text-gray-400 text-sm text-center py-8">Aucune demande</p>
            ) : (
              <div className="divide-y divide-gray-100">
                {(stats.recent_requests).map(req => (
                  <div key={req.id} className="flex items-center gap-4 py-3">
                    <div className="flex-1 min-w-0">
                      <Link to={`/purchases/requests/${req.id}`} className="text-sm font-medium text-gray-900 hover:text-blue-600 truncate block">
                        {req.reference} — {req.title}
                      </Link>
                      <p className="text-xs text-gray-500">{req.requested_by_name} · {req.department}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <PriorityBadge priority={req.priority} />
                      <StatusBadge status={req.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
