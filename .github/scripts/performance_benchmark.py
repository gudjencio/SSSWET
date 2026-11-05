#!/usr/bin/env python3
"""Repeatable, advisory browser performance measurements for the SSSWET web UI."""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

OBSERVER_INIT = r"""
(() => {
  window.__ssswetBench = { lcp: null, cls: 0, longTasks: [], layoutShifts: [] };
  try {
    new PerformanceObserver(list => {
      for (const entry of list.getEntries()) window.__ssswetBench.lcp = entry.startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (_) {}
  try {
    new PerformanceObserver(list => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) window.__ssswetBench.cls += entry.value;
        window.__ssswetBench.layoutShifts.push({
          value: entry.value,
          startTime: entry.startTime,
          sources: (entry.sources || []).slice(0, 5).map(source => ({
            node: source.node ? {
              tag: source.node.tagName || source.node.nodeName,
              id: source.node.id || null,
              class_name: typeof source.node.className === 'string' ? source.node.className : null
            } : null,
            previous_rect: source.previousRect ? {
              x: source.previousRect.x, y: source.previousRect.y,
              width: source.previousRect.width, height: source.previousRect.height
            } : null,
            current_rect: source.currentRect ? {
              x: source.currentRect.x, y: source.currentRect.y,
              width: source.currentRect.width, height: source.currentRect.height
            } : null
          }))
        });
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (_) {}
  try {
    new PerformanceObserver(list => {
      for (const entry of list.getEntries()) {
        window.__ssswetBench.longTasks.push({ duration: entry.duration, startTime: entry.startTime });
      }
    }).observe({ type: 'longtask', buffered: true });
  } catch (_) {}
})();
"""

def page_metrics(page: object) -> dict:
    return page.evaluate("""() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const paint = Object.fromEntries(performance.getEntriesByType('paint').map(e => [e.name, e.startTime]));
      const bench = window.__ssswetBench || {};
      const cards = document.querySelectorAll('#technology-grid .technology-card').length;
      const rect = selector => {
        const element = document.querySelector(selector);
        if (!element) return null;
        const box = element.getBoundingClientRect();
        return { x: box.x, y: box.y, width: box.width, height: box.height };
      };
      const geometry = {
        topbar: rect('.app-shell > .topbar'),
        language_control: rect('.app-shell > .topbar .language-control'),
        language_select: rect('#language'),
        action_links: rect('.top-action-links'),
        repair_slot: rect('.repair-project-slot'),
        repair_button: rect('.repair-project-button'),
        report_button: rect('#ssswet-report-button'),
        virtual_time_travel: rect('#virtual-time-travel-launch'),
        current_research_title: rect('#bot-current-technology-title'),
        command_hero: rect('.bot-command-hero'),
        command_visual: rect('.bot-command-visual')
      };
      const languageHeight = geometry.language_select?.height ?? null;
      const topbarHeight = geometry.topbar?.height ?? null;
      const expectedTopbarHeight = window.matchMedia('(max-width: 600px)').matches ? 52 : 56;
      const layoutChecks = {
        language_select_height: languageHeight !== null && Math.abs(languageHeight - 42) <= 1,
        topbar_height: topbarHeight !== null && Math.abs(topbarHeight - expectedTopbarHeight) <= 1,
        no_horizontal_overflow: document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1,
        repair_slot_height: Math.abs((geometry.repair_slot?.height ?? 0) - 44) <= 1,
        report_button_height: Math.abs((geometry.report_button?.height ?? 0) - 44) <= 1
      };
      return {
        navigation: nav ? {
          dns_ms: nav.domainLookupEnd - nav.domainLookupStart,
          connect_ms: nav.connectEnd - nav.connectStart,
          response_ms: nav.responseStart - nav.requestStart,
          dom_content_loaded_ms: nav.domContentLoadedEventEnd,
          load_event_ms: nav.loadEventEnd,
          transfer_bytes: nav.transferSize
        } : {},
        fcp_ms: paint['first-contentful-paint'] ?? null,
        lcp_ms: bench.lcp ?? null,
        cls: bench.cls ?? null,
        long_task_count: (bench.longTasks || []).length,
        long_task_total_ms: (bench.longTasks || []).reduce((n, x) => n + x.duration, 0),
        long_task_max_ms: Math.max(0, ...(bench.longTasks || []).map(x => x.duration)),
        layout_shift_count: (bench.layoutShifts || []).length,
        layout_shift_diagnostics: (bench.layoutShifts || []).slice(0, 10),
        dom_node_count: document.getElementsByTagName('*').length,
        catalogue_card_count: cards,
        document_ready_state: document.readyState,
        layout_geometry: geometry,
        layout_checks: layoutChecks
      };
    }""")

