import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
model = SentenceTransformer("BAAI/bge-m3")


def embedding():
    with open(f"{BASE_DIR}/../data_index/pic_name.json",'r',encoding="utf-8") as f:
        texts = [c["text"] for c in json.load(f)]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # 下面的操作是魔法
    # 到时候它会帮你把问题向量从1*768变成1000*768 然后直接一个矩阵获取一个结果向量 快得不行
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # 内积 = cosine（已归一化）
    index.add(embeddings)
    faiss.write_index(index, f"{BASE_DIR}/../data_index/pic_name.index")
    np.save(f"{BASE_DIR}/../data_index/pic_name.npy", embeddings)