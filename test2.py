import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import json
from itertools import chain

def step3_get_all_pdf(code):
    # 1. 設定初始網址與 Headers 偽裝
    base_url = f"https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/html/115_{code}.htm?v=1.0"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    # 啟用 requests Session 提高連線效率
    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(base_url)
        if response.status_code != 200:
            print(f"無法連線到主頁面，狀態碼：{response.status_code}")
            exit()
            
        # 解析主頁面（所有學校列表）
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
       
        code_title_td = soup.find("td", string="校系代碼")
        # init_csv("score_table.csv")

        if code_title_td:
            # 2. 找到「校系代碼」所在的整行 <tr>
            parent_tr = code_title_td.find_parent("tr")

            # 3. 在這一行裡面，尋找 class 包含 "g3" 的 <td>
            # 觀察 HTML 發現，科目、檢定、篩選倍率都帶有 g3，但科目是第一個
            target_td = parent_tr.find_all("td", class_="g3")

            if target_td and len(target_td) >= 3:
                school = soup.find('div', class_='colname').text.strip()
                department = soup.find('div', class_='gsdname').text.strip()

                # 4. 提取文字並轉成 List
                # stripped_strings 會自動去掉空白，並將 <br> 分隔的文字拆開
                subjects_list = list(target_td[0].stripped_strings)

                # fill_grades_csv(school, department, subjects_list, [""] * len(subjects_list), filename="score_table.csv")

                subjects = [s.strip() for s in target_td[0].get_text(separator="\n").split("\n") if s.strip()]
                # 第二個 g3 是檢定標準 (底標)
                standards = [s.strip() for s in  target_td[1].get_text(separator="\n").split("\n") if s.strip()]
                # 第三個 g3 是篩選倍率
                multipliers = [m.strip() for m in target_td[2].get_text(separator="\n").split("\n") if m.strip()]

                # 3. 完美對齊輸出
                print(f"【科目】: {subjects[0]} / {subjects[1]}")
                print(f"【檢定】: {standards[0]} / {standards[1]}")
                print(f"【倍率】: {multipliers[0]} / {multipliers[1]}")
                print("--- 成功抓取科目列表 ---")
                print(subjects_list)
                time.sleep(1) # 良好爬蟲習慣，每次請求稍微限制速度


            else:
                print("在該行中找不到 class 為 g3 的欄位")
        else:
            print("找不到『校系代碼』儲存格")


    except Exception as e:
        print(f"程式執行發生異常: {e}")


if __name__ == "__main__":
    # 以國立台灣大學為例，colno=001，colname=國立台灣大學
    step3_get_all_pdf(code="001022")