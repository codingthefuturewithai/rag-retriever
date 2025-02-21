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

    @mcp_server.tool()
    def web_search(
        search_string: str = Field(description="Search query string"),
        num_results: Optional[int] = Field(
            description="Number of results to return", default=5, ge=1
        ),
    ) -> list[types.TextContent]:
        """Perform a web search using DuckDuckGo.

        Args:
            search_string: Search query string
            num_results: Number of results to return (default: 5)
        """
        try:
            # Ensure num_results has a value
            actual_num_results = num_results if num_results is not None else 5

            logger.debug(
                f"Executing web search with query: {search_string}, num_results: {actual_num_results}"
            )

            # Get the raw search results from the imported module
            raw_results = search_module.web_search(search_string, actual_num_results)

            if not raw_results:
                return [types.TextContent(type="text", text="No results found.")]

            # Format results as markdown
            markdown = "# Web Search Results\n\n"
            for i, result in enumerate(raw_results, 1):
                markdown += f"## {i}. {result.title}\n\n"
                markdown += f"**URL:** {result.url}\n\n"
                markdown += f"{result.snippet}\n\n---\n\n"

            return [types.TextContent(type="text", text=markdown)]

        except Exception as e:
            logger.error(f"Error in web_search: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    @mcp_server.tool()
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
                f"score_threshold={actual_score_threshold}, full_content={full_content}"
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
                section.append(f"\n{item['content']}")
                section.append("\n---")
                sections.append("\n".join(section))

            markdown = "# Search Results\n\n" + "\n\n".join(sections)

            logger.debug(f"Query returned {len(results)} results")
            return [types.TextContent(type="text", text=markdown)]

        except Exception as e:
            logger.error(f"Error in query: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    @mcp_server.tool()
    async def fetch_url(
        url: str = Field(description="URL to fetch and process"),
        max_depth: Optional[int] = Field(
            description="Maximum depth for recursive URL loading", default=2, ge=0
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
                )
            finally:
                # Restore stdout and get the captured output
                sys.stdout = original_stdout
                output = stdout.getvalue()
                logger.debug(f"Captured output: {output}")

            if status == 0:  # Success status from process_url
                # Format the output as markdown, preserving progress information
                progress_text = (
                    output.strip() if output.strip() else "No progress output captured"
                )
                return [
                    types.TextContent(
                        type="text",
                        text=f"# URL Processing Complete\n\n"
                        f"Successfully processed URL: {url}\n\n"
                        f"## Progress Details\n\n```\n{progress_text}\n```\n\n"
                        f"Content has been stored in the vector store and is ready for querying.",
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Failed to process URL: {url} (status: {status})\n\n"
                        f"## Debug Output\n\n```\n{output}\n```",
                    )
                ]

        except Exception as e:
            logger.error(f"Error processing URL: {e}", exc_info=True)
            return [
                types.TextContent(type="text", text=f"Error processing URL: {str(e)}")
            ]


def run_sse_server(port: int = 8000) -> None:
    """Run the server in SSE mode using FastMCP's built-in SSE support."""
    logger.info(f"Starting SSE server on port {port}")

    # Create a new server instance for SSE
    sse_server = create_mcp_server()

    # Create Starlette app with SSE routes
    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=sse_server.handle_sse_request),
            Mount("/messages/", app=sse_server.handle_sse_messages),
        ],
    )

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()

# Only define these if running the file directly
if __name__ == "__main__":

    @click.command()
    @click.option("--port", default=3001, help="Port to listen on for SSE")
    def main(port: int) -> None:
        """Run the server directly in SSE mode."""
        logger.info(f"Starting SSE server on port {port}")

        # Update the server's port setting
        server.settings.port = port

        # Run the server in SSE mode using FastMCP's built-in support
        asyncio.run(server.run_sse_async())

    main()
