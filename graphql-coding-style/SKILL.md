---
name: graphql-coding-style
description: Coding standards, architectural patterns, security hardening, and best practices for GraphQL schema design and API implementation in Graphene Python and Django. Use when writing, modifying, or reviewing GraphQL schemas, queries, mutations, types, resolvers, and performance optimizations.
---

# GraphQL & Graphene Python Coding Style Guide

Authoritative standards, architectural design requirements, and security hardening patterns for authoring robust, maintainable, high-performance, and idiomatic GraphQL schemas and resolvers, with concrete implementations in **Graphene Python** and **`graphene-django`**.

---

## 🎯 1. Core Query & Schema Rules

### 1. List-Only Root Queries (No Single-Item Queries)
> [!IMPORTANT]
> **Always return a list of items from root queries.**
> Do **NOT** duplicate queries into single-item and list-of-items variants (e.g., do not create both `vulnerability(id: ID!)` and `vulnerabilities(...)`).

- Provide **only** the list query (e.g. `vulnerabilities`, `scans`, `tickets`, `assets`).
- To fetch a single entity by ID, pass the ID filter to the list query (e.g. `vulnerabilities(vulnerabilityId: "123")`), which returns a list containing that matching entity.
- **Benefits**: Eliminates resolver duplication, ensures uniform pagination/filtering logic, and keeps the root schema clean.

```graphql
# ❌ BAD: Redundant single-item and list queries
type Query {
  vulnerability(id: ID!): Vulnerability       # FORBIDDEN
  vulnerabilities(filter: FilterInput): [Vulnerability!]!
}

# ✅ GOOD: Unified list query supporting ID filtering
type Query {
  vulnerabilities(
    vulnerabilityId: ID,
    first: Int,
    after: String,
    filter: VulnerabilityFilterInput
  ): VulnerabilityConnection!
}
```

#### Graphene Python Implementation:
```python
import graphene
from graphene_django import DjangoObjectType

class Query(graphene.ObjectType):
    vulnerabilities = graphene.relay.ConnectionField(
        VulnerabilityType.connection,
        vulnerability_id=graphene.ID(description="Filter by specific vulnerability ID"),
        severity=graphene.String(),
    )

    def resolve_vulnerabilities(self, info: graphene.ResolveInfo, vulnerability_id=None, severity=None, **kwargs):
        # 1. Enforce Trust Boundary & Tenant Scoping
        org = info.context.organisation
        qs = Vulnerability.objects.filter(organisation=org)

        # 2. Filter by explicit entity ID
        if vulnerability_id is not None:
            _, raw_id = graphene.relay.Node.from_global_id(vulnerability_id) if ":" in str(vulnerability_id) else (None, vulnerability_id)
            qs = qs.filter(id=raw_id)
            
        if severity is not None:
            qs = qs.filter(severity=severity)
            
        return qs
```

---

### 2. Explicit ID Argument Naming (`<entity>Id`)
> [!IMPORTANT]
> When filtering or fetching by ID, **never name the argument a generic `id`**.

- Always include the object's entity name in the argument: `vulnerabilityId`, `scanId`, `assetId`, `ticketId`.
- In Python/Graphene, declare `snake_case` argument names (`vulnerability_id`), which Graphene automatically serializes to `camelCase` (`vulnerabilityId`) in the schema.

```python
# ❌ BAD in Graphene
scans = graphene.List(ScanType, id=graphene.ID())

# ✅ GOOD in Graphene
scans = graphene.List(ScanType, scan_id=graphene.ID())
```

---

### 3. Relational Resolution Over Root Queries
> [!IMPORTANT]
> If an object is related to or needed from another object, **update the GraphQL types to resolve it directly from the parent object**. Do **NOT** create a separate root query.

- Never create ad-hoc root queries like `ticketsByAsset(assetId: ID!)` or `vulnerabilitiesForScan(scanId: ID!)`.
- Instead, expose and resolve the child relation as a field on the parent type (`Asset.tickets`, `Scan.vulnerabilities`).

```graphql
# ❌ BAD: Disconnected root query for related entity
type Query {
  ticketsByAsset(assetId: ID!): [Ticket!]!   # FORBIDDEN
}

# ✅ GOOD: Traverse the graph naturally through type definitions
type Asset {
  id: ID!
  name: String!
  tickets(first: Int, after: String, status: TicketStatusEnum): TicketConnection! # Resolved on Asset type
}
```

---

