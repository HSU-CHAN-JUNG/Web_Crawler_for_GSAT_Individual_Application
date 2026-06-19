import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import json
from itertools import chain
import csv
import os
import random
import time

# 全局變數：核心網址與 Headers 設定
MAIN_URL = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/TotalGsdShow.htm"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': MAIN_URL  # 關鍵：下一隻程式存取時，必須假裝是從這個主頁點進去的
}
session = requests.Session()

def get_university_codes():
    """ 第一步：負責抓取所有學校的子網頁連結 """
    print("【第一階段】開始抓取所有網頁連結...")
    # session = requests.Session()
    response = session.get(MAIN_URL, headers={'User-Agent': HEADERS['User-Agent']})
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    all_urls = []
    
    output_filename = "universities_code.jsonl"
    with open(output_filename, "w", encoding="utf-8") as f:
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            school_name = a_tag.text.strip()
            
            if href and "ShowSchGsd.php" in href:
                full_url = urljoin(MAIN_URL, href)
                # 將學校名稱與完整網址包成字典存起來
                all_urls.append({
                    'name': school_name,
                    'url': full_url
                })
            # print(f"school_name: {school_name}\n")
            pattern = re.compile(
                        r"\((?P<code>\d+)\)(?P<name>\S+)\s+-\s*(?P<departments>\d+)系\(組\)"
                        )
            match = pattern.search(school_name)
            if match:
                # 提取捕捉到的群組資料
                data_dict = {
                    "school_name": match.group("name"),
                    "code": match.group("code"),
                    "total_departments": int(
                        match.group("departments")
                    ),  # 轉成數字型態
                }
            json_line = json.dumps(data_dict, ensure_ascii=False)
            f.write(json_line + "\n")
            
    print(f"成功收集到 {len(all_urls)} 個學校連結。\n")
    return all_urls

def get_all_pdf(code, ):
    # 1. 設定初始網址與 Headers 偽裝
    url = f"https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/html/115_{code}.htm?v=1.0"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    session.headers.update(headers)

    max_retries = 3  # 最多重試 3 次
    for attempt in range(max_retries):
        try:
            # 設定 timeout=10 秒，如果 10 秒內網站不理我，就跳到 except
            response = session.get(url, timeout=10)
            response.encoding = "utf-8"  # 確保中文正確

            if response.status_code == 200:
                # print("抓取成功！")
                break  # 成功了就跳出重試迴圈

        except requests.exceptions.RequestException as e:
            print(
                f"第 {attempt+1} 次連線失敗，原因：{e}。將在 5 秒後重試..."
            )
            time.sleep(5)  # 等待 5 秒再試
    else:
        print("❌ 已經重試 3 次皆失敗，可能 IP 已被暫時封鎖，請更換網路（如手機熱點）或晚點再跑。")

        
    # 解析主頁面（所有學校列表）
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

    school = soup.find('div', class_='colname').text.strip()
    department = soup.find('div', class_='gsdname').text.strip()
    code_title_td = soup.find("td", string="校系代碼")
    
    if code_title_td:
        # 2. 找到「校系代碼」所在的整行 <tr>
        parent_tr = code_title_td.find_parent("tr")
        # 3. 在這一行裡面，尋找 class 包含 "g3" 的 <td>
        # 觀察 HTML 發現，科目、檢定、篩選倍率都帶有 g3，但科目是第一個
        target_td = parent_tr.find_all("td", class_="g3")
        
        if target_td and len(target_td) >= 3:
            # 4. 提取文字並轉成 List
            # stripped_strings 會自動去掉空白，並將 <br> 分隔的文字拆開
            subjects_list = list(target_td[0].stripped_strings)
            grades_list = list(target_td[1].stripped_strings)

            fill_grades_csv(school, department, subjects_list, grades_list)
            # print("--- 成功抓取科目列表 ---")
            # print(subjects_list)

            time.sleep(random.uniform(1, 3)) # 良好爬蟲習慣，每次請求稍微限制速度
        else:
            print("在該行中找不到 class 為 g3 的欄位")



def init_csv(filename="table.csv"):
    """初始化 CSV 檔案，單純寫入第一行的標題欄位"""
    headers = ["學校", "學系", "國文", "數學A", "數學B", "英文", "自然", "社會"]

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # 只寫入第一行標題

    # print(f"【成功】已建立全新 CSV 檔案：{filename}")


def fill_grades_csv(school_name, department, subjects, grades, filename="table.csv"):
    """
    輸入學校名稱、科目 list、等第 list。
    自動在 CSV 結尾新增一行，並把等第填入對應的科目下方。
    """
    if not os.path.exists(filename):
        print(f"錯誤：找不到檔案 {filename}，正在自動為您初始化...")
        init_csv(filename)

    # 1. 讀取現有的 CSV 所有內容
    with open(filename, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("錯誤：檔案完全空白，請先執行 init_csv()")
        return

    headers = rows[0]  # 第一行永遠是標題：['學系/科目', '國文', '數學A', ...]

    # 2. 建立新的一列資料，預設全部留空
    # 長度與標題一樣長，例如：['', '', '', '', '', '', '']
    new_row = [""] * len(headers)

    # 將第一格（學系/科目）填入你指定的學校名稱
    new_row[0] = school_name
    new_row[1] = department

    # 3. 偵測並比對兩組 list
    for sub, grade in zip(subjects, grades):
        if sub in headers:
            col_idx = headers.index(sub)  # 找到科目所在的直欄編號
            new_row[col_idx] = grade  # 把等第填入該位置
            
            # print(f"[{school_name}] 成功對應：【{sub}】填入 -> {grade}")
        
        # else:
            # print(f"[{school_name}] 跳過：標題中沒有【{sub}】這個科目。")

    # 4. 將這一行新資料追加（Append）到原本的 rows 裡面
    rows.append(new_row)

    # 5. 寫回 CSV 檔案
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # print(f"【成功】{school_name} {department} 的資料已寫入 {filename}！\n")

# 執行主流程
if __name__ == "__main__":
    start_time = time.time()

    collected_links = get_university_codes()

    # 讀取外部的 .json 檔案
    with open("universities_code.jsonl", "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    init_csv()  # 在開始抓取 PDF 前，先確保 CSV 已經初始化好了
        # 啟用 requests Session 提高連線效率

    for item in data:
        if not item:
            continue  # 跳過空資料

        # 安全取得欄位名稱，注意：要跟你的 json 鍵名完全一致（單數 code 還是複數 codes）
        school = item.get("school_name")  
        code = item.get("code")  
        total_deps = item.get("total_departments", 0)
        # print(f"學校代碼: {code}，總系所數: {total_deps}")


        for i in range(1, total_deps + 1):
            # f"{i:02d}" 代表：將數字 i 格式化為 2 位數，不足的部分在前面補 0
            new_string = f"{code}{i:02d}2"
            # print(new_string)

            get_all_pdf(new_string)
        print(f"【成功】{school} 的資料已寫入！\n")
        
        
    end_time = time.time()
    print(f"總共花費 {end_time - start_time:.2f} 秒完成所有任務！")