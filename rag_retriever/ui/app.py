"""Streamlit UI for RAG Retriever."""

import streamlit as st
from rag_retriever.vectorstore.store import VectorStore
from rag_retriever.search.searcher import Searcher
from typing import Dict, Any
import pandas as pd
import logging
from importlib import resources
import os
from urllib.parse import urlparse
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """More permissive URL validation that doesn't rely on TLD checking."""
    try:
        result = urlparse(url)
        # Check for scheme and netloc
        has_scheme = bool(result.scheme in ("http", "https"))
        has_netloc = bool(result.netloc)
        # Basic netloc validation (at least one dot, valid chars)
        valid_netloc = bool(
            re.match(
                r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
                result.netloc,
            )
        )
        return all([has_scheme, has_netloc, valid_netloc])
    except Exception:
        return False


# Configure page settings
st.set_page_config(
    page_title="RAG Retriever UI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown(
    """
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #2196F3;
        --secondary-color: #4CAF50;
        --background-color: #f8f9fa;
        --text-color: #212529;
        --border-color: #dee2e6;
        --hover-color: #e9ecef;
    }
    
    /* Main container styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Typography */
    h1 {
        color: var(--text-color);
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 2rem !important;
    }
    
    h2, h3 {
        color: var(--text-color);
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Card-like containers */
    .stDataFrame, div[data-testid="stExpander"] {
        background-color: transparent;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color);
    }
    
    .stButton > button[kind="secondary"] {
        border: 1px solid var(--border-color);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 0.5rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--primary-color);
    }
    
    /* Alerts and messages */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem;
    }
    
    /* Dividers */
    .stDivider {
        margin: 2rem 0;
    }
    
    /* Animations */
    .stMarkdown, .stDataFrame, .element-container {
        transition: opacity 0.3s ease;
    }
    
    /* Tables */
    .stDataFrame table {
        border: none !important;
        background-color: transparent;
    }
    
    .stDataFrame th {
        background-color: transparent;
        font-weight: 600;
        border-bottom: 2px solid var(--border-color);
    }
    
    .stDataFrame td {
        font-size: 0.9rem;
        background-color: transparent;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: transparent;
        border-right: 1px solid var(--border-color);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    
    /* Search results */
    .search-result {
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        margin: 1rem 0;
        background-color: transparent;
        border-radius: 0 8px 8px 0;
        border: 1px solid var(--border-color);
    }
    
    /* Metadata container styling */
    .metadata-container {
        background-color: #2b3035;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: #e9ecef;
    }
    
    .metadata-container strong {
        color: #ffffff;
    }
</style>
""",
    unsafe_allow_html=True,
)


def delete_collection(collection_name: str) -> None:
    """Delete a collection using VectorStore."""
    store = VectorStore()
    store.clean_collection(collection_name)


def edit_collection_description(collection_name: str, new_description: str) -> None:
    """Update a collection's description."""
    store = VectorStore()
    collection = store._get_or_create_collection(collection_name)
    collection._collection_metadata.description = new_description
    store._save_collection_metadata()


def get_collection_stats(collection_name: str) -> Dict[str, Any]:
    """Get detailed collection statistics."""
    store = VectorStore()
    metadata = store.get_collection_metadata(collection_name)

    # Calculate derived statistics
    avg_chunks = (
        round(metadata["total_chunks"] / metadata["document_count"], 2)
        if metadata["document_count"] > 0
        else 0
    )

    return {
        "Collection Size": {
            "Documents": metadata["document_count"],
            "Total Chunks": metadata["total_chunks"],
            "Average Chunks per Document": avg_chunks,
        },
        "Timestamps": {
            "Created": metadata["created_at"],
            "Last Modified": metadata["last_modified"],
        },
    }


