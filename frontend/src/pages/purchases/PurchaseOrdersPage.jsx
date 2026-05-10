import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { purchaseOrderService } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { PageHeader, Table, StatusBadge } from '../../components/ui'
import { Eye } from 'lucide-react'

export default function PurchaseOrdersPage() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    purchaseOrderService.list({ search, status: statusFilter||undefined })
      .then(r => {
        let data = r.data.results||r.data
        // Magasinier can only see received or partially received orders
        if (user?.role === 'magasinier') {
          data = data.filter(order => ['recue_partielle', 'recue'].includes(order.status))
        }
        setItems(data)
      })
      .finally(() => setLoading(false))
  }, [search, statusFilter, user?.role])

  const columns = [
    { key: 'reference', title: 'Référence' },
    { key: 'supplier_name', title: 'Fournisseur' },
    { key: 'status', title: 'Statut', render: v => <StatusBadge status={v}/> },
    { key: 'lines_count', title: 'Lignes' },
    { key: 'total_amount', title: 'Montant', render: v => `${parseFloat(v||0).toLocaleString('fr-MA')} MAD` },
    { key: 'expected_date', title: 'Livraison prévue', render: v => v ? new Date(v).toLocaleDateString('fr-MA') : '—' },
    { key: 'created_at', title: 'Date création', render: v => new Date(v).toLocaleDateString('fr-MA') },
    { key: 'actions', title: '', render: (_, row) => (
      <button onClick={()=>navigate(`/purchases/orders/${row.id}`)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg"><Eye size={15}/></button>
    )},
  ]

  const pageTitle = user?.role === 'magasinier' ? 'Commandes à recevoir' : 'Bons de commande'

  return (
    <div className="space-y-5">
      <PageHeader title={pageTitle} subtitle={`${items.length} commande(s)`}/>
      <div className="card">
        <div className="flex gap-3 mb-4 flex-wrap">
          <input className="input max-w-xs" placeholder="Rechercher..." value={search} onChange={e=>setSearch(e.target.value)}/>
          <select className="input w-48" value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}>
            <option value="">Tous les statuts</option>
            {user?.role !== 'magasinier' && <option value="brouillon">Brouillon</option>}
            {user?.role !== 'magasinier' && <option value="envoyee">Envoyée</option>}
            {user?.role !== 'magasinier' && <option value="confirmee">Confirmée</option>}
            <option value="recue_partielle">Reçue partiellement</option>
            <option value="recue">Reçue</option>
            {user?.role !== 'magasinier' && <option value="cloturee">Clôturée</option>}
          </select>
        </div>
        <Table columns={columns} data={items} loading={loading} emptyMessage="Aucun bon de commande"/>
      </div>
    </div>
  )
}
