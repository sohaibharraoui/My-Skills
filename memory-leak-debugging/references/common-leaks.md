# Common Memory Leaks

When analyzing a retainer trace from `memlab`, look for these common patterns in the codebase:

## 1. Uncleared Event Listeners

Event listeners attached to global objects (like `window` or `document`) or long-living objects prevent garbage collection of the objects referenced in their callbacks.

**Fix:** Always call `removeEventListener` when a component unmounts or the listener is no longer needed.

## 2. Detached DOM Nodes

A DOM node is removed from the document tree but is still referenced by a JavaScript variable. While detachedness is a good signal for a memory leak, it's not always a bug. For example, websites sometimes intentionally cache detached navigation trees.

**Fix:** Signal the detached nodes to the user first. **Ask the user first** before nulling the references or changing the code, as the detached nodes might be part of an intentional cache. If confirmed as a leak, ensure variables holding DOM references are set to `null` when the node is removed, or limit their scope.

## 3. Unintentional Global Variables

Variables declared without `var`, `let`, or `const` (in non-strict mode) or explicitly attached to `window` remain in memory forever.

**Fix:** Use strict mode, properly declare variables, and avoid global state.

## 4. Closures

Closures can unintentionally keep references to large objects in their outer scope.

**Fix:** Nullify large objects when they are no longer needed, or refactor the closure to not capture unnecessary variables.

## 5. Unbounded Caches or Arrays

Data structures used for caching (like objects, Arrays, or Maps) that grow without limits.

**Fix:** Implement caching limits, use LRU caches, or use `WeakMap`/`WeakSet` for data associated with object lifecycles.

## 6. Runaway Reactive Render Loops (Virtual DOM & Listener Explosions)

An apparent memory leak where thousands of DOM nodes (100,000+) and event listeners (50,000+) spawn **within seconds on a single view**, locking up the main thread with massive Long Tasks (30s+). This is caused by:
- **Unguarded Bidirectional Watchers**: Parent prop updates child internal state; child watcher immediately emits back to parent without `_.isEqual` checks, triggering infinite ping-pong re-render cycles.
- **Inline Object/Array Literals in Templates**: Binding `:options="{ ... }"` or `:selected="[]"` passes a new reference on every tick, constantly re-mounting child subtrees.
- **Shared Reference Traps**: In-place array mutations on un-cloned props bypass equality guards.

**Fix:** Guard all bidirectional watchers with deep equality checks (`!_.isEqual(current, next)`), defensively copy arrays/objects across prop boundaries (`[...val]`), hoist inline literals into stable data fields or computeds, and eliminate deprecated Vue 2 `v-on="$listeners"`.

