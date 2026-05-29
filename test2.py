import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openpyxl import Workbook
# from sympy import re
import re

def step3_get_all_pdf(code):
    # 1. 設定初始網址與 Headers 偽裝
    base_url = f"https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/html/115_{code}.htm?v=1.0"
    # start_url = urljoin(base_url, "TotalGsdShow.htm")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    # # 2. 建立 Excel 活頁簿與標頭
    # wb = Workbook()
    # ws = wb.active
    # ws.append(["學校", "系所", "數學採計狀態"])  # 先寫入標頭，方便閱讀
    # excel_file = '採計數學.xlsx'

    # print("開始爬取 115 學年度個人申請校系分則...")

    # 啟用 requests Session 提高連線效率
    session = requests.Session()
    session.headers.update(headers)

    try:
        # response = session.get(start_url)
        response = session.get(base_url)
        if response.status_code != 200:
            print(f"無法連線到主頁面，狀態碼：{response.status_code}")
            exit()
            
        # 解析主頁面（所有學校列表）
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
       
        code_title_td = soup.find("td", string="校系代碼")

        if code_title_td:
            # 2. 找到「校系代碼」所在的整行 <tr>
            parent_tr = code_title_td.find_parent("tr")

            # 3. 在這一行裡面，尋找 class 包含 "g3" 的 <td>
            # 觀察 HTML 發現，科目、檢定、篩選倍率都帶有 g3，但科目是第一個
            target_td = parent_tr.find("td", class_="g3")

            if target_td:
                # 4. 提取文字並轉成 List
                # stripped_strings 會自動去掉空白，並將 <br> 分隔的文字拆開
                subjects_list = list(target_td.stripped_strings)

                print("--- 成功抓取科目列表 ---")
                print(subjects_list)
            else:
                print("在該行中找不到 class 為 g3 的欄位")
        else:
            print("找不到『校系代碼』儲存格")


    except Exception as e:
        print(f"程式執行發生異常: {e}")

if __name__ == "__main__":
    # 以國立台灣大學為例，colno=001，colname=國立台灣大學
    step3_get_all_pdf(code="001012")