import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { purchaseOrderService, receptionService } from '../../services/api'
import { StatusBadge, Modal } from '../../components/ui'
import { ArrowLeft, Send, Package } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function PurchaseOrderDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showReceptionModal, setShowReceptionModal] = useState(false)
  const [receptionLines, setReceptionLines] = useState([])
  const [receptionRef, setReceptionRef] = useState('')

  const load = () => { purchaseOrderService.get(id).then(r=>{ setOrder(r.data); setReceptionLines((r.data.order_lines||[]).map(l=>({order_line:l.id, quantity_received:0, max: parseFloat(l.quantity_ordered)-parseFloat(l.quantity_received), product_name: l.product_detail?.name||''}))) }).finally(()=>setLoading(false)) }
  useEffect(()=>{ load() },[id])

  const handleSend = async () => {
    try { await purchaseOrderService.send(id); toast.success('Commande envoyée'); load() }
    catch(e) { toast.error(e.response?.data?.error||'Erreur') }
  }

  const handleReception = async () => {
    const lines = receptionLines.filter(l=>parseFloat(l.quantity_received)>0).map(l=>({order_line:l.order_line, quantity_received:parseFloat(l.quantity_received)}))
    if (!lines.length) { toast.error('Saisissez au moins une quantité'); return }
    try {
      await receptionService.create({ order: parseInt(id), reference: receptionRef, lines })
      toast.success('Réception enregistrée'); setShowReceptionModal(false); load()
    } catch(e) { toast.error('Erreur lors de la réception') }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"/></div>
  if (!order) return null

  const canSend = order.status === 'brouillon' && ['admin','acheteur'].includes(user.role)
  const canReceive = ['envoyee','confirmee','recue_partielle'].includes(order.status) && ['admin','magasinier'].includes(user.role)

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex items-center gap-3">
        <button onClick={()=>navigate('/purchases/orders')} className="p-2 hover:bg-gray-100 rounded-lg"><ArrowLeft size={18}/></button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{order.reference}</h1>
          <div className="flex items-center gap-2 mt-1"><StatusBadge status={order.status}/><span className="text-sm text-gray-500">{order.supplier_name}</span></div>
        </div>
      </div>

      <div className="flex gap-3">
        {canSend && <button onClick={handleSend} className="btn-primary flex items-center gap-2"><Send size={15}/>Envoyer au fournisseur</button>}
        {canReceive && <button onClick={()=>setShowReceptionModal(true)} className="bg-teal-600 hover:bg-teal-700 text-white font-medium py-2 px-4 rounded-lg flex items-center gap-2"><Package size={15}/>Réceptionner</button>}
      </div>

      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-3">Informations</h2>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div><dt className="text-gray-500">Fournisseur</dt><dd className="font-medium">{order.supplier_name}</dd></div>
          <div><dt className="text-gray-500">Créée par</dt><dd className="font-medium">{order.ordered_by_name}</dd></div>
          <div><dt className="text-gray-500">Livraison prévue</dt><dd className="font-medium">{order.expected_date||'—'}</dd></div>
          <div><dt className="text-gray-500">Montant total</dt><dd className="font-bold text-blue-700">{parseFloat(order.total_amount||0).toLocaleString('fr-MA')} MAD</dd></div>
        </dl>
      </div>

      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-3">Lignes de commande</h2>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            <th className="text-left py-2 font-medium text-gray-500">Article</th>
            <th className="text-left py-2 font-medium text-gray-500">Commandé</th>
            <th className="text-left py-2 font-medium text-gray-500">Reçu</th>
            <th className="text-left py-2 font-medium text-gray-500">Prix unit.</th>
            <th className="text-left py-2 font-medium text-gray-500">Total</th>
          </tr></thead>
          <tbody>
            {order.order_lines?.map(l=>(
              <tr key={l.id} className="border-b border-gray-100">
                <td className="py-2">{l.product_detail?.name}</td>
                <td className="py-2">{parseFloat(l.quantity_ordered)} {l.product_detail?.unit}</td>
                <td className="py-2"><span className={l.is_fully_received?'text-green-600 font-medium':'text-orange-600'}>{parseFloat(l.quantity_received)}</span></td>
                <td className="py-2">{parseFloat(l.unit_price).toLocaleString('fr-MA')} MAD</td>
                <td className="py-2 font-medium">{parseFloat(l.total_price||0).toLocaleString('fr-MA')} MAD</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={showReceptionModal} onClose={()=>setShowReceptionModal(false)} title="Enregistrer une réception" size="lg">
        <div className="space-y-4">
          <div><label className="label">Référence BL fournisseur</label><input className="input" value={receptionRef} onChange={e=>setReceptionRef(e.target.value)} placeholder="Ex: BL-2024-001"/></div>
          <table className="w-full text-sm">
            <thead><tr className="border-b border-gray-200"><th className="text-left py-2 font-medium text-gray-500">Article</th><th className="text-left py-2 font-medium text-gray-500">Restant</th><th className="text-left py-2 font-medium text-gray-500">Quantité reçue</th></tr></thead>
            <tbody>
              {receptionLines.map((l,i)=>(
                <tr key={l.order_line} className="border-b border-gray-100">
                  <td className="py-2">{l.product_name}</td>
                  <td className="py-2">{l.max}</td>
                  <td className="py-2"><input type="number" min={0} max={l.max} step="0.01" className="input w-28 text-sm" value={l.quantity_received} onChange={e=>setReceptionLines(lines=>lines.map((x,j)=>j===i?{...x,quantity_received:e.target.value}:x))}/></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex gap-3"><button onClick={handleReception} className="btn-primary">Confirmer réception</button><button onClick={()=>setShowReceptionModal(false)} className="btn-secondary">Annuler</button></div>
        </div>
      </Modal>
    </div>
  )
}
