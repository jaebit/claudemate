---
title: "{{fact_title}}"
zone: memory
memory_type: factual
canonical_id: "{{canonical_id}}"
confidence: 1.0
source_task: "{{source_task}}"
source_commit: "{{commit_sha}}"
related_modules: []
created: "{{date}}"
last_updated: "{{date}}"
needs_review: false
tags: [memory, factual]
---

# {{fact_title}}

## Fact

<!-- LLM-ZONE -->
{{fact_statement}}
<!-- /LLM-ZONE -->

## Evidence

<!-- LLM-ZONE -->
{{evidence}}
<!-- /LLM-ZONE -->

## Scope

<!-- LLM-ZONE -->
- **Applies to**: {{scope}}
- **Verified in**: `{{source_file}}`
<!-- /LLM-ZONE -->

## Related

<!-- LLM-ZONE -->
{{related_links}}
<!-- /LLM-ZONE -->
