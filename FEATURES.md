# Mapping cahier des charges

| Module demande | Implementation |
| --- | --- |
| Users et roles | Modele `users.User`, roles metier, pages filtrees par role, Django Admin |
| Fournisseurs | App `suppliers`, CRUD template acheteur/admin, API DRF |
| Articles | App `products`, categories, seuils stock, fournisseurs lies |
| Categories | Modele `Category`, formulaire article, admin/API |
| Demandes d'achat | `PurchaseRequest` et `PurchaseRequestLine`, creation/soumission |
| Validation/rejet | Actions validateur, `ValidationLog`, commentaires |
| Consultations fournisseurs et devis | `SupplierConsultation`, `SupplierQuote`, reponse fournisseur sur commande |
| Bons de commande | `PurchaseOrder`, `PurchaseOrderLine`, generation depuis demande validee |
| Receptions | `Reception`, `ReceptionLine`, reception partielle/totale |
| Mouvements de stock | `StockMovement`, mise a jour apres reception, ajustements manuels |
| Notifications | `Notification`, affichage dashboard/sidebar |
| Audit logs | `AuditLog`, actions sensibles journalisees |
| Dashboard/reporting | Indicateurs demandes, commandes, stock critique, audit recent |

## Actions journalisees

- Creation et soumission de demande.
- Validation ou rejet.
- Creation et envoi de commande.
- Devis, confirmation ou refus fournisseur.
- Reception.
- Mise a jour de stock.
- Ouverture et reponse de conversation fournisseur.

## Limites conservees volontairement

- Pas de workflow complexe multi-niveaux.
- Pas de gestion comptable/facturation avancee.
- Pas de frontend JavaScript.
- Les diagrammes sont documentes en texte pour rester simples a maintenir.
