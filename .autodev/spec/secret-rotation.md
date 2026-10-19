# Secret rotation list (F001)

For the owner. This list names variables and services only, never values. No agent opened the secret file. The owner checked it on 2026-10-19 and reported its variable names. This list replaces the earlier version, which inferred a Google API key from the code: the file never held one.

`.devcontainer/.env` was tracked in this public repository from September 2025 until F001. Anyone may have copied it since then.

## Variables in the file (reported by the owner, 2026-10-19)
`PYTHONPATH`, `PYTHONUNBUFFERED`, `GFL_ENV`, `GFL_DEBUG`, `GFL_LOG_LEVEL`, `DATABASE_URL`, `API_HOST`, `API_PORT`, `WEB_HOST`, `WEB_PORT`, `SECRET_KEY`.

## Assessment
- **No third-party credential.** The file holds no Google, cloud, model-hub, CI or payment key, so no external account needs rotation.
- **`SECRET_KEY` and `DATABASE_URL`** belong to the local dev container. The database URL points at the compose test database. They protect nothing outside a developer's machine, *provided the same values are not used anywhere else*.
- **Action:**
  - Treat both values as public, and never reuse them in any deployed service.
  - Any future deployment generates its own values from a secret store.
  - `.devcontainer/.env.example` lists the names only.
- **History purge:** not recommended. It needs a force-push to a public repository with forks, and it protects nothing, because the values are dev-only and already public.
