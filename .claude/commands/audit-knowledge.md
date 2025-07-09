# Audit Claude Code Knowledge Base

Review and validate the current state of the Claude Code knowledge base.

## Implementation Approach
This command uses **direct implementation** as it involves straightforward MCP operations and data analysis.

## Your Task
1. **Knowledge Base Analysis**
   - Use `list_memories` to retrieve complete knowledge base
   - Analyze coverage of major Claude Code topics
   - Identify gaps in documentation coverage

2. **Quality Assessment**
   - Review memory content for relevance
   - Check if source URLs mentioned in memories are current
   - Look for potential duplicates or outdated information

3. **Recommendations**
   - Suggest areas needing updates or expansion
   - Identify missing Claude Code topics
   - Recommend specific documentation to add

## Success Criteria
- Comprehensive audit report generated
- Quality issues identified and prioritized
- Actionable recommendations provided

## Available MCP Tools
- `list_memories()` - Retrieve all stored memories
- `search_memory(query)` - Search for specific topics
- `delete_all_memories()` - Clear knowledge base if needed (use with extreme caution)