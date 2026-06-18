import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote


def get_university_data():
    # 1. 定義主網頁網址
    main_url = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/TotalGsdShow.htm"

    # 2. 設定基礎 Headers（關鍵：後續請求都要帶上 Referer）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': main_url  # 告訴伺服器：我們是從 TotalGsdShow.htm 點進來的
    }

    # 3. 使用 Session 機制維持連線狀態
    session = requests.Session()

    try:
        # 先請求一次主網頁
        response = session.get(main_url, headers={'User-Agent': headers['User-Agent']})
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"主網頁請求失敗，狀態碼：{response.status_code}")
            exit()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 4. 找出所有的學校超連結
        links = soup.find_all('a')
        print(f"成功解析主網頁，預計開始爬取 {len(links)} 所學校...")

        for a_tag in links:
            href = a_tag.get('href')
            school_name = a_tag.text.strip()
            
            if not href or "ShowSchGsd.php" not in href:
                continue  # 排除可能不是學校連結的標籤
                
            # 將相對路徑（ShowSchGsd.php?...）組合成完整的 URL
            sub_url = urljoin(main_url, href)
            
            print(f"正在抓取：{school_name}")
            
            # 5. 發送請求進去子超連結（因為 headers 裡面有帶 Referer，所以不會失效）
            sub_response = session.get(sub_url, headers=headers)
            sub_response.encoding = 'utf-8'
            
            if sub_response.status_code == 200:
                print(f"  => 成功進入！資料長度：{len(sub_response.text)}")
                
                # 這裡就是個別學校的網頁內容了，可以開始用 BeautifulSoup 抓裡面的校系
                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                
                # 舉例：你可以列印出子網頁的標題，看是不是正確的學校名稱
                # print(sub_soup.title.text if sub_soup.title else "無標題")
                
            else:
                print(f"  => 進入失敗，狀態碼：{sub_response.status_code}")
                
            print("-" * 50)

    except Exception as e:
        print(f"程式執行發生錯誤：{e}")
    