def display_search():
    """Display search interface."""
    st.header("Search Knowledge Store")

    # Initialize searcher
    searcher = Searcher()

    # Initialize session state for search results and expanded states
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "expanded_content" not in st.session_state:
        st.session_state.expanded_content = set()
    if "expanded_metadata" not in st.session_state:
        st.session_state.expanded_metadata = set()

    # Get list of collections for dropdown
    store = VectorStore()
    collections = store.list_collections()
    collection_names = [c["name"] for c in collections]

    # Search interface container
    with st.container():
        st.markdown('<div class="element-container">', unsafe_allow_html=True)

        # Search controls
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            query = st.text_input(
                "Search query",
                key="search_query",
                placeholder="Enter your search query...",
                help="Type your search terms here",
            )
        with col2:
            limit = st.number_input(
                "Max results",
                min_value=1,
                value=5,
                key="search_limit",
                help="Maximum number of results to show",
            )
        with col3:
            threshold = st.number_input(
                "Score threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                key="score_threshold",
                help="Minimum relevance score (0-1)",
            )

        # Collection selection
        col4, col5 = st.columns([3, 1])
        with col4:
            selected_collection = st.selectbox(
                "Search in collection",
                options=["All Collections"] + collection_names,
                index=0,
                key="search_collection",
                help="Choose which collection to search in",
            )
        with col5:
            show_full = st.checkbox(
                "Show full content",
                value=False,
                key="show_full",
                help="Display complete content in results",
            )

        # Search button
        search_clicked = st.button(
            "🔍 Search",
            type="primary",
            use_container_width=True,
            help="Click to perform search",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if search_clicked:
            if not query:
                st.warning("⚠️ Please enter a search query")
                return

            with st.spinner("🔍 Searching..."):
                try:
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
                        st.info("ℹ️ No results found")
                        st.session_state.search_results = None
                        return

                    st.session_state.search_results = results

                except Exception as e:
                    st.error(f"🚨 Error performing search: {str(e)}")

    # Display results if they exist
    if st.session_state.search_results:
        st.markdown("### Search Results")

        # Display results in cards
        for i, result in enumerate(st.session_state.search_results):
            with st.container():
                st.markdown('<div class="search-result">', unsafe_allow_html=True)

                # Source name as title
                source = (
                    result.source.split("/")[-1]
                    if "/" in result.source
                    else result.source
                )
                st.markdown(f"#### {source}")

                # Source URL and buttons in one row
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    # Encode URL for display to prevent browser validation
                    display_url = result.source.replace(
                        "://", "://\u200B"
                    )  # Insert zero-width space
                    st.markdown(f"*{display_url}*")
                with col2:
                    if result.source.startswith(("http://", "https://")):
                        # Use HTML anchor tag instead of JavaScript
                        st.markdown(
                            f'<a href="{result.source}" target="_blank"><button style="padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid var(--border-color); background-color: transparent; cursor: pointer; font-weight: 500;">🔗 Open</button></a>',
                            unsafe_allow_html=True,
                        )
                with col3:
                    # Toggle content expansion
                    is_expanded = i in st.session_state.expanded_content
                    if st.button("📄 Full Content", key=f"search_content_{i}"):
                        if is_expanded:
                            st.session_state.expanded_content.remove(i)
                        else:
                            st.session_state.expanded_content.add(i)
                with col4:
                    # Toggle metadata expansion
                    is_metadata_expanded = i in st.session_state.expanded_metadata
                    if st.button("ℹ️ Metadata", key=f"search_metadata_{i}"):
                        if is_metadata_expanded:
                            st.session_state.expanded_metadata.remove(i)
                        else:
                            st.session_state.expanded_metadata.add(i)

                # Content
                if i in st.session_state.expanded_content or show_full:
                    # Show full content
                    st.markdown(result.content)
                else:
                    # Show truncated content
                    content = (
                        result.content[:200] + "..."
                        if len(result.content) > 200
                        else result.content
                    )
                    st.markdown(content)
                    if len(result.content) > 200:
                        st.markdown("*Click 'Full Content' to see more*")

                # Show score
                st.markdown(f"*Relevance Score: {result.score:.2f}*")

                # Metadata (if expanded)
                if i in st.session_state.expanded_metadata:
                    with st.expander("Document Metadata", expanded=True):
                        for key, value in result.metadata.items():
                            if key not in [
                                "source",
                                "depth",
                            ]:  # Skip source and depth fields
                                st.markdown(f"**{key}**: {value}")

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)


