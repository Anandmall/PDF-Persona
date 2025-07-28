import fitz  # PyMuPDF
from collections import Counter
import re
import sys


def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    merged_blocks = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        last_style = None
        last_text = ""

        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    # Normalize font to ignore bold variations
                    base_font = span["font"].split(",")[0]
                    style = (round(span["size"], 2), base_font, span["color"])

                    if last_style is None:
                        last_style = style
                        last_text = span["text"]
                    elif style == last_style:
                        last_text += " " + span["text"]
                    else:
                        merged_blocks.append({
                            "text": last_text.strip(),
                            "style": {
                                "size": last_style[0],
                                "font": last_style[1],
                                "color": last_style[2]
                            },
                            "page": page_num + 1
                        })
                        last_style = style
                        last_text = span["text"]

        # Flush last span on page
        if last_text:
            merged_blocks.append({
                "text": last_text.strip(),
                "style": {
                    "size": last_style[0],
                    "font": last_style[1],
                    "color": last_style[2]
                },
                "page": page_num + 1
            })
    return merged_blocks

