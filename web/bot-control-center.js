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
  const fr = () => lang() === "fr";
  const labels = () => fr()
    ? {running:"Réseau actif · recherche en cours",idle:"Moteur en attente · aucun travail actif",completed:"Dernier cycle de recherche terminé",cycle:"Programmes traités",active:"Agents au travail",done:"Tâches terminées",review:"À vérifier",blocked:"Tâches bloquées",current:"Programme en cours",noCurrent:"Aucun programme actuellement actif",agent:"Agents actuellement au travail",recent:"Derniers passages enregistrés",none:"Aucun agent actif pour le moment",last:"Dernière activité",cycleDone:"Dernier cycle terminé",awaiting:"En attente des données du moteur local",notStarted:"Le moteur autonome n’a pas encore publié son premier état.",updated:"Dernière mise à jour",programme:"Programme",task:"Tâche",tasks:"Dernières tâches de recherche",taskComplete:"Recherche terminée · vérification requise",taskBlocked:"Bloquée · examen nécessaire",taskQueued:"En attente",taskActive:"En cours",taskRejected:"Rejetée",stale:"Signal ancien · vérifier le moteur local",thinking:"Analyse en cours",recentLabel:"Dernier passage",offline:"Moteur local inaccessible",working:"TRAVAIL EN COURS",emptyTasks:"Aucune tâche récente enregistrée"}
    : {running:"Network active · research in progress",idle:"Engine idle · no active work",completed:"Latest research cycle completed",cycle:"Programmes processed",active:"Working agents",done:"Completed tasks",review:"Awaiting review",blocked:"Blocked tasks",current:"Current programme",noCurrent:"No programme currently active",agent:"Agents currently working",recent:"Latest recorded passes",none:"No active agents at this time",last:"Last activity",cycleDone:"Latest cycle completed",awaiting:"Waiting for local engine data",notStarted:"The autonomous worker has not published its first state yet.",updated:"Last update",programme:"Programme",task:"Task",tasks:"Latest research tasks",taskComplete:"Research complete · verification required",taskBlocked:"Blocked · review needed",taskQueued:"Queued",taskActive:"In progress",taskRejected:"Rejected",stale:"Stale signal · check the local engine",thinking:"Analysis in progress",recentLabel:"Latest pass",offline:"Local engine unavailable",working:"WORKING",emptyTasks:"No recent tasks recorded"};
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const time = (value) => { if (!value) return "—"; const date = new Date(value); return Number.isNaN(date.getTime()) ? "—" : date.toLocaleTimeString(lang() || "en",{hour:"2-digit",minute:"2-digit",second:"2-digit"}); };
  const pretty = (value) => String(value || "—").replace(/([a-z])([A-Z])/g,"$1 $2").replace(/[_-]+/g," ").replace(/^./,c=>c.toUpperCase());
  function metric(value,label){return '<div class="bot-control-metric"><strong>'+escape(value)+'</strong><span>'+escape(label)+'</span></div>';}
  function robot(index){return '<span class="agent-avatar agent-avatar-'+((index%3)+1)+'"><span class="agent-robot-head"><i></i><i></i></span><span class="agent-robot-body"></span></span>';}
  async function load() {
    if (!metrics || !statusNode || typeof window.ssswetApiFetch !== "function") return;
    const t=labels();
    try {
      const response=await window.ssswetApiFetch("/api/bots");
      if(!response.ok) throw new Error("HTTP "+response.status);
      const data=await response.json();
      const worker=data.worker||{};
      const active=Array.isArray(data.active_agents)?data.active_agents:[];
      const recent=Array.isArray(data.recent_agents)?data.recent_agents:[];
      const running=worker.status==="running";
      const completed=worker.status==="cycle_completed";
      const stale=!!(worker.updated_at && Date.now()-new Date(worker.updated_at).getTime()>90000 && running);
      statusNode.dataset.state=running&&!stale?"running":(stale?"stale":(completed?"completed":"idle"));
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
      const activeCards=active.map((agent,index)=>'<article class="bot-control-agent bot-control-agent-live">'+robot(index)+'<div class="bot-agent-copy"><strong>'+escape(agent.id)+' · '+escape(agent.role)+'</strong><span>'+escape(t.thinking)+' · '+escape(pretty(worker.current_technology))+'</span><small>'+escape(t.task)+': '+escape(agent.task_id||worker.current_task_id||"—")+'</small></div><i class="bot-agent-pulse" aria-hidden="true"></i></article>');
      const recentCards=recent.slice(0,5).map((agent,index)=>'<article class="bot-control-agent bot-control-agent-recent">'+robot(index)+'<div class="bot-agent-copy"><strong>'+escape(agent.id)+' · '+escape(agent.role)+'</strong><span>'+escape(t.recentLabel)+' · '+escape(pretty(agent.technology))+'</span><small>'+escape(t.last)+': '+escape(time(agent.last_seen))+'</small></div></article>');
      if(taskTitle) taskTitle.textContent=t.tasks;
      const taskCards=(Array.isArray(data.recent_tasks)?data.recent_tasks:[]).slice(0,4).map(task=>{
        const state=task.status==="complete"?(task.review_required?t.taskComplete:(fr()?"Recherche terminée":"Research complete")):task.status==="blocked"?t.taskBlocked:task.status==="queued"?t.taskQueued:task.status==="active"?t.taskActive:t.taskRejected;
        return '<article class="bot-control-task"><strong>'+escape(pretty(task.domain))+'</strong><span>'+escape(task.objective)+'</span><small>'+escape(state)+'</small></article>';
      });
      agents.innerHTML='<div class="bot-agent-group"><strong>'+escape(t.agent)+'</strong>'+(activeCards.length?activeCards.join(""):'<p class="bot-command-empty">'+escape(t.none)+'</p>')+'</div><div class="bot-agent-group"><strong>'+escape(t.recent)+'</strong>'+(recentCards.length?recentCards.join(""):'<p class="bot-command-empty">'+escape(t.none)+'</p>')+'</div>';
      if(tasksNode) tasksNode.innerHTML=taskCards.length?taskCards.join(""):'<p class="bot-command-empty">'+escape(t.emptyTasks)+'</p>';
    } catch(error) {
      statusNode.dataset.state="offline";
      statusNode.textContent=t.offline;
      current.innerHTML='<strong>'+escape(t.awaiting)+'</strong><br><span>'+escape(String(error.message||error))+'</span>';
      metrics.innerHTML="";
      agents.innerHTML='<p class="bot-command-empty">'+escape(t.awaiting)+'.</p>';
      if(tasksNode) tasksNode.innerHTML="";
    }
  }
  window.SSSWET_BOT_CONTROL={refresh:load};
  $("bot-control-refresh")?.addEventListener("click",load);
  window.addEventListener("ssswet-language-changed",load);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)load();});
  load();
  window.setInterval(()=>{if(!document.hidden)load();},3000);
})();