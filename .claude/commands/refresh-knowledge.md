# Refresh Claude Code Knowledge

Update the Claude Code knowledge base by completely replacing it with fresh content.

## ⚠️ CRITICAL: Known OpenMemory MCP Bug

**The OpenMemory MCP server has a validation error bug that affects ALL memory operations:**

```
validation error for add_memoriesOutput
result
  Input should be a valid string [type=string_type, input_value={'results': []}, input_type=dict]
```

**IMPORTANT INSTRUCTIONS:**
1. **This error does NOT mean the operation failed** - memories ARE successfully stored
2. **You MUST ignore these validation errors** and continue as if the operation succeeded
3. **Do NOT retry operations** when you see this error - it will create duplicates
4. **Verify success** by checking the OpenMemory UI or using list_memories() after completion

This is a known issue with OpenMemory returning dict responses instead of strings. The error is cosmetic only.

## Arguments
Use $ARGUMENTS to specify what to refresh:
- "documentation" - refresh all official docs
- "blogs" - find and add recent blog insights
- "complete" - full refresh of everything

## CRITICAL: Full Refresh Strategy
Due to OpenMemory limitations (no selective update/delete), we MUST:
1. Delete ALL memories at the start
2. Rebuild from scratch
3. This prevents conflicting or outdated information

## Implementation Approach

### For Any Refresh (Main Process)
1. **IMMEDIATELY** call `delete_all_memories()` to clear the knowledge base
2. Discover all URLs that need to be crawled
3. Divide URLs into batches for parallel processing
4. Launch 3-5 sub-agents with specific URL assignments
5. Wait for all sub-agents to complete
6. Report summary of what was added

### Sub-Agent Task (Parallel Execution)
Launch sub-agents with --dangerously-skip-permissions, each handling specific URLs:
1. Crawl assigned pages only
2. Extract content and use `add_memories()` for each page
3. Return compressed summary: number of pages processed, any errors
4. NEVER call delete_all_memories in sub-agents

### Parallelization Guidelines
- Maximum 5 sub-agents for documentation crawl
- Each sub-agent gets ~10-20 pages
- If more pages exist, reuse sub-agents for additional batches
- Prioritize reliability over speed

### For Blog Insights (Sub-Agent Task)
1. Launch sub-agent with --dangerously-skip-permissions to search https://anthropic.com/blog for recent posts about:
   - "Claude Code"
   - "agentic coding"
   - "best practices"
   - "development workflows"
2. Extract relevant insights and practical tips
3. Add to knowledge base with appropriate metadata

## Success Criteria
- Targeted refresh completed successfully
- Report what new content was added
- Knowledge base maintains consistency and accuracy

## Available MCP Tools
- `add_memories(text)` - Add new or updated knowledge
- `search_memory(query)` - Find existing knowledge on a topic
- `list_memories()` - List all stored memories