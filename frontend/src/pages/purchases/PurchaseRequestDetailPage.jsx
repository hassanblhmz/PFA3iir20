import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { purchaseRequestService, supplierService } from '../../services/api'
import { StatusBadge, PriorityBadge, Modal } from '../../components/ui'
import { ArrowLeft, CheckCircle, XCircle, Send, ShoppingCart, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function PurchaseRequestDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [pr, setPr] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [comment, setComment] = useState('')
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showOrderModal, setShowOrderModal] = useState(false)
  const [suppliers, setSuppliers] = useState([])
  const [selectedSupplier, setSelectedSupplier] = useState('')
  const [expectedDate, setExpectedDate] = useState('')

  const load = () => { purchaseRequestService.get(id).then(r=>setPr(r.data)).finally(()=>setLoading(false)) }
  useEffect(() => { load(); supplierService.list().then(r=>setSuppliers(r.data.results||r.data)) }, [id])

  const action = async (fn, successMsg) => {
    setActionLoading(true)
    try { await fn(); toast.success(successMsg); load() }
    catch(e) { toast.error(e.response?.data?.error||'Erreur') }
    finally { setActionLoading(false) }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"/></div>
  if (!pr) return null

  const canValidate = ['admin','validateur'].includes(user.role) && ['soumis','en_validation'].includes(pr.status)
  const canSubmit = pr.status === 'brouillon' && (pr.requested_by === user.id || user.role === 'admin')
  const canCreateOrder = ['admin','acheteur'].includes(user.role) && pr.status === 'valide' && !pr.order

  return (
    <div className="space-y-5 max-w-4xl">
      <div className="flex items-center gap-3">
        <button onClick={()=>navigate('/purchases/requests')} className="p-2 hover:bg-gray-100 rounded-lg"><ArrowLeft size={18}/></button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{pr.reference} — {pr.title}</h1>
          <div className="flex items-center gap-2 mt-1"><StatusBadge status={pr.status}/><PriorityBadge priority={pr.priority}/></div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        {canSubmit && <button onClick={()=>action(()=>purchaseRequestService.submit(id),'Demande soumise')} disabled={actionLoading} className="btn-primary flex items-center gap-2"><Send size={15}/>Soumettre</button>}
        {canValidate && <button onClick={()=>action(()=>purchaseRequestService.validate(id,{comment}),'Demande validée')} disabled={actionLoading} className="bg-green-600 hover:bg-green-700 text-white btn-primary flex items-center gap-2"><CheckCircle size={15}/>Valider</button>}
        {canValidate && <button onClick={()=>setShowRejectModal(true)} disabled={actionLoading} className="btn-danger flex items-center gap-2"><XCircle size={15}/>Rejeter</button>}
        {canCreateOrder && <button onClick={()=>setShowOrderModal(true)} className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg flex items-center gap-2"><ShoppingCart size={15}/>Créer commande</button>}
      </div>

      {/* Infos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <div className="card">
            <h2 className="font-semibold text-gray-900 mb-3">Détails</h2>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-gray-500">Demandeur</dt><dd className="font-medium">{pr.requested_by_name}</dd></div>
              <div><dt className="text-gray-500">Département</dt><dd className="font-medium">{pr.department||'—'}</dd></div>
              <div><dt className="text-gray-500">Date souhaitée</dt><dd className="font-medium">{pr.needed_date||'—'}</dd></div>
              <div><dt className="text-gray-500">Créée le</dt><dd className="font-medium">{new Date(pr.created_at).toLocaleDateString('fr-MA')}</dd></div>
              {pr.notes && <div className="col-span-2"><dt className="text-gray-500">Remarques</dt><dd>{pr.notes}</dd></div>}
            </dl>
          </div>

          <div className="card">
            <h2 className="font-semibold text-gray-900 mb-3">Articles demandés</h2>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-200"><th className="text-left py-2 font-medium text-gray-500">Article</th><th className="text-left py-2 font-medium text-gray-500">Qté</th><th className="text-left py-2 font-medium text-gray-500">Prix unit.</th><th className="text-left py-2 font-medium text-gray-500">Total</th></tr></thead>
              <tbody>
                {pr.lines?.map(l=>(
                  <tr key={l.id} className="border-b border-gray-100">
                    <td className="py-2">{l.product_detail?.name||l.product}</td>
                    <td className="py-2">{parseFloat(l.quantity)} {l.product_detail?.unit}</td>
                    <td className="py-2">{parseFloat(l.unit_price).toLocaleString('fr-MA')} MAD</td>
                    <td className="py-2 font-medium">{parseFloat(l.total_price||0).toLocaleString('fr-MA')} MAD</td>
                  </tr>
                ))}
              </tbody>
              <tfoot><tr><td colSpan={3} className="py-3 text-right font-semibold">Total :</td><td className="py-3 font-bold text-blue-700">{parseFloat(pr.total_amount||0).toLocaleString('fr-MA')} MAD</td></tr></tfoot>
            </table>
          </div>
        </div>

        <div className="space-y-5">
          <div className="card">
            <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Clock size={16}/>Historique</h2>
            <div className="space-y-3">
              {pr.logs?.length===0 && <p className="text-gray-400 text-sm">Aucune action</p>}
              {pr.logs?.map(log=>(
                <div key={log.id} className="flex gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 flex-shrink-0"/>
                  <div>
                    <p className="text-sm font-medium capitalize">{log.action}</p>
                    <p className="text-xs text-gray-500">{log.performed_by_name} · {new Date(log.created_at).toLocaleDateString('fr-MA')}</p>
                    {log.comment && <p className="text-xs text-gray-600 mt-0.5 italic">"{log.comment}"</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal rejet */}
      <Modal isOpen={showRejectModal} onClose={()=>setShowRejectModal(false)} title="Rejeter la demande" size="sm">
        <div className="space-y-4">
          <div><label className="label">Motif du rejet *</label><textarea className="input" rows={4} value={comment} onChange={e=>setComment(e.target.value)} placeholder="Expliquez la raison du rejet..."/></div>
          <div className="flex gap-3">
            <button onClick={()=>{ if(!comment.trim()){toast.error('Motif requis');return} action(()=>purchaseRequestService.reject(id,{comment}),'Demande rejetée'); setShowRejectModal(false) }} className="btn-danger">Rejeter</button>
            <button onClick={()=>setShowRejectModal(false)} className="btn-secondary">Annuler</button>
          </div>
        </div>
      </Modal>

      {/* Modal commande */}
      <Modal isOpen={showOrderModal} onClose={()=>setShowOrderModal(false)} title="Créer un bon de commande" size="sm">
        <div className="space-y-4">
          <div>
            <label className="label">Fournisseur *</label>
            <select className="input" value={selectedSupplier} onChange={e=>setSelectedSupplier(e.target.value)}>
              <option value="">-- Sélectionner --</option>
              {suppliers.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div><label className="label">Date de livraison prévue</label><input type="date" className="input" value={expectedDate} onChange={e=>setExpectedDate(e.target.value)}/></div>
          <div className="flex gap-3">
            <button onClick={()=>{ if(!selectedSupplier){toast.error('Fournisseur requis');return} action(()=>purchaseRequestService.createOrder(id,{supplier_id:selectedSupplier,expected_date:expectedDate||undefined}),'Bon de commande créé'); setShowOrderModal(false) }} className="btn-primary">Créer la commande</button>
            <button onClick={()=>setShowOrderModal(false)} className="btn-secondary">Annuler</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
