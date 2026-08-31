---
name: triage-security-findings
description: Review and prioritize lists of application-security, mobile-security, API-security, penetration-test, bug-bounty, or scanner findings. Use when Codex must deduplicate findings, identify likely false positives or overstated impact, rank what to validate first, distinguish static indicators from demonstrated vulnerabilities, improve titles/descriptions, or define the minimum evidence needed for a defensible report.
---

# Triage Security Findings

Review the supplied findings skeptically and rank them by probability of being valid, ease of decisive validation, and likely security impact. Do not equate a scanner signal or insecure pattern with a demonstrated exploit.

## Workflow

1. Normalize titles and descriptions.
   - Correct obvious terminology errors.
   - Merge exact or semantic duplicates.
   - Separate distinct root causes that were combined into one finding.

2. Extract each claim.
   - Identify the vulnerable component and behavior.
   - Identify the claimed attacker, prerequisites, affected asset, and impact.
   - Mark missing details instead of inventing them.

3. Classify the evidence:
   - `Confirmed`: Reproducible exploit or direct observation demonstrates the claim and impact.
   - `Likely`: Strong code/configuration evidence exists, but impact still needs dynamic confirmation.
   - `Uncertain`: The claim depends on assumptions, environment, backend behavior, or missing prerequisites.
   - `Likely FP/Overstated`: The evidence shows only a pattern, prerequisite, or best-practice gap.

4. Rank validation priority using:
   - Probability the underlying condition is real.
   - Ability to obtain decisive evidence quickly and safely.
   - Severity if confirmed.
   - Number and difficulty of prerequisites.
   - Dependence on server-side behavior or inaccessible infrastructure.

5. Recommend exactly one finding to start with. Explain why it offers the best combination of validity and validation value, then order the rest.

6. State the minimum proof required for every finding. Prefer observable evidence such as:
   - Exact configuration, code path, database contents, or exported component.
   - Reproduction steps and actual versus expected behavior.
   - Request and response pairs using two authorized test identities for authorization flaws.
   - Android version, device state, permissions, and attacker prerequisites for mobile findings.

## Review Rules

- Treat static analysis as evidence of reachability or weakness, not proof of exploitability.
- Do not confirm BOLA/IDOR without showing that the server accepts unauthorized access or modification across two test-owned identities or objects.
- Do not confirm authentication bypass merely because local state changes unlock UI. Verify access to protected data or actions and whether the server independently enforces authentication.
- Do not confirm task hijacking from `taskAffinity`, launch mode, or exported activities alone. Require a working PoC on specified Android versions and a demonstrated sensitive consequence.
- For unencrypted private app storage, distinguish plaintext-at-rest from cross-sandbox exposure. State whether root, backup, debugging, physical access, another vulnerability, or an exported interface is required.
- For exported components, verify effective manifest values after merging, required permissions, caller checks, and whether invocation causes a security-relevant action.
- Reduce impact when exploitation requires root or prior device compromise unless the threat model explicitly includes those conditions.
- Never perform unauthorized production testing. Recommend controlled test accounts and owned records for backend authorization checks.

## Output Format

Begin with:

`Start with: <finding title>`

Then provide:

| Rank | Finding | Confidence | Why | Minimum validation |
|---|---|---|---|---|

After the table, include only applicable sections:

- `Duplicates or wording issues`
- `Claims that are currently overstated`
- `Evidence to collect first`

Keep the conclusion decisive. If evidence is insufficient, say which finding is most promising to validate first rather than declaring it valid.
