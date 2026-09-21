---
name: web-performance-review
description: Comprehensive runbook for conducting deep web performance audits, diagnosing slow websites, JavaScript execution, DOM rendering bottlenecks, and modern framework overhead (Vue.js / Nuxt.js) using Chrome DevTools Protocol (CDP) tooling and handling authenticated pages. Use when profiling slow pages, auditing Core Web Vitals, investigating Long Tasks, analyzing heap snapshots, or profiling authenticated dashboards and SPAs.
---

# Web Performance Review & Profiling with CDP

A systematic, evidence-based guide for conducting comprehensive web performance reviews using the **Chrome DevTools Protocol (CDP)** and the `chrome-devtools` MCP tooling suite.

This skill equips agents to diagnose macro page speed, isolate JavaScript execution bottlenecks, uncover DOM layout thrashing, audit modern reactive framework overhead (Vue.js / Nuxt.js), and successfully profile **authenticated dashboards and gated SPAs**.

---

## 🗺️ The 4-Tier Performance Architecture

Every performance investigation follows this top-down triage pipeline:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGE 0: AUTHENTICATION SETUP                      │
│     Inject Cookies / Web Storage / Headers OR Attach to Active Session  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                     TIER 1: MACRO WEBSITE REVIEW                        │
│   Network Waterfall • Server TTFB • Critical Rendering Path • CWV       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌─────────────────────────────────────┐   ┌───────────────────────────────┐
│   TIER 2: JAVASCRIPT COMPUTATION    │   │    TIER 3: DOM & RENDERING    │
│  • Long Tasks (> 50ms) / INP        │   │  • Layout Thrashing (Reflow)  │
│  • V8 Parse & Compile Cost          │   │  • Excessive DOM Tree Nodes   │
│  • GC Spikes & Heap Memory Leaks    │   │  • Paint Storms & Layer Drops │
└──────────────────┬──────────────────┘   └───────────────┬───────────────┘
                   │                                      │
                   └──────────────────┬───────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────────────────┐
│               TIER 4: MODERN REACTIVE FRAMEWORKS & SSR                  │
│  • Vue 3 Deep Proxy Overhead vs shallowRef • Nuxt SSR Hydration Pause   │
│  • __NUXT_DATA__ Payload Bloat • Duplicate Universal $fetch Invocations │
│  • Virtual DOM List Re-diffing (v-memo) • Composition API Memory Leaks  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ CDP Tooling Matrix & Capabilities

The review relies on both high-level MCP tools and low-level CDP domains:

| Diagnostic Need | High-Level Tool (`chrome-devtools`) | Low-Level CDP Domain & Command |
| :--- | :--- | :--- |
| **Trace Recording** | `performance_start_trace`, `performance_stop_trace` | `Tracing.start`, `Tracing.end` |
| **Trace Insights** | `performance_analyze_insight` | Built-in DevTools Trace Engine models |
| **CPU / Network Throttling** | `emulate(cpuThrottlingRate: 4)` | `Emulation.setCPUThrottlingRate`, `Network.emulateNetworkConditions` |
| **Auth & Header Injection** | `evaluate_script` / CDP Client | `Network.setCookies`, `Network.setExtraHTTPHeaders` |
| **Early Script Evaluation** | CDP Client | `Page.addScriptToEvaluateOnNewDocument` |
| **Memory & Heap Profiling** | `take_heapsnapshot` | `HeapProfiler.takeHeapSnapshot`, `HeapProfiler.enable` |
| **Network Waterfall** | `list_network_requests`, `get_network_request` | `Network.enable`, `Network.responseReceived` |
| **Visual Invalidation** | DevTools Rendering Settings | `Overlay.setShowPaintRects`, `Overlay.setShowLayoutShiftRegions` |

---

## 🔐 Working Around Authenticated Pages & Gated SPAs

Standard synthetic tools fail on authenticated apps because hard reloads spawn clean incognito sessions, instantly redirecting to `/login`.

Follow these four patterns (detailed in [references/auth-workarounds.md](references/auth-workarounds.md)):

### 1. Pre-Navigation Cookie & Header Injection
Before issuing `navigate_page` or starting a trace, set the required session cookies and headers:
- Use CDP `Network.setCookies` for `HttpOnly` session IDs.
- Use CDP `Network.setExtraHTTPHeaders` for `Authorization: Bearer <token>`.

