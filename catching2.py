import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import json
from itertools import chain

# 全局變數：核心網址與 Headers 設定
MAIN_URL = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/TotalGsdShow.htm"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': MAIN_URL  # 關鍵：下一隻程式存取時，必須假裝是從這個主頁點進去的
}

def step1_get_all_links():
    """ 第一步：負責抓取所有學校的子網頁連結 """
    print("【第一階段】開始抓取所有網頁連結...")
    session = requests.Session()
    response = session.get(MAIN_URL, headers={'User-Agent': HEADERS['User-Agent']})
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    all_urls = []
    
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
            
    print(f"成功收集到 {len(all_urls)} 個學校連結。\n")
    return all_urls

def step2_process_links(url_list):
    """ 第二步：接收上一步的連結列表，並帶上 Referer 進行深入爬取 """
    print("【第二階段】開始處理收集到的連結...")
    session = requests.Session()
    
    university_codes = []
    for item in url_list[0:2]:
        
        # 關鍵：這裏的 headers 一定要帶有含有 Referer 的那組設定
        response = session.get(item['url'], headers=HEADERS)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            codes = re.findall(rf"\d{{6}}", response.text)
            university_codes.append({
                'name': item['name'],
                'codes': list(set(codes))
            })
            print(f"成功抓到{item['name']}代碼數量: {len(set(codes))} 個")

            # with open("collection_codes.json", "a", encoding="utf-8") as f:
            #     f.write(json.dumps(university_codes, ensure_ascii=False) + "\n")

        else:
            print(f"  => 請求失敗，狀態碼：{response.status_code}")
            
        time.sleep(1) # 良好爬蟲習慣，每次請求稍微限制速度
    
    with open("collection_codes.json", "w", encoding="utf-8") as f:
        # 使用 json.dump 將資料寫入檔案
        json.dump(university_codes, f, ensure_ascii=False, indent=4)

    print("JSON 檔案寫入成功！")

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
                time.sleep(1) # 良好爬蟲習慣，每次請求稍微限制速度

            else:
                print("在該行中找不到 class 為 g3 的欄位")
        else:
            print("找不到『校系代碼』儲存格")


    except Exception as e:
        print(f"程式執行發生異常: {e}")

# 執行主流程
if __name__ == "__main__":

    # 1. 執行第一隻程式（Function 1）
    collected_links = step1_get_all_links()

    # 2. 執行下一隻程式（Function 2），並把連結陣列傳給它
    step2_process_links(collected_links)

    # 讀取外部的 .json 檔案
    with open("collection_codes.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 使用 itertools.chain 搭配生成器運算式，將所有 codes 串聯起來
    # 這樣做不會一次性產生巨大的 list，非常節省記憶體
    all_codes = chain.from_iterable(item["codes"] for item in data)

    # 3. 執行第三隻程式（Function 3），並把所有的 code 傳給它
    for code in all_codes:
        step3_get_all_pdf(code)
    