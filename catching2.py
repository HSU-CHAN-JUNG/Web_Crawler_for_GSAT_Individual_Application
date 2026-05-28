import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import json

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
    for item in url_list:
        
        # 關鍵：這裏的 headers 一定要帶有含有 Referer 的那組設定
        response = session.get(item['url'], headers=HEADERS)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            codes = re.findall(rf"\d{{6}}", response.text)
            university_codes.append({
                'name': item['name'],
                'codes': list(codes)
            })
            print(f"成功抓到{item['name']}代碼數量: {len(set(codes))} 個")

        else:
            print(f"  => 請求失敗，狀態碼：{response.status_code}")
            
        time.sleep(1) # 良好爬蟲習慣，每次請求稍微限制速度
    
    with open("collection_codes.json", "w", encoding="utf-8") as f:
        # 使用 json.dump 將資料寫入檔案
        json.dump(university_codes, f, ensure_ascii=False, indent=4)

    print("JSON 檔案寫入成功！")

# 執行主流程
if __name__ == "__main__":
    # 1. 執行第一隻程式（Function 1）
    collected_links = step1_get_all_links()

    # 2. 執行下一隻程式（Function 2），並把連結陣列傳給它
    step2_process_links(collected_links)