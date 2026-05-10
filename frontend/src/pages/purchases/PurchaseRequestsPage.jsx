import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { purchaseRequestService } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { PageHeader, Table, StatusBadge, PriorityBadge, ConfirmDialog } from '../../components/ui'
import { Plus, Eye, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PurchaseRequestsPage() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [deleteId, setDeleteId] = useState(null)
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    purchaseRequestService.list({ search, status: statusFilter||undefined })
      .then(r => {
        let data = r.data.results||r.data
        // Filter by role
        if (user?.role === 'demandeur') {
          data = data.filter(req => req.requested_by === user.id)
        } else if (user?.role === 'validateur') {
          data = data.filter(req => req.status === 'soumis')
        } else if (user?.role === 'acheteur') {
          data = data.filter(req => req.status === 'valide')
        }
        setItems(data)
      })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [search, statusFilter, user?.id])

  const handleDelete = async () => {
    try { await purchaseRequestService.delete(deleteId); toast.success('Demande supprimée'); load() }
    catch { toast.error('Impossible de supprimer') }
  }

  const columns = [
    { key: 'reference', title: 'Référence' },
    { key: 'title', title: 'Objet' },
    ...(user?.role !== 'demandeur' ? [{ key: 'requested_by_name', title: 'Demandeur' }] : []),
    { key: 'department', title: 'Département' },
    { key: 'priority', title: 'Priorité', render: v => <PriorityBadge priority={v}/> },
    { key: 'status', title: 'Statut', render: v => <StatusBadge status={v}/> },
    { key: 'total_amount', title: 'Montant', render: v => `${parseFloat(v||0).toLocaleString('fr-MA')} MAD` },
    { key: 'created_at', title: 'Date', render: v => new Date(v).toLocaleDateString('fr-MA') },
    { key: 'actions', title: '', render: (_, row) => (
      <div className="flex gap-2 justify-end">
        <button onClick={()=>navigate(`/purchases/requests/${row.id}`)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg"><Eye size={15}/></button>
        {row.status === 'brouillon' && user?.role === 'demandeur' && <button onClick={()=>setDeleteId(row.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><Trash2 size={15}/></button>}
      </div>
    )},
  ]

  const pageTitle = user?.role === 'demandeur' ? 'Mes demandes d\'achat' : 
                    user?.role === 'validateur' ? 'Demandes à valider' :
                    user?.role === 'acheteur' ? 'Demandes validées' :
                    'Demandes d\'achat'

  return (
    <div className="space-y-5">
      <PageHeader title={pageTitle} subtitle={`${items.length} demande(s)`}
        actions={user?.role === 'demandeur' && <Link to="/purchases/requests/new" className="btn-primary flex items-center gap-2"><Plus size={16}/>Nouvelle demande</Link>}/>
      <div className="card">
        <div className="flex gap-3 mb-4 flex-wrap">
          <input className="input max-w-xs" placeholder="Rechercher..." value={search} onChange={e=>setSearch(e.target.value)}/>
          <select className="input w-44" value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}>
            <option value="">Tous les statuts</option>
            {user?.role === 'demandeur' && <option value="brouillon">Brouillon</option>}
            {user?.role !== 'demandeur' && <option value="soumis">Soumis</option>}
            {user?.role !== 'acheteur' && <option value="valide">Validé</option>}
            {user?.role !== 'validateur' && <option value="rejete">Rejeté</option>}
            {user?.role !== 'demandeur' && <option value="commande">Commandé</option>}
          </select>
        </div>
        <Table columns={columns} data={items} loading={loading} emptyMessage="Aucune demande d'achat"/>
      </div>
      <ConfirmDialog isOpen={!!deleteId} onClose={()=>setDeleteId(null)} onConfirm={handleDelete} title="Supprimer la demande" message="Confirmer la suppression de cette demande ?" danger/>
    </div>
  )
}