### 2. Early `localStorage` Injection
In SPAs checking auth before mounting routes, injecting tokens via `evaluate_script` after navigation is too late. Use CDP `Page.addScriptToEvaluateOnNewDocument`:
```javascript
localStorage.setItem('auth_token', 'Bearer eyJhbGciOi...');
sessionStorage.setItem('is_authenticated', 'true');
```

### 3. Session Re-use via Persistent Profile
Connect CDP directly to an already logged-in Chrome instance:
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=~/.config/chrome-perf-profile "https://app.example.com"
```
Tools connecting to port `9222` inherit the active authenticated session without automated login steps.

### 4. Interaction Tracing vs. Navigation Tracing
> [!IMPORTANT]
> **Do NOT use `reload: true` when auditing SPAs!**
> A full reload wipes runtime caching and triggers async bootstrap endpoints (`/api/me`). Instead:
> 1. Navigate to the page and wait for data hydration (`wait_for`).
> 2. Call `performance_start_trace` with `reload: false`.
> 3. Perform the user action (click sort button, filter data table, open modal).
> 4. Call `performance_stop_trace`.

---

## 🔍 Phase 1: Macro Website & Critical Path Review

### 1. Hardware & Network Emulation
Real users rarely browse on high-end developer workstations. Always emulate mobile or mid-tier hardware:
- Call `emulate`:
  - `cpuThrottlingRate: 4` (simulates mid-tier mobile / office laptop)
  - `networkConditions`: Fast 3G or Slow 4G.

### 2. Record & Analyze Page Trace
1. Start trace: `performance_start_trace` (`reload: true`).
2. Examine the returned insight set IDs.
3. Drill into specific insight models via `performance_analyze_insight`:
   - `DocumentLatency`: Reveals server response time (TTFB). If > 600ms, the bottleneck is backend, database, or CDN cache misses.
   - `RenderBlocking`: Identifies `<link rel="stylesheet">` or `<script>` tags without `defer`/`async` delaying First Contentful Paint.
   - `LCPBreakdown`: Splits LCP into *TTFB → Load Delay → Load Duration → Render Delay*.
   - `LCPDiscovery`: Verifies if the LCP image was preloaded (`<link rel="preload">`) or hidden inside CSS.

---

## ⚡ Phase 2: JavaScript Execution & CPU Profiling

JavaScript blocks the single browser main thread. Tasks exceeding **50ms** are classified as **Long Tasks** and directly degrade **INP (Interaction to Next Paint)**.

### 1. Flame Chart & Call Tree Inspection
In the captured trace:
- Locate red-notched task bars on the **Main** thread.
- Switch to **Bottom-Up**: Sort by **Self Time** (time spent directly in the function body). This pinpoints expensive calculations, JSON string manipulation, or unoptimized sorting algorithms.
- Switch to **Call Tree**: Sort by **Total Time** to see which root frameworks or event handlers orchestrated the work.

### 2. V8 Parse & Compile Overhead
Look for `v8.compile` and `Evaluate Script` slices. Large JavaScript bundles (> 300KB uncompressed) can spend 200–500ms simply parsing before executing a single line.

### 3. Memory Leaks & Garbage Collection Thrashing
1. **GC Spikes**: If the trace shows frequent vertical yellow/purple GC spikes, the application is allocating short-lived objects rapidly, triggering aggressive Scavenger cycles.
2. **The 3-Snapshot Technique**:
   - Call `take_heapsnapshot` before action (Baseline).
   - Perform action and revert it (e.g. open and close a modal 5 times).
   - Call `take_heapsnapshot` (Post-action).
   - Compare snapshots: Check for `Detached HTMLDivElement`, uncleared event listeners, or growing RxJS/Vue reactive subscribers.

---

## 🎨 Phase 3: DOM Rendering & Physics

The browser follows an immutable pipeline: `JS -> Style Recalculation -> Layout (Reflow) -> Paint -> Composite`.

### 1. Layout Thrashing & Forced Synchronous Reflow
- **Cause**: Reading layout geometry (`offsetWidth`, `clientHeight`, `scrollTop`, `getBoundingClientRect()`) immediately after modifying styles in the same frame forces the browser to synchronously compute layout.
- **Trace Indicator**: Red warning flags labeled `Forced reflow is a likely bottleneck`.
- **Detection**: Run the layout thrashing detector snippet from [references/cdp-perf-snippets.md](references/cdp-perf-snippets.md).

### 2. DOM Node Bloat & Tree Depth
- **Thresholds**: Total nodes > **1,500**, Max depth > **32 levels**, Parents with > **50 direct children**.
- Run the DOM auditor snippet from [references/cdp-perf-snippets.md](references/cdp-perf-snippets.md).
- **Remediation**: Implement virtualized scrolling (render only visible viewport rows) and prune redundant nested wrapper `<div>`s.

### 3. Non-Composited Animations & Paint Storms
- Avoid animating `top`, `left`, `width`, `height`, or `margin` (triggers Layout & Paint).
- Animate strictly via GPU-accelerated composited properties: `transform` and `opacity`.

---

## 🧩 Phase 4: Modern Reactive Frameworks & SSR (Vue.js / Nuxt.js)

Single Page Applications (SPAs) and Server-Side Rendered (SSR) architectures introduce framework-specific overhead:

### 1. Reactivity Engine & Deep Proxy Tax
- **The Pitfall**: Storing large API payloads (e.g., 2,000 security findings, audit logs) in `ref()` or `reactive()` forces Vue to recursively wrap every nested array and object in a JavaScript `Proxy`. This increases memory 3–5× and triggers 200–400ms main-thread stalls during data assignment.
- **The Fix**: Use `shallowRef()` for read-only / tabular collections, and wrap complex third-party class instances (Chart.js, Monaco, Mapbox) in `markRaw()`.
- **Reference**: Detailed patterns in [references/vue-nuxt-perf.md](references/vue-nuxt-perf.md).

### 2. Nuxt 3 SSR Hydration Pause
- **The Pitfall**: After receiving pre-rendered HTML, the browser must walk the entire DOM to reconcile the Virtual DOM and attach event listeners (**Hydration**). When pages contain > 1,500 elements, clicks and taps are unresponsive for 300–800ms.
- **The Fix**: Employ Nuxt Server Islands (`nuxt/islands`), `<ClientOnly>` wrappers with lightweight skeleton placeholders, and deferred hydration (`Lazy...` components).
- **Reference**: Detailed patterns in [references/vue-nuxt-perf.md](references/vue-nuxt-perf.md).

### 3. Server Payload Bloat (`__NUXT_DATA__`)
- **The Pitfall**: Nuxt serializes all data fetched via `useAsyncData` / `useFetch` into an inline `<script id="__NUXT_DATA__">`. Returning unpruned database models inflates the initial HTML payload and doubles JSON parsing cost.
- **The Fix**: Prune fields server-side with `pick: ['id', 'title', 'status']` or `transform`. Run the payload inspector from [references/cdp-perf-snippets.md](references/cdp-perf-snippets.md).

### 4. Template Re-Diffing & Virtual DOM Cascades
- **The Pitfall**: Using `:key="index"` in `v-for` forces in-place DOM mutation, breaking input state and triggering layout reflows. Heavy lists re-diff every item whenever parent state changes.
- **The Fix**: Always use unique entity IDs (`:key="item.id"`), memoize complex list items with `v-memo="[item.id === selectedId, item.updated_at]"`, and virtualize lists > 100 items via `<v-virtual-scroll>` or `@tanstack/vue-virtual`.

---

## ⏱️ 15-Minute Performance Audit Runbook

Follow this checklist for any performance engagement:

1. **Setup Auth**: Inject session cookie via `Network.setCookies` or attach to port `9222` (see [references/auth-workarounds.md](references/auth-workarounds.md)).
2. **Throttle**: Call `emulate` with `cpuThrottlingRate: 4`.
3. **Macro Trace**: Run `performance_start_trace(reload: true)` → inspect `DocumentLatency` and `LCPBreakdown`.
4. **Nuxt / SSR Payload**: Execute `cdp-perf-snippets.md` `__NUXT_DATA__` inspector to check serialization size (< 100KB).
5. **Interactive Trace**: Call `performance_start_trace(reload: false)` → trigger the slow UI interaction → call `performance_stop_trace`.
6. **Analyze Long Tasks**: Check flame chart for tasks > 50ms; sort Bottom-Up by Self Time to identify expensive JS or deep proxy reactivity loops.
7. **Check DOM**: Execute `cdp-perf-snippets.md` DOM Tree Depth script via `evaluate_script` (< 1,500 nodes, depth < 32).
8. **Framework Reactivity & Memory**: Audit Vue reactive arrays with `cdp-perf-snippets.md` proxy auditor; take heap snapshot with `take_heapsnapshot` to confirm no detached DOM nodes retaining Vue `_vnode` instances.\n