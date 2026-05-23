# GestAchats - Gestion des achats et approvisionnements

Projet PFA EMSI pour piloter les demandes d'achat, fournisseurs, commandes,
receptions et mouvements de stock.

## Architecture

```text
pfa_project/
├── backend/              Django + DRF + JWT
│   ├── users/            Utilisateurs et roles
│   ├── suppliers/        Fournisseurs
│   ├── products/         Articles, categories, seuils
│   ├── purchases/        Demandes, validations, commandes, receptions
│   └── stock/            Mouvements et ajustements de stock
└── frontend/             Templates HTML/CSS servis par Django
    ├── index.html
    └── styles.css
```

Le frontend ne contient plus de JavaScript, React, Vite, npm, Tailwind ou
`node_modules`. Il est servi par Django et commence par la page de connexion.
Apres authentification, la racine affiche l'espace autorise du role connecte.

## Lancement rapide

### Windows

```powershell
.\start.ps1
```

### Linux/macOS

```bash
./start.sh
```

Les scripts installent les dependances Python, appliquent les migrations,
chargent les donnees de demonstration et lancent le backend Django.

```text
Login            : http://localhost:8000/login/
Espace connecte  : http://localhost:8000/
Comptes admin    : http://localhost:8000/accounts/
Templates HTML/CSS : frontend/
Backend API       : http://localhost:8000
Admin Django      : http://localhost:8000/admin
```

## Lancement manuel

```bash
cd backend
python -m venv ../.venv_local
../.venv_local/Scripts/python.exe -m pip install -r requirements.txt
../.venv_local/Scripts/python.exe manage.py migrate
../.venv_local/Scripts/python.exe seed_data.py
../.venv_local/Scripts/python.exe manage.py runserver
```

Ensuite, ouvrir `http://localhost:8000/`. Sans session active, Django redirige
vers `http://localhost:8000/login/`.

Pour tester les roles, ouvrir `http://localhost:8000/login/`, puis se
connecter avec un des comptes de demonstration.

## Comptes de demonstration

| Email | Mot de passe | Role |
| --- | --- | --- |
| admin@pfa.ma | admin123 | Administrateur |
| demandeur@pfa.ma | test123 | Demandeur |
| validateur@pfa.ma | test123 | Validateur |
| acheteur@pfa.ma | test123 | Acheteur |
| magasinier@pfa.ma | test123 | Magasinier |

## Relations metier verifiees

| Classe | Relations principales |
| --- | --- |
| `User` | `purchase_requests`, `purchase_orders`, `receptions`, `validation_logs`, `stock_movements`, `audit_logs` |
| `Supplier` | `products`, `purchase_orders`, `quotes`, `consultations`, `request_conversations` |
| `Product` | `suppliers`, `request_lines`, `order_lines`, `movements` |
| `PurchaseRequest` | `requested_by`, `lines`, `logs`, `consultations`, `supplier_conversations`, `order` |
| `PurchaseOrder` | `purchase_request`, `supplier`, `ordered_by`, `order_lines`, `receptions` |
| `Reception` | `order`, `received_by`, `lines` |
| `SupplierRequestConversation` | `purchase_request`, `request_line`, `supplier`, `demandeur`, `messages` |

La conversation fournisseur/demandeur est autorisee uniquement pour un article
critique, en rupture ou desactive. Le fournisseur et le demandeur sont controles
sur chaque message, et une conversation cloturee ne peut plus recevoir de
reponse.

## Endpoints principaux

```text
POST   /api/auth/login/
POST   /api/auth/refresh/
GET    /api/users/me/
GET    /api/suppliers/
GET    /api/products/
GET    /api/products/critical/
GET    /api/purchases/requests/
POST   /api/purchases/requests/{id}/submit/
POST   /api/purchases/requests/{id}/validate/
POST   /api/purchases/requests/{id}/reject/
POST   /api/purchases/requests/{id}/create_order/
GET    /api/purchases/orders/
POST   /api/purchases/orders/{id}/send/
POST   /api/purchases/receptions/
GET    /api/purchases/supplier-conversations/
POST   /api/purchases/supplier-conversations/{id}/reply/
POST   /api/purchases/supplier-conversations/{id}/close/
GET    /api/stock/movements/
POST   /api/stock/movements/adjust/
GET    /api/purchases/dashboard/
```

## Verification

```bash
cd backend
../.venv_local/Scripts/python.exe manage.py check
../.venv_local/Scripts/python.exe manage.py makemigrations --check --dry-run
```
