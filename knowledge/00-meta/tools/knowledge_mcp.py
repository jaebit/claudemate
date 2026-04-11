#!/usr/bin/env python3
"""MCP thin wrapper server for knowledge vault."""

import json
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

# Knowledge vault paths
KNOWLEDGE_ROOT = Path(__file__).parent.parent.parent
GRAPH_PATH = KNOWLEDGE_ROOT / "10-wiki" / "graph.json"
WIKI_PATH = KNOWLEDGE_ROOT / "10-wiki" / "modules"
MEMORY_PATH = KNOWLEDGE_ROOT / "30-memory"
BUDGET_PATH = KNOWLEDGE_ROOT / "00-meta" / "retrieval-budget.yaml"

def load_json_file(path: Path) -> Dict[str, Any]:
    """Load JSON file or return empty dict."""
    return json.load(open(path, 'r', encoding='utf-8')) if path.exists() else {}

def load_yaml_file(path: Path) -> Dict[str, Any]:
    """Load YAML file or return empty dict."""
    return yaml.safe_load(open(path, 'r', encoding='utf-8')) if path.exists() else {}

def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from content."""
    if not content.startswith('---\n'):
        return {}, content
    try:
        end_marker = content.find('\n---\n', 4)
        if end_marker == -1:
            return {}, content
        frontmatter_text = content[4:end_marker]
        body = content[end_marker + 5:]
        frontmatter = yaml.safe_load(frontmatter_text) or {}
        return frontmatter, body
    except:
        return {}, content

def graph_query(module_name: str, relation_type: str = "all") -> Dict[str, Any]:
    """Query module relationships from graph.json."""
    modules = load_json_file(GRAPH_PATH).get("modules", {})

    if module_name not in modules:
        return {"success": False, "error": f"Module '{module_name}' not found", "available_modules": list(modules.keys())}

    module_info = modules[module_name]
    result = {"success": True, "module": module_name, "path": module_info.get("path"), "version": module_info.get("version"), "relations": {}}

    if relation_type in ["dependsOn", "all"]:
        result["relations"]["dependsOn"] = module_info.get("dependencies", [])

    if relation_type in ["dependedBy", "all"]:
        dependents = [mod for mod, info in modules.items() if module_name in info.get("dependencies", [])]
        result["relations"]["dependedBy"] = dependents

    return result

def memory_search(keyword: str, memory_type: str = "all", min_confidence: float = 0.0) -> Dict[str, Any]:
    """Search memory notes by keyword."""
    results = []
    search_dirs = []

    if memory_type in ["factual", "all"]:
        search_dirs.append(MEMORY_PATH / "facts")
    if memory_type in ["experiential", "all"]:
        search_dirs.append(MEMORY_PATH / "experiences")

    keyword_lower = keyword.lower()

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for md_file in search_dir.glob("**/*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                frontmatter, body = parse_frontmatter(content)

                confidence = frontmatter.get("confidence", 1.0)
                if confidence < min_confidence:
                    continue

                title = frontmatter.get("title", md_file.stem)
                if keyword_lower in (title + " " + body).lower():
                    body_lower = body.lower()
                    idx = body_lower.find(keyword_lower)
                    snippet = body[max(0, idx - 50):min(len(body), idx + 100)].strip() if idx >= 0 else body[:150].strip()

                    results.append({
                        "title": title,
                        "type": "factual" if "facts" in str(search_dir) else "experiential",
                        "confidence": confidence,
                        "snippet": snippet + ("..." if len(snippet) == 150 else ""),
                        "path": str(md_file.relative_to(KNOWLEDGE_ROOT))
                    })
            except:
                continue

    return {"success": True, "keyword": keyword, "memory_type": memory_type, "results": sorted(results, key=lambda x: x["confidence"], reverse=True)}

def wiki_lookup(module_name: str) -> Dict[str, Any]:
    """Lookup module wiki page."""
    wiki_file = WIKI_PATH / f"{module_name}.md"

    if not wiki_file.exists():
        return {"success": False, "error": f"Wiki page for module '{module_name}' not found", "path": str(wiki_file)}

    try:
        content = wiki_file.read_text(encoding='utf-8')
        frontmatter, body = parse_frontmatter(content)
        return {"success": True, "module": module_name, "path": str(wiki_file.relative_to(KNOWLEDGE_ROOT)), "frontmatter": frontmatter, "content": body}
    except Exception as e:
        return {"success": False, "error": f"Failed to read wiki page: {str(e)}", "path": str(wiki_file)}

def page_index_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search knowledge wiki using PageIndex tree-search (no vectors required)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "page_index", Path(__file__).parent / "page_index.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        index = mod.build_index(KNOWLEDGE_ROOT / "10-wiki")
        results = mod.search_tree(index, query, max_results=max_results)
        return {"success": True, "query": query, "results": results, "total_indexed": len(index)}
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}

def retrieve_context(task_type: str, module: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve context within token budget for task type."""
    budgets = load_yaml_file(BUDGET_PATH).get("retrieval_budget", {})

    if task_type not in budgets:
        return {"success": False, "error": f"Unknown task_type '{task_type}'", "available_types": list(budgets.keys())}

    budget = budgets[task_type]
    context = {"success": True, "task_type": task_type, "module": module, "budget_used": {"wiki": 0, "factual": 0, "experiential": 0}, "content": {"wiki": [], "factual": [], "experiential": []}}

    # 1. Wiki content (if module specified)
    wiki_budget = budget.get("wiki_tokens", 0)
    if module and wiki_budget > 0:
        wiki_result = wiki_lookup(module)
        if wiki_result["success"]:
            content = wiki_result["content"]
            estimated_tokens = len(content) // 4
            if estimated_tokens <= wiki_budget:
                context["content"]["wiki"].append({"module": module, "content": content, "tokens": estimated_tokens})
                context["budget_used"]["wiki"] = estimated_tokens

    # 2. Factual memories
    factual_budget = budget.get("factual_tokens", 0)
    if factual_budget > 0:
        memory_result = memory_search(module if module else task_type, "factual", 0.7)
        used_tokens = 0
        for fact in memory_result["results"]:
            fact_tokens = len(fact["snippet"]) // 4
            if used_tokens + fact_tokens <= factual_budget:
                context["content"]["factual"].append(fact)
                used_tokens += fact_tokens
            else:
                break
        context["budget_used"]["factual"] = used_tokens

    # 3. Experiential memories
    exp_budget = budget.get("experiential_tokens", 0)
    if exp_budget > 0:
        exp_result = memory_search(module if module else task_type, "experiential", 0.5)
        used_tokens = 0
        for exp in exp_result["results"]:
            exp_tokens = len(exp["snippet"]) // 4
            if used_tokens + exp_tokens <= exp_budget:
                context["content"]["experiential"].append(exp)
                used_tokens += exp_tokens
            else:
                break
        context["budget_used"]["experiential"] = used_tokens

    return context

