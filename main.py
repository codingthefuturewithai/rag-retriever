from dotenv import load_dotenv
import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup, NavigableString
import argparse
import json
import warnings
from bs4 import GuessedAtParserWarning
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

load_dotenv()

# Set default persist directory to ./chromadb
DEFAULT_PERSIST_DIR = os.path.join(os.getcwd(), "chromadb")

# Common navigation and UI patterns to remove
UI_PATTERNS = [
    r"Theme\s+Auto\s+Light\s+Dark",
    r"Previous\s+topic|Next\s+topic",
    r"Navigation",
    r"Jump\s+to",
    r"Search",
    r"Skip\s+to\s+content",
]


def clean_text_content(element):
    """
    Recursively clean and extract text from HTML elements while preserving structure.
    """
    if isinstance(element, NavigableString):
        return element.strip()

    # Skip navigation and UI elements
    if (
        element.name in ["nav", "header", "footer"]
        or element.get("role") == "navigation"
    ):
        return ""

    # Skip elements with certain classes or IDs that typically contain navigation/UI
    classes = element.get("class", [])
    if any(c for c in classes if "nav" in c.lower() or "menu" in c.lower()):
        return ""

    # Preserve code blocks
    if element.name in ["pre", "code"]:
        return "\n" + element.get_text() + "\n"

    # Handle main content areas with special attention
    if element.name == "main" or element.get("role") == "main":
        text = " ".join(
            clean_text_content(child)
            for child in element.children
            if clean_text_content(child)
        )
        return "\n" + text + "\n"

    # Handle paragraphs and block elements
    if element.name in ["p", "div", "section", "article"]:
        text = " ".join(
            clean_text_content(child)
            for child in element.children
            if clean_text_content(child)
        )
        return "\n" + text + "\n" if text else ""

    # Handle headers with hierarchy
    if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(element.name[1])
        prefix = "#" * level + " "
        text = element.get_text().strip()
        return f"\n{prefix}{text}\n" if text else ""

    # Handle lists
    if element.name in ["ul", "ol"]:
        items = [
            clean_text_content(li) for li in element.find_all("li", recursive=False)
        ]
        return (
            "\n"
            + "\n".join(f"• {item.strip()}" for item in items if item.strip())
            + "\n"
        )

    # Recursively process other elements
    return " ".join(
        clean_text_content(child)
        for child in element.children
        if clean_text_content(child)
    )


def extract_clean_text(html_content):
    """
    Extract and clean text from HTML while preserving meaningful structure.
    """
    # Suppress parser warnings - we intentionally use lxml's html parser for maximum compatibility
    # lxml handles both HTML5 and XHTML, and is more forgiving of malformed markup than strict XML parsing
    warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

    soup = BeautifulSoup(
        html_content, "lxml"
    )  # Using lxml for speed and flexibility with all HTML types

    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()

    # Extract main content
    main_content = soup.find("main") or soup.find("article") or soup.find("body")
    if not main_content:
        main_content = soup

    # Get cleaned text
    text = clean_text_content(main_content)

    # Post-process the text
    # Replace multiple newlines with double newline (to preserve paragraph breaks)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    # Remove UI patterns
    for pattern in UI_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()


def get_embeddings():
    """Get OpenAI embeddings instance."""
    return OpenAIEmbeddings(model="text-embedding-3-large", dimensions=3072)


def get_page_content(url: str) -> str:
    """Get page content using Selenium for JavaScript support."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Wait for dynamic content to load
        time.sleep(2)
        content = driver.page_source
        driver.quit()
        return content
    except Exception as e:
        print(f"Error fetching page with Selenium: {str(e)}")
        raise


def load_url_to_docs(url: str, max_depth: int = 2):
    """Load and parse documents from a URL using Selenium for JavaScript support."""
    try:
        print(f"Attempting to load URL: {url} with max_depth: {max_depth}")
        content = get_page_content(url)
        # Clean and process the content
        cleaned_text = extract_clean_text(content)

        # Create a Document with metadata
        from langchain_core.documents import Document

        doc = Document(page_content=cleaned_text, metadata={"source": url})

        print(f"Successfully loaded document with {len(cleaned_text)} characters")
        return [doc]
    except Exception as e:
        print(f"Error loading URL: {str(e)}")
        raise


def get_or_create_db(
    persist_directory: str = DEFAULT_PERSIST_DIR,
    documents=None,
    json_output: bool = False,
):
    """Get existing vector store or create a new one if it doesn't exist."""
    embeddings = get_embeddings()

    # Check if the directory exists and has contents
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        if not json_output:
            print(f"Loading existing vector store from: {persist_directory}")
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )

    if documents is None:
        raise ValueError(
            "No existing vector store found and no documents provided to create one."
        )

    if not json_output:
        print(f"Creating new vector store at: {persist_directory}")

    # Create the directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)

    # Create and return the database
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
    )


def process_and_store_documents(
    docs, persist_directory: str = DEFAULT_PERSIST_DIR, json_output: bool = False
):
    """Process documents by splitting them into chunks and store in Chroma."""
    # Initialize text splitter for better chunk sizes
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )

    # Split documents into chunks
    splits = text_splitter.split_documents(docs)

    # Create or update vector store
    db = get_or_create_db(persist_directory, splits, json_output)
    return len(splits)


