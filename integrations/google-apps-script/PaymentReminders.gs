/*
 * SSSWET voluntary payment reminders for Google Apps Script.
 *
 * This module is intentionally separate from the public website. It stores only
 * email addresses submitted by users who explicitly request reminders.
 * Every subscription requires email confirmation. Payments are never automatic.
 *
 * Integration instructions: integrations/google-apps-script/README.md
 */

const SSSWET_REMINDER_PREFIX = "SSSWET_PAYMENT_REMINDER_";
const SSSWET_REMINDER_PAYPAL = "https://www.paypal.com/paypalme/gudjencio";

function registerPaymentReminder_(payload) {
  const email = String(payload.email || "").trim().toLowerCase();
  const frequency = String(payload.frequency || "");
  const language = String(payload.language || "en").toLowerCase().startsWith("fr") ? "fr" : "en";
  const technology = String(payload.technology || "SSSWET").slice(0, 100);
  const totalUsd = Number(payload.total_usd);
  const installments = Math.floor(Number(payload.installments));
  const installmentUsd = Number(payload.installment_usd);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error("Invalid email address.");
  if (!["weekly", "monthly", "yearly"].includes(frequency)) throw new Error("Invalid reminder frequency.");
  if (payload.first_payment_confirmed !== true) throw new Error("The first payment must be confirmed by the user.");
  if (!Number.isFinite(totalUsd) || totalUsd < 10 || !Number.isInteger(installments) || installments < 1) throw new Error("Invalid instalment plan.");
  if (!Number.isFinite(installmentUsd) || installmentUsd < 10) throw new Error("Each payment must be at least USD 10.");

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const properties = PropertiesService.getScriptProperties();
    const token = Utilities.getUuid().replace(/-/g, "") + Utilities.getUuid().replace(/-/g, "");
    const record = {
      token: token,
      email: email,
      frequency: frequency,
      language: language,
      technology: technology,
      totalUsd: Number(totalUsd.toFixed(2)),
      installments: installments,
      installmentUsd: Number(installmentUsd.toFixed(2)),
      status: "pending",
      createdAt: new Date().toISOString(),
      nextReminderAt: null
    };
    properties.setProperty(SSSWET_REMINDER_PREFIX + token, JSON.stringify(record));
    const confirmationUrl = ScriptApp.getService().getUrl() + "?reminder_token=" + encodeURIComponent(token);
    const subject = language === "fr" ? "Confirmez vos rappels de paiement SSSWET" : "Confirm your SSSWET payment reminders";
    const body = language === "fr"
      ? "Vous avez demandé des rappels volontaires pour votre prochain paiement SSSWET.\n\nConfirmez votre inscription : " + confirmationUrl + "\n\nAucun prélèvement automatique ne sera effectué. Vous pouvez vous désinscrire depuis chaque e-mail de rappel."
      : "You requested voluntary reminders for your next SSSWET payment.\n\nConfirm your subscription: " + confirmationUrl + "\n\nNo automatic charge will be made. You can unsubscribe from every reminder email.";
    GmailApp.sendEmail(email, subject, body, {name: "SSSWET"});
    return {ok: true, pending: true};
  } finally {
    lock.releaseLock();
  }
}

function handlePaymentReminderGet_(e) {
  const parameters = (e && e.parameter) || {};
  if (parameters.reminder_token) {
    const result = confirmPaymentReminder_(String(parameters.reminder_token));
    return HtmlService.createHtmlOutput(result.fr
      ? "<h2>Inscription confirmée</h2><p>Les rappels volontaires SSSWET sont activés. Aucun paiement automatique ne sera effectué.</p>"
      : "<h2>Subscription confirmed</h2><p>Your voluntary SSSWET reminders are active. No automatic payment will be made.</p>");
  }
  if (parameters.unsubscribe_token) {
    const result = unsubscribePaymentReminder_(String(parameters.unsubscribe_token));
    return HtmlService.createHtmlOutput(result.fr
      ? "<h2>Désinscription effectuée</h2><p>Vous ne recevrez plus ces rappels.</p>"
      : "<h2>Unsubscribed</h2><p>You will no longer receive these reminders.</p>");
  }
  return null;
}

function confirmPaymentReminder_(token) {
  return updatePaymentReminder_(token, function(record) {
    record.status = "active";
    record.nextReminderAt = nextPaymentReminderDate_(new Date(), record.frequency).toISOString();
  });
}

function unsubscribePaymentReminder_(token) {
  return updatePaymentReminder_(token, function(record) {
    record.status = "unsubscribed";
  });
}

function updatePaymentReminder_(token, update) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const properties = PropertiesService.getScriptProperties();
    const key = SSSWET_REMINDER_PREFIX + token;
    const stored = properties.getProperty(key);
    if (!stored) throw new Error("Reminder subscription not found.");
    const record = JSON.parse(stored);
    update(record);
    properties.setProperty(key, JSON.stringify(record));
    return {fr: record.language === "fr"};
  } finally {
    lock.releaseLock();
  }
}

function nextPaymentReminderDate_(from, frequency) {
  const date = new Date(from.getTime());
  if (frequency === "weekly") date.setDate(date.getDate() + 7);
  else if (frequency === "monthly") date.setMonth(date.getMonth() + 1);
  else date.setFullYear(date.getFullYear() + 1);
  return date;
}

function sendDuePaymentReminders_() {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const properties = PropertiesService.getScriptProperties();
    const stored = properties.getProperties();
    const now = new Date();
    Object.keys(stored).filter(function(key) {
      return key.indexOf(SSSWET_REMINDER_PREFIX) === 0;
    }).forEach(function(key) {
      const record = JSON.parse(stored[key]);
      if (record.status !== "active" || !record.nextReminderAt || new Date(record.nextReminderAt) > now) return;
      const fr = record.language === "fr";
      const amount = Number(record.installmentUsd || 10).toFixed(2);
      const payUrl = SSSWET_REMINDER_PAYPAL + "/" + amount + "USD";
      const unsubscribeUrl = ScriptApp.getService().getUrl() + "?unsubscribe_token=" + encodeURIComponent(record.token);
      const subject = fr ? "Rappel volontaire de paiement SSSWET" : "SSSWET voluntary payment reminder";
      const body = fr
        ? "Ceci est le rappel que vous avez demandé pour votre prochaine contribution à " + record.technology + ".\\n\\nMontant indicatif de la prochaine échéance : " + amount + " USD.\\nEffectuer le paiement volontaire : " + payUrl + "\\n\\nAucun prélèvement automatique n'est effectué. Après votre paiement, vous pouvez conserver ce calendrier ou vous désinscrire : " + unsubscribeUrl
        : "This is the reminder you requested for your next contribution to " + record.technology + ".\\n\\nIndicative next instalment: USD " + amount + ".\\nMake the voluntary payment: " + payUrl + "\\n\\nNo automatic charge is made. After payment, you may keep this schedule or unsubscribe: " + unsubscribeUrl;
      GmailApp.sendEmail(record.email, subject, body, {name: "SSSWET"});
      record.nextReminderAt = nextPaymentReminderDate_(now, record.frequency).toISOString();
      properties.setProperty(key, JSON.stringify(record));
    });
  } finally {
    lock.releaseLock();
  }
}

function installPaymentReminderTrigger_() {
  const exists = ScriptApp.getProjectTriggers().some(function(trigger) {
    return trigger.getHandlerFunction() === "sendDuePaymentReminders_";
  });
  if (!exists) {
    ScriptApp.newTrigger("sendDuePaymentReminders_").timeBased().everyDays(1).atHour(9).create();
  }
}
