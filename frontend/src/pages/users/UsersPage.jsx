import React, { useEffect, useState } from 'react'
import { userService } from '../../services/api'
import { PageHeader, Table, Modal } from '../../components/ui'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

const ROLES = ['admin','demandeur','validateur','acheteur','magasinier']
const INITIAL_FORM = { email:'', username:'', first_name:'', last_name:'', role:'demandeur', department:'', phone:'', password:'', password_confirm:'' }

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editUser, setEditUser] = useState(null)
  const [form, setForm] = useState(INITIAL_FORM)

  const load = () => {
    setLoading(true)
    userService.list().then(r=>setUsers(r.data.results||r.data)).finally(()=>setLoading(false))
  }
  useEffect(()=>{ load() },[])

  const openCreate = () => { setEditUser(null); setForm(INITIAL_FORM); setShowModal(true) }
  const openEdit = (u) => { setEditUser(u); setForm({...u, password:'', password_confirm:''}); setShowModal(true) }

  const handleSubmit = async () => {
    try {
      if (editUser) { await userService.update(editUser.id, {first_name:form.first_name,last_name:form.last_name,role:form.role,department:form.department,phone:form.phone,is_active:form.is_active}); toast.success('Utilisateur mis à jour') }
      else { await userService.create(form); toast.success('Utilisateur créé') }
      setShowModal(false); load()
    } catch(e) { toast.error(Object.values(e.response?.data||{})[0]?.[0]||'Erreur') }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer cet utilisateur ?')) return
    try { await userService.delete(id); toast.success('Supprimé'); load() }
    catch { toast.error('Erreur suppression') }
  }

  const ROLE_COLORS = { admin:'bg-purple-100 text-purple-700', demandeur:'bg-blue-100 text-blue-700', validateur:'bg-green-100 text-green-700', acheteur:'bg-orange-100 text-orange-700', magasinier:'bg-teal-100 text-teal-700' }
  const ROLE_LABELS = { admin:'Admin', demandeur:'Demandeur', validateur:'Validateur', acheteur:'Acheteur', magasinier:'Magasinier' }

  const columns = [
    { key: 'full_name', title: 'Nom complet' },
    { key: 'email', title: 'Email' },
    { key: 'role', title: 'Rôle', render: v => <span className={`badge ${ROLE_COLORS[v]}`}>{ROLE_LABELS[v]}</span> },
    { key: 'department', title: 'Département' },
    { key: 'is_active', title: 'Actif', render: v => <span className={`badge ${v?'bg-green-100 text-green-700':'bg-gray-100 text-gray-500'}`}>{v?'Oui':'Non'}</span> },
    { key: 'actions', title: '', render: (_, row) => (
      <div className="flex gap-2 justify-end">
        <button onClick={()=>openEdit(row)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg"><Pencil size={15}/></button>
        <button onClick={()=>handleDelete(row.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><Trash2 size={15}/></button>
      </div>
    )},
  ]

  const set = (k,v) => setForm(f=>({...f,[k]:v}))

  return (
    <div className="space-y-5">
      <PageHeader title="Utilisateurs" subtitle={`${users.length} utilisateur(s)`}
        actions={<button onClick={openCreate} className="btn-primary flex items-center gap-2"><Plus size={16}/>Nouvel utilisateur</button>}/>
      <div className="card">
        <Table columns={columns} data={users} loading={loading} emptyMessage="Aucun utilisateur"/>
      </div>

      <Modal isOpen={showModal} onClose={()=>setShowModal(false)} title={editUser?'Modifier utilisateur':'Nouvel utilisateur'}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Prénom</label><input className="input" value={form.first_name} onChange={e=>set('first_name',e.target.value)}/></div>
            <div><label className="label">Nom</label><input className="input" value={form.last_name} onChange={e=>set('last_name',e.target.value)}/></div>
          </div>
          {!editUser && <>
            <div><label className="label">Email *</label><input type="email" className="input" value={form.email} onChange={e=>set('email',e.target.value)}/></div>
            <div><label className="label">Nom d'utilisateur *</label><input className="input" value={form.username} onChange={e=>set('username',e.target.value)}/></div>
            <div><label className="label">Mot de passe *</label><input type="password" className="input" value={form.password} onChange={e=>set('password',e.target.value)}/></div>
            <div><label className="label">Confirmer mot de passe *</label><input type="password" className="input" value={form.password_confirm} onChange={e=>set('password_confirm',e.target.value)}/></div>
          </>}
          <div>
            <label className="label">Rôle</label>
            <select className="input" value={form.role} onChange={e=>set('role',e.target.value)}>
              {ROLES.map(r=><option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
            </select>
          </div>
          <div><label className="label">Département</label><input className="input" value={form.department} onChange={e=>set('department',e.target.value)}/></div>
          <div><label className="label">Téléphone</label><input className="input" value={form.phone} onChange={e=>set('phone',e.target.value)}/></div>
          {editUser && <div className="flex items-center gap-2"><input type="checkbox" id="ua" checked={form.is_active} onChange={e=>set('is_active',e.target.checked)}/><label htmlFor="ua" className="text-sm text-gray-700">Compte actif</label></div>}
          <div className="flex gap-3 pt-2">
            <button onClick={handleSubmit} className="btn-primary">Enregistrer</button>
            <button onClick={()=>setShowModal(false)} className="btn-secondary">Annuler</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
