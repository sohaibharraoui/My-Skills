# CDP Performance Diagnostic Snippets

Production-ready snippets that can be evaluated directly via `evaluate_script` or in the Chrome DevTools console during a performance review.

---

## 1. Long Tasks Monitor (> 50ms Blocking Main Thread)

Logs all blocking Long Tasks with their duration, startTime, and container attribution:

```javascript
(() => {
  if (!window.PerformanceObserver) {
    return 'PerformanceObserver not supported';
  }
  
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.warn(`[LONG TASK DETECTED] Duration: ${entry.duration.toFixed(2)}ms (over 50ms budget)`, {
        startTime: entry.startTime.toFixed(2),
        name: entry.name,
        attribution: entry.attribution.map(a => ({
          name: a.name,
          containerType: a.containerType,
          containerSrc: a.containerSrc,
          containerId: a.containerId,
          containerName: a.containerName
        }))
      });
    }
  });

  observer.observe({ entryTypes: ['longtask'] });
  return 'Long Task observer active. Perform user interactions now.';
})();
```

---

## 2. Layout Thrashing & Forced Synchronous Reflow Detector

Monkey-patches DOM geometry getters to alert when a geometry read occurs immediately after a style write in the same JavaScript execution turn:

```javascript
(() => {
  const geometryGetters = [
    'offsetWidth', 'offsetHeight', 'offsetTop', 'offsetLeft',
    'clientWidth', 'clientHeight', 'clientTop', 'clientLeft',
    'scrollWidth', 'scrollHeight', 'scrollTop', 'scrollLeft'
  ];

  let pendingStyleWrite = false;
  let writeLocation = '';

  // Intercept style sets
  const origSetAttribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function(name, val) {
    if (name === 'style' || name === 'class') {
      pendingStyleWrite = true;
      writeLocation = new Error().stack.split('\n')[2];
    }
    return origSetAttribute.apply(this, arguments);
  };

  // Intercept geometric reads
  geometryGetters.forEach((prop) => {
    const descriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, prop);
    if (!descriptor || !descriptor.get) return;
    
    Object.defineProperty(HTMLElement.prototype, prop, {
      get: function() {
        if (pendingStyleWrite) {
          console.error(`[LAYOUT THRASHING] Reading '${prop}' immediately after style write!`, {
            element: this,
            triggerStack: new Error().stack.split('\n').slice(2, 5).join('\n'),
            priorWriteStack: writeLocation
          });
          pendingStyleWrite = false; // Reset to avoid log flood
        }
        return descriptor.get.call(this);
      }
    });
  });

  // Reset flag at end of microtask/frame
  requestAnimationFrame(() => {
    pendingStyleWrite = false;
  });

  return 'Layout Thrashing interceptor active.';
})();
```

---

## 3. DOM Tree Complexity & Depth Auditor

Computes total nodes, maximum depth, and elements with excessive children:

```javascript
(() => {
  const allElements = Array.from(document.querySelectorAll('*'));
  let maxDepth = 0;
  let deepestElement = null;

  allElements.forEach(el => {
    let depth = 0;
    let parent = el;
    while (parent.parentElement) {
      depth++;
      parent = parent.parentElement;
    }
    if (depth > maxDepth) {
      maxDepth = depth;
      deepestElement = el;
    }
  });

  // Find parents with high child count
  const excessiveParents = allElements
    .filter(el => el.children.length > 50)
    .map(el => ({
      tag: el.tagName.toLowerCase(),
      id: el.id || undefined,
      class: el.className || undefined,
      childCount: el.children.length
    }))
    .slice(0, 10);

  const report = {
    totalNodes: allElements.length,
    status: allElements.length > 1500 ? 'CRITICAL (> 1,500 nodes)' : 'HEALTHY',
    maxDepth: maxDepth,
    depthStatus: maxDepth > 32 ? 'CRITICAL (> 32 levels)' : 'HEALTHY',
    deepestTag: deepestElement ? deepestElement.tagName.toLowerCase() : null,
    excessiveParents
  };

  console.table(report);
  return report;
})();
```

---

## 4. Detached DOM Nodes Inspector

Finds DOM elements in memory that are disconnected from `document.body` (common cause of DOM memory leaks in SPAs):

