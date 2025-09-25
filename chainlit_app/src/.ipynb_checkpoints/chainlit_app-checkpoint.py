# filepath: src/chainlit_app.py
import chainlit as cl
from app_config import MOONSHOT_API_KEY, MOONSHOT_BASE_URL, COMMANDS
from services import get_openai_client, get_weaviate_client, get_retriever, process_uploaded_image, process_image_from_url
from tooling import build_tool_map, detect_tools_and_execute
from llm_utils import llm_rerank_results
from rag.retriever import Retriever

client = get_openai_client(MOONSHOT_API_KEY, MOONSHOT_BASE_URL)
weaviate_client = get_weaviate_client()
retriever = get_retriever(weaviate_client, "dviz_c", ["image_url", "section_11_description"], "combined_vector")
tool_map = build_tool_map(weaviate_client, Retriever)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("retriever", retriever)
    await cl.Message(
        content="👋 Welcome to the Data Visualization Search App! \n\n"
                "You can:\n"
                "- 🔍 Search for existing visualizations by typing your query\n"
                "- 📤 Upload an image to analyze and add to the database\n\n"
                "Try asking: 'Show me bar charts' or upload a visualization image!"
    ).send()
    await cl.context.emitter.set_commands(COMMANDS)

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content.strip()
    retr = cl.user_session.get("retriever")

    if message.command:
        if message.command == "img":
            await cl.Message(
                content="📤 **Upload Image Mode**\n\nPlease upload an image file to analyze. You can:\n"
                        "- Drag and drop an image file\n"
                        "- Click the attachment button (📎) to select a file\n"
                        "- Supported formats: JPG, PNG, GIF, etc.\n\n"
                        "*Upload your visualization image and I'll analyze it for you!*"
            ).send()
            return

        if message.command == "tools":
            thinking_msg = cl.Message(content="🔧 Analyzing your query with tools...")
            await thinking_msg.send()
            tool_analysis = await analyze_user_query_with_tools(user_query)
            per_tool_results = tool_analysis.get("hits", [])
            has_tools = tool_analysis.get("has_tools", False)
            results = retr.retrieve(user_query)
            elements = []
            sections = []
            if per_tool_results:
                tool_section = "🎯 **Detected filters from your query:**\n"
                for hit in per_tool_results:
                    hit_field = hit.get('field', '')
                    hit_query = hit.get('query', '')
                    tool_section += f"\n• **Filter:** {hit_field} | Query: \"{hit_query}\""
                    hit_results = hit.get("results", [])
                    if hit_results:
                        tool_section += f"\n  Top matches:"
                        for idx, r in enumerate(hit_results[:3], 1):
                            image_url = r.get("image_url")
                            if image_url:
                                tool_section += f"\n    {idx}. ![Visualization {idx}]({image_url})"
                            else:
                                tool_section += f"\n    {idx}. (no image available)"
                            if r.get("image_url"):
                                try:
                                    img_el = cl.Image(
                                        name=f"{hit_field}_{idx}",
                                        display="inline",
                                        url=r["image_url"]
                                    )
                                    elements.append(img_el)
                                except Exception as e:
                                    print(f"Image error: {e}")
                    else:
                        tool_section += "\n  (no matches found)"
                sections.append(tool_section)
            if results and getattr(results, "objects", None):
                main_header = (
                    f"🔎 **General semantic search found {len(results.objects)} visualizations:**\n"
                    if has_tools else
                    f"**I found {len(results.objects)} visualizations related to your query:**\n"
                )
                main_section = main_header + "\n"
                for i, doc in enumerate(results.objects[:5], 1):
                    doc_content = doc.properties.get("section_11_description") or "No description available."
                    image_url = doc.properties.get("image_url")
                    main_section += f"**Result {i}**\n"
                    main_section += f"- **Description:** {doc_content}\n"
                    if image_url:
                        try:
                            img_el = cl.Image(name=f"result_{i}", display="inline", url=image_url)
                            elements.append(img_el)
                            main_section += f"- 🖼️ **Visualization {i}**\n"
                        except Exception as e:
                            print(f"Image error: {e}")
                            main_section += f"![Visualization {i}]({image_url})\n"
                    else:
                        main_section += "- No image available.\n"
                    main_section += "\n"
                if elements:
                    main_section += f"\n📸 **{len(elements)} visualization(s) displayed below**\n"
                sections.append(main_section)
            else:
                if has_tools:
                    sections.append("No additional semantic results beyond the targeted filter matches.")
                else:
                    sections.append("No visualizations matched your query. Try different or broader terms.")
            thinking_msg.content = "\n\n---\n\n".join(sections)
            if elements:
                thinking_msg.elements = elements
            await thinking_msg.update()
            return

        if message.command == "hybrid_search":
            if not hasattr(retr, "hybrid_retrieve"):
                await cl.Message(content="Hybrid search not available (method missing). Restart the app after updating code.").send()
                return
            thinking_msg = cl.Message(content="🔍 Running hybrid (keyword + vector) search...")
            await thinking_msg.send()
            results = retr.hybrid_retrieve(user_query)
            elements, sections = [], []
            if results and getattr(results, "objects", None):
                main_section = f"🔎 **Hybrid search found {len(results.objects)} visualizations:**\n\n"
                for i, doc in enumerate(results.objects[:5], 1):
                    props = getattr(doc, "properties", {}) or {}
                    desc = props.get("section_11_description") or "No description available."
                    img = props.get("image_url")
                    main_section += f"**Result {i}**\n- Description: {desc}\n"
                    if img:
                        try:
                            elements.append(cl.Image(name=f"hybrid_{i}", display="inline", url=img))
                            main_section += "- Image displayed below\n"
                        except Exception:
                            main_section += f"- {img}\n"
                    main_section += "\n"
                if elements:
                    main_section += f"📸 {len(elements)} image(s) below."
                sections.append(main_section)
            else:
                sections.append("No hybrid results.")
            thinking_msg.content = "\n\n---\n\n".join(sections)
            if elements:
                thinking_msg.elements = elements
            await thinking_msg.update()
            return

        if message.command == "fullcontext":
            thinking_msg = cl.Message(content="🧠 Gathering extended context (top 100 results)...")
            await thinking_msg.send()

            # Step 1: retrieve top 100 (vector)
            raw_results = retr.retrieve(user_query, limit=100)

            if not raw_results or not getattr(raw_results, "objects", None):
                thinking_msg.content = "No results found for extended context."
                await thinking_msg.update()
                return

            objs = raw_results.objects
            # Step 2: rerank with LLM (if more than 1)
            try:
                if len(objs) > 1:
                    reranked = await llm_rerank_results(client, user_query, objs)
                    objs = reranked
            except Exception as e:
                print(f"Rerank error: {e}")

            # Step 3: take top 20
            top_k = objs[:20]

            elements = []
            lines = [f"🔍 **Top 20 (from initial 100) matches for:** {user_query}\n"]
            for i, doc in enumerate(top_k, 1):
                props = getattr(doc, "properties", {}) or {}
                desc = props.get("section_11_description") or "No description."
                desc_trunc = (desc[:280] + "...") if len(desc) > 300 else desc
                img = props.get("image_url")
                lines.append(f"**{i}.** {desc_trunc}")
                if img:
                    try:
                        elements.append(cl.Image(name=f"fullctx_{i}", display="inline", url=img))
                        lines.append(f"- Image shown below")
                    except Exception:
                        lines.append(f"- {img}")
                lines.append("")

            if elements:
                lines.append(f"📸 {len([e for e in elements])} image(s) displayed below.")
            thinking_msg.content = "\n".join(lines)
            if elements:
                thinking_msg.elements = elements
            await thinking_msg.update()
            return

    # Ignore URLs and waiting states
    if cl.user_session.get("waiting_for_url") or user_query.startswith(('http://', 'https://')):
        return



async def analyze_user_query_with_tools(user_query: str):
    try:
        hits = detect_tools_and_execute(client, user_query, tool_map)
        return {
            "hits": [h.__dict__ for h in hits],
            "has_tools": len(hits) > 0
        }
    except Exception as e:
        print(f"Tool detection error: {e}")
        return {"hits": [], "has_tools": False}