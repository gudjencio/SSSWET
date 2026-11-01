# Google Apps Script payment reminders

This optional service sends recurring reminders only to people who explicitly request them. Every address must be confirmed by email. Reminders are not payment instructions from SSSWET and do not trigger automatic charges.

## Install

1. Open the Google Apps Script project already used by SSSWET.
2. Add the contents of `PaymentReminders.gs` as a new script file.
3. In the existing `doPost(e)`, read the form payload using the project's existing `parsePostBody(e)` helper. The website sends a simple URL-encoded form request to avoid browser preflight restrictions. Resolve the nested JSON payload, then add the branch before the research-success relay's secret check. If your existing function already declares a variable named `payload`, replace that declaration with this normalized form instead of declaring it twice:

   ```javascript
   const incoming = parsePostBody(e);
   const payload = incoming && incoming.payload ? JSON.parse(incoming.payload) : incoming;
   if (payload.type === "payment_reminder_register") {
     try {
       return jsonResponse(registerPaymentReminder_(payload));
     } catch (error) {
       return jsonResponse({ok:false, message:String(error && error.message || error)});
     }
   }
   ```

   Keep the existing research-success relay and professional email workflow intact. Do not remove its secret validation. The reminder branch uses email double opt-in and does not use or expose the research relay secret.
4. In the existing `doGet(e)`, add this at the beginning:

   ```javascript
   const reminderResponse = handlePaymentReminderGet_(e);
   if (reminderResponse) return reminderResponse;
   ```

   Then leave the existing email-console page response unchanged.
5. Save and deploy a **new version** of the existing web app. It must execute as the project owner.
6. In `web/donation-config.js`, set `PAYMENT_REMINDER_URL` to the deployed web-app URL. This URL is public; never put the relay secret in the website.
7. In the Apps Script editor, select and run `installPaymentReminderTrigger_` once. Approve the requested Gmail and trigger permissions.

## Behaviour

- Minimum contribution: USD 10, converted to the visitor's display currency using a live indicative USD exchange rate.
- A split plan divides the total into the largest practical number of equal, separate payments while keeping each payment at or above USD 10. For example, USD 1,000 becomes 100 voluntary payments of USD 10.
- Each payment opens PayPal separately. SSSWET does not store payment credentials and does not automatically charge users.
- Reminder frequencies: weekly, monthly or yearly.
- Registration requires the user to confirm that the first payment has been made, then confirm their email address.
- The daily trigger sends reminders when due. Each email contains an unsubscribe link.
- Reminder subscriptions are stored in Apps Script Script Properties. The service does not read PayPal transactions, so it cannot verify instalments or stop automatically when a balance is paid. Users should unsubscribe after completing their plan.

## Privacy and operation

Only the email address, selected frequency, technology label and reminder-plan amounts are stored for this opt-in feature. Do not publish private credentials or relay secrets in this repository. Review applicable privacy and email rules before enabling the service for public use.
