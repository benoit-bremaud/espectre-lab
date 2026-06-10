---
paths:
  - "src/api/**/*.ts"
  - "src/server/**/*.ts"
---

# Conventions API

<!-- Adapte à ton projet -->

- Toutes les entrées validées avec Zod avant traitement
- Format de réponse uniforme : `{ data: T } | { error: { code, message } }`
- Codes HTTP : 200 succès, 400 validation, 401 non authentifié, 403 non autorisé, 404 absent, 500 erreur serveur
- Logs structurés (JSON), jamais de `console.log` en prod
- Rate limit sur tous les endpoints publics
