import React, { useEffect, useState } from 'react'
import { stockService, productService } from '../../services/api'
import { PageHeader, Table, StatusBadge, Modal } from '../../components/ui'
import { AlertTriangle, Plus, ShoppingCart } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function StockPage() {
  const [movements, setMovements] = useState([])
  const [criticalProducts, setCriticalProducts] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdjModal, setShowAdjModal] = useState(false)
  const [showSaleModal, setShowSaleModal] = useState(false)
  const [adjForm, setAdjForm] = useState({ product:'', type:'entree', quantity:0, reason:'' })
  const [saleForm, setSaleForm] = useState({ product:'', quantity:1, customer:'', reference:'' })
  const { user } = useAuth()

  const load = () => {
    setLoading(true)
    Promise.all([
      stockService.listMovements(),
      stockService.getCritical(),
      productService.list()
    ]).then(([m,c,p]) => {
      setMovements(m.data.results||m.data)
      setCriticalProducts(c.data.results||[])
      setProducts(p.data.results||p.data)
    }).finally(()=>setLoading(false))
  }
  useEffect(()=>{ load() },[])

  const handleAdjust = async () => {
    if (!adjForm.product || !adjForm.quantity || !adjForm.reason) { toast.error('Remplissez tous les champs'); return }
    try {
      await stockService.adjust({...adjForm, product:parseInt(adjForm.product), quantity:parseFloat(adjForm.quantity)})
      toast.success('Ajustement effectué'); setShowAdjModal(false); setAdjForm({product:'',type:'entree',quantity:0,reason:''}); load()
    } catch(e) { toast.error(e.response?.data?.error||'Erreur') }
  }

  const handleSale = async () => {
    if (!saleForm.product || !saleForm.quantity) { toast.error('SÃ©lectionnez un article et une quantitÃ©'); return }
    try {
      await stockService.adjust({
        product: parseInt(saleForm.product),
        type: 'sortie',
        quantity: parseFloat(saleForm.quantity),
        reason: saleForm.customer ? `Vente client - ${saleForm.customer}` : 'Vente client',
        reference: saleForm.reference,
      })
      toast.success('Vente enregistrÃ©e')
      setShowSaleModal(false)
      setSaleForm({ product:'', quantity:1, customer:'', reference:'' })
      load()
    } catch(e) {
      toast.error(e.response?.data?.error || e.response?.data?.quantity?.[0] || 'Stock insuffisant ou donnÃ©es invalides')
    }
  }

  const movColumns = [
    { key: 'created_at', title: 'Date', render: v => new Date(v).toLocaleString('fr-MA') },
    { key: 'product_detail', title: 'Article', render: v => v?.name||'—' },
    { key: 'type_display', title: 'Type' },
    { key: 'quantity', title: 'Quantité', render: v => parseFloat(v) },
    { key: 'stock_before', title: 'Avant', render: v => parseFloat(v) },
    { key: 'stock_after', title: 'Après', render: v => parseFloat(v) },
    { key: 'reason', title: 'Motif' },
    { key: 'performed_by_name', title: 'Par' },
  ]

  const critColumns = [
    { key: 'code', title: 'Référence' },
    { key: 'name', title: 'Désignation' },
    { key: 'current_stock', title: 'Stock actuel', render: (v,r) => <span className={parseFloat(v)<=0?'text-red-600 font-bold':'text-orange-600 font-semibold'}>{parseFloat(v)} {r.unit}</span> },
    { key: 'min_stock', title: 'Seuil min', render: v => parseFloat(v) },
    { key: 'stock_status', title: 'État', render: v => <StatusBadge status={v}/> },
  ]

  return (
    <div className="space-y-5">
      <PageHeader title="Gestion du Stock"
        actions={['admin','magasinier'].includes(user.role) && (
          <div className="flex flex-wrap gap-2">
            <button onClick={()=>setShowSaleModal(true)} className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center gap-2">
              <ShoppingCart size={16}/>Nouvelle vente
            </button>
            <button onClick={()=>setShowAdjModal(true)} className="btn-primary flex items-center gap-2"><Plus size={16}/>Ajustement de stock</button>
          </div>
        )}
      />

      {criticalProducts.length > 0 && (
        <div className="card border-orange-200 bg-orange-50">
          <div className="flex items-center gap-2 mb-3 text-orange-700">
            <AlertTriangle size={18}/><h2 className="font-semibold">Articles en stock critique ({criticalProducts.length})</h2>
          </div>
          <Table columns={critColumns} data={criticalProducts} loading={false} emptyMessage=""/>
        </div>
      )}

      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-4">Mouvements de stock</h2>
        <Table columns={movColumns} data={movements} loading={loading} emptyMessage="Aucun mouvement"/>
      </div>

      <Modal isOpen={showAdjModal} onClose={()=>setShowAdjModal(false)} title="Ajustement de stock" size="sm">
        <div className="space-y-4">
          <div>
            <label className="label">Article *</label>
            <select className="input" value={adjForm.product} onChange={e=>setAdjForm(f=>({...f,product:e.target.value}))}>
              <option value="">-- Sélectionner --</option>
              {products.map(p=><option key={p.id} value={p.id}>{p.code} — {p.name} (stock: {parseFloat(p.current_stock)})</option>)}
            </select>
          </div>
          <div>
            <label className="label">Type de mouvement *</label>
            <select className="input" value={adjForm.type} onChange={e=>setAdjForm(f=>({...f,type:e.target.value}))}>
              <option value="entree">Entrée</option>
              <option value="sortie">Sortie</option>
              <option value="ajustement">Ajustement (valeur absolue)</option>
            </select>
          </div>
          <div><label className="label">Quantité *</label><input type="number" step="0.01" className="input" value={adjForm.quantity} onChange={e=>setAdjForm(f=>({...f,quantity:e.target.value}))}/></div>
          <div><label className="label">Motif *</label><input className="input" value={adjForm.reason} onChange={e=>setAdjForm(f=>({...f,reason:e.target.value}))} placeholder="Inventaire, correction, retour..."/></div>
          <div className="flex gap-3"><button onClick={handleAdjust} className="btn-primary">Confirmer</button><button onClick={()=>setShowAdjModal(false)} className="btn-secondary">Annuler</button></div>
        </div>
      </Modal>

      <Modal isOpen={showSaleModal} onClose={()=>setShowSaleModal(false)} title="Nouvelle vente" size="sm">
        <div className="space-y-4">
          <div>
            <label className="label">Article vendu *</label>
            <select className="input" value={saleForm.product} onChange={e=>setSaleForm(f=>({...f,product:e.target.value}))}>
              <option value="">-- SÃ©lectionner --</option>
              {products.map(p=><option key={p.id} value={p.id}>{p.code} â€” {p.name} (stock: {parseFloat(p.current_stock)})</option>)}
            </select>
          </div>
          <div><label className="label">QuantitÃ© vendue *</label><input type="number" min="0.01" step="0.01" className="input" value={saleForm.quantity} onChange={e=>setSaleForm(f=>({...f,quantity:e.target.value}))}/></div>
          <div><label className="label">Client</label><input className="input" value={saleForm.customer} onChange={e=>setSaleForm(f=>({...f,customer:e.target.value}))} placeholder="Nom du client"/></div>
          <div><label className="label">RÃ©fÃ©rence</label><input className="input" value={saleForm.reference} onChange={e=>setSaleForm(f=>({...f,reference:e.target.value}))} placeholder="Ex: VTE-001"/></div>
          <div className="flex gap-3"><button onClick={handleSale} className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg">Enregistrer la vente</button><button onClick={()=>setShowSaleModal(false)} className="btn-secondary">Annuler</button></div>
        </div>
      </Modal>
    </div>
  )
}
