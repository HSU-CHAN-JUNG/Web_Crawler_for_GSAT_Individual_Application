from bs4 import BeautifulSoup
import requests

url = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/TotalGsdShow.htm"

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
clean_chengchi_url = f"https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/ShowSchGsd.php?"


# 4. 關鍵：加上 Referer 偽裝，告訴伺服器我們是從列表頁點進來的
headers = {
    "Referer": pages_url
}

response = session.get(clean_chengchi_url, headers=headers)
response.encoding = 'utf-8'

# 檢查是否成功抓到正確網頁（若畫面只出現幾行 JavaScript 代表 Cookie 失敗或過期了）
if "國立" in response.text or "大學" in response.text:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 解析網頁中的學校與代碼
    for link in soup.find_all('a'):
        text = link.get_text(strip=True)
        if '(' in text or '（' in text:
            print(text)
else:
    print("抓取失敗：被網站的防爬蟲機制阻擋了！請檢查 Cookie 是否正確或過期，或改用方案一。")