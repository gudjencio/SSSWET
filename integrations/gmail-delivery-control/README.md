# Private Gmail delivery control (Google Apps Script)

This tool is intended for the project operator's private Google account only. It creates institutional outreach drafts and helps review delivery-related email threads.

## Files

- `Code.gs`: owner-restricted server functions.
- `index.html`: private dashboard.
- `appsscript.json`: explicit Gmail and identity scopes.

## Setup

1. Sign in to `ssswetindustries@gmail.com`.
2. Open [Google Apps Script](https://script.google.com/) and create a standalone project.
3. Copy `Code.gs` into the script editor.
4. Add an HTML file named exactly `index` and copy `index.html` into it.
5. In Project Settings, enable **Show "appsscript.json" manifest file** and replace its contents with the manifest in this folder.
6. Save, run `getDeliveryThreads` once and review the requested Gmail permissions.
7. Deploy as a web app with **Execute as: Me** and **Who has access: Only myself**. Never select public or anyone-with-link access.
8. Open the private deployment URL while signed in to the project account.

If Google Workspace policy prevents the account identity check or owner-only deployment, do not weaken the access check.

## Delivery email procedure

1. Verify the full order amount in the official payment provider account; do not rely on an email notification alone.
2. Verify that the specific technology was actually delivered and receipt is confirmed.
3. In Gmail, apply the label `SSSWET/Delivery-Complete` to the corresponding thread.
4. Open the private dashboard. Check both confirmation boxes and move that one thread to Trash.
5. Gmail Trash is reversible and Gmail applies its normal retention/deletion policy. This script does not permanently erase messages.

The script does not read all mailbox messages, send mail, delete unlabelled threads or perform bulk deletion. It only lists metadata/snippets for threads explicitly labelled by the owner. Each archive action requires two separate human confirmations plus an explicit confirmation phrase checked by the server.

## Institutional outreach

The form creates a Gmail draft only. It does not send it. Use it only when a specific authority, research institution, standards body or qualified organization is genuinely needed. Add accurate project details, existing evidence, known limitations, the specific assistance requested, the safest lawful first steps and applicable approval questions. Review the recipient, every factual statement and attachments in Gmail before sending manually.

## Privacy and security

- Do not publish the Apps Script deployment URL.
- Do not share this project with other Google accounts.
- Do not store payment credentials, card data or unnecessary personal data in this tool.
- Delivery addresses should be collected only after the product is genuinely available, the buyer has accepted the terms and the full payment has cleared. Keep addresses out of GitHub, public logs and the research journal.
- Keep records required for accounting, legal, warranty and consumer-protection obligations.
- The private audit note stores only the thread ID, subject, timestamp and action in Script Properties. It does not store message bodies or delivery addresses.
