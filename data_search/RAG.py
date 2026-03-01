import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from sentence_transformers import CrossEncoder
import sys

def get_resource_path(relative_path):
    """ 获取资源绝对路径，兼容开发环境和 PyInstaller 环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径 (dist/meme_search/_internal)
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

reranker = CrossEncoder("BAAI/bge-reranker-large")

# embedding 模型（必须和之前一致）
model = SentenceTransformer("BAAI/bge-m3")
# 向量
embeddings = np.load(get_resource_path(os.path.join("data_index", "pic_name.npy")))
# index
index = faiss.read_index(get_resource_path(os.path.join("data_index", "pic_name.index")))

def vector_retrieve(query, chunks, top_k=20):
    q_emb = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "idx": idx,
            "score": float(score),
            "text": chunks[idx]["text"],
            "source": chunks[idx].get("source", "")
        })
    return results

def rerank(query, docs, top_k=5):
    pairs = [(query, d["text"]) for d in docs]
    scores = reranker.predict(pairs)

    for d, s in zip(docs, scores):
        d["rerank_score"] = float(s)

    docs = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
    return docs[:top_k]


def rag_answer(query, chunks):
    vec_results = vector_retrieve(query, chunks, top_k=20)
    retrieved = rerank(query, vec_results, top_k=5)
    return [d["text"] for d in retrieved]


def get_ans(query):
    with open(get_resource_path(os.path.join("data_index", "pic_name.json")), 'r', encoding="utf-8") as f:
        chunks = json.load(f)
    text=rag_answer(query,chunks)
    link=["raw_data/"+a+".jpg" for a in text]
    return text,link