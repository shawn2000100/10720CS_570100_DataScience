import sys
import os
import json
import time
from datetime import datetime
from urllib.parse import quote, unquote
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


# 針對關鍵字在Google News上爬蟲，並存進資料夾裡
def crawl_news(search_keyword, language_mode):
    # 針對關鍵字建立資料夾
    today = str(datetime.today().strftime('%m%d'))
    newdir = search_keyword + '_' + today
    if not os.path.exists(newdir): # 判斷資料夾是否存在
        os.makedirs(newdir)        # 建立資料夾

    # 判斷是中文還是英文爬蟲，因為到時候要編碼
    if language_mode == 'ch':
        search_keyword = quote(search_keyword.encode('utf-8'))  # 要用中文爬蟲比較麻煩，須要特別編碼一下!，這個quote有它的用意，是給url用的
    elif language_mode != 'ch' and language_mode != 'en':
        print('輸入的格式應該有誤...')
        print('範例: python crawler.py 學歷通膨 ch')
        print('範例: python crawler.py degree+inflation en')
        return

    # 開始Google爬蟲，因為每個網址都長得不太一樣，所以之後我要用迴圈慢慢換網址來爬
    # 這是第一頁用的網址
    page1_url = 'https://www.google.com.tw/search?q=' + search_keyword + '&num=100&source=lnms&tbm=nws&sa=X&ved=0ahUKEwjM0uqM3MjiAhVKHKYKHaPIAEcQ_AUIECgB&biw=1536&bih=754'
    # 這是第二頁用的網址
    page2_url =  'https://www.google.com.tw/search?q=' + search_keyword + '&num=100&tbm=nws&ei=AaryXMrQMILVmAXx2ZPoCA&start=100&sa=N&ved=0ahUKEwiK1eeU3MjiAhWCKqYKHfHsBI0Q8NMDCOIC&biw=1536&bih=754&dpr=1.25'
    # 這是第三用的網址
    page3_url = 'https://www.google.com.tw/search?q=' + search_keyword + '&num=100&tbm=nws&ei=zqvyXL_ZKMiT8wWMx5zoDA&start=200&sa=N&ved=0ahUKEwi_-Mjw3cjiAhXIybwKHYwjB804ZBDw0wMI2AI&biw=1536&bih=754&dpr=1.25'
    # 標明自己的身分很重要!，可以從瀏覽器的 inspect => request header 來看
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    search_result = list() # 這是拿來存所有爬蟲結果的
    for page_url in [page1_url, page2_url, page3_url]:
        req = Request(url=page_url, headers=headers)
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")

        # 開始找要的資料
        items = soup.findAll("div", {"class": "g"})
        for item in items:
            news_title = item.find("h3", {"class": "r"}).find("a").text
            news_link = item.find("h3", {"class": "r"}).find("a")['href'] # 或者 item.find("h3", {"class": "r"}).find("a").get("href") 也可以
            news_text = item.find("div", {"class": "st"}).text
            # 把爬到的新聞標題、鏈結、摘要 存進一個dict，類似JSON格式
            search_result.append({
                "news_title": news_title,
                "news_link": news_link,
                "news_text": news_text
            })

        print("--- page: %s 完成" % page_url)
        time.sleep(5) # 睡覺很重要，不然會被當成DDOS ban掉

    # print(search_result)
    # 輸出檔案到新增的資料夾 keywords_DDMM/keywords.json
    with open(newdir + '/' + unquote(search_keyword) + '.json', 'w') as output_file:
        json.dump(search_result, output_file, indent=4)


if __name__ == '__main__':
    # 不要直接開啟主程式，於命令列開啟
    if len(sys.argv) == 1:
        print('請在命令列模式打開~')
        print('範例: python crawler.py 學歷通膨 ch')
        print('範例: python crawler.py degree+inflation en')
    # 在命令列打關鍵字爬蟲
    elif len(sys.argv) == 3:
        search_keyword, language_mode = sys.argv[1], sys.argv[2]
        print('--- 開始爬蟲: ' + search_keyword + ' ---')
        crawl_news(search_keyword, language_mode)
        print('--- 爬蟲完成 ---')
    else:
        print('輸入的格式應該有誤...')
        print('範例: python crawler.py 學歷通膨 ch')
        print('範例: python crawler.py degree+inflation en')