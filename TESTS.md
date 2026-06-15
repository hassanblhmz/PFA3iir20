# Tests manuels

Ces scenarios sont prevus pour une verification de demo apres `migrate` et `seed_data.py`.

## 1. Login

- Aller sur `http://localhost:8000/login/`.
- Se connecter avec `admin@pfa.ma / admin123`.
- Verifier la redirection vers le dashboard.

## 2. Creer un fournisseur

- Se connecter comme `acheteur@pfa.ma / test123`.
- Ouvrir `Fournisseurs`.
- Ajouter un fournisseur.
- Verifier son affichage dans la liste.

## 3. Creer un article

- Rester connecte comme acheteur.
- Ouvrir `Articles`.
- Ajouter un article avec seuil minimum.
- Verifier le badge de statut stock.

## 4. Creer une demande d'achat

- Se connecter comme `demandeur@pfa.ma / test123`.
- Ouvrir `Demandes`.
- Creer une demande avec une premiere ligne.
- Soumettre la demande.

## 5. Valider ou rejeter une demande

- Se connecter comme `validateur@pfa.ma / test123`.
- Ouvrir la demande soumise.
- Valider avec commentaire.
- Verifier le journal de validation.

## 6. Creer un bon de commande

- Se connecter comme `acheteur@pfa.ma / test123`.
- Ouvrir la demande validee.
- Generer une commande avec un fournisseur.
- Envoyer la commande.

## 7. Reponse fournisseur

- Se connecter comme `fournisseur@pfa.ma / test123`.
- Ouvrir `Commandes`.
- Soumettre un devis ou confirmer la commande.
- Verifier le statut fournisseur.

## 8. Enregistrer une reception

- Se connecter comme `magasinier@pfa.ma / test123`.
- Ouvrir la commande.
- Receptionner une quantite.
- Verifier le statut de reception.

## 9. Verifier le mouvement de stock

- Ouvrir `Stock`.
- Verifier que le mouvement d'entree existe.
- Verifier que le stock de l'article a augmente.

## 10. Verifier dashboard, notifications et audit

- Ouvrir le dashboard.
- Verifier les indicateurs demandes, commandes, stock critique.
- Verifier les notifications recentes.
- Se connecter comme admin et ouvrir `Comptes`.
- Verifier les audit logs.

## Commandes techniques

```bash
cd backend
../.venv_local/Scripts/python.exe manage.py check
../.venv_local/Scripts/python.exe manage.py makemigrations --check --dry-run
```