# MCP Protocol Implementation
def handle_initialize(params):
    return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "knowledge-mcp", "version": "1.0.0"}}

def handle_list_tools(params):
    return {"tools": [
        {"name": "graph_query", "description": "Query module relationships from dependency graph", "inputSchema": {"type": "object", "properties": {"module_name": {"type": "string", "description": "Module name to query"}, "relation_type": {"type": "string", "enum": ["dependsOn", "dependedBy", "all"], "default": "all"}}, "required": ["module_name"]}},
        {"name": "memory_search", "description": "Search memory notes by keyword", "inputSchema": {"type": "object", "properties": {"keyword": {"type": "string", "description": "Search keyword"}, "memory_type": {"type": "string", "enum": ["factual", "experiential", "all"], "default": "all"}, "min_confidence": {"type": "number", "minimum": 0, "maximum": 1, "default": 0}}, "required": ["keyword"]}},
        {"name": "wiki_lookup", "description": "Lookup module wiki page content", "inputSchema": {"type": "object", "properties": {"module_name": {"type": "string", "description": "Module name to lookup"}}, "required": ["module_name"]}},
        {"name": "retrieve_context", "description": "Retrieve token-budget-aware context for task type", "inputSchema": {"type": "object", "properties": {"task_type": {"type": "string", "enum": ["explore", "locate", "edit", "validate"]}, "module": {"type": "string", "description": "Optional module focus"}}, "required": ["task_type"]}},
        {"name": "page_index_search", "description": "Tree-based lexical search over knowledge wiki pages", "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}}
    ]}

def handle_call_tool(params):
    tool_name = params.get("name")
    args = params.get("arguments", {})

    try:
        if tool_name == "graph_query":
            result = graph_query(args["module_name"], args.get("relation_type", "all"))
        elif tool_name == "memory_search":
            result = memory_search(args["keyword"], args.get("memory_type", "all"), args.get("min_confidence", 0))
        elif tool_name == "wiki_lookup":
            result = wiki_lookup(args["module_name"])
        elif tool_name == "retrieve_context":
            result = retrieve_context(args["task_type"], args.get("module"))
        elif tool_name == "page_index_search":
            result = page_index_search(args["query"], args.get("max_results", 10))
        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}

        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error: {str(e)}"}]}

def main():
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "initialize":
                response = handle_initialize(params)
            elif method == "tools/list":
                response = handle_list_tools(params)
            elif method == "tools/call":
                response = handle_call_tool(params)
            else:
                response = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

            output = {"jsonrpc": "2.0", "id": request_id}
            if "error" in response:
                output["error"] = response["error"]
            else:
                output["result"] = response

            print(json.dumps(output), flush=True)

        except Exception as e:
            error_response = {"jsonrpc": "2.0", "id": request.get("id") if 'request' in locals() else None, "error": {"code": -32603, "message": f"Internal error: {str(e)}"}}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()