### 4. Nullability & Blast Radius Control
In GraphQL, if a non-null (`!`) field throws an error at runtime, **the error bubbles up to the nearest nullable parent**, potentially destroying the entire response tree.

- **Inputs (`InputObjectType`)**: Required arguments and fields MUST be non-null (`required=True` in Graphene) to fail fast during schema validation.
- **Output Object Fields**: Default to nullable for external integrations, child associations, and secondary fields so partial service failures degrade gracefully.
- **Entity IDs & System Identifiers**: Type IDs as non-null (`id: ID!` / `required=True`).

```graphql
# ❌ DANGEROUS: Single sub-service failure nullifies the entire user object
type UserProfile {
  id: ID!
  name: String!
  billingDetails: BillingDetails!    # If billing service fails, entire UserProfile is NULL
  creditScore: Int!                 # If 3rd party score API fails, entire UserProfile is NULL
}

# ✅ RESILIENT: Graceful partial failure delivery
type UserProfile {
  id: ID!
  name: String!
  billingDetails: BillingDetails     # Returns null + error in 'errors', user data is preserved
  creditScore: Int
}
```

---

## 🏷 2. Naming & Case Conventions

Follow standard GraphQL naming conventions. Graphene automatically handles `snake_case` (Python) to `camelCase` (GraphQL) conversions:

| Construct | GraphQL Case | Graphene Python Declaration | Example |
| :--- | :--- | :--- | :--- |
| **Object Types & Interfaces** | `PascalCase` | `class VulnerabilityType(graphene.ObjectType)` | `Vulnerability`, `Node` |
| **Fields & Query Names** | `camelCase` | `scan_status = graphene.String()` | `scanStatus`, `vulnerabilities` |
| **Arguments** | `camelCase` (`<entity>Id`) | `vulnerability_id = graphene.ID()` | `vulnerabilityId`, `pageSize` |
| **Mutations** | `camelCase` (Verb + Noun) | `class CreateTicket(graphene.relay.ClientIDMutation)` | `createTicket`, `updateStatus` |
| **Input Object Types** | `PascalCase` + `Input` | `class CreateTicketInput(graphene.InputObjectType)` | `CreateTicketInput` |
| **Payload Object Types** | `PascalCase` + `Payload` | Handled by `ClientIDMutation` or `*Payload` | `CreateTicketPayload` |
| **Enum Types** | `PascalCase` | `class SeverityLevel(graphene.Enum)` | `SeverityLevel` |
| **Enum Values** | `SCREAMING_SNAKE_CASE` | `CRITICAL = "CRITICAL"` | `CRITICAL`, `IN_PROGRESS` |

---

## 🔄 3. Mutation Design & `ClientIDMutation`

### 1. Single Input Parameter & `ClientIDMutation`
Always use `graphene.relay.ClientIDMutation`. It automatically encapsulates arguments in an `input` object, handles `client_mutation_id`, and creates the standard payload response structure:

```python
import graphene

class UserErrorType(graphene.ObjectType):
    field = graphene.List(graphene.NonNull(graphene.String), required=True)
    message = graphene.String(required=True)
    code = graphene.String()

class CreateScan(graphene.relay.ClientIDMutation):
    class Input:
        target_url = graphene.String(required=True)
        profile_id = graphene.ID(required=True)

    # Response Payload Fields
    scan = graphene.Field(ScanType)
    user_errors = graphene.List(graphene.NonNull(UserErrorType), required=True)
    success = graphene.Boolean(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info: graphene.ResolveInfo, **input_data):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionError("Authentication required.")

        org = info.context.organisation
        target_url = input_data.get("target_url")
        errors = []

        # Domain Validation
        if not target_url.startswith(("http://", "https://")):
            errors.append(UserErrorType(
                field=["input", "targetUrl"],
                message="Target URL must include http or https protocol.",
                code="INVALID_URL_SCHEME"
            ))
            return CreateScan(scan=None, user_errors=errors, success=False)

        scan = Scan.objects.create(
            target_url=target_url,
            organisation=org,
            created_by=user
        )
        return CreateScan(scan=scan, user_errors=[], success=True)
```

### 2. Intent-Driven (Task-Oriented) Mutations
Avoid generic CRUD mutations that accept giant property bags (`updateTicket(...)`). Use intent-driven mutations that reflect specific business actions:

```python
# ❌ Generic CRUD Anti-Pattern
class UpdateTicket(graphene.relay.ClientIDMutation): ...

# ✅ Intent-Driven Mutations
class AssignTicket(graphene.relay.ClientIDMutation): ...
class ChangeTicketSeverity(graphene.relay.ClientIDMutation): ...
class CloseTicket(graphene.relay.ClientIDMutation): ...
```

