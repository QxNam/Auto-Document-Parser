PROMPT = (
    "Extract the content of this PDF into high-quality Markdown format.\n"
    "- Maintain all hierarchical structures (headings, subheadings, lists).\n"
    "- Convert tables to standard Markdown tables. If a table is too complex or wide, "
    "represent it as a CSV within a code block.\n"
    "- Preserve the original reading order across pages.\n"
    "- Do not include any conversational preamble or comments, output ONLY the markdown content."
)