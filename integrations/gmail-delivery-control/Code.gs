/**
 * SSSWET Gmail delivery and institutional-outreach helper.
 * Deploy as a private web app: Execute as Me; access Only myself.
 * Never publish the deployment URL. Emails are never sent automatically.
 * A verified delivery thread is moved to Gmail Trash, not permanently erased.
 */
const SSSWET_CONFIG = Object.freeze({
  OWNER_EMAIL: "ssswetindustries@gmail.com",
  COMPLETED_LABEL: "SSSWET/Delivery-Complete",
  MAX_THREADS: 40,
  ARCHIVE_CONFIRMATION: "PAYMENT_AND_DELIVERY_VERIFIED"
});

function doGet() {
  assertOwner_();
  return HtmlService.createHtmlOutputFromFile("index")
    .setTitle("SSSWET — Private Gmail delivery control")
    .addMetaTag("viewport", "width=device-width, initial-scale=1");
}

function getDeliveryThreads() {
  assertOwner_();
  const label = GmailApp.getUserLabelByName(SSSWET_CONFIG.COMPLETED_LABEL);
  if (!label) return {label: SSSWET_CONFIG.COMPLETED_LABEL, needsLabel: true, threads: []};
  return {
    label: SSSWET_CONFIG.COMPLETED_LABEL,
    needsLabel: false,
    threads: label.getThreads(0, SSSWET_CONFIG.MAX_THREADS).map(function(thread) {
      const messages = thread.getMessages();
      const latest = messages[messages.length - 1];
      return {id:thread.getId(),subject:latest.getSubject(),from:latest.getFrom(),
        date:latest.getDate().toISOString(),messageCount:messages.length,
        snippet:latest.getPlainBody().slice(0,180).replace(/\s+/g," ")};
    })
  };
}

function moveVerifiedDeliveryToTrash(threadId, confirmationPhrase) {
  assertOwner_();
  if (confirmationPhrase !== SSSWET_CONFIG.ARCHIVE_CONFIRMATION) throw new Error("Explicit payment-and-delivery confirmation is required.");
  if (typeof threadId !== "string" || !/^[A-Za-z0-9_-]{8,80}$/.test(threadId)) throw new Error("Invalid Gmail thread identifier.");
  const thread = GmailApp.getThreadById(threadId);
  if (!thread || thread.isInTrash()) throw new Error("Thread not found or already in Trash.");
  const requiredLabel = GmailApp.getUserLabelByName(SSSWET_CONFIG.COMPLETED_LABEL);
  if (!requiredLabel || !thread.getLabels().some(label => label.getName() === SSSWET_CONFIG.COMPLETED_LABEL)) {
    throw new Error("Apply the required Gmail label only after manual review.");
  }
  const latest = thread.getMessages().slice(-1)[0];
  PropertiesService.getScriptProperties().setProperty("SSSWET_DELIVERY_ARCHIVE_"+thread.getId(),JSON.stringify({
    threadId:thread.getId(),subject:latest.getSubject().slice(0,180),verifiedAt:new Date().toISOString(),
    action:"moved_to_trash_after_manual_payment_and_delivery_confirmation"
  }));
  thread.moveToTrash();
  return {ok:true,message:"Thread moved to Gmail Trash. It was not permanently erased."};
}

function createInstitutionalDraft(form) {
  assertOwner_();
  if (!form || typeof form !== "object") throw new Error("Draft details are required.");
  const recipient=String(form.recipient||"").trim(),organization=String(form.organization||"").trim();
  const technology=String(form.technology||"").trim(),objective=String(form.objective||"").trim();
  const details=String(form.details||"").trim(),startingPoint=String(form.startingPoint||"").trim();
  const subject=String(form.subject||"").trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)) throw new Error("Enter a valid institutional email address.");
  if (![organization,technology,objective,details,startingPoint].every(Boolean)) throw new Error("Complete all required project and request details.");
  if ([subject,organization,technology,objective,details,startingPoint].some(value=>value.length>6000)) throw new Error("A field is too long.");
  const body=[
    "Dear "+organization+" team,","",
    "I am contacting you on behalf of SSSWET (Super Soldier's Space Warping Engineering & Tech), an independent research-software and technology-research initiative. The French interface name is ETDESS.","",
    "TECHNOLOGY AREA",technology,"","REQUEST AND OBJECTIVE",objective,"",
    "PROJECT CONTEXT, EVIDENCE AND LIMITATIONS",details,"",
    "PROPOSED FIRST STEPS",startingPoint,"",
    "We would appreciate guidance on the most appropriate lawful and technically responsible route to begin: relevant scientific or technical standards, competent authorities, institutional partners, feasibility studies, required permits, safety and ethics reviews, and restrictions that should be addressed before work proceeds.","",
    "We do not assume that the proposed technology is currently feasible or available. We intend to distinguish published evidence, hypotheses, simulations, prototypes and independently reviewed results, and to comply with applicable law and qualified oversight.","",
    "If this request falls outside your remit, we would be grateful for a referral to the appropriate department or organization.","",
    "Kind regards,","SSSWET Project Team","ssswetindustries@gmail.com",
    "https://gudjencio.github.io/SSSWET/","https://sites.google.com/view/ssswet"
  ].join("\n");
  const draft=GmailApp.createDraft(recipient,subject||"Request for guidance on lawful research and feasibility — SSSWET",body);
  return {ok:true,draftId:draft.getId(),message:"Draft created in Gmail. It has not been sent."};
}

function assertOwner_() {
  const effective=String(Session.getEffectiveUser().getEmail()||"").toLowerCase();
  const active=String(Session.getActiveUser().getEmail()||"").toLowerCase();
  const owner=SSSWET_CONFIG.OWNER_EMAIL.toLowerCase();
  if(effective!==owner||(active&&active!==owner)) throw new Error("Access denied. This private tool is restricted to the project Gmail account.");
}