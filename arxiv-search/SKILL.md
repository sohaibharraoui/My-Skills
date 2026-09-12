---
name: arxiv-search
description: Search arXiv research papers, download papers, inspect abstracts, query citation graphs, and extract LaTeX sections. Use when researching academic papers, finding scientific literature, citing preprints, or extracting math equations from arXiv.
---

# arXiv Academic Research & Literature Discovery

Search, retrieve, analyze, and cite academic preprints across Computer Science, AI, Mathematics, Physics, Quantitative Biology, Quantitative Finance, and Statistics using the `arxiv` MCP tools.

---

## 🔍 Capabilities

The arXiv MCP server (`blazickjp/arxiv-mcp-server`) connects agents directly to arXiv's repository:
- **Search & Discovery**: Query by keywords, topics, authors, and arXiv subject categories with date/relevance sorting.
- **Abstract & Metadata**: Inspect paper titles, authors, categories, publication dates, and abstracts without full downloads.
- **Full Text Reading**: Download and parse papers into structured Markdown for detailed analysis and synthesis.
- **LaTeX Source Extraction**: Extract raw LaTeX sections to preserve exact mathematical formulas, theorems, and algorithms.
- **Citation Graph & Export**: Explore paper citations, references, and export BibTeX records.
- **Topic Monitoring**: Watch research topics and check alerts for new preprint publications.

---

## 🛠 Available MCP Tools

### 1. `search_papers`
Search arXiv for research papers matching a query.
```json
{
  "query": "Retrieval Augmented Generation hallucination",
  "max_results": 5,
  "sort_by": "relevance",
  "sort_order": "descending"
}
```

### 2. `get_abstract`
Fetch the abstract and detailed metadata for a specific paper by its arXiv ID.
```json
{
  "paper_id": "2312.10997"
}
```

### 3. `download_paper`
Download and parse a paper to local storage for full-text reading and semantic search.
```json
{
  "paper_id": "1706.03762"
}
```

### 4. `list_papers`
List all papers currently downloaded to local storage.
```json
{}
```

### 5. `read_paper`
Read the contents of a previously downloaded paper from local storage.
```json
{
  "paper_id": "1706.03762"
}
```

### 6. `get_paper_latex` & `get_paper_latex_section`
Extract raw LaTeX source or specific sections (e.g. methodology, equations) from an arXiv paper.
```json
{
  "paper_id": "1706.03762",
  "section_name": "Attention"
}
```

### 7. `citation_graph` & `export_citations`
Traverse citations and export BibTeX entries for literature reviews.
```json
{
  "paper_id": "1706.03762",
  "format": "bibtex"
}
```

---

## 💡 Best Practices

1. **Start with Search / Abstract**: Use `search_papers` or `get_abstract` first to identify the most relevant papers before downloading full text.
2. **Preserve Mathematical Precision**: When analyzing formal models, loss functions, or proofs, use `get_paper_latex_section` to inspect the author's original LaTeX equations.
3. **Structured Citations**: When citing arXiv papers in documentation or research notes, include the arXiv ID, authors, publication year, and URL link (e.g. `https://arxiv.org/abs/<id>`).
