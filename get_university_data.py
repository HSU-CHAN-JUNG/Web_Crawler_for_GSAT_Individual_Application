import requests
from bs4 import BeautifulSoup
import re

def get_university_data(colno, colname):
    # 1. 建立一個能自動記錄 Cookie 的 Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 2. 乖乖走完前置流程，向伺服器領取「通行證 (Cookie)」
    index_url = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/index.php"
    pages_url = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/pages.php"

    print("正在建立連線並領取 Cookie...")
    session.get(index_url)
    session.get(pages_url)  # 模擬走到大學列表頁面

    # 3. 把原本網址後面那一長串 %20 (空白) 清乾淨，只保留到學校名稱
    clean_chengchi_url = f"https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/ShowSchGsd.php?colno={colno}&colname={colname}"


    # 4. 關鍵：加上 Referer 偽裝，告訴伺服器我們是從列表頁點進來的
    headers = {
        "Referer": pages_url
    }

    print(f"帶著通行證與 Referer 進入{colname}網頁...")
    response = session.get(clean_chengchi_url, headers=headers)
    response.encoding = 'utf-8'

    # 5. 測試是否成功拿到網頁內容
    soup = BeautifulSoup(response.text, "html.parser")
    print(f"網頁標題: {soup.title.text if soup.title else '失敗'}")

    # 看看有沒有抓到政大的科系代碼 (006xxx)
    codes = re.findall(rf"\({colno}\d{{3}}\)", response.text)
    print(f"成功抓到{colname}代碼數量: {len(set(codes))} 個")

if __name__ == "__main__":
    # 以國立政治大學為例，colno=006，colname=國立政治大學
    get_university_data(colno="001", colname="國立台灣大學")