```javascript
(() => {
  const detachedNodes = [];
  
  // Recursively inspect candidate elements stored on global variables or caches
  function isDetached(el) {
    return el instanceof Node && !document.body.contains(el);
  }

  // Sample check on common window caches
  const candidateKeys = Object.keys(window).filter(k => !k.startsWith('webkit') && !k.startsWith('chrome'));
  
  for (const key of candidateKeys) {
    try {
      const val = window[key];
      if (isDetached(val)) {
        detachedNodes.push({ source: `window.${key}`, node: val.nodeName });
      }
    } catch (e) {}
  }

  return {
    detectedCandidateDetachedNodes: detachedNodes,
    recommendation: 'Take a Chrome Heap Snapshot and filter by "Detached HTML" for exhaustive analysis.'
  };
})();
```

---

## 5. Navigation & Critical Rendering Path Metrics

Calculates the complete navigation waterfall breakdown:

```javascript
(() => {
  const [nav] = performance.getEntriesByType('navigation');
  if (!nav) return 'No navigation entry available';

  const ttfb = nav.responseStart - nav.requestStart;
  const download = nav.responseEnd - nav.responseStart;
  const domInteractive = nav.domInteractive - nav.responseEnd;
  const domProcessing = nav.domComplete - nav.domInteractive;
  const loadDuration = nav.loadEventEnd - nav.loadEventStart;

  const summary = {
    '1. DNS Lookup (ms)': +(nav.domainLookupEnd - nav.domainLookupStart).toFixed(2),
    '2. TCP Handshake (ms)': +(nav.connectEnd - nav.connectStart).toFixed(2),
    '3. Server TTFB (ms)': +ttfb.toFixed(2),
    '4. Content Download (ms)': +download.toFixed(2),
    '5. DOM Parsing (ms)': +domInteractive.toFixed(2),
    '6. Subresource Load (ms)': +domProcessing.toFixed(2),
    '7. Total Page Load (ms)': +nav.duration.toFixed(2)
  };

  console.table(summary);
  return summary;
})();
```

---

## 6. Nuxt 3 & Vue 3 Runtime Diagnostics

### A. Nuxt SSR Payload (`__NUXT_DATA__`) Size Inspector
Evaluates inline payload serialization cost in Nuxt 3 applications:

```javascript
(() => {
  const nuxtDataScript = document.getElementById('__NUXT_DATA__');
  if (!nuxtDataScript) {
    return { status: 'NOT_FOUND', message: 'No __NUXT_DATA__ element found on current page.' };
  }

  const rawContent = nuxtDataScript.textContent || '';
  const byteLength = new Blob([rawContent]).size;
  const kbSize = +(byteLength / 1024).toFixed(2);

  let parsedKeys = 0;
  try {
    const parsed = JSON.parse(rawContent);
    parsedKeys = Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length;
  } catch (e) {}

  const result = {
    payloadSizeKB: kbSize,
    serializedEntries: parsedKeys,
    rating: kbSize < 50 ? 'EXCELLENT (<50KB)' : kbSize < 150 ? 'ACCEPTABLE (<150KB)' : 'BLOATED (>150KB)',
    recommendation: kbSize > 100 
      ? 'Payload exceeds 100KB! Use `pick: [...]` or `transform: ...` in `useFetch` / `useAsyncData` to prune unused database fields.' 
      : 'Payload footprint is well-proportioned.'
  };

  console.table(result);
  return result;
})();
```

### B. Vue 3 Reactivity Overhead & Proxy Auditor
Inspects reactive objects and measures potential memory bloat from deep proxies:

```javascript
(() => {
  // Checks if a candidate object is a Vue 3 reactive proxy
  const isVueProxy = (val) => val !== null && typeof val === 'object' && val.__v_raw !== undefined;

  let proxyCount = 0;
  let largeArrayProxies = [];

  function inspectObject(obj, path = 'window', depth = 0) {
    if (depth > 4 || !obj || typeof obj !== 'object') return;

    if (isVueProxy(obj)) {
      proxyCount++;
      if (Array.isArray(obj) && obj.length > 500) {
        largeArrayProxies.push({
          path,
          length: obj.length,
          recommendation: 'Replace `ref([])` with `shallowRef([])` to eliminate per-element proxy instantiation overhead.'
        });
      }
    }

    try {
      const keys = Object.keys(obj);
      for (const k of keys.slice(0, 50)) {
        if (!k.startsWith('webkit') && !k.startsWith('_')) {
          inspectObject(obj[k], `${path}.${k}`, depth + 1);
        }
      }
    } catch (e) {}
  }

  inspectObject(window);

  const report = {
    detectedVueProxies: proxyCount,
    oversizedReactiveArrays: largeArrayProxies
  };

  console.log('Vue 3 Reactivity Audit:', report);
  return report;
})();
```\n