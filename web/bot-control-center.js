(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const statusNode = $("bot-control-status");
  const metrics = $("bot-control-metrics");
  const current = $("bot-control-current");
  const agents = $("bot-control-agents");
  const tasksNode = $("bot-control-tasks");
  const taskTitle = $("bot-control-task-title");
  const lang = () => (document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const labels = () => lang() === "fr"
    ? {running:"Recherche autonome en cours",idle:"Aucun cycle autonome enregistré",completed:"Dernier cycle terminé",cycle:"Programmes terminés dans ce cycle",active:"Agents actuellement au travail",done:"Tâches de recherche terminées",blocked:"Tâches bloquées",review:"Résultats en attente de vérification",current:"Programme en cours",noCurrent:"Aucun programme en cours",agent:"Agent actif",recent:"Derniers agents ayant effectué un passage",none:"Aucune activité d’agent enregistrée",last:"Dernière activité",cycleDone:"Dernier cycle terminé",awaiting:"En attente de données du moteur local",notStarted:"Le worker autonome n’a pas encore publié son premier état.",updated:"Mise à jour",programme:"Programme",task:"Tâche",tasks:"Tâches de recherche récentes",taskComplete:"Recherche terminée · vérification requise",taskBlocked:"Bloquée · examen nécessaire",taskQueued:"En attente",taskActive:"En cours",taskRejected:"Rejetée",stale:"Dernier état ancien : vérifier le moteur local"}
    : {running:"Autonomous research is running",idle:"No autonomous cycle recorded",completed:"Latest cycle completed",cycle:"Programmes completed in this cycle",active:"Agents currently working",done:"Completed research tasks",blocked:"Blocked tasks",review:"Outputs awaiting verification",current:"Current programme",noCurrent:"No programme currently active",agent:"Active agent",recent:"Recent agents with recorded passes",none:"No agent activity recorded",last:"Last activity",cycleDone:"Last cycle completed",awaiting:"Waiting for local engine telemetry",notStarted:"The autonomous worker has not published its first state yet.",updated:"Updated",programme:"Programme",task:"Task",tasks:"Recent research tasks",taskComplete:"Research complete · verification required",taskBlocked:"Blocked · review needed",taskQueued:"Queued",taskActive:"In progress",taskRejected:"Rejected",stale:"Last heartbeat is old: check the local engine"};
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const time = (value) => { if (!value) return "—"; const date = new Date(value); return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString(lang() || "en"); };
  const pretty = (value) => String(value || "—").replace(/([a-z])([A-Z])/g,"$1 $2").replace(/[_-]+/g," ").replace(/^./,c=>c.toUpperCase());
  function metric(value,label){return '<div class="bot-control-metric"><strong>'+escape(value)+'</strong><span>'+escape(label)+'</span></div>';}
  async function load() {
    if (!metrics || !statusNode || typeof window.ssswetApiFetch !== "function") return;
    const t=labels();
    try {
      const response=await window.ssswetApiFetch("/api/bots");
      const data=await response.json();
      const worker=data.worker||{};
      const active=Array.isArray(data.active_agents)?data.active_agents:[];
      const recent=Array.isArray(data.recent_agents)?data.recent_agents:[];
      const running=worker.status==="running";
      const completed=worker.status==="cycle_completed";
      const stale=worker.updated_at && Date.now()-new Date(worker.updated_at).getTime()>90000 && running;
      statusNode.dataset.state=running&&!stale?"running":"idle";
      statusNode.textContent=stale?t.stale:(running?t.running:(completed?t.completed:(worker.status==="not_started"?t.notStarted:t.idle)));
      metrics.innerHTML=[
        metric((worker.completed_programmes||0)+" / "+(worker.total_programmes||32),t.cycle),
        metric(active.length,t.active),
        metric(data.completed_tasks||0,t.done),
        metric(data.pending_review_outputs||0,t.review),
        metric(data.blocked_tasks||0,t.blocked)
      ].join("");
      const currentTech=worker.current_technology?pretty(worker.current_technology):t.noCurrent;
      const cycleLine=completed?t.cycleDone+": "+time(worker.last_cycle_completed_at):t.updated+": "+time(worker.updated_at);
      current.innerHTML='<strong>'+escape(t.current)+':</strong> '+escape(currentTech)+'<br><span>'+escape(cycleLine)+'</span>';
      const activeCards=active.map(agent=>'<article class="bot-control-agent"><strong>'+escape(agent.id)+' · '+escape(agent.role)+'</strong><span>'+escape(t.programme)+': '+escape(pretty(worker.current_technology))+' · '+escape(t.task)+': '+escape(agent.task_id||worker.current_task_id||"—")+'</span></article>');
      const recentCards=recent.slice(0,8).map(agent=>'<article class="bot-control-agent"><strong>'+escape(agent.id)+' · '+escape(agent.role)+'</strong><span>'+escape(t.programme)+': '+escape(pretty(agent.technology))+' · '+escape(t.last)+': '+escape(time(agent.last_seen))+'</span></article>');
      if(taskTitle) taskTitle.textContent=t.tasks;
      const taskCards=(Array.isArray(data.recent_tasks)?data.recent_tasks:[]).slice(0,8).map(task=>{
        const state=task.status==="complete"?(task.review_required?t.taskComplete:(fr()?"Recherche terminée":"Research complete")):task.status==="blocked"?t.taskBlocked:task.status==="queued"?t.taskQueued:task.status==="active"?t.taskActive:t.taskRejected;
        return '<article class="bot-control-task"><strong>'+escape(pretty(task.domain))+'</strong><span>'+escape(task.objective)+'</span><small>'+escape(state)+'</small></article>';
      });
      if(tasksNode) tasksNode.innerHTML=taskCards.length?taskCards.join(""):'<p class="bot-control-status">'+escape(t.none)+'</p>';
      agents.innerHTML='<div class="bot-control-agent-list"><strong>'+escape(t.agent)+'</strong>'+ (activeCards.length?activeCards.join(""):'<p class="bot-control-status">'+escape(t.none)+'</p>')+'</div><div class="bot-control-agent-list"><strong>'+escape(t.recent)+'</strong>'+ (recentCards.length?recentCards.join(""):'<p class="bot-control-status">'+escape(t.none)+'</p>')+'</div>';
    } catch(error) {
      statusNode.dataset.state="offline";
      statusNode.textContent=t.awaiting+" · "+String(error.message||error);
    }
  }
  window.SSSWET_BOT_CONTROL={refresh:load};
  $("bot-control-refresh")?.addEventListener("click",load);
  window.addEventListener("ssswet-language-changed",load);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)load();});
  load();
  window.setInterval(()=>{if(!document.hidden)load();},3000);
})();