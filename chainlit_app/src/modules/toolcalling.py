import json
from weaviate.classes.query import MetadataQuery, Filter
from openai import OpenAI
from dataclasses import dataclass
import json
from dataclasses import dataclass
from typing import List
import os
# ====== Initialize Clients ======
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"), 
    base_url = "https://api.moonshot.ai/v1",
)

# Weaviate client
import weaviate
from typing import List, Dict
def detect_tools_and_execute(llm_client, user_query: str, weaviate_client):
    """
    Detects tools and executes combined search with vectors and filters
    """
    tools = generate_tools()
    resp = llm_client.chat.completions.create(
        model="kimi-k2-0711-preview",
        messages=[
            {
                "role": "system", 
                "content": """You are a data visualization search assistant. Your task is to analyze user queries and call the MOST RELEVANT search function.

IMPORTANT RULES:
1. Call ONLY ONE function unless the user explicitly mentions MULTIPLE DISTINCT aspects
2. For general queries about chart purposes/goals, use search_plot_goal
3. For specific chart type requests, use search_plot_type or search_primary_category
4. Only call multiple functions when user mentions BOTH chart type AND visual attributes (e.g., "bar chart with dark background")
5. Don't generate multiple similar chart types - let the semantic search handle variations

EXAMPLES:
- "a plot that shows proportion" → ONLY call search_primary_category("Part-to-Whole")
- "vertical bar plot with dark background" → call search_plot_type("vertical bar plot") AND search_background_type("dark background")
- "scatter plot" → ONLY call search_plot_type("scatter plot")
- "chart with trend lines" → ONLY call search_statistical_methods("trend lines")
- "faceted visualization" → ONLY call search_layout("faceted visualization")

For broad conceptual queries, use the most appropriate single search function and let semantic search find relevant matches."""
            },
            {
                "role": "user", 
                "content": user_query
            }
        ],
        tools=tools,
        tool_choice="auto",
        temperature=0
    )
    
    msg = resp.choices[0].message
    hits = []
    
    if msg.tool_calls:
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            args = json.loads(tc.function.arguments)
            
            if fn_name.startswith("search_"):
                field = fn_name.replace("search_", "")
            else:
                continue
            
            config = FIELD_TOOLS.get(field, {})
            field_type = config.get("type", "vector")
            
            hit = ToolHit(
                field=field,
                query=args.get("query", ""),
                field_type=field_type
            )
            
            if field_type == "vector":
                hit.vector = VECTOR_NAME_MAP.get(field, f"{field}_vector")
            elif field_type == "filter":
                hit.filter_field = config.get("field_name", field)
            
            hits.append(hit)
    
    # Execute combined search
    results = execute_combined_search(weaviate_client, hits, user_query)
    return hits, results
