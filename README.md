# 🛒 GestAchats — Gestion des Achats & Approvisionnements
### Projet de Fin d'Année (PFA) — EMSI 2024

Application web complète de gestion des achats et approvisionnements avec workflow de validation, gestion des commandes, réceptions et stocks.

---

## 🏗️ Architecture

```
pfa_project/
├── backend/          # Django + DRF + JWT
│   ├── users/        # Auth & gestion des rôles
│   ├── suppliers/    # Fournisseurs
│   ├── products/     # Articles & catégories
│   ├── purchases/    # Demandes, commandes, réceptions
│   ├── stock/        # Mouvements de stock
│   └── core/         # Settings, URLs
└── frontend/         # React + Vite + Tailwind CSS
    └── src/
        ├── components/  # Layout & composants UI
        ├── pages/       # Toutes les pages
        ├── services/    # API calls (axios)
        └── context/     # Auth context
```

---

## 🚀 Lancement rapide

### Prérequis
- Python 3.10+
- Node.js 18+

### Backend Django

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python manage.py migrate

# Générer les données de test
python seed_data.py

# Lancer le serveur
python manage.py runserver
```
➡️ Backend accessible sur : **http://localhost:8000**
➡️ Admin Django : **http://localhost:8000/admin**

### Frontend React

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```
➡️ Frontend accessible sur : **http://localhost:3000**

---

## 👤 Comptes de démonstration

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| admin@pfa.ma | admin123 | Administrateur |
| demandeur@pfa.ma | test123 | Demandeur |
| validateur@pfa.ma | test123 | Validateur |
| acheteur@pfa.ma | test123 | Acheteur |
| magasinier@pfa.ma | test123 | Magasinier |

---

## 🔑 Fonctionnalités par rôle

| Fonctionnalité | Admin | Demandeur | Validateur | Acheteur | Magasinier |
|---|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Créer demande achat | ✅ | ✅ | | | |
| Valider/Rejeter demande | ✅ | | ✅ | | |
| Créer bon de commande | ✅ | | | ✅ | |
| Réceptionner commande | ✅ | | | | ✅ |
| Ajustement stock | ✅ | | | | ✅ |
| Gérer utilisateurs | ✅ | | | | |
| CRUD Fournisseurs/Articles | ✅ | 👁️ | 👁️ | ✅ | 👁️ |

---

## 📡 API Endpoints principaux

```
POST   /api/auth/login/                    # Connexion JWT
POST   /api/auth/refresh/                  # Refresh token
GET    /api/users/me/                      # Profil connecté
GET    /api/suppliers/                     # Liste fournisseurs
GET    /api/products/                      # Liste articles
GET    /api/products/critical/             # Articles stock critique
GET    /api/purchases/requests/            # Demandes d'achat
POST   /api/purchases/requests/{id}/submit/   # Soumettre demande
POST   /api/purchases/requests/{id}/validate/ # Valider demande
POST   /api/purchases/requests/{id}/reject/   # Rejeter demande
POST   /api/purchases/requests/{id}/create_order/ # Créer commande
GET    /api/purchases/orders/              # Bons de commande
POST   /api/purchases/orders/{id}/send/    # Envoyer commande
POST   /api/purchases/receptions/          # Enregistrer réception
GET    /api/stock/movements/               # Mouvements de stock
POST   /api/stock/movements/adjust/        # Ajustement stock
GET    /api/purchases/dashboard/           # Stats dashboard
```

---

## 🛠️ Technologies utilisées

**Backend :**
- Django 4.2 + Django REST Framework 3.14
- JWT (djangorestframework-simplejwt)
- SQLite (dev) / PostgreSQL (prod)
- CORS Headers

**Frontend :**
- React 18 + Vite
- Tailwind CSS 3
- React Router 6
- Axios (HTTP client)
- Chart.js + React-ChartJS-2
- React Hot Toast

---

## 📦 Production (optionnel)

Pour PostgreSQL, modifier `core/settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pfa_db',
        'USER': 'postgres',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

*Réalisé dans le cadre du PFA — École Marocaine des Sciences de l'Ingénieur (EMSI) 2024*
