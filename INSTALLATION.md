# Installation

## Prerequis

- Python 3
- Git
- Navigateur web

## Lancement avec script Windows

```powershell
cd pfa_project
.\start.ps1
```

## Lancement manuel Windows

```powershell
cd pfa_project
py -m venv .venv_local
.\.venv_local\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\.venv_local\Scripts\python.exe manage.py migrate
..\.venv_local\Scripts\python.exe seed_data.py
..\.venv_local\Scripts\python.exe manage.py runserver
```

## Lancement manuel Linux/macOS

```bash
cd pfa_project
python3 -m venv .venv_local
./.venv_local/bin/python -m pip install -r backend/requirements.txt
cd backend
../.venv_local/bin/python manage.py migrate
../.venv_local/bin/python seed_data.py
../.venv_local/bin/python manage.py runserver
```

## Variables d'environnement

Les valeurs par defaut sont prevues pour le demo local. Pour une configuration propre, definir:

```text
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

## Acces

- Application: `http://localhost:8000/`
- Login: `http://localhost:8000/login/`
- Admin Django: `http://localhost:8000/admin/`

## Superuser

```bash
cd backend
../.venv_local/Scripts/python.exe manage.py createsuperuser
```

Sous Linux/macOS:

```bash
../.venv_local/bin/python manage.py createsuperuser
```
