import sys
import re
import os
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen


# 第一個功能，先將 paper連結、標題、作者 輸出
def crawl_paper_info(keyword):
    # 第一步先針對關鍵字來建立資料夾
    newdir = keyword + '_0309/'
    if not os.path.exists(newdir):  # 判斷資料夾是否存在
        os.makedirs(newdir)  # 建立資料夾

    # 開始爬蟲
    url = "https://arxiv.org/search/?searchtype=all&query=" + keyword + "&abstracts=show&size=100&order="
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    # 準備輸出檔案
    with open(newdir + 'paper_info.txt', 'w', encoding='utf8') as output_file:
        # 首先進入搜尋結果頁面
        targets = soup.find_all('li', 'arxiv-result')
        # 依序進入文章
        for div in targets:
            link = div.find('p', 'list-title is-inline-block').find('a')['href']
            # print(link)
            output_file.write(link + '\n')

            title = div.find('p', 'title is-5 mathjax').text.strip()
            # print(title)
            output_file.write(title + '\n')

            author_list = div.find('p', 'authors').find_all('a')
            for author in author_list:
                # print(author.text, end=';')
                output_file.write(author.text + ';')
            # print()
            output_file.write('\n')
            # print(' --- ')
            # output_file.write(' --- ' + '\n')
        # 輸出全部完成，關閉檔案
        output_file.close()


def crawl_frequent_word(keyword):
    # 開始爬蟲
    url = "https://arxiv.org/search/?searchtype=all&query=" + keyword + "&abstracts=show&size=100&order="
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    # 接著開始將所有摘要存起來
    all_abstract = list()
    targets = soup.find_all('span', 'abstract-full has-text-grey-dark mathjax')
    # 依序存取文章摘要
    for abstract in targets:
        content = abstract.text.strip()[:-14].lower()  # 為了去除後面那討厭的 Less
        content = re.sub(r'[~!@#$%^&*()-_+{},.\\/]', '', content)  # 接著去除標點符號
        all_abstract.append(content)  # 把這篇摘要放進list裡面

    # 摘要全部存取完成，開始統計字母頻率
    freq_list = dict()
    # 首先打開stop_words
    with open('stop_words.txt', 'r') as stop_word_file:
        stop_word_list = stop_word_file.read()
    for paper in all_abstract:
        # print(paper)
        for word in paper.split():
            if word not in stop_word_list:
                # print(word)
                # print(type(word))
                if word not in freq_list.keys():  # 如果此單字從沒出現在統計中
                    freq_list[word] = 1
                else:  # 此單字曾出現過
                    freq_list[word] += 1
    freq_list = sorted(freq_list.items(), key=lambda x: x[1], reverse=True)  # 字典排序用
    # print(freq_list)

    # 統計完成，開始輸出檔案
    newdir = keyword + '_0309/'
    if not os.path.exists(newdir):  # 基本上，上一個函式已經建立過資料夾了。但還是判斷一下資料夾是否存在
        os.makedirs(newdir)  # 若不存在，建立資料夾
    # 準備輸出檔案
    with open(newdir + 'frequent_word.txt', 'w', encoding='utf8') as output_file:
        output_count = 0  # 計算輸出了幾筆
        for word in freq_list:
            if output_count <= 50:  # 還未輸出完前50筆資料
                # print(str(word[0]) + ' ' + str(word[1]))
                output_file.write(
                    str(word[0]) + ' ' + str(word[1]) + '\n')
                output_count += 1


if __name__ == '__main__':
    # 直接開啟主程式的話，預設爬蟲關鍵字為data+mining
    if len(sys.argv) == 1:
        crawl_paper_info('data+mining')
        time.sleep(1) # 睡一下，不要給對方伺服器太大的負擔
        print('crawl paper info done')
        crawl_frequent_word('data+mining')
        time.sleep(1) # 睡一下，不要給對方伺服器太大的負擔
        print('crawl frequent word done')
    # 在命令列打關鍵字爬蟲
    elif len(sys.argv) == 2:
        crawl_paper_info(sys.argv[1])
        time.sleep(1)  # 睡一下，不要給對方伺服器太大的負擔
        print('crawl paper info done')
        crawl_frequent_word(sys.argv[1])
        time.sleep(1)  # 睡一下，不要給對方伺服器太大的負擔
        print('crawl frequent word done')
