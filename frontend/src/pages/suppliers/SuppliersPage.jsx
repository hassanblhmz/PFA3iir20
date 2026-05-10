import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supplierService } from '../../services/api'
import { PageHeader, Table, StatusBadge, ConfirmDialog } from '../../components/ui'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState(null)
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    supplierService.list({ search }).then(r => setSuppliers(r.data.results || r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [search])

  const handleDelete = async () => {
    try { await supplierService.delete(deleteId); toast.success('Supprimé'); load() }
    catch { toast.error('Erreur suppression') }
  }

  const columns = [
    { key: 'code', title: 'Code' },
    { key: 'name', title: 'Raison sociale' },
    { key: 'contact_name', title: 'Contact' },
    { key: 'email', title: 'Email' },
    { key: 'city', title: 'Ville' },
    { key: 'payment_terms', title: 'Délai', render: v => `${v}j` },
    { key: 'status', title: 'Statut', render: v => <StatusBadge status={v} /> },
    { key: 'actions', title: '', render: (_, row) => (
      <div className="flex gap-2 justify-end">
        <button onClick={() => navigate(`/suppliers/${row.id}/edit`)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg"><Pencil size={15}/></button>
        <button onClick={() => setDeleteId(row.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><Trash2 size={15}/></button>
      </div>
    )},
  ]

  return (
    <div className="space-y-5">
      <PageHeader title="Fournisseurs" subtitle={`${suppliers.length} fournisseur(s)`}
        actions={<Link to="/suppliers/new" className="btn-primary flex items-center gap-2"><Plus size={16}/>Nouveau</Link>} />
      <div className="card">
        <div className="mb-4"><input className="input max-w-xs" placeholder="Rechercher..." value={search} onChange={e => setSearch(e.target.value)}/></div>
        <Table columns={columns} data={suppliers} loading={loading} emptyMessage="Aucun fournisseur"/>
      </div>
      <ConfirmDialog isOpen={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={handleDelete} title="Supprimer le fournisseur" message="Cette action est irréversible." danger/>
    </div>
  )
}