---

## 📄 4. Pagination & List Design (Relay Cursor Spec)

All list queries and relationships MUST follow the **Relay Connection Specification**.

### Graphene Countable Connection Pattern:
```python
import graphene
from graphene_django import DjangoObjectType

class CountableConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int(required=True)

    def resolve_total_count(self, info: graphene.ResolveInfo):
        # self.length represents the total count in the queryset before slicing
        return self.length

class VulnerabilityType(DjangoObjectType):
    class Meta:
        model = Vulnerability
        interfaces = (graphene.relay.Node,)
        connection_class = CountableConnection
        fields = ("id", "title", "severity", "created_at")
```

### Key Rules for Pagination:
1. **Opaque Cursors**: Cursors must be base64-encoded strings representing the record's sort key (e.g., `base64("created_at:2026-08-22T10:00:00Z#id:9872")`), not raw database primary keys or offsets.
2. **Never Use Offset Pagination**: Avoid `LIMIT/OFFSET` pagination on large tables due to $O(N)$ scan performance costs and drifting window anomalies during concurrent writes.

---

## ⚡ 5. Resolver Performance & N+1 Prevention

### 1. The DataLoader Pattern (Request-Scoped Batching)
> [!IMPORTANT]
> **DataLoaders MUST be instantiated per HTTP request.**
> Never use global/singleton DataLoaders, which cause cross-tenant memory leaks and stale data anomalies.

Attach DataLoaders to the request context in Django middleware or the GraphQL view's context:

```python
from promise import Promise
from promise.dataloader import DataLoader

class TicketsByAssetLoader(DataLoader):
    """Batches all asset_id queries occurring in the current tick into 1 SQL query."""
    def batch_load_fn(self, asset_ids):
        tickets = Ticket.objects.filter(asset_id__in=asset_ids)
        ticket_map = {aid: [] for aid in asset_ids}
        for ticket in tickets:
            ticket_map[ticket.asset_id].append(ticket)
        return Promise.resolve([ticket_map[aid] for aid in asset_ids])

class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ("id", "name")

    tickets = graphene.List(graphene.NonNull(TicketType))

    def resolve_tickets(self: Asset, info: graphene.ResolveInfo):
        # Cleanly delegates to the request-scoped DataLoader batch queue
        return info.context.tickets_by_asset_loader.load(self.id)
```

### 2. Field Lookahead & AST Inspection (`select_related` / `prefetch_related`)
In Graphene-Django, inspect the GraphQL `info` AST at the root query level to execute `select_related` / `prefetch_related` or SQL JOINs based on the requested child fields:

```python
def resolve_scans(self, info: graphene.ResolveInfo, **kwargs):
    queryset = Scan.objects.all()
    selected_fields = {field.name.value for field in info.field_nodes[0].selection_set.selections}
    
    if "organisation" in selected_fields:
        queryset = queryset.select_related("organisation")
    if "vulnerabilities" in selected_fields:
        queryset = queryset.prefetch_related("vulnerabilities")
        
    return queryset
```

---

## 🔒 6. Security Hardening (*Black Hat GraphQL* Guidelines)

Pass custom validation rules directly into your `GraphQLView` in `urls.py`:

```python
# urls.py
from django.conf import settings
from graphene_django.views import GraphQLView
from graphql.validation.rules import NoSchemaIntrospectionCustomRule

class SecureGraphQLView(GraphQLView):
    def get_validation_rules(self, context=None):
        rules = super().get_validation_rules(context)
        
        # 1. Disable introspection in production
        if not settings.DEBUG:
            rules.append(NoSchemaIntrospectionCustomRule)
            
        # 2. Enforce AST Query Depth Limiting (Max Depth = 8)
        rules.append(MaxDepthValidationRule(max_depth=8))
        return rules
```

### AST Depth Limiter Implementation:
```python
from graphql.validation.rules import ValidationRule
from graphql.language.ast import FieldNode
from graphql.error import GraphQLError

class MaxDepthValidationRule(ValidationRule):
    def __init__(self, context, max_depth=8):
        self.context = context
        self.max_depth = max_depth

    def enter_operation_definition(self, node, key, parent, path, ancestors):
        depth = self._calculate_depth(node)
        if depth > self.max_depth:
            self.context.report_error(
                GraphQLError(f"Query depth of {depth} exceeds maximum allowed depth of {self.max_depth}.")
            )

    def _calculate_depth(self, node, current_depth=0):
        if not hasattr(node, "selection_set") or node.selection_set is None:
            return current_depth
        max_child_depth = current_depth
        for selection in node.selection_set.selections:
            if isinstance(selection, FieldNode):
                if selection.name.value.startswith("__"):
                    continue
                child_depth = self._calculate_depth(selection, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        return max_child_depth
```

