---
name: oreilly-search
description: Search the O'Reilly Learning platform for technical books, video courses, tutorials, playlists, and interactive labs. Use when researching technical concepts, finding authoritative book references, querying the O'Reilly content catalog, or discovering technical learning materials.
---

# O'Reilly Learning Platform Search & Discovery

Search over 50,000+ expert-vetted books, video courses, live events, and interactive materials on the O'Reilly Learning platform using the `search_oreilly_content` MCP tool.

---

## 🔍 Capabilities

The O'Reilly MCP integration allows querying:
- **Books & Chapters**: Search by topic, author, publisher, or title across O'Reilly, Packt, Pearson, Wiley, and more.
- **Courses & Videos**: Find structured courses and recorded technical deep-dives.
- **Interactive Labs & Playlists**: Discover curated skill paths and hands-on scenarios.

---

## 🛠 Available MCP Tool

### `search_oreilly_content`

```json
{
  "query": "Kubernetes security best practices",
  "n_items": 5,
  "content_types": ["books", "courses", "interactive"],
  "order_by": "relevance",
  "sort_order": "desc"
}
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | `"*"` | Search keywords or topic. |
| `n_items` | `integer` | `5` | Maximum number of results to return. |
| `content_types` | `array[string]` | `[]` (all) | Filter by types: `'books'`, `'videos'`, `'courses'`, `'articles'`, `'interactive'`, `'certifications'`, `'audiobooks'`, `'playlists'`, `'live-events'`, `'skill-plan'`. |
| `languages` | `array[string]` | `["en"]` | Language ISO codes (e.g., `["en"]`, `["fr"]`, `["de"]`). |
| `publisher_filter` | `array[string]` | `[]` | Filter by publishers (e.g., `["O'Reilly Media", "Packt Publishing"]`). |
| `author_filter` | `array[string]` | `[]` | Filter by authors (e.g., `["Martin Kleppmann", "Luciano Ramalho"]`). |
| `order_by` | `string` | `None` | Ordering: `'relevance'`, `'popularity'`, `'rating'`, `'date_added'`, `'date_published'`, `'last_updated'`, `'upcoming_events'`. |
| `sort_order` | `string` | `"desc"` | Sort direction: `'asc'` or `'desc'`. |

---

## 💡 Best Practices

1. **Be Specific with Queries**: Instead of broad terms like `"python"`, use `"python concurrency async asyncio"` or `"django graphql authentication"`.
2. **Filter by Content Type**: When looking for comprehensive literature, specify `content_types: ["books"]`. For quick walkthroughs or deep dives, use `["videos", "courses"]`.
3. **Reference Found Books**: When answering technical design questions or explaining architecture, cite the specific books and authors discovered via search to provide authoritative answers.
