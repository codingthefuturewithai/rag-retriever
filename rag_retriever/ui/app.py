"""Streamlit UI for RAG Retriever."""

import streamlit as st
from rag_retriever.vectorstore.store import VectorStore
from rag_retriever.search.searcher import Searcher
from typing import Dict, Any
import pandas as pd

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
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1rem 0;
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
    }
    
    .stDataFrame th {
        background-color: var(--background-color);
        font-weight: 600;
    }
    
    .stDataFrame td {
        font-size: 0.9rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: white;
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
        padding-left: 1rem;
        margin: 1rem 0;
        background-color: white;
        border-radius: 0 8px 8px 0;
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
                    # Clear expanded states
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
                        st.info("ℹ️ No results found")
                        st.session_state.search_results = None
                        return

                    st.session_state.search_results = results

                except Exception as e:
                    st.error(f"🚨 Error performing search: {str(e)}")

    # Display results if they exist
    if st.session_state.search_results:
        st.markdown("### Search Results")

        for i, result in enumerate(st.session_state.search_results, 1):
            # Result container with card styling
            st.markdown('<div class="search-result">', unsafe_allow_html=True)

            # Score indicator with color
            score_color = (
                "#4CAF50"
                if result.score >= 0.7
                else "#FF9800" if result.score >= 0.5 else "#F44336"
            )

            st.markdown(
                f"""
                <h4 style="margin-bottom: 0.5rem;">Result {i}</h4>
                <p style="color: {score_color}; font-weight: 600; margin: 0;">
                    Relevance Score: {result.score:.2f}
                </p>
                <p style="color: gray; margin: 0.5rem 0;">
                    Source: {result.source}
                </p>
                """,
                unsafe_allow_html=True,
            )

            # Content display with animation
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
                    content_key = f"content_{i}"
                    is_content_expanded = i in st.session_state.expanded_content

                    if is_content_expanded:
                        st.markdown(result.content)
                        if st.button("📕 Show less", key=f"less_{content_key}"):
                            st.session_state.expanded_content.remove(i)
                            st.session_state.button_clicked = f"less_{content_key}"
                            st.rerun()
                    else:
                        if st.button("📖 Show full content", key=f"more_{content_key}"):
                            st.session_state.expanded_content.add(i)
                            st.session_state.button_clicked = f"more_{content_key}"
                            st.rerun()

            # Metadata handling with improved UI
            metadata_key = f"metadata_{i}"
            is_metadata_expanded = i in st.session_state.expanded_metadata

            if is_metadata_expanded:
                with st.expander("📋 Metadata", expanded=True):
                    st.json(result.metadata)
                if st.button("Hide metadata", key=f"hide_{metadata_key}"):
                    st.session_state.expanded_metadata.remove(i)
                    st.session_state.button_clicked = f"hide_{metadata_key}"
                    st.rerun()
            else:
                if st.button("📋 Show metadata", key=f"show_{metadata_key}"):
                    st.session_state.expanded_metadata.add(i)
                    st.session_state.button_clicked = f"show_{metadata_key}"
                    st.rerun()

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
        collections_to_compare = st.multiselect(
            "Select collections to compare",
            options=[c["name"] for c in collections],
            help="Select 2 or more collections to compare their statistics",
            key="compare_collections",
        )

        if len(collections_to_compare) >= 2:
            if st.button(
                "Compare Collections", type="primary", use_container_width=True
            ):
                st.session_state.show_comparison = True
                st.session_state.show_stats = False
                st.session_state.collections_to_compare = collections_to_compare
                st.rerun()

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
                "Last Modified": pd.to_datetime(stats["Timestamps"]["Last Modified"]),
            }
        )

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


def main():
    """Main Streamlit application."""

    # Add logo and title in a row
    col1, col2 = st.columns([1, 4])

    with col1:
        # Load and display logo
        try:
            st.image("rag_retriever/static/CTF-logo.jpg", width=100)
        except:
            st.warning(
                "Logo not found. Place CTF-logo.jpg in rag_retriever/static/ directory"
            )

    with col2:
        st.title("RAG Retriever UI")

    # Add tabs for different functionality
    tab1, tab2 = st.tabs(["Collections", "Search"])

    with tab1:
        display_collections()

    with tab2:
        display_search()


if __name__ == "__main__":
    main()
