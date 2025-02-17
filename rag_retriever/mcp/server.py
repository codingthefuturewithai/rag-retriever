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

from rag_retriever.main import search_content, process_url
from rag_retriever.vectorstore.store import VectorStore
from rag_retriever.search import web_search as search_module
from rag_retriever.search.searcher import Searcher
from rag_retriever.utils.config import config

# Configure logging to write to stderr instead of a file
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
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
stderr_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stderr_handler.setFormatter(formatter)
root_logger.addHandler(stderr_handler)

# Enable debug logging for all relevant loggers
logger.setLevel(logging.DEBUG)
mcp_logger.setLevel(logging.DEBUG)
uvicorn_logger.setLevel(logging.DEBUG)


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
        query: str, num_results: Optional[int] = 5
    ) -> list[types.TextContent]:
        """Perform a web search using DuckDuckGo.

        Args:
            query: Search query string
            num_results: Number of results to return (default: 5)
        """
        try:
            logger.debug(
                f"Executing web search with query: {query}, num_results: {num_results}"
            )

            # Get the raw search results from the imported module
            raw_results = search_module.web_search(query, num_results)

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
        query_text: str,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        full_content: bool = True,
    ) -> list[types.TextContent]:
        """Search the vector store for relevant content."""
        try:
            logger.debug(
                f"Executing query tool with: query='{query_text}', limit={limit}, "
                f"score_threshold={score_threshold}, full_content={full_content}"
            )

            # Capture stdout to get the JSON output
            import io
            import sys

            stdout = io.StringIO()
            sys.stdout = stdout

            # Call search_content which prints JSON to stdout
            status = search_content(
                query_text,
                limit=limit,
                score_threshold=score_threshold,
                full_content=full_content,
                json_output=True,
                verbose=True,
            )

            # Restore stdout and get the captured output
            sys.stdout = sys.__stdout__
            output = stdout.getvalue()
            logger.debug(f"Raw output from search_content: {output}")

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


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    """Entry point for the MCP server"""
    try:
        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        else:
            asyncio.run(server.run_sse_async())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
