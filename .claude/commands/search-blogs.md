# Search for Recent Claude Code Insights

Find and incorporate recent Anthropic blog posts and insights about Claude Code best practices.

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
Use $ARGUMENTS to specify search focus:
- "best practices"
- "workflows"
- "tutorials"
- "updates"
- etc.

## Implementation Approach
Main process coordinates blog discovery and manages memory updates.

## Your Task (Main Process)

1. **Blog Discovery Phase**
   Launch 2 sub-agents in parallel with --dangerously-skip-permissions:
   - Sub-agent 1: Search https://anthropic.com/blog
   - Sub-agent 2: Search https://anthropic.com/engineering
   - Each searches for posts from last 6 months about Claude Code
   - Returns list of relevant URLs with brief summaries

2. **Content Extraction Phase**
   - Review discovered blog URLs
   - Divide URLs among 2-3 sub-agents for parallel processing
   - Each sub-agent:
     - Fetches full blog content
     - Extracts Claude Code specific insights
     - Uses `add_memories` for each valuable insight
     - Returns summary of insights added

3. **Coordination**
   - Wait for all sub-agents to complete
   - Compile summary of all new insights added
   - Report total blog posts processed

## Sub-Agent Instructions
When launched as a sub-agent:
1. Search/process ONLY assigned blog source or URLs
2. Focus on Claude Code specific content:
   - Best practices
   - Workflow improvements
   - New features
   - Practical tips
3. Call `add_memories(text)` for each insight with source URL
4. Return compressed summary
5. NEVER call delete_all_memories

## Note on Updates
Unlike full refresh, blog searches typically ADD new insights without deleting existing knowledge, as blog posts are additive content.

## Success Criteria
- Recent relevant insights discovered and added
- Practical tips and workflows incorporated
- Knowledge base enhanced with community wisdom

## Available MCP Tools
- `add_memories(text)` - Add new blog insights
- `search_memory(query)` - Check for existing knowledge
- `list_memories()` - List all stored memories