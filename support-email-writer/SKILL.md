---
name: support-email-writer
description: Draft professional customer support email replies in the Ostorlab style. Use when the user asks to write, rewrite, polish, or rephrase an email response to a support request, feature request, customer update, bug report, implementation update, or technical follow-up.
---

# Support Email Writer

## Core Style

Write concise, professional support emails with a calm, helpful tone.

Use this voice:

- Direct and clear, without sounding cold.
- Polite and appreciative.
- Confident about completed work or current status.
- Specific enough to answer the request, but not overloaded with internal details.
- Neutral and factual when timelines, limitations, or ongoing work are involved.

Avoid:

- Overpromising exact delivery when the timeline is uncertain.
- Casual phrasing such as "we did a big part of it" or "for now".
- Long explanations unless the customer asked for technical detail.
- Marketing language, hype, or excessive apologies.

## Email Structure

Use this structure by default:

```text
Hello <Name>,

Thank you for reaching out.

<Answer the request directly. State the current status, what has been completed, what changed, or what is planned.>

<Add timeline, availability, attachments, IDs, screenshots, or next steps if relevant.>

Please let us know if you have any questions or if there is anything specific you would like us to take into consideration.

Best regards,
```

Use `Dear <Name>,` only for more formal customers or when the user asks for a formal tone.

## Common Response Patterns

For implemented features:

```text
The requested enhancement has now been implemented. <Describe the change and the customer-visible benefit.>
```

For work in progress:

```text
The requested feature is currently under development. A significant part of the implementation has already been completed, and we expect it to be available <timeframe>.
```

For sharing evidence or artifacts:

```text
Please find attached <files/artifacts>. These examples were taken from <brief context>.
```

For technical clarification:

```text
For reference, <include IDs, versions, standards, or reproduction context>.
```

For product comparison or explanation:

```text
<Product/feature A> is primarily focused on <scope>. <Product/feature B> goes beyond this by <broader scope and value>.
```

## Rewrite Rules

When the user provides rough wording:

1. Preserve the meaning and business facts.
2. Improve grammar, tone, and professionalism.
3. Replace informal wording with precise support language.
4. Keep the email short unless the request requires detail.
5. Include a closing sentence inviting questions or extra requirements.

When the customer name is known, address them by first name unless the user provides a preferred form of address.

When no sender name is provided, leave the signature as:

```text
Best regards,
```

Do not invent attachments, screenshots, release dates, IDs, or implementation details. If the user gives an approximate timeline such as "around 2 weeks", phrase it as "approximately two weeks" or "expected in approximately two weeks".

## Example

Input facts:

- Customer: Marc
- Request: Would like an Ostorlab MCP
- Status: In progress, significant part implemented, public release planned in around two weeks

Output:

```text
Hello Marc,

Thank you for reaching out.

The Ostorlab MCP is currently under development, and a significant part of the implementation has already been completed. We plan to make it available for public use, with an expected release timeline of approximately two weeks.

Please let us know if there are any specific MCP capabilities or workflows you would like us to take into consideration.

Best regards,
```
