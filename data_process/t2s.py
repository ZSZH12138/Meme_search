from opencc import OpenCC
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
cc=OpenCC('t2s')

def t2s():
    names=os.listdir(f"{BASE_DIR}/../raw_data")
    fails=[]

    for name in names:
        try:
            text=name.strip().rstrip(".jpg")
            converted=cc.convert(text)
            os.rename(f"{BASE_DIR}/../raw_data/{name}",f"{BASE_DIR}/../raw_data/{converted}.jpg")
        except:
            fails.append(name)
            continue

    if fails:
        print("-------------------------------")
        print("繁体字转换简体字失败如下：")
    for fail in fails:
        print(fail)
    if fails:
        print("----------------------------")