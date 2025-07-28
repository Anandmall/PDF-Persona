# main.py

import os
import json
import fitz
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def load_pdf_chunks(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if not text:
            continue

        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
        for para in paragraphs:
            chunks.append({
                "text": para,
                "page": page_num + 1
            })

    return chunks


def extract_persona_and_job(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n", 1)
        persona = lines[0].strip()
        job = lines[1].strip() if len(lines) > 1 else ""
        return persona, job


def run_ranking(doc_paths, persona, job, top_k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, under 100MB

    context = f"{persona}: {job}"
    query_embedding = model.encode(context)

    all_sections = []
    all_embeddings = []

    for pdf_path in doc_paths:
        doc_name = os.path.basename(pdf_path)
        chunks = load_pdf_chunks(pdf_path)

        for chunk in chunks:
            all_sections.append({
                "document": doc_name,
                "page": chunk["page"],
                "text": chunk["text"]
            })
            all_embeddings.append(model.encode(chunk["text"]))

    similarities = cosine_similarity([query_embedding], all_embeddings)[0]
    ranked_indices = similarities.argsort()[::-1][:top_k]

    extracted_sections = []
    subsection_analysis = []

    for rank, idx in enumerate(ranked_indices, 1):
        section = all_sections[idx]
        extracted_sections.append({
            "document": section["document"],
            "page_number": section["page"],
            "section_title": section["text"].split("\n")[0][:100],
            "importance_rank": rank
        })

        subsection_analysis.append({
            "document": section["document"],
            "refined_text": section["text"],
            "page_number": section["page"]
        })

    return extracted_sections, subsection_analysis


def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    doc_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]
    persona_file = os.path.join(input_dir, "persona.txt")

    persona, job = extract_persona_and_job(persona_file)

    extracted_sections, subsection_analysis = run_ranking(doc_paths, persona, job)

    result = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in doc_paths],
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(os.path.join(output_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ Result saved to output/result.json")


if __name__ == "__main__":
    main()