def search_documents(
    query: str,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    limit: int = 5,
    json_output: bool = False,
    score_threshold: float = 0.2,
):
    """Search the vector store for relevant documents.

    The relevance scores typically range from 0.0 to 1.0, where:
    - Scores around 0.3+ indicate high relevance
    - Scores around 0.2-0.3 indicate moderate relevance
    - Scores below 0.2 indicate low relevance
    """
    try:
        db = get_or_create_db(persist_directory, json_output=json_output)

        # Old implementation using similarity_search_with_score
        # results = db.similarity_search_with_score(query, k=limit)
        # if not json_output:
        #     print("\nDebug - Raw results with scores:")
        #     for i, (doc, score) in enumerate(results):
        #         preview = doc.page_content[:100].replace("\n", " ").strip()
        #         print(f"{i+1}. Score: {score:.4f} - Content: {preview}...")

        # New implementation using similarity_search_with_relevance_scores
        results = db.similarity_search_with_relevance_scores(
            query,
            k=limit,
            score_threshold=score_threshold,
        )
        if not json_output:
            print("\nDebug - Raw results with relevance scores:")
            for i, (doc, score) in enumerate(results):
                preview = doc.page_content[:100].replace("\n", " ").strip()
                print(f"{i+1}. Score: {score:.4f} - Content: {preview}...")

        # Filter results by score threshold
        filtered_results = [
            (doc, score) for doc, score in results if score >= score_threshold
        ]
        if not json_output:
            print(
                f"\nFiltered {len(results)} results to {len(filtered_results)} results using threshold {score_threshold}"
            )
        return filtered_results
    except Exception as e:
        if not json_output:
            print(f"Search error: {str(e)}")
        return []


def format_search_result(doc_with_score, index: int, show_full: bool = False):
    """Format a single search result for display."""
    doc, score = doc_with_score  # Unpack the document and its score
    source = doc.metadata.get("source", "Unknown source")
    content = doc.page_content.replace("\n", " ").strip()

    # Show full content or preview based on the show_full flag
    display_content = (
        content
        if show_full
        else (content[:200] + "..." if len(content) > 200 else content)
    )

    return (
        f"\nResult {index + 1}:"
        f"\nSource: {source}"
        f"\nRelevance Score: {score:.4f}"
        f"\nContent: {display_content}\n"
        f"\n{'-' * 80}"
    )


def format_doc_for_json(doc_with_score):
    """Format a document for JSON output."""
    doc, score = doc_with_score  # Unpack the document and its score
    return {
        "source": doc.metadata.get("source", "Unknown source"),
        "content": doc.page_content.strip(),
        "score": float(
            score
        ),  # Convert numpy float to Python float for JSON serialization
        "metadata": doc.metadata,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Load URL content into vector store and query it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch and index content from LangChain tutorials
  python recursive_url_loader.py --fetch https://python.langchain.com/docs/tutorials/ --max-depth 2

  # Query the vector store for tutorials
  python recursive_url_loader.py --query "What tutorials are available for LangChain?"
        """,
    )

    # Make URL optional and mutually exclusive with fetch/query
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "url", nargs="?", help="URL to process (deprecated: use --fetch instead)"
    )
    group.add_argument("--fetch", help="Fetch and index content from a URL")
    group.add_argument("--query", help="Query to search for in the documents")

    # Other arguments
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum depth for recursive URL loading",
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of results to return"
    )
    parser.add_argument(
        "--persist-directory",
        default=DEFAULT_PERSIST_DIR,
        help="Directory to persist vector store",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show full document content instead of preview",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=0.2,
        help="Only return results with scores above this threshold (default: 0.2)",
    )

    args = parser.parse_args()

    try:
        # Handle fetch (either from positional URL or --fetch option)
        url_to_fetch = args.url or args.fetch
        if url_to_fetch:
            docs = load_url_to_docs(url_to_fetch, max_depth=args.max_depth)
            num_chunks = process_and_store_documents(
                docs, args.persist_directory, args.json
            )
            if not args.json:
                print(
                    f"\nVector store location: {os.path.abspath(args.persist_directory)}"
                )
                print(f"Loading content from {url_to_fetch}")
                print(f"Found {len(docs)} documents")
                print(
                    f"Processed into {num_chunks} chunks and stored in vector database"
                )

        # If query is provided, search the vector store
        if args.query:
            results = search_documents(
                args.query,
                args.persist_directory,
                args.limit,
                args.json,
                args.score_threshold,
            )

            if results:
                if args.json:
                    # For JSON output, just print the JSON array without any other output
                    json_results = [format_doc_for_json(result) for result in results]
                    print(json.dumps(json_results, indent=2))
                else:
                    print(
                        f"\nVector store location: {os.path.abspath(args.persist_directory)}"
                    )
                    print(f"\nSearching for: '{args.query}'")
                    if args.score_threshold:
                        print(f"Score threshold: {args.score_threshold}")
                    for i, result in enumerate(results):
                        print(format_search_result(result, i, show_full=args.full))
            elif not args.json:
                print("\nNo relevant documents found.")

        # If neither URL nor query is provided, just try to load the vector store
        if not args.url and not args.query:
            try:
                db = get_or_create_db(args.persist_directory, json_output=args.json)
                if not args.json:
                    print(
                        f"\nVector store location: {os.path.abspath(args.persist_directory)}"
                    )
                    print("Vector store loaded successfully")
            except ValueError as e:
                if not args.json:
                    print(f"Error: {str(e)}")

    except Exception as e:
        if not args.json:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