def display_collections():
    """Display collections table with metadata."""
    st.header("Collections Management")

    # Initialize session state
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False
        st.session_state.collection_to_delete = None
    if "show_edit_description" not in st.session_state:
        st.session_state.show_edit_description = False
        st.session_state.collection_to_edit = None
        st.session_state.current_description = ""
    if "show_stats" not in st.session_state:
        st.session_state.show_stats = False
        st.session_state.collection_to_show = None
    if "show_comparison" not in st.session_state:
        st.session_state.show_comparison = False
        st.session_state.collections_to_compare = []

    # Initialize vector store
    store = VectorStore()
    collections = store.list_collections()

    if not collections:
        st.info("No collections found.")
        return

    # Display collections table
    df = pd.DataFrame(collections)
    columns = [
        "name",
        "created_at",
        "last_modified",
        "document_count",
        "total_chunks",
        "description",
    ]
    df = df[columns]
    df.columns = [col.replace("_", " ").title() for col in df.columns]

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

    # Collection Management Section
    st.divider()
    st.subheader("Collection Actions")

    selected_collection = st.selectbox(
        "Select collection to manage",
        options=[c["name"] for c in collections],
        help="Select a collection to manage",
    )

    if selected_collection:
        if selected_collection != "default":
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Edit Description",
                    type="secondary",
                    use_container_width=True,
                    help="Edit the collection's description",
                ):
                    handle_edit_description(selected_collection, collections)
            with col2:
                if st.button(
                    "Delete Collection",
                    type="secondary",
                    use_container_width=True,
                    help="Permanently delete this collection",
                ):
                    handle_delete_collection(selected_collection)
        else:
            st.info("The default collection cannot be modified.")

        # Show management dialogs if active
        if st.session_state.show_delete_confirm:
            st.divider()
            show_delete_confirmation()

        if st.session_state.show_edit_description:
            st.divider()
            show_edit_description()

        # Statistics Section
        st.divider()
        st.subheader("Collection Statistics")

        # Individual Stats
        if st.button("View Collection Stats", type="primary", use_container_width=True):
            st.session_state.show_stats = True
            st.session_state.show_comparison = False
            st.session_state.collection_to_show = selected_collection
            st.rerun()

        # Collection Comparison
        st.markdown("#### Compare with Other Collections")
        st.session_state.collections_to_compare = st.multiselect(
            "Select collections to compare",
            options=[c["name"] for c in collections],
            help="Select 2 or more collections to compare their statistics",
            key="compare_collections",
        )

        # Show comparison immediately when 2 or more collections are selected
        if len(st.session_state.collections_to_compare) >= 2:
            show_collection_comparison()

    # Show statistics views if active
    if st.session_state.show_stats:
        st.divider()
        show_collection_stats()

    if st.session_state.show_comparison:
        st.divider()
        show_collection_comparison()


def handle_edit_description(collection_name: str, collections: list):
    """Handle edit description button click."""
    current_desc = next(
        (c["description"] for c in collections if c["name"] == collection_name),
        "",
    )
    st.session_state.show_edit_description = True
    st.session_state.collection_to_edit = collection_name
    st.session_state.current_description = current_desc
    st.rerun()


def handle_delete_collection(collection_name: str):
    """Handle delete collection button click."""
    st.session_state.show_delete_confirm = True
    st.session_state.collection_to_delete = collection_name
    st.rerun()


def show_delete_confirmation():
    collection_name = st.session_state.collection_to_delete
    st.warning(
        f"Are you sure you want to delete collection '{collection_name}'?",
        icon="⚠️",
    )
    col6, col7 = st.columns([1, 1])
    with col6:
        if st.button("Yes, Delete", type="primary", use_container_width=True):
            try:
                delete_collection(collection_name)
                st.session_state.show_delete_confirm = False
                st.session_state.collection_to_delete = None
                st.success(f"Collection '{collection_name}' deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting collection: {str(e)}")
    with col7:
        if st.button("No, Cancel", type="secondary", use_container_width=True):
            st.session_state.show_delete_confirm = False
            st.session_state.collection_to_delete = None
            st.rerun()


def show_edit_description():
    st.divider()
    st.subheader(f"Edit Description for '{st.session_state.collection_to_edit}'")

    new_description = st.text_area(
        "Collection Description",
        value=st.session_state.current_description,
        height=100,
        help="Enter a description for this collection",
        key="edit_description",
    )

    col4, col5 = st.columns([1, 1])
    with col4:
        if st.button("Save Description", type="primary", use_container_width=True):
            try:
                edit_collection_description(
                    st.session_state.collection_to_edit, new_description
                )
                st.session_state.show_edit_description = False
                st.session_state.collection_to_edit = None
                st.session_state.current_description = ""
                st.success("Description updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating description: {str(e)}")
    with col5:
        if st.button("Cancel", type="secondary", use_container_width=True):
            st.session_state.show_edit_description = False
            st.session_state.collection_to_edit = None
            st.session_state.current_description = ""
            st.rerun()


