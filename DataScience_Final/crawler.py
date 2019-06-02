import sys
import os
import json
import time
from urllib.parse import quote
from urllib.request import urlopen, Request # 另一種爬法
from bs4 import BeautifulSoup



# 第一個功能，先將 paper連結、標題、作者 輸出
def crawl_news(keyword):
    # 第一步先針對關鍵字來建立資料夾
    newdir = keyword + '_0602'
    if not os.path.exists(newdir): # 判斷資料夾是否存在
        os.makedirs(newdir)        # 建立資料夾

    # 判斷是中文還是英文爬蟲，因為到時候要編碼
    if sys.argv[2] == 'ch':
        keyword = quote(keyword.encode('utf-8')) # 要用中文爬蟲比較麻煩，須要特別編碼一下!
    elif sys.argv[2] != 'ch' and sys.argv[2] != 'en':
        print('你應該輸入錯格式了!')
        return

    # 開始Google爬蟲
    # 這是第一頁用的網址
    url1 = 'https://www.google.com.tw/search?q=' + keyword + '&num=100&source=lnms&tbm=nws&sa=X&ved=0ahUKEwjM0uqM3MjiAhVKHKYKHaPIAEcQ_AUIECgB&biw=1536&bih=754'
    # 這是第二頁用的網址
    url2 =  'https://www.google.com.tw/search?q=' + keyword + '&num=100&tbm=nws&ei=AaryXMrQMILVmAXx2ZPoCA&start=100&sa=N&ved=0ahUKEwiK1eeU3MjiAhWCKqYKHfHsBI0Q8NMDCOIC&biw=1536&bih=754&dpr=1.25'
    # 這是第三用的網址
    url3 = 'https://www.google.com.tw/search?q=' + keyword + '&num=100&tbm=nws&ei=zqvyXL_ZKMiT8wWMx5zoDA&start=200&sa=N&ved=0ahUKEwi_-Mjw3cjiAhXIybwKHYwjB804ZBDw0wMI2AI&biw=1536&bih=754&dpr=1.25'

    # 標明自己身分，可以從瀏覽器的 inspect => request header 來看
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    # 這是拿來存所有爬蟲結果的
    search_result = list()

    # 因為每個網址都長得不太一樣，所以我用迴圈慢慢換網址來爬
    for url in [url1, url2, url3]:
        req = Request(url=url, headers=headers)
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")

        # 開始找要的資料
        items = soup.findAll("div", {"class": "g"})
        for item in items:
            # title
            news_title = item.find("h3", {"class": "r"}).find("a").text
            # url
            news_link = item.find("h3", {"class": "r"}).find("a")['href'] # 或者 item.find("h3", {"class": "r"}).find("a").get("href")
            # content
            news_text = item.find("div", {"class": "st"}).text

            # add item into json object
            search_result.append({
                "news_title": news_title,
                "news_link": news_link,
                "news_text": news_text
            })

        time.sleep(5) # 爬完很累，睡5秒
    # print(search_result)

    # 準備輸出檔案 degree+inflation_0602
    with open(newdir + '/' + 'search_result.json', 'w') as output_file:
        json.dump(search_result, output_file, indent=4)

if __name__ == '__main__':
    # 不要直接開啟主程式，於命令列開啟
    if len(sys.argv) == 1:
        print('請在命令列模式打開~')
        print('範例: python crawler.py 學歷通膨 ch')
        print('範例: python crawler.py degree+inflation en')
    # 在命令列打關鍵字爬蟲
    elif len(sys.argv) == 3:
        crawl_news(sys.argv[1])
