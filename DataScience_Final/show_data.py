#encoding=utf-8
import sys
import os
import json
from apyori import apriori
import jieba

stop_word_list = [', ', ',', '...', '的', '\xa0', ' ', '「', '」', '。', '，', '、', '（', '）', '：', '.', '...',
                  'a', 'is', 'of', 'the', 'an', 'to', 'as', 'at', 'by', 'in', 'on', 'with', 'for', 'and', 'are', 'that']

# 輸出frequent pattern
def freq_pat_analy(data):
    # print(data)
    # 標題部分並無明顯之 frequent pattern...
    association_rules = apriori(data)
    association_results = list(association_rules)
    for i in association_results:
        print(i)
        print()


# 讀取英文版本之json資料檔案，因為中文版之處理方式較麻煩 (需斷詞)，故分成兩種版本之函式
def read_json_en():
    # 我們要一次處理多個 json 檔案
    file_name = ['diploma+inflation_0602', 'degree+inflation_0602', 'credential+inflation_0602', 'grade+inflation_0608', 'Academic+Inflation_0608']
    json_data_list = list()
    for name in file_name:
        if os.path.exists(name):
            with open(name + '/' + 'search_result.json', 'r') as input_file:
                tmp_json_data = json.load(input_file)
                json_data_list.extend(tmp_json_data)
        else:
            print('檔案名稱 %s 應該有誤，請檢查' % (name))
    # print(json_data_list)
    # print(len(json_data_list))

    global title_keywords_en, text_keywords_en
    title_keywords_en = []
    text_keywords_en = []
    for news in json_data_list:
        # 處理新聞標題
        title = news['news_title'].lower().split() # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
        # print(title)

        tmp = []
        for char in title:
            if char not in stop_word_list:
               tmp.append(char)
        title_keywords_en.append(tmp)
        # 處理內文
        text = news['news_text'].lower().split() # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
        # print(text)
        tmp = []
        for char in text:
            if char not in stop_word_list:
                tmp.append(char)
        text_keywords_en.append(tmp)


# 讀取中文版本之json資料檔案，因為中文版之處理方式較麻煩 (需斷詞)，故分成兩種版本之函式
def read_json_ch():
    # 我們要一次處理多個 json 檔案
    file_name = ['學歷貶值_0608', '學歷通膨_0602', '學歷氾濫_0608', '學歷不值錢_0608']
    json_data_list = list()
    for name in file_name:
        if os.path.exists(name):
            with open(name + '/' + 'search_result.json', 'r') as input_file:
                tmp_json_data = json.load(input_file)
                json_data_list.extend(tmp_json_data)
        else:
            print('檔案名稱 %s 應該有誤，請檢查' % (name))
    # print(json_data_list)
    # print(len(json_data_list))

    global title_keywords_ch, text_keywords_ch
    title_keywords_ch = []
    text_keywords_ch = []
    # jieba.set_dictionary('dict.txt.big') # 設定詞庫
    for news in json_data_list:
        # 處理新聞標題
        title = news['news_title'] # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        # print(title)
        seg_list = jieba.cut(title, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(title, HMM=True)   # 搜尋引擎模式，不知道有沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        title_keywords_ch.append(split_word)

        # 處理內文
        text = news['news_text'] # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        # print(text)
        seg_list = jieba.cut(text, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(text, HMM=True)   # 搜尋引擎模式，不知道有沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        text_keywords_ch.append(split_word)

    # print(title_keywords_ch)
    # print(text_keywords_ch)

    # 中文字串處理用
    tmp = []
    for sentence in title_keywords_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                tmp2.append(word)
        tmp.append(tmp2)
    title_keywords_ch = tmp

    tmp = []
    for sentence in text_keywords_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                tmp2.append(word)
        tmp.append(tmp2)
    text_keywords_ch = tmp

    # print(title_keywords_ch)
    # print(text_keywords_ch)



if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     print('請在命令列模式開啟')
    #     print('範例: python show_data.py')
    # elif len(sys.argv) == 3:
    #     read_json(sys.argv[1], sys.argv[2])

    read_json_en()
    print(' 開始英文版Frequent Pattern分析 ')
    freq_pat_analy(title_keywords_en)
    print(' - - - - - - - - - - - - - - - - - - - - - -  ')
    freq_pat_analy(text_keywords_en)
    print(' 英文版Frequent Pattern分析結束 ')

    read_json_ch()
    print(' 開始中文版Frequent Pattern分析 ')
    freq_pat_analy(title_keywords_ch)
    print(' ==========================================  ')
    freq_pat_analy(text_keywords_ch)
    print(' 中文版Frequent Pattern分析結束 ')