# Seed Claude Code Knowledge Base

Initialize the complete Claude Code knowledge base from authoritative sources.

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

## Implementation Approach
Main process coordinates discovery and parallel ingestion using sub-agents.

## Your Task (Main Process)

1. **Clear Existing Knowledge**
   - First, call `delete_all_memories()` to ensure clean start
   - This prevents any conflicts with existing memories

2. **Documentation Discovery**
   Launch ONE sub-agent with --dangerously-skip-permissions to:
   - Start at https://docs.anthropic.com/en/docs/claude-code/overview
   - Discover ALL pages under /docs/claude-code/ path
   - Return a complete list of URLs (not content, just URLs to save context)

3. **Parallel Ingestion**
   - Divide discovered URLs into batches (10-20 URLs per batch)
   - Launch 3-5 sub-agents in parallel with --dangerously-skip-permissions, each with a specific URL batch
   - Each sub-agent:
     - Fetches content for assigned URLs only
     - Uses `add_memories` for each page
     - Returns summary: pages processed, errors encountered
   - Wait for all sub-agents to complete before proceeding

## Sub-Agent Instructions
When launched as a sub-agent with URL list:
1. Process ONLY the assigned URLs
2. For each URL:
   - Fetch content with WebFetch
   - Extract clean, meaningful content
   - Call `add_memories(text)` with content + source URL
3. Return compressed summary (not full content)
4. NEVER call delete_all_memories

## Parallelization Strategy
- Discovery: 1 sub-agent (needs to traverse links)
- Ingestion: 3-5 sub-agents (parallel processing)
- Batch size: 10-20 URLs per sub-agent
- If >100 URLs, process in multiple rounds

3. **Report Results**
   - List all pages discovered and ingested
   - Report any failures or issues encountered
   - Provide summary of knowledge base size and organization

## Success Criteria
- Complete documentation structure mapped and ingested
- All content stored in OpenMemory with source URLs
- Clean, searchable knowledge base established

## Available MCP Tools
- `add_memories(text)` - Add new knowledge to the memory store
- `search_memory(query)` - Search for existing knowledge
- `list_memories()` - List all stored memories