def show_collection_comparison():
    st.divider()
    st.subheader("Collection Comparison")

    # Get stats for all selected collections
    comparison_data = []
    for collection_name in st.session_state.collections_to_compare:
        try:
            stats = get_collection_stats(collection_name)
            comparison_data.append(
                {
                    "Collection": collection_name,
                    "Documents": stats["Collection Size"]["Documents"],
                    "Total Chunks": stats["Collection Size"]["Total Chunks"],
                    "Avg Chunks/Doc": stats["Collection Size"][
                        "Average Chunks per Document"
                    ],
                    "Created": pd.to_datetime(stats["Timestamps"]["Created"]),
                    "Last Modified": pd.to_datetime(
                        stats["Timestamps"]["Last Modified"]
                    ),
                }
            )
        except Exception as e:
            st.error(f"Error getting stats for collection {collection_name}: {str(e)}")
            return

    if not comparison_data:
        st.warning("No valid collections to compare")
        return

    # Create comparison DataFrame
    comparison_df = pd.DataFrame(comparison_data)

    # Display metrics comparison
    st.markdown("#### Size Metrics")

    # Create a bar chart comparing document counts
    doc_chart_data = pd.DataFrame(
        {
            "Collection": comparison_df["Collection"],
            "Documents": comparison_df["Documents"],
            "Total Chunks": comparison_df["Total Chunks"],
        }
    ).melt(id_vars=["Collection"], var_name="Metric", value_name="Count")

    import plotly.express as px

    # Calculate chart height based on number of collections
    chart_height = max(300, len(st.session_state.collections_to_compare) * 100)

    fig = px.bar(
        doc_chart_data,
        x="Count",
        y="Collection",
        color="Metric",
        orientation="h",
        height=chart_height,
        title="Documents and Chunks by Collection",
        barmode="group",
    )

    fig.update_layout(
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_title="",
        xaxis_title="Count",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display average chunks comparison
    st.markdown("#### Average Chunks per Document")
    avg_fig = px.bar(
        comparison_df,
        x="Collection",
        y="Avg Chunks/Doc",
        height=300,
        title="Average Chunks per Document by Collection",
    )
    avg_fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_title="Average Chunks",
        xaxis_title="",
    )
    st.plotly_chart(avg_fig, use_container_width=True)

    # Display timeline comparison
    st.markdown("#### Collection Timelines")
    timeline_data = []
    for _, row in comparison_df.iterrows():
        age = row["Last Modified"] - row["Created"]
        timeline_data.append(
            {
                "Collection": row["Collection"],
                "Created": row["Created"].strftime("%b %d, %Y at %H:%M:%S"),
                "Last Modified": row["Last Modified"].strftime("%b %d, %Y at %H:%M:%S"),
                "Age": f"{age.days} days, {age.seconds // 3600} hours, {(age.seconds % 3600) // 60} minutes",
            }
        )

    timeline_df = pd.DataFrame(timeline_data)
    st.dataframe(
        timeline_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Collection": st.column_config.TextColumn("Collection", width="medium"),
            "Created": st.column_config.TextColumn("Created", width="medium"),
            "Last Modified": st.column_config.TextColumn(
                "Last Modified", width="medium"
            ),
            "Age": st.column_config.TextColumn("Age", width="medium"),
        },
    )

    if st.button("Close Comparison", type="secondary", use_container_width=True):
        st.session_state.show_comparison = False
        st.session_state.collections_to_compare = []
        st.rerun()


