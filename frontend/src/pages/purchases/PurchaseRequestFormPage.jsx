import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { purchaseRequestService, productService } from '../../services/api'
import { PageHeader } from '../../components/ui'
import { Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

const EMPTY_LINE = { product: '', quantity: 1, unit_price: 0, notes: '' }

export default function PurchaseRequestFormPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [form, setForm] = useState({ title:'', priority:'normale', needed_date:'', notes:'', lines:[{...EMPTY_LINE}] })
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { productService.list().then(r => setProducts(r.data.results||r.data)) }, [])

  const setF = (k,v) => setForm(f=>({...f,[k]:v}))
  const setLine = (i,k,v) => setForm(f=>({ ...f, lines: f.lines.map((l,idx)=>idx===i?{...l,[k]:v}:l) }))
  const addLine = () => setForm(f=>({...f, lines:[...f.lines,{...EMPTY_LINE}]}))
  const removeLine = i => setForm(f=>({...f, lines: f.lines.filter((_,idx)=>idx!==i)}))

  const total = form.lines.reduce((s,l)=>s+(parseFloat(l.quantity||0)*parseFloat(l.unit_price||0)),0)

  const handleSubmit = async (e, asDraft=false) => {
    e.preventDefault()
    if (form.lines.every(l=>!l.product)) { toast.error('Ajoutez au moins un article'); return }
    setLoading(true)
    try {
      const validLines = form.lines.filter(l=>l.product).map(l=>({...l, product:parseInt(l.product), quantity:parseFloat(l.quantity), unit_price:parseFloat(l.unit_price)}))
      const r = await purchaseRequestService.create({...form, lines:validLines})
      if (!asDraft) await purchaseRequestService.submit(r.data.id)
      toast.success(asDraft?'Brouillon sauvegardé':'Demande soumise avec succès')
      navigate('/purchases/requests')
    } catch(err) { toast.error(err.response?.data?.detail||'Erreur') }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-5 max-w-4xl">
      <PageHeader title="Nouvelle demande d'achat"/>
      <div className="card space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2"><label className="label">Objet *</label><input className="input" value={form.title} onChange={e=>setF('title',e.target.value)} required/></div>
          <div>
            <label className="label">Priorité</label>
            <select className="input" value={form.priority} onChange={e=>setF('priority',e.target.value)}>
              <option value="normale">Normale</option><option value="urgente">Urgente</option><option value="critique">Critique</option>
            </select>
          </div>
          <div><label className="label">Date souhaitée</label><input type="date" className="input" value={form.needed_date} onChange={e=>setF('needed_date',e.target.value)}/></div>
          <div className="sm:col-span-2"><label className="label">Remarques</label><input className="input" value={form.notes} onChange={e=>setF('notes',e.target.value)}/></div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Lignes d'articles</h3>
            <button type="button" onClick={addLine} className="btn-secondary text-sm flex items-center gap-1"><Plus size={14}/>Ajouter une ligne</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-200">
                <th className="text-left py-2 px-2 text-gray-500 font-medium">Article</th>
                <th className="text-left py-2 px-2 text-gray-500 font-medium w-24">Qté</th>
                <th className="text-left py-2 px-2 text-gray-500 font-medium w-32">Prix unit. (MAD)</th>
                <th className="text-left py-2 px-2 text-gray-500 font-medium w-28">Total</th>
                <th className="w-8"></th>
              </tr></thead>
              <tbody>
                {form.lines.map((line,i)=>(
                  <tr key={i} className="border-b border-gray-100">
                    <td className="py-2 px-2">
                      <select className="input text-sm" value={line.product} onChange={e=>{
                        const p = products.find(x=>x.id===parseInt(e.target.value))
                        setLine(i,'product',e.target.value)
                        if(p) setLine(i,'unit_price',p.unit_price)
                      }}>
                        <option value="">-- Sélectionner --</option>
                        {products.map(p=><option key={p.id} value={p.id}>{p.code} — {p.name}</option>)}
                      </select>
                    </td>
                    <td className="py-2 px-2"><input type="number" min="0.01" step="0.01" className="input text-sm" value={line.quantity} onChange={e=>setLine(i,'quantity',e.target.value)}/></td>
                    <td className="py-2 px-2"><input type="number" min="0" step="0.01" className="input text-sm" value={line.unit_price} onChange={e=>setLine(i,'unit_price',e.target.value)}/></td>
                    <td className="py-2 px-2 font-medium">{(parseFloat(line.quantity||0)*parseFloat(line.unit_price||0)).toLocaleString('fr-MA')}</td>
                    <td className="py-2 px-2">{form.lines.length>1&&<button onClick={()=>removeLine(i)} className="text-gray-300 hover:text-red-500"><Trash2 size={14}/></button>}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot><tr><td colSpan={3} className="py-3 px-2 text-right font-semibold text-gray-700">Total estimé :</td><td className="py-3 px-2 font-bold text-blue-700">{total.toLocaleString('fr-MA')} MAD</td><td></td></tr></tfoot>
            </table>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button onClick={e=>handleSubmit(e,false)} disabled={loading} className="btn-primary">{loading?'Envoi...':'Soumettre la demande'}</button>
          <button onClick={e=>handleSubmit(e,true)} disabled={loading} className="btn-secondary">Sauvegarder en brouillon</button>
          <button type="button" onClick={()=>navigate('/purchases/requests')} className="btn-secondary">Annuler</button>
        </div>
      </div>
    </div>
  )
}
