import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_data():
    names=os.listdir(f"{BASE_DIR}/../raw_data")
    res=[]
    for i,name in enumerate(names):
        res.append(
            {"idx":i,
             "text":name.strip().rstrip(".jpg"),
             "link":f"raw_data/{name}"
             }
        )

    with open(f"{BASE_DIR}/../data_index/pic_name.json",'w',encoding="utf-8") as f:
        json.dump(res,f)