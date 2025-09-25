from modules.image_utils import convert_github_url_to_raw

def format_visualization_markdown(i, j, doc, plot_url):
    # Only convert if it's a GitHub URL
    if "github.com" in plot_url:
        raw_image_url = convert_github_url_to_raw(plot_url)
    else:
        raw_image_url = plot_url
    return f"""
**Visualization {i}.{j+1}**
![Visualization {i}.{j+1}]({raw_image_url})
**Description:** {doc.properties.get('section_11_description', '')}
[View Source]({plot_url})
\n
"""