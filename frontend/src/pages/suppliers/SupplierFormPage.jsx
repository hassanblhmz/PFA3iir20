import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { supplierService } from '../../services/api'
import { PageHeader } from '../../components/ui'
import toast from 'react-hot-toast'

const INITIAL = { code:'', name:'', contact_name:'', email:'', phone:'', address:'', city:'', country:'Maroc', ice:'', payment_terms:30, status:'actif', notes:'' }

export default function SupplierFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL)
  const [loading, setLoading] = useState(false)
  const isEdit = !!id

  useEffect(() => {
    if (isEdit) supplierService.get(id).then(r => setForm(r.data))
  }, [id])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      if (isEdit) { await supplierService.update(id, form); toast.success('Fournisseur mis à jour') }
      else { await supplierService.create(form); toast.success('Fournisseur créé') }
      navigate('/suppliers')
    } catch(err) { toast.error(err.response?.data?.code?.[0] || 'Erreur') }
    finally { setLoading(false) }
  }

  const Field = ({ label, k, type='text', required }) => (
    <div>
      <label className="label">{label}{required && <span className="text-red-500 ml-1">*</span>}</label>
      <input type={type} className="input" value={form[k]} onChange={e=>set(k,e.target.value)} required={required}/>
    </div>
  )

  return (
    <div className="space-y-5 max-w-3xl">
      <PageHeader title={isEdit?'Modifier fournisseur':'Nouveau fournisseur'} />
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Code" k="code" required/>
            <Field label="Raison sociale" k="name" required/>
            <Field label="Contact" k="contact_name"/>
            <Field label="Email" k="email" type="email"/>
            <Field label="Téléphone" k="phone"/>
            <Field label="Ville" k="city"/>
            <Field label="Pays" k="country"/>
            <Field label="ICE" k="ice"/>
            <div>
              <label className="label">Délai paiement (jours)</label>
              <input type="number" className="input" value={form.payment_terms} onChange={e=>set('payment_terms',e.target.value)}/>
            </div>
            <div>
              <label className="label">Statut</label>
              <select className="input" value={form.status} onChange={e=>set('status',e.target.value)}>
                <option value="actif">Actif</option>
                <option value="inactif">Inactif</option>
                <option value="suspendu">Suspendu</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Adresse</label>
            <textarea className="input" rows={2} value={form.address} onChange={e=>set('address',e.target.value)}/>
          </div>
          <div>
            <label className="label">Notes</label>
            <textarea className="input" rows={2} value={form.notes} onChange={e=>set('notes',e.target.value)}/>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={loading} className="btn-primary">{loading?'Enregistrement...':'Enregistrer'}</button>
            <button type="button" onClick={()=>navigate('/suppliers')} className="btn-secondary">Annuler</button>
          </div>
        </form>
      </div>
    </div>
  )
}