def show_collection_stats():
    st.divider()
    st.subheader(f"Statistics for '{st.session_state.collection_to_show}'")

    try:
        stats = get_collection_stats(st.session_state.collection_to_show)
        size_data = stats["Collection Size"]
        time_data = stats["Timestamps"]

        # Create two columns for metrics
        col_metrics1, col_metrics2 = st.columns(2)

        with col_metrics1:
            st.metric(
                "Documents",
                size_data["Documents"],
                help="Total number of documents in the collection",
            )
            st.metric(
                "Total Chunks",
                size_data["Total Chunks"],
                help="Total number of text chunks after splitting documents",
            )

        with col_metrics2:
            st.metric(
                "Average Chunks per Document",
                f"{size_data['Average Chunks per Document']:.1f}",
                help="Average number of chunks each document is split into",
            )

        # Display size metrics with a bar chart
        st.markdown("#### Collection Size Distribution")

        # Create bar chart data with better formatting
        chart_data = pd.DataFrame(
            {
                "Category": ["Documents", "Chunks"],
                "Count": [size_data["Documents"], size_data["Total Chunks"]],
            }
        ).set_index("Category")

        # Calculate chart height based on data range
        max_value = max(size_data["Documents"], size_data["Total Chunks"])
        chart_height = min(
            max(150, max_value * 0.8), 300
        )  # Dynamic height between 150-300px

        # Use plotly for more control over the chart
        import plotly.express as px

        fig = px.bar(
            chart_data,
            orientation="v",
            height=chart_height,
            labels={"value": "Count", "Category": ""},
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis_range=[0, max_value * 1.1],  # Add 10% padding to top
        )
        st.plotly_chart(fig, use_container_width=True)

        # Display timestamps in a more compact format
        st.markdown("#### Collection Timeline")
        created = pd.to_datetime(time_data["Created"])
        modified = pd.to_datetime(time_data["Last Modified"])

        # Calculate time difference
        time_diff = modified - created

        col_time1, col_time2 = st.columns(2)
        with col_time1:
            st.info(
                f"**Created**  \n{created.strftime('%b %d, %Y at %H:%M:%S')}",
                icon="🕒",
            )
        with col_time2:
            st.info(
                f"**Last Modified**  \n{modified.strftime('%b %d, %Y at %H:%M:%S')}",
                icon="📝",
            )

        # Show time difference if it's significant
        if (
            time_diff.total_seconds() > 60
        ):  # Only show if difference is more than a minute
            st.caption(
                f"Collection age: {time_diff.days} days, "
                f"{time_diff.seconds // 3600} hours, "
                f"{(time_diff.seconds % 3600) // 60} minutes"
            )

        # Add close button at the bottom
        st.divider()
        if st.button("Close Stats", type="secondary", use_container_width=True):
            st.session_state.show_stats = False
            st.session_state.collection_to_show = None
            st.rerun()

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")
        if st.button("Close", type="secondary"):
            st.session_state.show_stats = False
            st.session_state.collection_to_show = None
            st.rerun()


