# Authenticated Pages Workaround Guide for CDP Performance Reviews

Automated performance audits frequently break on authenticated pages. Tools like Lighthouse or cold trace reloads (`reload: true`) spawn clean sessions or clear state, redirecting the browser to `/login` or corporate SSO.

This guide provides tested patterns to bypass, inject, and maintain authentication state during Chrome DevTools Protocol (CDP) performance reviews.

---

## 🔑 The 4 Authentication Storage Paradigms

Web applications store authentication state across four primary mechanisms:

1. **HttpOnly Cookies** (e.g., `sessionid`, `connect.sid`, `jwt`): Handled exclusively by the browser networking layer. Cannot be accessed via JavaScript `document.cookie`.
2. **Client-Accessible Cookies** (e.g., `csrftoken`, `token`): Can be read and written via JavaScript.
3. **Web Storage (`localStorage` / `sessionStorage`)**: Common in Single Page Applications (React, Vue, Angular) storing JWTs (`access_token`, `refresh_token`).
4. **In-Memory / Closure State**: Tokens retrieved via OAuth/OIDC handshake and kept in JavaScript memory. Lost on page reload.

---

## Strategy 1: CDP Pre-Navigation State Injection

The most reliable approach for automated runs. Before navigating to the audited page, inject cookies and web storage via CDP.

### A. Injecting HttpOnly Cookies via CDP `Network.setCookies`

Using CDP's `Network` domain allows setting HttpOnly, Secure, and SameSite cookies that JavaScript cannot touch:

```json
// CDP Command: Network.setCookies
{
  "cookies": [
    {
      "name": "sessionid",
      "value": "abc123xyz789",
      "domain": ".example.com",
      "path": "/",
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax",
      "expires": 1798761600
    },
    {
      "name": "csrftoken",
      "value": "csrf_token_value_here",
      "domain": ".example.com",
      "path": "/",
      "httpOnly": false,
      "secure": true
    }
  ]
}
```

### B. Injecting `localStorage` / `sessionStorage` via `Page.addScriptToEvaluateOnNewDocument`

When SPAs rely on tokens in `localStorage`, setting them via `evaluate_script` *after* navigation is often too late—the app has already evaluated its auth guard and triggered a redirect.

Use CDP `Page.addScriptToEvaluateOnNewDocument` to execute synchronous initialization script before *any* page script runs:

```javascript
// CDP Command: Page.addScriptToEvaluateOnNewDocument
{
  "source": `
    (function() {
      localStorage.setItem('auth_token', 'Bearer <mock_jwt_token_here>');
      localStorage.setItem('user_profile', JSON.stringify({
        id: 'usr_123',
        org: 'acme-corp',
        role: 'admin'
      }));
      sessionStorage.setItem('is_authenticated', 'true');
    })();
  `
}
```

### C. Injecting Authorization Headers via `Network.setExtraHTTPHeaders`

If the backend expects an `Authorization: Bearer <token>` header on HTML or API requests:

```json
// CDP Command: Network.setExtraHTTPHeaders
{
  "headers": {
    "Authorization": "Bearer <mock_jwt_token_here>",
    "X-Client-Version": "2.4.0"
  }
}
```

---

> [!CAUTION]
> **Security Warning (Remote Debugging)**: 
> Exposing `--remote-debugging-port=9222` grants unrestricted programmatic control over the browser, cookies, and local filesystem. 
> - Always bind strictly to `127.0.0.1` (never `0.0.0.0` or public interfaces).
> - Never expose the debugging port over network boundaries without SSH tunneling.
> - Terminate the Chrome instance when performance profiling is complete.

### Step 1: Launch Chrome with Remote Debugging & User Data Dir

```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.config/chrome-perf-profile" \
  --no-first-run \
  --no-default-browser-check \
  "https://app.example.com/dashboard"
```

1. Manually log in once via the opened browser window (completing 2FA/SSO).
2. The authentication session, IndexedDB, cookies, and localStorage are saved to `$HOME/.config/chrome-perf-profile`.
3. Subsequent automated CDP runs connecting to port `9222` will inherit the logged-in session immediately.

---

> [!WARNING]
> **Credential File Handling**: Files storing browser storage state (such as `auth-state.json`) contain plaintext session cookies and bearer tokens. Always store them in local scratch directories and ensure `auth-state.json` and `*.auth.json` are included in `.gitignore` to prevent credential leaks.

## Strategy 3: Interaction Tracing vs Navigation Tracing in SPAs

In authenticated SPAs, a full page reload (`reload: true`) causes the application to:
1. Re-download bundle scripts.
2. Initialize root Vue/React app.
3. Make an asynchronous `/api/me` call.
4. Mount the dashboard.

This distorts interaction metrics. To measure actual application performance (e.g., clicking a report, filtering a table, opening a drawer):

### 1. Pre-warm and Hydrate
- Navigate to the authenticated route.
- Wait for the primary data table or graph to render completely (`wait_for`).

### 2. Record an Interaction-Only Trace
- Start trace with `reload: false`:
  ```json
  // performance_start_trace
  { "reload": false }
  ```
- Trigger the user action (click table sort, submit search, change page size).
- Wait for DOM updates to stabilize.
- Stop trace (`performance_stop_trace`) to isolate pure client-side execution, layout reflow, and DOM rendering without navigation overhead.

---

## Strategy 4: Exporting & Importing Storage State (Playwright / Puppeteer Bridge)

If conducting audits via scripts before analyzing via CDP:

```javascript
// Step 1: Log in once and save state
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('https://app.example.com/login');
  await page.fill('#username', 'test_user');
  await page.fill('#password', 'test_password');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
  
  // Save storage state (cookies + localStorage)
  await context.storageState({ path: 'auth-state.json' });
  await browser.close();
})();
```

```javascript
// Step 2: Launch CDP audit with pre-loaded state
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ storageState: 'auth-state.json' });
  const page = await context.newPage();
  
  // Open CDP Session
  const client = await page.context().newCDPSession(page);
  await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await client.send('Tracing.start', {
    categories: ['devtools.timeline', 'v8.execute', 'blink.user_timing']
  });

  await page.goto('https://app.example.com/dashboard');
  
  const traceData = await client.send('Tracing.end');
  await browser.close();
})();
```\n