
import json

async def query_rewrite(client, user_query, history: list = None):
    history_str = ""
    if history:
        # Format the last few turns of history for the prompt
        formatted_history = []
        for turn in history[-4:]: # Use last 4 turns to keep it concise
            role = "User" if turn["role"] == "user" else "Assistant"
            formatted_history.append(f"{role}: {turn['content']}")
        history_str = "\n".join(formatted_history)

    QUERY_REWRITE_PROMPT = f"""
    [CONTEXT & ROLE]
    You are a strict keyword extractor. Your job is to analyze the CURRENT USER QUERY in the context of the CONVERSATION HISTORY and extract relevant keywords that match a controlled vocabulary.



    [CONTROLLED VOCABULARIES FOR TRANSLATION]

    **Plot Types:** Part-to-Whole, Diverging, Pictogram, Time Series, Slope, Circular, Strips, Trees, Tiles, 3D, Waffle, Bullet Chart, Histogram, Density Plot, Empirical CDF, t-SNE, Correlation, Scatter Plot, Violin Plot, Abstract, Experimental, Distribution, Clusters, Ranking, Outliers, Fractions, Size Comparison, Kinship, Log Scale, Inclusion, Uncertainty, Comparisons, Relationships

    **Theme & Grid:** 
    - Background: light, dark
    - Grid Orientation: horizontal, vertical, both, radial, none
    - Grid Layout: single, grid, faceted, small multiples, stacked, side by side, circular, radial, overlay, irregular, matrix
    - Grid Type: major, minor, implicit, subtle, reference lines, none
    - Grid Style: solid, dashed, dotted, thin, light, subtle, faint, minimal, none

    **Arrangement:** single, grid, facets, small multiples, stacked, side by side, overlay, hierarchical, grouped, clustered

    **Coordinates:** cartesian, cartesian_3d, polar, circular, geographic_general, flow_network, schematic, linear, categorical, logarithmic, mixed, none

    **Typography:** sans-serif, serif, slab serif, monospace, script, handwritten, blackletter

    **Color Palettes:** sequential, diverging, qualitative, categorical, monochrome, grayscale, semantic, brand colors, highlight, accent, mixed palette

    **Statistical Elements:** totals_sums, averages_means, percentages_rates, changes_growth, rankings_comparisons, distributions, trend_lines, correlation_patterns, confidence_bounds, outliers_extremes, aggregations, benchmarks_targets, anomalies, none

    [TRANSLATION RULES]
    1.  **Context preservation**: Keep ALL original context (locations, topics, sources, etc.)
    2.  **Identify Keywords:** Scan the `[CURRENT USER QUERY]` for words that match or are synonymous with terms in the `[CONTROLLED VOCABULARIES]`.ONLY translate if user explicitly mentions or strongly implies a term.
    3.  **Conceptual Expansion (Plot Types ONLY):** If the user describes a function (e.g., "show relationship"), you may translate this into specific plot types (e.g., `Correlation`, `Scatter Plot`).
    4.  **ABSOLUTE PROHIBITION:** You MUST NOT add ANY keyword that is not explicitly mentioned or directly implied by the user's query and the conversation history.
    5.  **Output Format:** Return ONLY a comma-separated list of the extracted and translated keywords.
    6.  **No Extra Text:** Do NOT include any explanations, just the keywords.
    7.  **No Duplicates:** Each keyword should appear only once in the output.
    8.  **Order:** Maintain the order of keywords as they appear in the user's query where possible.
    9. **omit**: ommit ggplot2 or datawrapper from output if mentioned
    10. **Geographic Specificity:** If a geographic region is mentioned (e.g., "Europe", "Asia"), include it as a keyword (e.g., `europe`, `asia`) along with `geographic_general`.
    11. **No Negatives:** Do NOT include any keywords that the user explicitly states they do NOT want.
    12. **No Uncertainty:** If the user's intent is unclear, do NOT guess or add keywords. Only include what is certain.

    [EXAMPLES WITH HISTORY]
    History: User: "show me scatter plots with a dark background"
    → "Scatter Plot, dark background"

    History: User: "faceted plot with regression line"
    → "faceted, trend_lines, Regression"
    
    Input: "visualizations showing map of europe in datawrapper"
    Output: "map, geographic_general,europe"
    [TASK]
    Apply the strict translation process to the user query below. Generate a comma-separated list.

    [CURRENT USER QUERY]
    {user_query}
    """
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": QUERY_REWRITE_PROMPT}],
            max_tokens=150,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        return content
    except Exception as e:
        print(f"Error in query rewriting: {e}")
        return user_query
    
    
    

async def llm_rerank_results(client, query, results_objects,rewritten_user_query = '', relevance_threshold=0.5):
    if not results_objects or len(results_objects) == 0:
        return []
    result_texts = []
    for i, doc in enumerate(results_objects):
        doc_content = doc.properties.get("section_11_description", "")
        result_texts.append({"id": i, "content": doc_content})
    prompt = f"""As a data visualization expert, carefully analyze these visualization results for relevance to the user's query.
      The user sends a query about data visualizations he wants to retrieve from a vector database, and you must determine which results best match the intent and requirements of that query.
      Use the users instruction to retrieve the most relevant results based on what the user finds important.


USER QUERY: "{query}"

SEARCH RESULTS:
{json.dumps(result_texts, indent=2)}

INSTRUCTIONS:
1. Analyze how well each result matches the semantic meaning of the query
2. Consider visualization type, data structure, and visual elements
3. ONLY include results that are genuinely relevant to the query
4. Exclude results that don't match the user's intent or visualization needs
5. Return results in order from most to least relevant prioritizing plot types and data

Your response should be a JSON array with just the IDs of RELEVANT results in order of relevance.
If a result doesn't match the query at all, don't include it.
Example format: [2, 0, 3]

Only respond with the JSON array.
"""
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        try:
            ranking = json.loads(content)
            if isinstance(ranking, list):
                reordered_results = []
                for idx in ranking:
                    if isinstance(idx, int) and 0 <= idx < len(results_objects):
                        reordered_results.append(results_objects[idx])
                return reordered_results
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response as JSON: {content}")
    except Exception as e:
        print(f"Error in LLM reranking: {e}")
    filtered_results = []
    for obj in results_objects:
        if hasattr(obj, 'distance') and obj.distance is not None:
            if obj.distance < (1.0 - relevance_threshold):
                filtered_results.append(obj)
        else:
            filtered_results.append(obj)
    return filtered_results