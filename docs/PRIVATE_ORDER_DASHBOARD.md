# Private order dashboard

Open the local dashboard at `http://127.0.0.1:8765/admin.html` after starting the local service.

## Configure the administrator token

Generate a long random token locally (do not commit it or send it to anyone):

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set it as the `SSSWET_ADMIN_TOKEN` environment variable before starting SSSWET.

PowerShell:

```powershell
$env:SSSWET_ADMIN_TOKEN = "paste-your-private-token-here"
ssswet-local
```

macOS/Linux:

```bash
export SSSWET_ADMIN_TOKEN="paste-your-private-token-here"
ssswet-local
```

The dashboard keeps the token in page memory only. It is not written to local storage or cookies. The private API checks the token, loopback client address, Host and Origin. Keep the server bound to `127.0.0.1`; do not expose it through a public tunnel, LAN, reverse proxy or the Google Sites mirror.

The dashboard records operator-entered payment confirmations; it does not verify PayPal transactions automatically. Check the provider's official transaction history before recording a payment. Never enter customer addresses here.

This is a local operator prototype. Before production use, add operating-system account protection, HTTPS for any remote administration, stronger operator identity/audit controls, backup/restore procedures and a legally compliant separate fulfilment-address workflow.
