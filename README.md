# GestAchats - Systeme web de gestion des achats et approvisionnements

GestAchats est un projet PFA EMSI realise avec Django. Il couvre un workflow simple de gestion des achats: demande d'achat, validation, consultation/reponse fournisseur, bon de commande, reception, mouvement de stock, notifications et audit.

L'application reste volontairement academic-friendly: rendu serveur Django, templates HTML, CSS simple, Django Admin et API DRF. Aucun React, Vue, Angular ou JavaScript frontend n'est requis.

## Acteurs

| Acteur | Role principal |
| --- | --- |
| Admin | Administration des comptes, supervision globale |
| Demandeur | Creation et suivi des demandes d'achat |
| Validateur | Validation ou rejet motive des demandes |
| Acheteur | Fournisseurs, articles, commandes et suivi des devis |
| Magasinier | Reception, mouvements de stock, alertes critiques |
| Direction | Consultation dashboard/reporting |
| Fournisseur | Reponse aux commandes et conversations fournisseur |

## Fonctionnalites principales

- Authentification Django avec roles metier.
- Referentiel fournisseurs.
- Referentiel articles et categories.
- Demandes d'achat avec lignes, priorite et statut.
- Validation/rejet avec journal de validation.
- Conversations fournisseur/demandeur pour articles critiques ou indisponibles.
- Bons de commande generes depuis une demande validee.
- Reponses fournisseur: devis, confirmation, refus, statut livraison.
- Receptions partielles ou totales.
- Mouvements de stock automatiques apres reception et ajustements manuels.
- Alertes stock critique selon le seuil minimum.
- Notifications applicatives simples.
- Audit logs pour les actions sensibles.
- Dashboard server-rendered avec indicateurs et activite recente.

## Stack technique

- Python 3
- Django 5
- Django REST Framework
- SQLite pour le demo local
- Templates Django HTML
- CSS local dans `frontend/styles.css`

## Installation rapide

### Windows

```powershell
cd pfa_project
.\start.ps1
```

### Linux/macOS

```bash
cd pfa_project
./start.sh
```

Les scripts creent/utilisent `.venv_local`, installent les dependances, appliquent les migrations, chargent les donnees de demo et lancent Django sur `http://localhost:8000/`.

## Installation manuelle

```bash
cd pfa_project/backend
python -m venv ../.venv_local
../.venv_local/Scripts/python.exe -m pip install -r requirements.txt
../.venv_local/Scripts/python.exe manage.py migrate
../.venv_local/Scripts/python.exe seed_data.py
../.venv_local/Scripts/python.exe manage.py runserver
```

Sous Linux/macOS, remplacer `../.venv_local/Scripts/python.exe` par `../.venv_local/bin/python`.

## Creer un superuser

```bash
cd pfa_project/backend
../.venv_local/Scripts/python.exe manage.py createsuperuser
```

## Comptes de demonstration

| Email | Mot de passe | Role |
| --- | --- | --- |
| admin@pfa.ma | admin123 | Administrateur |
| demandeur@pfa.ma | test123 | Demandeur |
| validateur@pfa.ma | test123 | Validateur |
| acheteur@pfa.ma | test123 | Acheteur |
| magasinier@pfa.ma | test123 | Magasinier |
| fournisseur@pfa.ma | test123 | Fournisseur |

## Liens utiles

- Application: `http://localhost:8000/`
- Login: `http://localhost:8000/login/`
- Django Admin: `http://localhost:8000/admin/`
- Comptes demo: `http://localhost:8000/accounts/`
- API: `http://localhost:8000/api/`

## Configuration

Les valeurs locales par defaut restent utilisables pour la demo. Pour eviter de partager un secret, copier `.env.example` et definir les variables dans votre shell ou environnement:

```text
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

## Captures d'ecran

Ajouter ici les captures pour le rapport/soutenance:

- Login
- Dashboard
- Demandes d'achat
- Commandes
- Stock
- Audit logs

## Verification

```bash
cd pfa_project/backend
../.venv_local/Scripts/python.exe manage.py check
../.venv_local/Scripts/python.exe manage.py makemigrations --check --dry-run
```

Voir aussi `INSTALLATION.md`, `TESTS.md`, `FEATURES.md` et le dossier `docs/`.