# Field definitions + trigger keyword hints
FIELD_TOOLS = {
    # Vectorized fields
    "data_types": {
        "description": "Search by data and variable types",
        "keywords": ["data", "variable", "type", "categorical", "numerical", "continuous", "discrete", "ordinal"],
        "type": "vector"
    },
    "variable_mapping": {
        "description": "Search by how variables are mapped to visual elements",
        "keywords": ["mapping", "encode", "encoding", "variable", "x-axis", "y-axis", "size", "shape"],
        "type": "vector"
    },
    "color_encoding": {
        "description": "Search by color encoding and color mapping details",
        "keywords": ["color encoding", "color mapping", "hue", "saturation", "color scale", "legend"],
        "type": "vector"
    },
    "legend_guides": {
        "description": "Search by legend and guide details",
        "keywords": ["legend", "guide", "key", "scale", "colorbar", "legend position"],
        "type": "vector"
    },
    "chart_elements": {
        "description": "Search by chart element identification",
        "keywords": ["element", "component", "part", "bars", "points", "lines", "shapes", "markers"],
        "type": "vector"
    },
    "layout": {
        "description": "Search by layout and arrangement details",
        "keywords": ["layout", "arrangement", "position", "placement", "spacing", "margins", "alignment"],
        "type": "vector"
    },
    "axes_scales": {
        "description": "Search by axes and scales configuration",
        "keywords": ["axis", "scale", "range", "domain", "ticks", "labels", "log scale", "linear"],
        "type": "vector"
    },
    "statistical_methods": {
        "description": "Search by statistical and analytical methods used",
        "keywords": ["statistical", "analysis", "method", "regression", "correlation", "trend", "model"],
        "type": "vector"
    },
    "annotations": {
        "description": "Search by annotations and storytelling elements",
        "keywords": ["annotation", "text", "label", "callout", "highlight", "story", "narrative"],
        "type": "vector"
    },
    "plot_goal": {
        "description": "Search by plot purpose or goal",
        "keywords": ["goal", "purpose", "objective", "intent", "why", "show", "demonstrate", "illustrate"],
        "type": "vector"
    },
    "searchable_keywords": {
        "description": "Search by general keywords and tags",
        "keywords": ["keyword", "tag", "category", "type", "style", "feature"],
        "type": "vector"
    },
    "innovative_features": {
        "description": "Search by innovative or noteworthy design features",
        "keywords": ["innovative", "unique", "creative", "novel", "interesting", "noteworthy", "special", "advanced"],
        "type": "vector"
    },
    "description": {
        "description": "Search by general description and content",
        "keywords": ["description", "about", "what", "content", "shows", "displays", "represents"],
        "type": "vector"
    },
    "plot_type": {
        "description": "Search by plot type",
        "keywords": ["bar", "line", "scatter", "pie", "histogram", "box plot", "heatmap", "plot type", "chart type"],
        "type": "vector",
    },
    "primary_category": {
        "description": "Search by plot primary category",
        "keywords": ["Part-to-Whole", "Diverging", "Pictogram", "Time Series", "Slope", "Circular", "Strips", "Trees", "Tiles", "3D", "Waffle", "Bullet Chart", "Histogram", "Density Plot", "Empirical CDF", "t-SNE", "Correlation", "Scatter Plot", "Violin Plot", "Abstract", "Experimental", "Distribution", "Clusters", "Ranking", "Outliers", "Fractions", "Size Comparison", "Kinship", "Log Scale", "Inclusion", "Uncertainty", "Comparisons", "Relationships"],
        "type": "vector",
    },
    
    # Filter fields (controlled vocabularies)
    "background_color": {
        "description": "Search by background color",
        "keywords": [ "background color" ],
        "type": "filter",
        "field_name": "background_color"
    },
    "background_type": {
        "description": "Search by background type",
        "keywords": ["light", "dark", "background type", "dark background", "light background","black", "white", "gray"],
        "type": "filter", 
        "field_name": "background_type"
    },
    "grid_color": {
        "description": "Search by grid line color",
        "keywords": ["grid", "gridlines", "grid color", "grid lines", "major grid", "minor grid"],
        "type": "filter",
        "field_name": "grid_color"
    },
    "grid_orientation": {
        "description": "Search by grid orientation",
        "keywords": ["horizontal", "vertical", "both", "radial", "grid orientation"],
        "type": "filter",
        "field_name": "grid_orientation"
    },
    "grid_layout": {
        "description": "Search by grid layout",
        "keywords": ["single", "grid", "faceted", "small multiples", "stacked", "side by side", "circular", "radial"],
        "type": "filter",
        "field_name": "grid_layout"
    },
    "grid_style": {
        "description": "Search by grid style",
        "keywords": ["solid", "dashed", "dotted", "thin", "light", "subtle", "grid style"],
        "type": "filter",
        "field_name": "grid_style"
    },

    "coordinate_type": {
        "description": "Search by coordinate system type",
        "keywords": ["cartesian", "polar", "geographic", "3d", "coordinate system"],
        "type": "filter",
        "field_name": "coordinate_type"
    },
    "palette_type": {
        "description": "Search by color palette type",
        "keywords": ["sequential", "diverging", "qualitative", "categorical", "monochrome", "palette"],
        "type": "filter",
        "field_name": "palette_type"
    },
    "readability_assessment": {
        "description": "Search by readability level",
        "keywords": ["readability", "readable", "clear", "legible", "high", "medium", "low"],
        "type": "filter",
        "field_name": "readability_assessment"
    }
}