def display_discover():
    """Display content discovery and ingestion interface."""
    st.header("Discover Content")

    # Initialize session state for URL entries and search results
    if "url_entries" not in st.session_state:
        st.session_state.url_entries = [{"url": "", "max_depth": 0}]
    if "web_search_results" not in st.session_state:
        st.session_state.web_search_results = None
    if "processing_state" not in st.session_state:
        st.session_state.processing_state = {"status": "idle", "progress": 0}
    if "validation_states" not in st.session_state:
        st.session_state.validation_states = {}
    if "selected_discover_urls" not in st.session_state:
        st.session_state.selected_discover_urls = set()
    if "discover_url_depths" not in st.session_state:
        st.session_state.discover_url_depths = {}

    # Web Search Section
    st.subheader("Web Search")
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search_query = st.text_input(
                "Search query",
                key="discover_search_query",
                placeholder="Enter search terms to find relevant content...",
                help="Enter keywords to search for relevant web content",
            )
        with col2:
            num_results = st.number_input(
                "Number of results",
                min_value=1,
                max_value=20,
                value=5,
                key="discover_num_results",
                help="Maximum number of search results to display",
            )
        with col3:
            search_provider = st.selectbox(
                "Provider",
                options=["Default", "DuckDuckGo", "Google"],
                key="discover_search_provider",
                help="Search provider to use. Default uses the configured default provider (falls back to DuckDuckGo if Google credentials not configured)",
            )

        search_clicked = st.button(
            "🔍 Search",
            type="primary",
            key="discover_search_button",
            use_container_width=True,
            help="Search for web content",
        )

        # Handle search
        if search_clicked:
            if not search_query:
                st.warning("⚠️ Please enter a search query")
            else:
                with st.spinner("🔍 Searching..."):
                    try:
                        from rag_retriever.search.web_search import (
                            web_search,
                            get_search_provider,
                            GoogleSearchProvider,
                            DuckDuckGoSearchProvider,
                        )
                        from rag_retriever.utils.config import config

                        # Convert provider selection to API parameter
                        provider = (
                            None
                            if search_provider == "Default"
                            else search_provider.lower()
                        )

                        logger.debug(f"Selected provider in UI: {search_provider}")
                        logger.debug(f"Provider parameter for web_search: {provider}")

                        # Log the default provider from config
                        default_provider = config.search.get(
                            "default_provider", "duckduckgo"
                        )
                        logger.debug(
                            f"Default provider from config: {default_provider}"
                        )

                        try:
                            # Get the actual provider that will be used
                            actual_provider = get_search_provider(provider)
                            provider_type = type(actual_provider).__name__
                            logger.debug(
                                f"Actual provider instance type: {provider_type}"
                            )

                            # Show which provider will be used
                            if isinstance(actual_provider, GoogleSearchProvider):
                                st.info("🔍 Using Google Search")
                                logger.info("Using Google Search provider")
                            else:
                                st.info("🦆 Using DuckDuckGo Search")
                                logger.info("Using DuckDuckGo provider")

                            # Perform the search
                            results = web_search(
                                search_query, num_results, provider=provider
                            )

                            if results:
                                logger.debug(f"Got {len(results)} results")
                                st.session_state.web_search_results = results
                            else:
                                logger.warning("No results returned from search")
                                st.warning("No results found")
                                st.session_state.web_search_results = None

                        except ValueError as e:
                            error_msg = str(e)
                            logger.error(f"ValueError in web search: {error_msg}")
                            st.error(f"🚨 {error_msg}")
                            st.info(
                                "💡 Try using DuckDuckGo instead, or configure Google Search credentials."
                            )
                            st.session_state.web_search_results = None
                    except Exception as e:
                        logger.error(
                            f"Unexpected error in web search: {str(e)}", exc_info=True
                        )
                        st.error(f"🚨 Error performing search: {str(e)}")
                        st.session_state.web_search_results = None

    # Display search results
    if st.session_state.web_search_results:
        st.markdown("### Search Results")

        # Add select all checkbox
        if st.checkbox("Select All Results", key="discover_select_all"):
            st.session_state.selected_discover_urls = {
                result.url for result in st.session_state.web_search_results
            }
        else:
            st.session_state.selected_discover_urls.clear()

        # Display results in cards
        for i, result in enumerate(st.session_state.web_search_results):
            with st.container():
                st.markdown('<div class="search-result">', unsafe_allow_html=True)

                # Title and selection in one row
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"#### {result.title}")
                with col2:
                    is_selected = result.url in st.session_state.selected_discover_urls
                    if st.checkbox(
                        "Select", key=f"discover_select_{i}", value=is_selected
                    ):
                        st.session_state.selected_discover_urls.add(result.url)
                    else:
                        st.session_state.selected_discover_urls.discard(result.url)

                # URL and open link
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Encode URL for display to prevent browser validation
                    display_url = result.url.replace(
                        "://", "://\u200B"
                    )  # Insert zero-width space
                    st.markdown(f"*{display_url}*")
                with col2:
                    if result.url.startswith(("http://", "https://")):
                        # Use HTML anchor tag instead of JavaScript
                        st.markdown(
                            f'<a href="{result.url}" target="_blank"><button style="padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid var(--border-color); background-color: transparent; cursor: pointer; font-weight: 500;">🔗 Open</button></a>',
                            unsafe_allow_html=True,
                        )

                # Snippet
                st.markdown(result.snippet)

                # Max depth selector (only show if selected)
                if result.url in st.session_state.selected_discover_urls:
                    depth = st.number_input(
                        "Max Depth",
                        min_value=0,
                        max_value=5,
                        value=st.session_state.discover_url_depths.get(result.url, 0),
                        key=f"depth_discover_{i}",
                        help="Maximum depth of pages to crawl (0 = current page only)",
                    )
                    # Store the depth value in session state
                    st.session_state.discover_url_depths[result.url] = depth

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        # Collection selection for processing
        if st.session_state.selected_discover_urls:
            st.divider()

            # Get list of collections
            store = VectorStore()
            collections = store.list_collections()
            collection_names = [c["name"] for c in collections]

            col1, col2 = st.columns([3, 1])
            with col1:
                selected_collection = st.selectbox(
                    "Select collection",
                    options=["Create New Collection"] + collection_names,
                    key="process_collection",
                    help="Choose which collection to add the content to",
                )

            # Show new collection input if selected
            if selected_collection == "Create New Collection":
                # Wrap inputs in a form to better handle focus changes
                with st.form(key="new_collection_form"):
                    new_collection_name = st.text_input(
                        "New collection name",
                        key="new_collection_name",
                        help="Enter a name for the new collection",
                    )
                    new_collection_description = st.text_area(
                        "Collection description",
                        key="new_collection_description",
                        help="Enter a description for the new collection",
                    )
                    # Add a hidden submit button to handle form submission properly
                    submitted = st.form_submit_button("Create", type="primary")
                    if submitted:
                        if not new_collection_name:
                            st.error("Please enter a name for the new collection")
                        else:
                            try:
                                # Create new collection
                                collection = store._get_or_create_collection(
                                    new_collection_name
                                )
                                if new_collection_description:
                                    collection._collection_metadata.description = (
                                        new_collection_description
                                    )
                                    store._save_collection_metadata()
                                selected_collection = new_collection_name
                                st.success(
                                    f"Created new collection: {new_collection_name}"
                                )
                            except Exception as e:
                                st.error(f"Error creating collection: {str(e)}")

            # Process button
            process_button = st.button(
                f"Process {len(st.session_state.selected_discover_urls)} Selected URLs",
                type="primary",
                disabled=False,
                use_container_width=True,
                help="Process and index the selected URLs",
            )

            if process_button:
                # Initialize VectorStore first
                store = VectorStore()

                if selected_collection == "Create New Collection":
                    if not new_collection_name:
                        st.error("Please enter a name for the new collection")
                        return

                    try:
                        # Create new collection
                        collection = store._get_or_create_collection(
                            new_collection_name
                        )
                        if new_collection_description:
                            collection._collection_metadata.description = (
                                new_collection_description
                            )
                            store._save_collection_metadata()
                        selected_collection = new_collection_name
                        st.success(f"Created new collection: {new_collection_name}")
                    except Exception as e:
                        st.error(f"Error creating collection: {str(e)}")
                        return

                # Process URLs with progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                error_container = st.container()

                total_urls = len(st.session_state.selected_discover_urls)
                processed_urls = 0
                errors = []

                for url in st.session_state.selected_discover_urls:
                    try:
                        status_text.text(f"Processing {url}...")
                        depth = st.session_state.discover_url_depths.get(url, 0)

                        # Use the process_url function from main.py
                        from rag_retriever.main import process_url

                        result = process_url(
                            url=url,
                            max_depth=depth,
                            verbose=True,
                            collection_name=selected_collection,
                        )

                        if result == 0:  # Success
                            processed_urls += 1
                            progress = processed_urls / total_urls
                            progress_bar.progress(progress)
                            st.success(f"Successfully processed: {url}")
                        else:
                            errors.append((url, "Failed to process URL"))
                            st.error(f"Error processing {url}")

                    except Exception as e:
                        errors.append((url, str(e)))
                        st.error(f"Error processing {url}: {str(e)}")

                # Show final status
                if errors:
                    with error_container:
                        st.error("Some URLs failed to process:")
                        for url, error in errors:
                            st.markdown(f"- **{url}**: {error}")

                if processed_urls > 0:
                    st.success(f"Successfully processed {processed_urls} URLs")
                    # Clear selections after successful processing
                    st.session_state.selected_discover_urls.clear()
                    st.session_state.discover_url_depths.clear()
                    st.rerun()

    # Direct URL Input Section
    st.divider()
    st.subheader("Direct URL Input")

    # Display existing URL entries
    for i, entry in enumerate(st.session_state.url_entries):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                url = st.text_input(
                    "URL",
                    value=entry["url"],
                    key=f"url_{i}",
                    placeholder="Enter a URL to index...",
                    help="Enter the web page URL you want to add to your knowledge base",
                )

                # Update URL in session state
                st.session_state.url_entries[i]["url"] = url

                # Display URL with zero-width space to prevent browser validation
                if url:
                    display_url = url.replace("://", "://\u200B")
                    st.markdown(f"Current URL: *{display_url}*")

                # Basic URL validation
                if url:
                    is_valid = is_valid_url(url)
                    st.session_state.validation_states[f"url_{i}"] = is_valid

                    if not is_valid:
                        st.error("Please enter a valid URL (e.g., https://example.com)")

            with col2:
                depth = st.number_input(
                    "Max Depth",
                    min_value=0,
                    max_value=5,
                    value=entry["max_depth"],
                    key=f"depth_{i}",
                    help="Maximum depth of pages to crawl (0 = current page only)",
                )
                # Update depth in session state
                st.session_state.url_entries[i]["max_depth"] = depth

            with col3:
                if st.button("Remove", key=f"remove_{i}", help="Remove this URL"):
                    st.session_state.url_entries.pop(i)
                    # Remove validation state
                    st.session_state.validation_states.pop(f"url_{i}", None)
                    st.rerun()

    # Add URL button
    if st.button("➕ Add Another URL", use_container_width=True):
        st.session_state.url_entries.append({"url": "", "max_depth": 0})
        st.rerun()

    # Only show collection selection and process button if there are valid URLs
    valid_urls = [
        entry["url"]
        for entry in st.session_state.url_entries
        if entry["url"]
        and st.session_state.validation_states.get(
            f"url_{st.session_state.url_entries.index(entry)}", False
        )
    ]

    if valid_urls:
        st.divider()

        # Get list of collections
        store = VectorStore()
        collections = store.list_collections()
        collection_names = [c["name"] for c in collections]

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_collection = st.selectbox(
                "Select collection",
                options=["Create New Collection"] + collection_names,
                key="direct_process_collection",
                help="Choose which collection to add the content to",
            )

        # Show new collection input if selected
        if selected_collection == "Create New Collection":
            # Wrap inputs in a form to better handle focus changes
            with st.form(key="new_collection_form"):
                new_collection_name = st.text_input(
                    "New collection name",
                    key="new_collection_name",
                    help="Enter a name for the new collection",
                )
                new_collection_description = st.text_area(
                    "Collection description",
                    key="new_collection_description",
                    help="Enter a description for the new collection",
                )
                # Add a hidden submit button to handle form submission properly
                submitted = st.form_submit_button("Create", type="primary")
                if submitted:
                    if not new_collection_name:
                        st.error("Please enter a name for the new collection")
                    else:
                        try:
                            # Create new collection
                            collection = store._get_or_create_collection(
                                new_collection_name
                            )
                            if new_collection_description:
                                collection._collection_metadata.description = (
                                    new_collection_description
                                )
                                store._save_collection_metadata()
                            selected_collection = new_collection_name
                            st.success(f"Created new collection: {new_collection_name}")
                        except Exception as e:
                            st.error(f"Error creating collection: {str(e)}")

        # Process URLs button
        process_button = st.button(
            f"Process {len(valid_urls)} URLs",
            type="primary",
            use_container_width=True,
            help="Process and index the entered URLs",
        )

        if process_button:
            # Initialize VectorStore first
            store = VectorStore()

            if selected_collection == "Create New Collection":
                if not new_collection_name:
                    st.error("Please enter a name for the new collection")
                    return

                try:
                    # Create new collection
                    collection = store._get_or_create_collection(new_collection_name)
                    if new_collection_description:
                        collection._collection_metadata.description = (
                            new_collection_description
                        )
                        store._save_collection_metadata()
                    selected_collection = new_collection_name
                    st.success(f"Created new collection: {new_collection_name}")
                except Exception as e:
                    st.error(f"Error creating collection: {str(e)}")
                    return

            # Process URLs with progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            error_container = st.container()

            total_urls = len(valid_urls)
            processed_urls = 0
            errors = []

            for url in valid_urls:
                try:
                    status_text.text(f"Processing {url}...")
                    # Get depth for this URL
                    url_index = next(
                        i
                        for i, entry in enumerate(st.session_state.url_entries)
                        if entry["url"] == url
                    )
                    depth = st.session_state.url_entries[url_index]["max_depth"]

                    # Use the process_url function from main.py
                    from rag_retriever.main import process_url

                    result = process_url(
                        url=url,
                        max_depth=depth,
                        verbose=True,
                        collection_name=selected_collection,
                    )

                    if result == 0:  # Success
                        processed_urls += 1
                        progress = processed_urls / total_urls
                        progress_bar.progress(progress)
                        st.success(f"Successfully processed: {url}")
                    else:
                        errors.append((url, "Failed to process URL"))
                        st.error(f"Error processing {url}")

                except Exception as e:
                    errors.append((url, str(e)))
                    st.error(f"Error processing {url}: {str(e)}")

            # Show final status
            if errors:
                with error_container:
                    st.error("Some URLs failed to process:")
                    for url, error in errors:
                        st.markdown(f"- **{url}**: {error}")

            if processed_urls > 0:
                st.success(f"Successfully processed {processed_urls} URLs")
                # Clear URL entries after successful processing
                st.session_state.url_entries = [{"url": "", "max_depth": 0}]
                st.session_state.validation_states = {}
                st.rerun()


def main():
    """Main Streamlit application."""

    # Add logo and title in a row
    col1, col2 = st.columns([1, 4])

    with col1:
        # Load and display logo using importlib.resources
        try:
            with (
                resources.files("rag_retriever")
                .joinpath("static/CTF-logo.jpg")
                .open("rb") as f
            ):
                image_data = f.read()
                st.image(image_data, width=100)
        except Exception as e:
            st.warning(f"Logo not found. Error: {str(e)}")

    with col2:
        st.title("RAG Retriever UI")

    # Add tabs for different functionality
    tab1, tab2, tab3 = st.tabs(["Collections", "Search Knowledge Store", "Discover"])

    with tab1:
        display_collections()

    with tab2:
        display_search()

    with tab3:
        display_discover()


if __name__ == "__main__":
    main()
