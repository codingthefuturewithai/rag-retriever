"""MCP server implementation for RAG Retriever"""

from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.stdio import stdio_server
import mcp.types as types
import logging
import json
import sys
from urllib.parse import unquote
import asyncio
import anyio
import click
from pathlib import Path
from pydantic import Field
import os
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn

from rag_retriever.main import search_content, process_url
from rag_retriever.vectorstore.store import VectorStore
from rag_retriever.search import web_search as search_module
from rag_retriever.search.searcher import Searcher
from rag_retriever.utils.config import config

# Configure logging based on environment
log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()

# Configure logging to write to stderr instead of a file
logging.basicConfig(
    stream=sys.stderr,
    force=True,  # Force override any existing handlers
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get all relevant loggers
logger = logging.getLogger("rag_retriever.mcp")
mcp_logger = logging.getLogger("mcp.server")
uvicorn_logger = logging.getLogger("uvicorn")
root_logger = logging.getLogger()

# Remove any existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add stderr handler to root logger
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stderr_handler.setFormatter(formatter)
root_logger.addHandler(stderr_handler)

# Set log levels based on environment
logger.setLevel(log_level)
mcp_logger.setLevel(log_level)
uvicorn_logger.setLevel(log_level)
root_logger.setLevel(log_level)

if log_level == "DEBUG":
    logger.debug("RAG Retriever MCP Server starting with debug logging enabled")


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    logger.info("Creating FastMCP server")
    server = FastMCP(
        "RAG Retriever",
        host="localhost",
        port=8000,
        debug=True,
        log_level="DEBUG",
    )
    logger.info("FastMCP server instance created")
    logger.debug(f"Server attributes: {dir(server)}")
    logger.debug(f"Server configuration: {vars(server)}")

    # Register all tools with the server
    register_tools(server)

    return server


def register_tools(mcp_server: FastMCP) -> None:
    """Register all MCP tools with the server"""

    @mcp_server.tool(
        name="list_collections",
        description="List all available vector store collections with document counts, creation dates, and metadata. Shows which collections contain indexed content for semantic search. No parameters required.",
    )
    def list_collections() -> list[types.TextContent]:
        """List all available collections in the vector store.
        
        Returns information about each collection including:
        - Collection name
        - Number of documents
        - Creation/modification timestamps (if available)
        """
        try:
            logger.debug("Listing vector store collections")
            
            # Create a VectorStore instance to access collection information
            store = VectorStore()
            collections = store.list_collections()
            
            if not collections:
                return [types.TextContent(type="text", text="No collections found in the vector store.")]
            
            # Format collections as markdown
            markdown = "# Vector Store Collections\n\n"
            
            for collection in collections:
                name = collection.get("name", "Unknown")
                count = collection.get("count", 0)
                
                markdown += f"## {name}\n\n"
                markdown += f"**Document Count:** {count}\n\n"
                
                # Add metadata if available
                if "metadata" in collection and collection["metadata"]:
                    markdown += "**Metadata:**\n"
                    for key, value in collection["metadata"].items():
                        markdown += f"- {key}: {value}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
            
            return [types.TextContent(type="text", text=markdown)]
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error listing collections: {str(e)}")]

    @mcp_server.tool(
        name="web_search",
        description="Search the web using Google or DuckDuckGo. Takes a search query string, optional number of results (default 5), and optional provider ('google' or 'duckduckgo'). Returns web search results with titles, URLs, and snippets.",
    )
    def web_search(
        search_string: str = Field(description="Search query string"),
        num_results: Optional[int] = Field(
            description="Number of results to return (if None, uses default from config)",
            default=None,
            ge=1,
        ),
        provider: Optional[str] = Field(
            description="Search provider to use ('google' or 'duckduckgo'). If not specified, uses default from config. "
            "When Google is used (either by default or explicitly) but credentials aren't configured, "
            "it falls back to DuckDuckGo for default case or shows error for explicit case.",
            default=None,
            choices=["google", "duckduckgo"],
        ),
    ) -> list[types.TextContent]:
        """Perform a web search using the specified provider.

        Args:
            search_string: Search query string
            num_results: Number of results to return (uses default from config if None)
            provider: Search provider to use ('google' or 'duckduckgo').
                     If not specified, uses default from config.
                     When Google is used (either by default or explicitly) but credentials aren't configured,
                     it falls back to DuckDuckGo for default case or shows error for explicit case.
        """
        try:
            logger.debug(
                f"Executing web search with query: {search_string}, "
                f"num_results: {num_results}, provider: {provider}"
            )

            # Get the raw search results from the imported module
            raw_results = search_module.web_search(
                search_string, num_results=num_results, provider=provider
            )

            if not raw_results:
                return [types.TextContent(type="text", text="No results found.")]

            # Format results as markdown
            markdown = "# Web Search Results\n\n"
            for i, result in enumerate(raw_results, 1):
                markdown += f"## {i}. {result.title}\n\n"
                markdown += f"**URL:** {result.url}\n\n"
                markdown += f"{result.snippet}\n\n---\n\n"

            return [types.TextContent(type="text", text=markdown)]

        except ValueError as e:
            # This will be raised when Google is explicitly requested but not configured
            logger.error(f"ValueError in web_search: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            logger.error(f"Error in web_search: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    @mcp_server.tool(
        name="vector_search",
        description="Search indexed content using semantic similarity. Takes a query string, optional result limit (default 8), optional score threshold (default 0.3), optional collection name (defaults to 'default'), and optional search_all_collections flag. Returns relevant documents with scores and source information.",
    )
    async def query(
        query_text: str = Field(description="The search query text"),
        limit: Optional[int] = Field(
            description="Maximum number of results to return", default=None, ge=1
        ),
        score_threshold: Optional[float] = Field(
            description="Minimum score threshold for results",
            default=None,
            ge=0.0,
            le=1.0,
        ),
        full_content: bool = Field(
            description="Whether to return full content", default=True
        ),
        collection_name: Optional[str] = Field(
            description="Name of collection to search in (defaults to 'default')",
            default=None,
        ),
        search_all_collections: bool = Field(
            description="Whether to search across all collections",
            default=False,
        ),
    ) -> list[types.TextContent]:
        """Search the vector store for relevant content."""
        try:
            # Direct prints to stderr to bypass logging
            print("DIRECT PRINT: Query function entered", file=sys.stderr, flush=True)
            print(
                f"DIRECT PRINT: Arguments received - query_text: {query_text}, limit: {limit}",
                file=sys.stderr,
                flush=True,
            )

            logger.info("QUERY FUNCTION CALLED - INFO LEVEL")
            logger.debug("QUERY FUNCTION CALLED - DEBUG LEVEL")

            # Ensure proper handling of optional parameters
            actual_limit = limit if limit is not None else None
            actual_score_threshold = (
                score_threshold if score_threshold is not None else None
            )

            logger.debug(
                f"Query parameters: query='{query_text}', limit={actual_limit}, "
                f"score_threshold={actual_score_threshold}, full_content={full_content}, "
                f"collection_name={collection_name}, search_all_collections={search_all_collections}"
            )

            # Capture stdout using StringIO
            import io

            stdout = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = stdout

            try:
                logger.debug("Calling search_content function")
                # Call search_content which prints JSON to stdout
                status = search_content(
                    query_text,
                    limit=actual_limit,
                    score_threshold=actual_score_threshold,
                    full_content=full_content,
                    json_output=True,
                    verbose=True,
                    collection_name=collection_name,
                    search_all_collections=search_all_collections,
                )
                logger.debug("search_content function completed")
            finally:
                # Restore stdout and get the captured output
                sys.stdout = original_stdout
                output = stdout.getvalue()
                logger.debug(f"Raw search output: {output}")

            # If no results found in the output message
            if "No results found matching the query" in output:
                logger.debug("No results found in search output")
                return [
                    types.TextContent(
                        type="text", text="No results found matching your query."
                    )
                ]

            # If output is empty or whitespace only
            if not output.strip():
                logger.debug("Empty output from search_content")
                return [
                    types.TextContent(
                        type="text", text="No results found matching your query."
                    )
                ]

            # Parse the JSON results
            try:
                results = json.loads(output.strip())
                if not results:
                    logger.debug("Empty results list after JSON parsing")
                    return [
                        types.TextContent(
                            type="text", text="No results found matching your query."
                        )
                    ]
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON output: {e}\nOutput was: {output}")
                return [
                    types.TextContent(
                        type="text", text="No results found matching your query."
                    )
                ]

            # Format results as markdown
            if not results:
                return [
                    types.TextContent(
                        type="text", text="No results found matching your query."
                    )
                ]

            sections = []
            for i, item in enumerate(results, 1):
                section = []
                section.append(f"## Result {i} (Score: {item['score']:.2f})")
                if item.get("source"):
                    section.append(f"\n**Source:** {item['source']}")
                if item.get("collection"):
                    section.append(f"\n**Collection:** {item['collection']}")
                section.append(f"\n{item['content']}")
                section.append("\n---")
                sections.append("\n".join(section))

            markdown = "# Search Results\n\n" + "\n\n".join(sections)

            logger.debug(f"Query returned {len(results)} results")
            return [types.TextContent(type="text", text=markdown)]

        except Exception as e:
            logger.error(f"Error in query: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    @mcp_server.tool(
        name="crawl_and_index_url",
        description="Crawl a website and index its content for semantic search. Takes a URL, optional max_depth for recursive crawling (default 2), and optional collection_name (defaults to 'default'). Processes web pages, extracts text, and stores in vector database. Returns confirmation when crawling starts.",
    )
    async def fetch_url(
        url: str = Field(description="URL to fetch and process"),
        max_depth: Optional[int] = Field(
            description="Maximum depth for recursive URL loading", default=2, ge=0
        ),
        collection_name: Optional[str] = Field(
            description="Name of collection to store content in (defaults to 'default')",
            default=None,
        ),
    ) -> list[types.TextContent]:
        """Fetch and process content from a URL, optionally crawling linked pages.

        Uses the existing RAG Retriever web scraping functionality to fetch, process,
        and store content in the vector store.
        """
        try:
            logger.debug(f"Processing URL: {url} with max_depth: {max_depth}")

            # Use exact same pattern as CLI's --fetch command
            actual_max_depth = max_depth if max_depth is not None else 2

            # Create a background task to handle the processing
            async def process_url_task():
                try:
                    # Capture stdout to get progress information
                    import io
                    import sys

                    stdout = io.StringIO()
                    original_stdout = sys.stdout
                    sys.stdout = stdout

                    try:
                        # Call process_url with same parameters as CLI
                        status = await asyncio.to_thread(
                            process_url,
                            url,  # First positional arg like CLI
                            max_depth=actual_max_depth,  # Named arg like CLI
                            verbose=True,  # Always enable verbose for MCP feedback
                            collection_name=collection_name,  # Pass collection name
                        )
                    finally:
                        # Restore stdout and get the captured output
                        sys.stdout = original_stdout
                        output = stdout.getvalue()
                        logger.debug(f"Captured output: {output}")

                except Exception as e:
                    logger.error(f"Error in background task: {e}", exc_info=True)

            # Start the background task
            asyncio.create_task(process_url_task())

            # Return immediately with a status message
            collection_info = (
                f" in collection '{collection_name}'" if collection_name else ""
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"# URL Processing Started\n\n"
                    f"Started processing URL: {url} with max_depth={actual_max_depth}{collection_info}\n\n"
                    f"The processing will continue in the background. You can proceed with other operations.\n\n"
                    f"Note: The content will be available for querying once processing is complete.",
                )
            ]

        except Exception as e:
            logger.error(f"Error initiating URL processing: {e}", exc_info=True)
            return [
                types.TextContent(type="text", text=f"Error processing URL: {str(e)}")
            ]


def run_sse_server(port: int = 8000) -> None:
    """Run the server in SSE mode using FastMCP's built-in SSE support."""
    logger.info(f"Starting SSE server on port {port}")

    # Create a new server instance for SSE
    sse_server = create_mcp_server()
    sse_server.settings.port = port

    # Run the server in SSE mode
    asyncio.run(sse_server.run_sse_async())


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()

# Create stdio server for MCP clients
app = stdio_server(server)

# Only define these if running the file directly
if __name__ == "__main__":

    @click.command()
    @click.option("--port", default=3001, help="Port to listen on for SSE")
    def main(port: int) -> None:
        """Run the server directly in SSE mode."""
        run_sse_server(port)

    main()
