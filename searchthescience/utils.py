from typing import Optional


def format_search_result_markdown(
    title: str,
    url: str,
    body: Optional[str] = None,
    additional_info: Optional[dict] = None,
) -> str:
    """Format search results consistently in markdown"""
    markdown = f"### {title}\n"
    markdown += f"[{url}]({url})\n\n"

    if body:
        markdown += f"{body}\n\n"

    if additional_info:
        for key, value in additional_info.items():
            if value:  # Only add if value exists
                markdown += f"**{key}:** {value}\n"

    return markdown.strip()
