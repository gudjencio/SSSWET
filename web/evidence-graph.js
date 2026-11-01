(() => {
  "use strict";

  const get = (path) => fetch(path, { headers: { Accept: "application/json" }, cache: "no-store" }).then((r) => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  });

  const root = document.getElementById("evidence-graph");
  const status = document.getElementById("evidence-graph-status");
  if (!root || !status) return;

  const t = () => {
    const fr = document.documentElement.lang === "fr";
    return {
      unavailable: fr ? "Le graphe des preuves est momentanément indisponible." : "The evidence graph is temporarily unavailable.",
      empty: fr ? "Aucun lien de preuve enregistré pour ce dossier." : "No evidence links are recorded for this dossier.",
      source: fr ? "Source" : "Source",
      protocol: fr ? "Protocole" : "Protocol",
      dataset: fr ? "Donnée" : "Dataset",
      run: fr ? "Exécution" : "Run",
      comparison: fr ? "Reproduction" : "Reproduction",
      objection: fr ? "Objection" : "Objection",
      review: fr ? "Revue" : "Review",
      dispute: fr ? "Litige" : "Dispute",
      event: fr ? "Événement" : "Event",
      state: fr ? "État des preuves" : "Evidence state",
      center: fr ? "Dossier" : "Dossier",
      legend: fr ? "Légende" : "Legend",
      trace: fr ? "Relations enregistrées uniquement" : "Recorded relationships only",
      noInference: fr ? "Le graphe ne déduit pas de relations absentes des enregistrements." : "The graph does not infer relationships missing from the records."
    };
  };

  const palette = {
    source: "#8d8d8d", protocol: "#b7a06a", dataset: "#7e9b9b", run: "#8b7eaa",
    comparison: "#9a8c67", objection: "#a56f6f", review: "#718e71", dispute: "#9a7777",
    event: "#777", state: "#c6a978", center: "#e5e5e5"
  };

  function text(value) { return value == null || value === "" ? "—" : String(value); }

  function typeFor(item) {
    const kind = String(item.kind || item.type || "event").toLowerCase();
    return Object.prototype.hasOwnProperty.call(palette, kind) ? kind : "event";
  }

  function buildNodes(dossier) {
    const nodes = [{ id: "dossier", label: text(dossier.title || dossier.dossier_id), type: "center" }];
    const add = (items, type, idKey, labelKey) => {
      if (!Array.isArray(items)) return;
      items.forEach((item, index) => {
        const id = type + ":" + text(item[idKey] || index);
        nodes.push({ id, label: text(item[labelKey] || item[idKey] || id), type });
      });
    };
    add(dossier.sources, "source", "source_id", "title");
    add(dossier.protocols, "protocol", "protocol_id", "version");
    add(dossier.datasets, "dataset", "dataset_id", "version");
    add(dossier.runs, "run", "run_id", "status");
    add(dossier.comparisons, "comparison", "comparison_id", "status");
    add(dossier.objections, "objection", "id", "summary");
    add(dossier.disputes, "dispute", "case_id", "status");
    add((dossier.events || []).filter((event) => event.kind === "review"), "review", "event_id", "decision");
    return nodes;
  }

  function buildEdges(dossier, nodes) {
    const edges = [];
    const has = (id) => nodes.some((node) => node.id === id);
    const link = (a, b) => { if (has(a) && has(b)) edges.push([a, b]); };
    const dossierId = "dossier";

    nodes.filter((node) => node.id !== dossierId).forEach((node) => link(dossierId, node.id));

    (dossier.runs || []).forEach((run) => {
      const runId = "run:" + text(run.run_id);
      if (run.protocol_id) link("protocol:" + text(run.protocol_id), runId);
      if (run.dataset_id) link("dataset:" + text(run.dataset_id), runId);
    });
    (dossier.comparisons || []).forEach((comparison) => {
      const id = "comparison:" + text(comparison.comparison_id);
      if (comparison.reference_run_id) link("run:" + text(comparison.reference_run_id), id);
      if (comparison.candidate_run_id) link("run:" + text(comparison.candidate_run_id), id);
    });
    return edges;
  }

  function render(dossier) {
    const labels = t();
    root.replaceChildren();
    const nodes = buildNodes(dossier);
    const edges = buildEdges(dossier, nodes);
    if (nodes.length <= 1) {
      const empty = document.createElement("p"); empty.className = "visual-empty"; empty.textContent = labels.empty; root.append(empty); return;
    }

    const width = 760;
    const height = Math.max(280, Math.min(620, 150 + nodes.length * 24));
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", labels.trace);
    svg.classList.add("evidence-graph-svg");

    const positions = new Map();
    const center = { x: width / 2, y: height / 2 };
    positions.set("dossier", center);
    const peripheral = nodes.filter((node) => node.id !== "dossier");
    peripheral.forEach((node, index) => {
      const angle = (-Math.PI / 2) + (index / peripheral.length) * Math.PI * 2;
      const radius = Math.min(width, height) * 0.35;
      positions.set(node.id, { x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius });
    });

    edges.forEach(([a, b]) => {
      const pa = positions.get(a), pb = positions.get(b);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", pa.x); line.setAttribute("y1", pa.y); line.setAttribute("x2", pb.x); line.setAttribute("y2", pb.y);
      line.classList.add("evidence-graph-edge"); svg.append(line);
    });

    nodes.forEach((node) => {
      const p = positions.get(node.id);
      const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
      group.classList.add("evidence-graph-node");
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", p.x); circle.setAttribute("cy", p.y); circle.setAttribute("r", node.type === "center" ? 24 : 13);
      circle.setAttribute("fill", palette[node.type]); circle.setAttribute("fill-opacity", node.type === "center" ? ".22" : ".14");
      circle.setAttribute("stroke", palette[node.type]);
      group.append(circle);
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", p.x); label.setAttribute("y", p.y + (node.type === "center" ? 40 : 29));
      label.setAttribute("text-anchor", "middle"); label.textContent = node.label.slice(0, 28);
      group.append(label);
      group.setAttribute("tabindex", "0");
      group.setAttribute("role", "button");
      group.setAttribute("aria-label", node.label);
      svg.append(group);
    });

    root.append(svg);
    const legend = document.createElement("div"); legend.className = "evidence-graph-legend";
    const types = ["source", "protocol", "dataset", "run", "comparison", "objection", "review", "dispute", "state"];
    types.forEach((type) => { const item = document.createElement("span"); item.textContent = labels[type]; item.style.setProperty("--evidence-node-color", palette[type]); legend.append(item); });
    root.append(legend);
    const note = document.createElement("p"); note.className = "evidence-graph-note"; note.textContent = labels.noInference; root.append(note);
  }

  window.addEventListener("ssswet-evidence-dossier", (event) => { if (event.detail) render(event.detail); });
  window.SSSWETRenderEvidenceGraph = render;
  status.textContent = t().trace;
})();
