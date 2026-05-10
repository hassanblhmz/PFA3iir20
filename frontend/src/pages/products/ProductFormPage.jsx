import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { productService, supplierService } from '../../services/api'
import { PageHeader } from '../../components/ui'
import toast from 'react-hot-toast'

const INITIAL = { code:'', name:'', description:'', category:'', unit:'pièce', unit_price:0, current_stock:0, min_stock:0, max_stock:0, suppliers:[], is_active:true }
const UNITS = ['pièce','kg','litre','carton','palette','mètre','lot']

export default function ProductFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL)
  const [categories, setCategories] = useState([])
  const [allSuppliers, setAllSuppliers] = useState([])
  const [loading, setLoading] = useState(false)
  const isEdit = !!id

  useEffect(() => {
    Promise.all([productService.listCategories(), supplierService.list()]).then(([c,s]) => {
      setCategories(c.data.results||c.data)
      setAllSuppliers(s.data.results||s.data)
    })
    if (isEdit) productService.get(id).then(r => setForm({...r.data, suppliers: r.data.suppliers||[]}))
  }, [id])

  const set = (k,v) => setForm(f=>({...f,[k]:v}))
  const toggleSupplier = sid => set('suppliers', form.suppliers.includes(sid)?form.suppliers.filter(x=>x!==sid):[...form.suppliers,sid])

  const handleSubmit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      if (isEdit) { await productService.update(id,form); toast.success('Article mis à jour') }
      else { await productService.create(form); toast.success('Article créé') }
      navigate('/products')
    } catch(err) { toast.error(err.response?.data?.code?.[0]||'Erreur lors de la sauvegarde') }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-5 max-w-3xl">
      <PageHeader title={isEdit?'Modifier article':'Nouvel article'}/>
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="label">Référence *</label><input className="input" value={form.code} onChange={e=>set('code',e.target.value)} required/></div>
            <div><label className="label">Désignation *</label><input className="input" value={form.name} onChange={e=>set('name',e.target.value)} required/></div>
            <div>
              <label className="label">Catégorie</label>
              <select className="input" value={form.category} onChange={e=>set('category',e.target.value)}>
                <option value="">-- Sélectionner --</option>
                {categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Unité</label>
              <select className="input" value={form.unit} onChange={e=>set('unit',e.target.value)}>
                {UNITS.map(u=><option key={u} value={u}>{u}</option>)}
              </select>
            </div>
            <div><label className="label">Prix unitaire (MAD)</label><input type="number" step="0.01" className="input" value={form.unit_price} onChange={e=>set('unit_price',e.target.value)}/></div>
            <div><label className="label">Stock actuel</label><input type="number" step="0.01" className="input" value={form.current_stock} onChange={e=>set('current_stock',e.target.value)}/></div>
            <div><label className="label">Seuil minimum</label><input type="number" step="0.01" className="input" value={form.min_stock} onChange={e=>set('min_stock',e.target.value)}/></div>
            <div><label className="label">Stock maximum</label><input type="number" step="0.01" className="input" value={form.max_stock} onChange={e=>set('max_stock',e.target.value)}/></div>
          </div>
          <div><label className="label">Description</label><textarea className="input" rows={3} value={form.description} onChange={e=>set('description',e.target.value)}/></div>
          <div>
            <label className="label">Fournisseurs associés</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {allSuppliers.map(s=>(
                <label key={s.id} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border cursor-pointer text-sm transition-colors ${form.suppliers.includes(s.id)?'border-blue-500 bg-blue-50 text-blue-700':'border-gray-200 hover:border-gray-300'}`}>
                  <input type="checkbox" className="hidden" checked={form.suppliers.includes(s.id)} onChange={()=>toggleSupplier(s.id)}/>
                  {s.name}
                </label>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="active" checked={form.is_active} onChange={e=>set('is_active',e.target.checked)}/>
            <label htmlFor="active" className="text-sm text-gray-700">Article actif</label>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={loading} className="btn-primary">{loading?'Enregistrement...':'Enregistrer'}</button>
            <button type="button" onClick={()=>navigate('/products')} className="btn-secondary">Annuler</button>
          </div>
        </form>
      </div>
    </div>
  )
}
