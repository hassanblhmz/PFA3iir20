# Activity diagrams

Placeholder pour les diagrammes d'activite.

```mermaid
flowchart TD
  A[Demande brouillon] --> B[Soumission]
  B --> C{Decision validateur}
  C -->|Valider| D[Demande validee]
  C -->|Rejeter| E[Demande rejetee]
  D --> F[Creation commande]
  F --> G[Envoi fournisseur]
  G --> H[Reception]
  H --> I[Mouvement stock]
```
