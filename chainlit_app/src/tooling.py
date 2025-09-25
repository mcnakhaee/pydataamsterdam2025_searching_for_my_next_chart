from modules.toolcalling import FIELD_TOOLS, VECTOR_NAME_MAP, ToolHit
from rag.retriever import Retriever

def build_tool_map(shared_client, RetrieverClass):
    def make_field_tool(field):
        vector_name = VECTOR_NAME_MAP.get(field, f"{field}_vector")
        def _run(arguments):
            q = arguments["query"]
            retr = RetrieverClass(
                client=shared_client,
                collection_name="dviz_c",
                return_properties=["image_url", "section_11_description"],
                target_vector=vector_name
            )
            resp = retr.retrieve(q)
            objects = getattr(resp, "objects", []) or []
            out = []
            for obj in objects:
                out.append({
                    "image_url": obj.properties.get("image_url"),
                    "description": obj.properties.get("section_11_description") or obj.properties.get("section_11_description") or ""
                })
            return {"results": out}
        return _run
    return {f"set_{field}_filter": make_field_tool(field) for field in FIELD_TOOLS.keys()}

def detect_tools_and_execute(client, user_query, tool_map):
    hits = []
    lower_query = user_query.lower()
    for field, config in FIELD_TOOLS.items():
        matched_keywords = [kw for kw in config["keywords"] if kw.lower() in lower_query]
        if matched_keywords:
            query = user_query
            fn_name = f"set_{field}_filter"
            fn = tool_map.get(fn_name)
            if fn:
                try:
                    results = fn({"query": query})
                    vector_name = VECTOR_NAME_MAP.get(field, f"{field}_vector")
                    hits.append(ToolHit(
                        field=field,
                        query=query,
                        vector=vector_name,
                        results=results.get("results", [])
                    ))
                except Exception as e:
                    print(f"Error executing {field} tool: {e}")
    return hits