def catalogue_scale(page: object, sizes: list[int]) -> list[dict]:
    return page.evaluate("""async sizes => {
      const grid = document.querySelector('#technology-grid');
      const template = grid && grid.querySelector('.technology-card');
      if (!grid || !template) return sizes.map(size => ({ cards: size, supported: false }));
      const results = [];
      for (const size of sizes) {
        const fragment = document.createDocumentFragment();
        for (let i = 0; i < size; i++) {
          const card = template.cloneNode(true);
          card.dataset.benchmarkFixture = 'true';
          fragment.appendChild(card);
        }
        const start = performance.now();
        grid.appendChild(fragment);
        const appendMs = performance.now() - start;
        const layoutStart = performance.now();
        void grid.getBoundingClientRect().height;
        const layoutReadMs = performance.now() - layoutStart;
        const frameStart = performance.now();
        await new Promise(resolve => requestAnimationFrame(resolve));
        const nextFrameMs = performance.now() - frameStart;
        results.push({
          cards: size,
          append_ms: appendMs,
          layout_read_ms: layoutReadMs,
          next_frame_ms: nextFrameMs
        });
        grid.querySelectorAll('[data-benchmark-fixture="true"]').forEach(node => node.remove());
        await new Promise(resolve => requestAnimationFrame(resolve));
      }
      return results;
    }""", sizes)