# Map field names to their corresponding vector names
VECTOR_NAME_MAP = {
    "data_types": "section_1_data_and_variable_types_vector",
    "variable_mapping": "section_2_variable_mapping_vector",
    "color_encoding": "section_3_color_encoding_details_vector",
    "chart_elements": "section_4_chart_element_identification_vector",
    "layout": "section_5_layout_details_vector",
    "axes_scales": "section_6_axes_and_scales_vector",
    "annotations": "section_7_annotation_and_storytelling_elements_vector",
    "plot_goal": "section_8_plot_goal_vector",
    "searchable_keywords": "section_9_searchable_keywords_vector",
    "innovative_features": "section_10_innovative_or_noteworthy_design_features_vector",
    "description": "section_11_description_vector",
    "combined": "combined_vector",
    "primary_category": "primary_category_vector",
    "plot_type": "plot_type_vector"
}



def generate_tools():
    """Generate OpenAI function tools for each field"""
    tools = []
    for field, config in FIELD_TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": f"search_{field}",
                "description": f"{config['description']}. Use when user mentions: {', '.join(config['keywords'][:5])}...",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"Search query related to {field}"
                        }
                    }
                }
            }
        })
    

    
    return tools


@dataclass
class ToolHit:
    field: str
    query: str
    field_type: str  # 'vector' or 'filter'
    vector: str = None
    filter_field: str = None
    results: list = None
def execute_combined_search(weaviate_client, hits: List[ToolHit], original_query: str):
    """
    Execute search with a combination of vector queries and filters.
    """
    print(f"\n--- [DEBUG] Executing Combined Search ---")
    print(f"Original Query: '{original_query}'")
    print(f"Detected Hits: {len(hits)}")

    vector_hits = [h for h in hits if h.field_type == "vector"]
    filter_hits = [h for h in hits if h.field_type == "filter"]

    print(f"Vector Hits: {len(vector_hits)}")
    print(f"Filter Hits: {len(filter_hits)}")

    # Determine the primary vector search
    if vector_hits:
        primary_vector_target = vector_hits[0].vector
        query_text = vector_hits[0].query
        print(f"Using VECTOR hit for search. Target Vector: '{primary_vector_target}', Query: '{query_text}'")
    else:
        primary_vector_target = "section_11_description_vector"
        query_text = original_query
        print(f"Using DEFAULT vector search. Target Vector: '{primary_vector_target}', Query: '{query_text}'")

    # Build filters with robust value mapping
    filters_list = []
    for hit in filter_hits:
        query_value = hit.query.lower().strip()
        filter_field = hit.filter_field
        filter_value = query_value

        # SIMPLIFIED LOGIC: Only normalize the background_theme tool
        if filter_field == "background_type": # This now comes from our single 'background_theme' tool
            if any(word in query_value for word in ["dark", "black"]):
                filter_value = "dark"
            elif any(word in query_value for word in ["light", "white"]):
                filter_value = "light"
            else:
                print(f"Skipping background filter for ambiguous query '{query_value}'.")
                continue
        
        print(f"Creating FILTER: Field='{filter_field}', Value='{filter_value}' (from query='{query_value}')")
        filters_list.append(Filter.by_property(filter_field).equal(filter_value))


    # Combine all filters using a logical AND
    combined_filter = None
    if len(filters_list) > 0:
        combined_filter = Filter.all_of(filters_list)
        print(f"Applied combined filter: {combined_filter}")
    else:
        print("No filters were applied.")

    try:
        # Ensure the filtered field is returned for debugging
        return_props = ["image_url", "section_11_description", "post_title", "post_url", "image_description", "external_link", "background_type"]
        
        collection = weaviate_client.collections.get("dviz_c_structured_v3")
        results = collection.query.near_text(
            query=query_text,
            limit=100,
            target_vector=primary_vector_target,
            filters=combined_filter,
            return_metadata=MetadataQuery(distance=True),
            return_properties=return_props
        )
        
        print(f"Weaviate search executed successfully.")
        
        if hasattr(results, 'objects'):
            print(f"Found {len(results.objects)} results from Weaviate.")
            # Log the background type of the first few results to check the data
            for i, obj in enumerate(results.objects[:3]):
                bg_type = obj.properties.get("background_type", "N/A")
                print(f"  - Result {i+1} background_type: '{bg_type}'")
            return results.objects
        else:
            print("Weaviate response did not contain 'objects'.")
            return []
        
    except Exception as e:
        print(f"!!!!!! WEAVIATE SEARCH ERROR: {e} !!!!!!")
        return []
