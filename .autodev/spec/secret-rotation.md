# Secret rotation list (F001)

For the owner. This list names services and owners only. It holds no values. No agent opened the secret file; the services below come from the variable names that the code and the dev-container configuration read.

The file .devcontainer/.env was tracked in this public repository from September 2025 (onboarding audit) until F001. Removing it from the tree does not remove it from git history or from any clone or fork made since. Treat every credential it held as public.

## Order of work

1. The owner opens the file locally and lists every credential in it, including any the code does not read.
2. Each credential is rotated by the person who controls the account (table below).
3. Only after rotation, the owner decides on the history purge (separate decision in next-steps.md). A purge without rotation gives no protection, because the old values are already public.

## Services

### Google API key for Gemini (variable GOOGLE_API_KEY)
- **Service** - Google AI Studio or Google Cloud project that issued the key (Generative Language API), used by the GFL translator apps.
- **What rotating means** - create a new key in the same project, put it in each local copy of the env file and in any deployment that uses it, then delete the old key. Also check the project's API usage and billing reports for calls since September 2025 that the team did not make, and restrict the new key to the Generative Language API.
- **Who** - the Google account or project owner who created the key (the owner to confirm; probably the Fundación de Neurociencias Google Cloud administrator).

### Any other credential found in the file
- **Service** - each service named by a variable in the file that the code does not read (for example database, cloud storage, model hub or CI tokens).
- **What rotating means** - revoke the old credential at the service, issue a new one, store it outside git, and review the service's access log since September 2025.
- **Who** - the account holder for that service; the owner assigns one person per credential and records the date of rotation.

## Not affected

- PYTHONPATH and GFL_ENV are configuration values, not credentials.
- The PostgreSQL password in the dev-container compose file is a local test-container default. It is not a production credential, but it should not be reused anywhere else.
