# filepath: src/chainlit_app.py
import chainlit as cl
import requests
from app_config import MOONSHOT_API_KEY, MOONSHOT_BASE_URL, COMMANDS,QWEN_VL_API_KEY, QWEB_VL_BASE_URL,WEAVIATE_CLOUD_URL,WEAVIATE_CLUSTER_API_KEY,Mistral_API_KEY, WEAVIATE_COLLECTION_NAME
from services import get_openai_client, get_weaviate_client, get_retriever
from llm_utils import llm_rerank_results, query_rewrite
from rag.retriever import Retriever
# In your main app
from modules.toolcalling import detect_tools_and_execute
from process_images import analyze_image_with_llm, image_bytes_to_base64, process_image_bytes
import logging
from weaviate.classes.query import Filter
client = get_openai_client(MOONSHOT_API_KEY, MOONSHOT_BASE_URL)
qwen_client = get_openai_client( QWEN_VL_API_KEY, QWEB_VL_BASE_URL) 
weaviate_client = get_weaviate_client()

# Pass the actual weaviate client, not the wrapper
retriever = Retriever(
    client=weaviate_client,  # Use the actual weaviate client
    collection_name="dviz_c_structured_v3",
    return_properties=["image_url", "section_11_description", "post_title", "post_url", "image_description","external_link"],
    target_vector="section_11_description_vector"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_source_website(query: str):
    """
    Detect if user mentions a specific source website and return appropriate filter
    """
    query_lower = query.lower()
    
    if "flowingdata" in query_lower or "flowing data" in query_lower:
        return "flowingdata"
    elif "ggplot2" in query_lower or "ggplot" in query_lower:
        return "ggplot2"  
    elif "datawrapper" in query_lower or "data wrapper" in query_lower:
        return "datawrapper"
    
    return None


# Update the format_results_for_display function
async def format_results_for_display(results: list, title: str):
    """
    Sends each result as a separate message with description and image.
    """
    if not results:
        await cl.Message(content="No matching visualizations found.").send()
        return

    # Send title message first
    await cl.Message(content=f"**{title}**").send()

    # Send each result as a separate message
    for i, doc in enumerate(results, 1):
        props = getattr(doc, "properties", {}) or {}
        #desc = props.get("section_11_description") or "No description available."
        #desc_trunc = (desc[:200] + "...") if len(desc) > 200 else desc
        image_url = props.get("image_url")
        post_title = props.get("post_title") or "No title"
        post_url = props.get("post_url")
        external_link = props.get("external_link")
        if external_link:
            post_url = external_link
        image_description = props.get("image_description") or "No image description available."

        # Build the result content with all the information
        #result_content = f"**{i}. {post_title}**\n\n"
        #result_content += f"**Description:** {desc_trunc}\n\n"
        result_content = f"**Image Description:** {image_description}\n\n"
        
        # Add links
        if image_url:
            result_content += f"🖼️ [View Visualization]({image_url})\n"
        if post_url:
            result_content += f"📄 [View Original Post]({post_url})"
        if external_link:
            result_content += f"\n🔗 [External Link]({external_link})"
        
        if image_url:
            try:
                # Send message with both text and image
                await cl.Message(
                    content=result_content,
                    elements=[cl.Image(name=f"viz_{i}", display="inline", url=image_url, size="medium")]
                ).send()
            except Exception as e:
                print(f"Error creating image element for {image_url}: {e}")
                await cl.Message(content=result_content).send()
        else:
            await cl.Message(content=result_content).send()

async def process_image_from_url(image_url: str, client):
    try:
        logger.info(f"Fetching image from URL: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        logger.info("Image fetched successfully, processing content...")
        
        image_content = process_image_bytes(response.content)
        img_base = image_bytes_to_base64(image_content)
        logger.info("Image content processed, analyzing with LLM...")
        
        description = analyze_image_with_llm(client, img_base, prompt_img)
        logger.info("Image analysis completed.")
        return description
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error while fetching image: {req_err}")
        return None
    except Exception as e:
        logger.error(f"Error processing image from URL: {e}")
        return None

async def process_uploaded_image(image_file, client):
    try:
        image_content = process_image_bytes(image_file.content)
        img_base = image_bytes_to_base64(image_content)
        description = analyze_image_with_llm(client, img_base, prompt_img)
        return description
    except Exception as e:
        print(f"Error processing image with OpenAI: {e}")
        return None

prompt_img = """[CONTEXT & ROLE]
You are a specialized and meticulous Data Visualization Analyst AI. Your purpose is to analyze data visualizations and provide a max 3-4 sentence description optimized for semantic search and matching.

the description should includes:

1. **Chart Type & Structure**: 
2. **Data & Variables**: 
3. **Visual Design Elements**: 
   - Color scheme and encoding
   - Typography and text elements
   - Layout and arrangement
   - Grid lines and axes
   - Legend and guides

4. **Key Patterns & Insights**

5. **Design Features**:

6. **Context**: 

Your description should be detailed enough with relevant keeywords that someone could understand the visualization without seeing it, and comprehensive enough to enable accurate semantic matching with similar visualizations in a database.

Focus on creating a rich, descriptive text that captures both the technical aspects and the communicative purpose of the visualization.
it should be max 3-4 sentences, concise and to the point."""

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("retriever", retriever)
    cl.user_session.set("history", [])  # Initialize chat history
    await cl.Message(
        content=(
            "👋 **Welcome to the Data Visualization Search App!**\n\n"
            "I can help you find visualizations from sources like Datawrapper, and TidyTuesday.\n\n"
            "**Here's how you can search:**\n"
            "- ⌨️ **Describe a chart**: Type what you're looking for. The more specific, the better!\n"
            "  - *Example:* `Find scatter plots with a dark background and a blue color scheme.`\n"
            "- 🖼️ **Use an image**: Upload an image or paste an image URL to find similar visualizations.\n"
            "- 🔍 **Filter by source**: Mention `flowingdata`, `ggplot2`, or `datawrapper` in your query.\n"
            "  - *Example:* `Show me bar charts from flowingdata.`\n"
            "- 🛠️ **Use commands**: Access advanced search options like `Hybrid Search` and `Long Context Retrieval` using the command button."
        )
    ).send()
    await cl.context.emitter.set_commands(COMMANDS)

@cl.on_message
async def on_message(message: cl.Message):
    
    user_query = message.content.strip()
    source_website = detect_source_website(user_query)
    filter_message = f" (filtered by {source_website})" if source_website else ""
    filter_condition = None
    if source_website:
        filter_condition = Filter.by_property("source_website").equal(source_website)
    # Handle image URL paste before query rewriting
    if user_query.startswith(('http://', 'https://')):
        processing_msg = cl.Message(content="🔄 Detected URL - processing image...")
        await processing_msg.send()
        
        try:
            description = await process_image_from_url(user_query, qwen_client)
            
            if description:
                await processing_msg.remove()
                
                # Show analyzed image first
                await cl.Message(
                    content=f"✅ **Image from URL successfully analyzed!**\n\n**Analysis:** {description}",
                    elements=[cl.Image(name="Analyzed Image", display="inline", url=user_query, size="large")]
                ).send()
                
                # Search for similar results
                results = retriever.retrieve(description, filters = filter_condition,limit=100)
                if results and getattr(results, "objects", None):
                    reranked_objects = await llm_rerank_results(qwen_client, description, results.objects)
                    top_k_results = reranked_objects[:20]
                    await format_results_for_display(top_k_results, f"Top {len(top_k_results)} Similar Visualizations Found")
            else:
                processing_msg.content = "❌ Error analyzing the image from URL. Please check the URL and try again."
                await processing_msg.update()
            return
        except Exception as e:
            processing_msg.content = f"❌ Error processing URL: {str(e)}"
            await processing_msg.update()
            return

    # Handle file uploads before query rewriting
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File):
                thinking_msg = cl.Message(content="🔍 Analyzing uploaded image...")
                await thinking_msg.send()
                
                try:
                    description = await process_uploaded_image(element, qwen_client)
                    
                    if description:
                        await thinking_msg.remove()

                        # Show uploaded image first
                        await cl.Message(
                            content=f"✅ **Uploaded image successfully analyzed!**\n\n**Analysis:** {description}",
                            elements=[cl.Image(name="Uploaded Image", display="inline", content=element.content, size="large")]
                        ).send()

                        # Search for similar results
                        results = retriever.retrieve(description,filters = filter_condition, limit=100)
                        if results and getattr(results, "objects", None):
                            reranked_objects = await llm_rerank_results(qwen_client, description, results.objects)
                            top_k_results = reranked_objects[:20]
                            await format_results_for_display(top_k_results, f"Top {len(top_k_results)} Similar Visualizations Found")
                    else:
                        thinking_msg.content = "❌ Error analyzing uploaded image."
                        await thinking_msg.update()
                except Exception as e:
                    thinking_msg.content = f"❌ Error processing uploaded image: {str(e)}"
                    await thinking_msg.update()
                return

    # --- Regular Text Query Logic ---
    rewritten_user_query = await query_rewrite(qwen_client, user_query)
    await cl.Message(content=f"🔄 **Rewritten Query:** {rewritten_user_query}").send()
    
    retr = cl.user_session.get("retriever")

    if message.command:
        if message.command == "upload_image":
            await cl.Message(content="📤 Please upload an image to analyze...").send()
            return

        if message.command == "analyze_url":
            await cl.Message(
                content="🔗 **Image URL Mode**\n\nPlease provide the URL of the image you want to analyze.\n\n"
                        "**Example:**\n"
                        "`https://example.com/chart.png`\n\n"
                        "*Just paste the image URL in your next message and I'll analyze it!*"
            ).send()
            cl.user_session.set("waiting_for_url", True)
            return
        
        if message.command == "deconstruct_elements_tool":
            thinking_msg = cl.Message(content="🔧 Analyzing your query with tools...")
            await thinking_msg.send()
            
            print(f"DEBUG: User query: {user_query}")  # Add this debug line
            
            tool_analysis = await analyze_user_query_with_tools(user_query)
            results = tool_analysis.get("results", [])
            hits = tool_analysis.get("hits", [])

            print(f"DEBUG: Got {len(hits)} hits and {len(results)} results")  # Add this debug line

            # Create a message to show the detected tools
            if hits:
                tool_info = []
                for hit in hits:
                    tool_name = f"search_{hit.field}"
                    arguments = {"query": hit.query, "field": hit.field, "field_type": hit.field_type}
                    tool_info.append(f"- **Tool:** `{tool_name}` | **Arguments:** `{arguments}`")
                
                tool_message = f"🛠️ **Tools Called:**\n" + "\n".join(tool_info)
                await cl.Message(content=tool_message).send()
            else:
                await cl.Message(content="🚫 No tools were detected for this query.").send()

            if results:
                try:
                    await thinking_msg.remove()
                    reranked_results = await llm_rerank_results(qwen_client, user_query, results, rewritten_user_query)
                    top_k_results = reranked_results[:20]
                    title = f"Top {len(top_k_results)} Results (Tool-Based Search)"
                    await format_results_for_display(top_k_results, title)
                except Exception as e:
                    print(f"Rerank error in tool calling: {e}")
                    title = "Top 30 Results (Fallback)"
                    await format_results_for_display(results[:30], title)
            else:
                thinking_msg.content = "No visualizations matched your query using the detected tools."
                await thinking_msg.update()
            return

        if message.command == "hybrid_search":
            thinking_msg = cl.Message(content="🔍 Running hybrid (keyword + vector) search...")
            await thinking_msg.send()
            results = retr.hybrid_retrieve(user_query, filters = filter_condition, limit=100, alpha=0.5)

            if results and getattr(results, "objects", None):
                try:
                    await thinking_msg.remove()
                    reranked_results = await llm_rerank_results(qwen_client, user_query, results.objects)
                    top_k_results = reranked_results[:20]
                    title = f"Top {len(top_k_results)} Hybrid Search Results (Reranked)"
                    await format_results_for_display(top_k_results, title)
                except Exception as e:
                    logger.error(f"Error during LLM reranking: {e}")
                    top_k_results = results.objects[:20]
                    title = f"Top {len(top_k_results)} Hybrid Search Results"
                    await format_results_for_display(top_k_results, title)
            else:
                thinking_msg.content = "No results found with hybrid search."
                await thinking_msg.update()
            return

        if message.command == "long_context_retrieval":
            thinking_msg = cl.Message(content="🧠 Gathering extended context (top 150 results)...")
            await thinking_msg.send()
            raw_results = retr.retrieve(rewritten_user_query,filters = filter_condition, limit=150)

            if not raw_results or not getattr(raw_results, "objects", None):
                thinking_msg.content = "No results found for extended context."
                await thinking_msg.update()
                return

            objs = raw_results.objects
            try:
                if len(objs) > 1:
                    await thinking_msg.remove()
                    reranked = await llm_rerank_results(qwen_client, user_query, objs, rewritten_user_query)
                    objs = reranked
            except Exception as e:
                print(f"Rerank error: {e}")

            top_k = objs
            title = f"Top {len(top_k)} Long-Context Results (Reranked from 150)"
            await format_results_for_display(top_k, title)
            return

    # Regular search handling
    if not cl.user_session.get("waiting_for_url") and not user_query.startswith(('http://', 'https://')):
        results = retr.retrieve(rewritten_user_query, filters = filter_condition,limit=10)
        
        if results and getattr(results, "objects", None):
            title = f"Top {len(results.objects)} Results for: '{user_query}'"
            await format_results_for_display(results.objects, title)
        else:
            await cl.Message(content=f"No visualizations found for: {user_query}").send()

async def analyze_user_query_with_tools(user_query: str):
    try:
        hits, results = detect_tools_and_execute(client, user_query, weaviate_client)
        return {
            "hits": hits,  # Return the actual ToolHit objects, not dict conversion
            "results": results,
            "has_tools": len(hits) > 0
        }
    except Exception as e:
        print(f"Tool detection error: {e}")
        return {"hits": [], "results": [], "has_tools": False}