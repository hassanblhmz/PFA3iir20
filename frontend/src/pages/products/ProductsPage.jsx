/**
 * Page liste des articles
 */
import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { productService } from '../../services/api'
import { PageHeader, StatusBadge, Table, ConfirmDialog } from '../../components/ui/index'
import { Plus, Edit, Trash2, Search, Filter, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ProductsPage() {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterCat, setFilterCat] = useState('')
  const [deleteId, setDeleteId] = useState(null)

  const load = () => {
    setLoading(true)
    const params = {}
    if (search) params.search = search
    if (filterCat) params.category = filterCat
    productService.list(params)
      .then(r => setProducts(r.data.results || r.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    productService.listCategories().then(r => setCategories(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [search, filterCat])

  const handleDelete = async () => {
    try {
      await productService.delete(deleteId)
      toast.success('Article supprimé')
      load()
    } catch {
      toast.error('Impossible de supprimer cet article')
    }
  }

  const columns = [
    { key: 'code', title: 'Référence', render: v => <span className="font-mono text-sm text-gray-600">{v}</span> },
    { key: 'name', title: 'Désignation', render: (v) => <span className="font-medium text-gray-900">{v}</span> },
    { key: 'category_name', title: 'Catégorie' },
    { key: 'unit', title: 'Unité' },
    { key: 'unit_price', title: 'Prix unitaire', render: v => <span className="font-medium">{Number(v).toLocaleString('fr-MA')} MAD</span> },
    { key: 'current_stock', title: 'Stock actuel', render: (v, row) => (
      <div className="flex items-center gap-2">
        <span className={row.is_critical ? 'text-red-600 font-bold' : 'text-gray-700'}>{v}</span>
        {row.is_critical && <AlertTriangle size={14} className="text-red-500" />}
      </div>
    )},
    { key: 'min_stock', title: 'Seuil min' },
    { key: 'stock_status', title: 'Statut', render: v => <StatusBadge status={v} /> },
    { key: 'id', title: 'Actions', render: (id) => (
      <div className="flex items-center gap-2">
        <button onClick={() => navigate(`/products/${id}/edit`)} className="p-1.5 hover:bg-blue-50 rounded-lg text-blue-600">
          <Edit size={15} />
        </button>
        <button onClick={() => setDeleteId(id)} className="p-1.5 hover:bg-red-50 rounded-lg text-red-500">
          <Trash2 size={15} />
        </button>
      </div>
    )},
  ]

  return (
    <div>
      <PageHeader
        title="Articles"
        subtitle="Catalogue des produits et matériaux"
        actions={
          <Link to="/products/new" className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Nouvel article
          </Link>
        }
      />

      <div className="card">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <div className="relative flex-1 min-w-[200px] max-w-xs">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Rechercher..." className="input pl-9"
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <select className="input w-auto" value={filterCat} onChange={e => setFilterCat(e.target.value)}>
            <option value="">Toutes catégories</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <Table columns={columns} data={products} loading={loading} emptyMessage="Aucun article trouvé" />
      </div>

      <ConfirmDialog isOpen={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={handleDelete}
        title="Supprimer l'article" message="Voulez-vous vraiment supprimer cet article ?" danger />
    </div>
  )
}
