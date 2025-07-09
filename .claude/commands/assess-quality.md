# Assess Content Quality in RAG Retriever

Evaluate the quality, accuracy, and reliability of content in your RAG Retriever collections to ensure high-quality search results.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup.

## Implementation Approach
This command uses **direct implementation** for systematic quality assessment of indexed content.

## Your Task

### 1. **Quality Assessment Overview**
**CRITICAL**: Poor quality, outdated, or contradictory documentation corrupts your knowledge base and leads to wrong answers. Quality assessment is essential for reliable RAG systems.

### 2. **Pre-Assessment Setup**
- Use `list_collections` to get overview of all collections
- Identify collections that need quality assessment
- Choose representative topics for each collection to test

### 3. **Systematic Quality Testing**
For each collection, perform these tests:

**A. Accuracy Testing**
- Search for 3-5 topics you know well in each collection
- Verify that answers are factually correct
- Check for incomplete or misleading information

**B. Consistency Testing**
- Search for the same topic across different collections
- Look for contradictory information
- Identify conflicting recommendations or facts

**C. Currency Testing**
- Search for version-specific information (e.g., "Python 3.12 features")
- Check if results reflect current vs. outdated information
- Look for deprecated methods or obsolete practices

**D. Relevance Testing**
- Monitor search relevance scores consistently
- Collections with scores consistently below 0.3 indicate quality issues
- Test edge cases and less common topics

### 4. **Quality Issues to Flag**
- **Contradictory information**: Same topic, different answers
- **Outdated content**: Old versions, deprecated features
- **Incomplete information**: Partial explanations, missing context
- **Poor source quality**: Unreliable or low-authority sources
- **Duplicate content**: Same information indexed multiple times

### 5. **Quality Assessment Report**
Create a report covering:
- **High-quality collections**: Accurate, current, comprehensive
- **Problem collections**: Specific quality issues identified
- **Recommendations**: Which collections need re-indexing, updating, or removal
- **Action items**: Prioritized list of quality improvements needed

### 6. **Remediation Suggestions**
- **Re-index from better sources**: Replace low-quality content
- **Remove outdated collections**: Clean up obsolete information
- **Consolidate duplicates**: Merge similar collections
- **Update content**: Refresh collections with current information

## Quality Assessment Workflow

### Sample Quality Test Queries
Use these types of queries to assess quality:

**For Technical Documentation:**
- "How to install [technology]" - Should give current installation methods
- "Best practices for [topic]" - Should reflect current standards
- "Error: [specific error]" - Should provide accurate troubleshooting

**For API Documentation:**
- "How to use [API endpoint]" - Should match current API version
- "[Function name] parameters" - Should list correct parameters
- "Authentication with [service]" - Should show current auth methods

**For General Knowledge:**
- Ask about topics you know well to verify accuracy
- Test for common misconceptions or outdated information
- Verify facts against authoritative sources

### Red Flags to Watch For
- **Inconsistent advice**: Different answers to same question
- **Version conflicts**: Multiple versions of same information
- **Broken examples**: Code that doesn't work with current versions
- **Low relevance scores**: Consistently poor search results
- **Missing context**: Answers that are technically correct but incomplete

## Success Criteria
- Systematic quality assessment of all collections
- Identification of specific quality issues and their impact
- Prioritized recommendations for improvement
- Clear action plan for maintaining content quality

## Available MCP Tools
- `list_collections()` - Get complete collection inventory
- `vector_search(query_text, collection_name, search_all_collections)` - Test search quality systematically
- `crawl_and_index_url(url, max_depth, collection_name)` - Re-index content from better sources

## Remember
Quality assessment is not a one-time activity. Schedule regular quality reviews to maintain the reliability of your RAG system. Poor quality content is worse than no content - it actively misleads users and reduces trust in the system.