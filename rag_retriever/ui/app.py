"""Streamlit UI for RAG Retriever."""

import streamlit as st
from rag_retriever.vectorstore.store import VectorStore
from rag_retriever.search.searcher import Searcher


def delete_collection(collection_name: str) -> None:
    """Delete a collection using VectorStore."""
    store = VectorStore()
    store.clean_collection(collection_name)


def display_search():
    """Display search interface."""
    st.header("Search")

    # Initialize searcher
    searcher = Searcher()

    # Initialize session state for expanded sections and button clicks
    if "expanded_metadata" not in st.session_state:
        st.session_state.expanded_metadata = set()
    if "expanded_content" not in st.session_state:
        st.session_state.expanded_content = set()
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = None

    # Get list of collections for dropdown
    store = VectorStore()
    collections = store.list_collections()
    collection_names = [c["name"] for c in collections]

    # Search controls
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        query = st.text_input("Search query", key="search_query")
    with col2:
        limit = st.number_input("Max results", min_value=1, value=5, key="search_limit")
    with col3:
        threshold = st.number_input(
            "Score threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            key="score_threshold",
        )

    # Collection selection
    col4, col5 = st.columns([3, 1])
    with col4:
        selected_collection = st.selectbox(
            "Search in collection",
            options=["All Collections"] + collection_names,
            index=0,
            key="search_collection",
        )
    with col5:
        show_full = st.checkbox("Show full content", value=False, key="show_full")

    # Search button
    if st.button("Search", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a search query")
            return

        try:
            # Clear expanded states on new search
            st.session_state.expanded_metadata = set()
            st.session_state.expanded_content = set()
            st.session_state.button_clicked = None

            # Perform search
            search_all = selected_collection == "All Collections"
            if not search_all:
                searcher = Searcher(collection_name=selected_collection)

            results = searcher.search(
                query=query,
                limit=limit,
                score_threshold=threshold,
                search_all_collections=search_all,
            )

            if not results:
                st.info("No results found")
                st.session_state.search_results = None
                return

            # Store results in session state
            st.session_state.search_results = results

        except Exception as e:
            st.error(f"Error performing search: {str(e)}")

    # Display results if they exist in session state
    if st.session_state.search_results:
        st.markdown("### Search Results")

        for i, result in enumerate(st.session_state.search_results, 1):
            st.markdown(
                f"""
                #### Result {i} - Score: {result.score:.4f}
                **Source:** {result.source}
                """
            )

            # Content handling
            if show_full:
                st.markdown(result.content)
            else:
                preview = (
                    result.content[:200] + "..."
                    if len(result.content) > 200
                    else result.content
                )
                st.markdown(preview)

                if len(result.content) > 200:
                    # Generate unique keys for content buttons
                    content_key = f"content_{i}"

                    # Check if content is expanded
                    is_content_expanded = i in st.session_state.expanded_content

                    # Show the appropriate button and content
                    if is_content_expanded:
                        st.markdown(result.content)
                        if st.button("Show less", key=f"less_{content_key}"):
                            st.session_state.expanded_content.remove(i)
                            st.session_state.button_clicked = f"less_{content_key}"
                            st.rerun()
                    else:
                        if st.button("Show full content", key=f"more_{content_key}"):
                            st.session_state.expanded_content.add(i)
                            st.session_state.button_clicked = f"more_{content_key}"
                            st.rerun()

            # Metadata handling
            # Generate unique keys for metadata buttons
            metadata_key = f"metadata_{i}"

            # Check if metadata is expanded
            is_metadata_expanded = i in st.session_state.expanded_metadata

            # Show the appropriate button and metadata
            if is_metadata_expanded:
                st.json(result.metadata)
                if st.button("Hide metadata", key=f"hide_{metadata_key}"):
                    st.session_state.expanded_metadata.remove(i)
                    st.session_state.button_clicked = f"hide_{metadata_key}"
                    st.rerun()
            else:
                if st.button("Show metadata", key=f"show_{metadata_key}"):
                    st.session_state.expanded_metadata.add(i)
                    st.session_state.button_clicked = f"show_{metadata_key}"
                    st.rerun()

            st.divider()


def display_collections():
    """Display collections table with metadata."""
    st.header("Collections Management")

    # Initialize session state for deletion flow
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False
        st.session_state.collection_to_delete = None

    # Initialize vector store
    store = VectorStore()

    # Get collections
    collections = store.list_collections()

    if not collections:
        st.info("No collections found.")
        return

    # Create a DataFrame for better display
    import pandas as pd

    df = pd.DataFrame(collections)

    # Reorder columns for better presentation
    columns = [
        "name",
        "created_at",
        "last_modified",
        "document_count",
        "total_chunks",
        "description",
    ]
    df = df[columns]

    # Rename columns for better display
    df.columns = [col.replace("_", " ").title() for col in df.columns]

    # Display the table with sorting enabled
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn(
                "Name",
                help="Collection name",
                width="medium",
            ),
            "Created At": st.column_config.DatetimeColumn(
                "Created At",
                help="When the collection was created",
                format="D MMM YYYY, HH:mm",
                width="medium",
            ),
            "Last Modified": st.column_config.DatetimeColumn(
                "Last Modified",
                help="When the collection was last modified",
                format="D MMM YYYY, HH:mm",
                width="medium",
            ),
            "Document Count": st.column_config.NumberColumn(
                "Document Count",
                help="Number of documents in the collection",
                width="small",
            ),
            "Total Chunks": st.column_config.NumberColumn(
                "Total Chunks",
                help="Total number of chunks in the collection",
                width="small",
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                help="Collection description",
                width="large",
            ),
        },
    )

    # Add delete collection functionality
    if len(collections) > 1:  # Don't allow deleting if only default collection exists
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_collection = st.selectbox(
                "Select collection to delete",
                options=[c["name"] for c in collections if c["name"] != "default"],
                help="Select a collection to delete. The default collection cannot be deleted.",
            )
        with col2:
            if st.button(
                "Delete Collection", type="secondary", use_container_width=True
            ):
                st.session_state.show_delete_confirm = True
                st.session_state.collection_to_delete = selected_collection
                st.rerun()

        # Show confirmation dialog if needed
        if st.session_state.show_delete_confirm:
            st.warning(
                f"Are you sure you want to delete collection '{st.session_state.collection_to_delete}'?",
                icon="⚠️",
            )
            col3, col4 = st.columns([1, 1])
            with col3:
                if st.button("Yes, Delete", type="primary", use_container_width=True):
                    try:
                        delete_collection(st.session_state.collection_to_delete)
                        st.session_state.show_delete_confirm = False
                        st.session_state.collection_to_delete = None
                        st.success(
                            f"Collection '{selected_collection}' deleted successfully!"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting collection: {str(e)}")
            with col4:
                if st.button("No, Cancel", type="secondary", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    st.session_state.collection_to_delete = None
                    st.rerun()


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="RAG Retriever UI",
        page_icon="🔍",
        layout="wide",
    )

    st.title("RAG Retriever UI")

    # Add tabs for different functionality
    tab1, tab2 = st.tabs(["Collections", "Search"])

    with tab1:
        display_collections()

    with tab2:
        display_search()


if __name__ == "__main__":
    main()
