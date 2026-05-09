# Partner Frontend

Local browser UI for editing Partnership Profiles and stepping through simulated bridge auctions.

The canonical frontend engineering document is:

```text
docs/07_frontend_architecture.md
```

The current prototype is a no-build React app served by `server.mjs`. It uses the local backend at `http://127.0.0.1:8765`.

From the repository root, start both local servers with one command:

```bat
run_local.cmd
```

Keep that CMD window open while using Partner.

Start the backend:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe backend\server.py
```

Start the frontend:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe frontend\server.mjs
```

Open:

```text
http://127.0.0.1:5173
```

The repository also includes `package.json` so this can become a Vite app when npm or another package manager is available.