def run_trial(browser: object, url: str, viewport: dict, trial: int) -> dict:
    context = browser.new_context(viewport=viewport, device_scale_factor=1)
    page = context.new_page()
    page.add_init_script(OBSERVER_INIT)
    started = time.perf_counter()
    response = page.goto(url, wait_until="load", timeout=90000)
    cold_navigation_wait_ms = round((time.perf_counter() - started) * 1000, 2)
    page.wait_for_timeout(1800)
    cold = page_metrics(page)
    cold["http_status"] = response.status if response else None
    cold["navigation_wait_ms"] = cold_navigation_wait_ms
    cold["settle_observation_ms"] = 1800
    scales = catalogue_scale(page, [100, 500, 1000])
    locale_layouts = []
    # Synthetic translated-copy stress scenarios avoid triggering live-engine
    # refreshes while checking longer labels and both writing directions.
    locale_scenarios = [
        {
            "locale": "fr", "direction": "ltr",
            "fund": "Soutenir les programmes de recherche et les technologies",
            "repair": "Réparer le projet si son interface ne fonctionne plus",
            "report": "Signaler", "virtual": "Explorer notre cartographie virtuelle du temps"
        },
        {
            "locale": "de", "direction": "ltr",
            "fund": "Forschungsprogramme und Technologien unterstützen",
            "repair": "Projektoberfläche bei Problemen wiederherstellen",
            "report": "Melden", "virtual": "Virtuelle Zeitreise-Kartierung erkunden"
        },
        {
            "locale": "ar", "direction": "rtl",
            "fund": "ادعم برامج البحث والتقنيات",
            "repair": "إصلاح واجهة المشروع عند حدوث مشكلة",
            "report": "إبلاغ", "virtual": "استكشف الخرائط الافتراضية للسفر عبر الزمن"
        },
        {
            "locale": "ja", "direction": "ltr",
            "fund": "研究プログラムと技術を支援する",
            "repair": "問題が発生した場合にプロジェクトを修復",
            "report": "報告", "virtual": "仮想タイムトラベルマッピングを探索"
        }
    ]
    for scenario in locale_scenarios:
        page.evaluate(
            """spec => {
                document.documentElement.lang = spec.locale;
                document.documentElement.dir = spec.direction;
                document.body.dir = spec.direction;
                const setText = (selector, value) => {
                    const element = document.querySelector(selector);
                    if (element) element.textContent = value;
                };
                setText('#fund-techs-button', spec.fund);
                setText('.repair-project-button', spec.repair);
                setText('#ssswet-report-button', spec.report);
                setText('#virtual-time-travel-launch', spec.virtual);
            }""",
            scenario
        )
        page.wait_for_timeout(150)
        locale_metrics = page_metrics(page)
        locale_layouts.append({
            "locale_scenario": scenario["locale"],
            "direction": scenario["direction"],
            "synthetic_copy": True,
            "layout_checks": locale_metrics["layout_checks"],
            "layout_geometry": locale_metrics["layout_geometry"],
            "cls_after_copy_change": locale_metrics["cls"]
        })
    page.wait_for_timeout(100)
    # A second navigation in the same context provides a warm-cache observation.
    warm_started = time.perf_counter()
    page.reload(wait_until="load", timeout=90000)
    warm_navigation_wait_ms = round((time.perf_counter() - warm_started) * 1000, 2)
    page.wait_for_timeout(1200)
    warm = page_metrics(page)
    warm["navigation_wait_ms"] = warm_navigation_wait_ms
    warm["settle_observation_ms"] = 1200
    context.close()
    return {"trial": trial, "viewport": viewport, "cold": cold, "warm": warm, "catalogue_scale": scales, "locale_layouts": locale_layouts}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("SSSWET_BENCH_URL", "http://127.0.0.1:8765/"))
    parser.add_argument("--output", default="performance-results/benchmark.json")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()
    if args.trials < 1 or args.trials > 10:
        parser.error("--trials must be between 1 and 10")

    viewports = [
        {"name": "desktop", "width": 1440, "height": 900},
        {"name": "mobile", "width": 390, "height": 844},
    ]
    results = {
        "schema_version": 2,
        "project": "SSSWET",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "browser": "Chromium (Playwright)",
            "ci": os.environ.get("GITHUB_ACTIONS") == "true",
            "commit": os.environ.get("GITHUB_SHA"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
        },
        "method": {
            "trials_per_viewport": args.trials,
            "cache": "cold first navigation and warm reload in the same browser context",
            "catalogue_scale": "100, 500 and 1000 cloned cards appended to the live catalogue, then removed",
            "limitations": [
                "CI virtual hardware is not a physical low-end phone or desktop.",
                "Synthetic catalogue scaling is a stress probe, not a user-experience score.",
                "LCP is sampled after a fixed settling interval and may differ from field data.",
                "No pass/fail performance threshold is imposed until stable baselines exist."
            ]
        },
        "trials": []
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for viewport in viewports:
            for trial in range(1, args.trials + 1):
                results["trials"].append(run_trial(browser, args.url, viewport, trial))
        browser.close()

    for viewport in viewports:
        group = [item for item in results["trials"] if item["viewport"]["name"] == viewport["name"]]
        for mode in ("cold", "warm"):
            for metric in ("navigation_wait_ms", "fcp_ms", "lcp_ms", "cls", "long_task_total_ms", "dom_node_count"):
                values = [item[mode].get(metric) for item in group if isinstance(item[mode].get(metric), (int, float))]
                if values:
                    results.setdefault("summary", {}).setdefault(viewport["name"], {}).setdefault(mode, {})[metric] = {
                        "median": round(statistics.median(values), 3),
                        "min": round(min(values), 3),
                        "max": round(max(values), 3)
                    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "trials": len(results["trials"]), "summary": results.get("summary", {})}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