---

## 🛡️ 7. Access Control & Authorization (Query & Mutation Level Only)

> [!IMPORTANT]
> **Access control, permissions, and tenant isolation MUST be performed exclusively at the Query and Mutation level.**
> **Do NOT re-implement access control checks, tenant scoping, or permission filtering inside Type-level field resolvers.**

### 1. Types are Pure Graph Navigators
- Field resolvers on GraphQL types (e.g., `TicketStreamType.resolve_tickets`, `ScanType.resolve_vulnerabilities`) should simply return the associated relation or queryset directly (`self.tickets.all()`).
- Assume that any entity reaching the type layer has already been authorized, scoped, and validated by the root query or mutation that fetched it.
- Keep type resolvers simple, readable, and focused purely on data graph navigation.

### 2. Query & Mutation Layer as the Trust Boundary
- Root queries and mutations are the sole trust boundary responsible for:
  - Authenticating the caller and verifying API tokens / sessions.
  - Enforcing multi-tenancy isolation (scoping querysets to the authenticated organisation/workspace).
  - Evaluating role-based access control (RBAC) and object-level access (OLA).

```python
# ❌ BAD: Over-engineered type resolver re-checking org context and permissions
class TicketStreamType(DjangoObjectType):
    def resolve_tickets(self, info: graphene.ResolveInfo):
        # FORBIDDEN: Re-checking auth context and filtering in type resolver
        org, user = info.context.organisation, info.context.user
        if self.organisation != org:
            return Ticket.objects.none()
        if user and not user.is_admin(org):
            return self.tickets.filter(user_access=user)
        return self.tickets.all()


# ✅ GOOD: Clean, simple type resolver; access control is handled at query level
class TicketStreamType(DjangoObjectType):
    def resolve_tickets(self: TicketStream, info: graphene.ResolveInfo):
        stream = typing.cast(TicketStream, self)
        return stream.tickets.all()
```

---

## ⚠️ 8. Error Modeling & Resilience

### 1. Two-Tier Error Architecture
- **Top-Level `errors`**: Reserved strictly for technical, transport, and unexpected infrastructure failures (e.g., unauthenticated requests, syntax errors, 500 internal server exceptions). Sanitize stack traces in production.
- **Domain & Validation Errors**: Modeled directly in the schema via payload `user_errors` or Graphene Union Types.

### 2. Union-Based Result Pattern for Complex Operations in Graphene
```python
class CreateUserSuccess(graphene.ObjectType):
    user = graphene.Field(UserType, required=True)

class EmailAlreadyRegisteredError(graphene.ObjectType):
    message = graphene.String(required=True)
    suggested_action = graphene.String(required=True)

class CreateUserResult(graphene.Union):
    class Meta:
        types = (CreateUserSuccess, EmailAlreadyRegisteredError)

class CreateUser(graphene.Mutation):
    class Arguments:
        input = CreateUserInput(required=True)

    Output = CreateUserResult

    def mutate(self, info: graphene.ResolveInfo, input):
        if User.objects.filter(email=input.email).exists():
            return EmailAlreadyRegisteredError(
                message="Email is already in use.",
                suggested_action="Please sign in or reset your password."
            )
        user = User.objects.create_user(**input)
        return CreateUserSuccess(user=user)
```

---

## 🚀 9. Caching, Transport & Schema Governance

### 1. Automatic Persisted Queries (APQ) & Edge Caching
- Use APQ to send a SHA-256 hash instead of long GraphQL query strings.
- Execute read queries via HTTP `GET` with APQ hashes to enable edge/CDN caching.

### 2. Safe Deprecation in Graphene
Use the `deprecation_reason` parameter on any Graphene field or enum value to safely deprecate fields:

```python
class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ("id", "created_at")

    ip_address = graphene.String(
        deprecation_reason="Use 'primary_ip' or 'ip_addresses'. Removal targeted for 2026-12-31."
    )
    primary_ip = graphene.String(required=True)
    ip_addresses = graphene.List(graphene.NonNull(graphene.String), required=True)
```
