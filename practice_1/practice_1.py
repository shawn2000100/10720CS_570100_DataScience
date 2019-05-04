# coding=utf-8
from bs4 import BeautifulSoup
from urllib.request import urlopen
import numpy as np
import matplotlib.pyplot as plt
import pickle
import json

# 我們做一個爬蟲小範例
def crawler():
    # ----- crawler 會用到的函式 -----
    # 將url轉成beautifulsoup
    def url_to_soup(url):
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        return soup

    # 找出頁數數量
    def find_carpage(soup):
        carnum = soup.find('span', id='lblTopShowDesc')('b')
        carnum = int(carnum[0].text.replace(',', '')) # 有時候會遇到2,094台車之類的數字，要把，去掉
        page = int(carnum / 10)
        if carnum % 10 != 0:
            page += 1
        return page

    # 將收到的<ui> <li> tag (車子的資料) 轉成字典並回傳
    def parse_detail(detail):
        attribute_list = ['廠牌', '車款', '里程數', '每日平均里程', '年份', '顏色', '車輛所在地', '排氣量', '售價', '牌照稅', '燃料稅']
        thisCar = dict()  # 這台車的資料會被存成字典(JSON)
        for d in detail:
            # 用split(':')來將冒號的兩邊切割開來，分出資料欄位和資料
            attribute_and_content = d.text.strip().split('：')
            # print(attribute_and_content) # 從這邊可以看出，字串仍需做一些處理

            if attribute_and_content[0] in attribute_list:
                # 我們將一些不想顯示的資料去掉 (replace)
                data = attribute_and_content[1].replace(u'\xa0', '').replace('c.c', '').replace(',', '').replace('萬',
                                                                                                                 '').replace(
                    '年', '').replace('公里', '').replace('比較價格', '').strip()
                thisCar[attribute_and_content[0]] = data

        # 因為有時候會有 2011年10月 這種輸入，故要處理一下
        if len(thisCar['年份']) != 4:
            thisCar['年份'] = thisCar['年份'][:4]
        return thisCar


    # ----- crawler主程式 -----
    head = 'https://www.findcar.com.tw'  # 汽車網站的根網址
    url = 'https://www.findcar.com.tw/datalist.aspx?u=1&b=41&i=' # 爬Luxgen的資料
    # url = 'https://www.findcar.com.tw/datalist.aspx?u=1&b=9&i='    # 爬BMW的資料
    soup = url_to_soup(url + '1')
    page = find_carpage(soup)  # 抓頁數用

    # 準備一頁一頁的爬取裡面的所有文章，存車子的資料
    allcar = list()  # 這個list會存很多台車子的資料(字典)
    for p in range(1, min(page+1, 51)):
        print('current page :', p)
        soup = url_to_soup(url + str(p))  # 爬某頁的資料
        # 某些特殊情況需處理
        if '為了提供關聯性最高的搜尋結果，我們省略了部分的查詢結果' in str(soup):
            break

        # 依序進入每一篇文章裡
        target = soup.find_all('a', 'atitle cartitle')
        for t in target:
            car_url = head + t['href']
            soup = url_to_soup(car_url)

            detail = soup.find('ul', 'vehicle-details')('li')  # 把汽車文章內所有屬於<ui>的<li>抓下來
            # 把一輛車的資料存起來，這邊會返回一個字典
            onecar = parse_detail(detail)
            onecar['link'] = car_url  # 最後再把車子的 url 加進去 list 內
            allcar.append(onecar)
    print('--- crawling finished ---')

    # 將爬下來的結果存成pickle檔案
    # 這邊要自己設定一下輸出檔名!!!!!!!!
    output_name = 'Luxgen'
    with open(output_name + '.pickle', 'wb') as output_file:
        pickle.dump(allcar, output_file)
    # 練習將爬下來的結果存成json檔案
    with open(output_name + '.json', 'w') as output_file:
        json.dump(allcar, output_file, ensure_ascii=False, indent=4)

# 資料分析小範例
def data_analyze(file_name):
    # ----- 資料分析需用到的小函式 -----
    #  用xlable當x軸，售價當y軸 回傳對應的資料(x, y)
    def get_xy(allcar, xlabel):
        x = list()
        y = list()
        for i in allcar:
            # ['廠牌', '車款', '里程數', '每日平均里程', '年份', '顏色', '車輛所在地', '排氣量', '售價', '牌照稅', '燃料稅']
            if xlabel in i.keys() and i['售價']!='請電洽':
                x.append(float(i[xlabel]))
                y.append(float(i['售價']))
        return x, y


    # ----- 資料分析主程式 -----
    # 這邊看你要分析哪些檔案
    if '.pickle' in file_name:
        with open(file_name, 'rb') as f:
            input_data = pickle.load(f)
        # print(input_data)
    elif '.json' in file_name:
        with open(file_name, 'r') as f:
            input_data = json.load(f)
        # print(input_data)

    # ['廠牌', '車款', '里程數', '每日平均里程', '年份', '顏色', '車輛所在地', '排氣量', '售價', '牌照稅', '燃料稅']
    x, y = get_xy(input_data, '年份') # 可依序輸入上面的attribute來看各屬性與價格之關聯
    fit = np.polyfit(x, y, 1)
    fit_fn = np.poly1d(fit)
    # 開始畫圖，記得，X軸依你的選擇而不同
    p1, = plt.plot(x, y, 'k.')
    p2, = plt.plot(x, fit_fn(x), 'r')
    plt.xlabel('xlable')
    plt.ylabel('price (10 thousand)')
    plt.title(file_name)
    plt.show()


# ----- 主程式在這 -----
# 爬蟲用，基本上網址要自己設定。資料爬完後會存成 pickle 以及 json 檔案
crawler()
# 資料分析用，看要分析哪種車廠，名字要改一下
file_name = 'Luxgen'
data_analyze(file_name + '.pickle')
data_analyze(file_name + '.json')