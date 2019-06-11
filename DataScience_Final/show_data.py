#encoding=utf-8
import sys
import os
import json
from apyori import apriori
import jieba
from langconv import*  # 繁體轉簡體用，為了讓 結巴 的中文斷詞表現更好

# 有些字我們不在乎
stop_word_list = [', ', ',', '...', '的', '\xa0', ' ', '「', '」', '。', '，', '、', '（', '）', '：', '.', '...', '】', '【', '....', '”',
                  'a', 'is', 'of', 'the', 'an', 'to', 'as', 'at', 'by', 'in', 'on', 'with', 'for', 'and', 'are', 'that', 'have', 'has', 'had', 'we',
                  '-', '—', 'your', 'its', '', '“', '／', '；', '》', '《', '“', 'he', 'they', 'was', 'or', 'be', 'this', 'how', 'his', 'per',
                  'it\'s', 'so', 'who', 'were', 'their', 'it', 'what', 'you']


# 讀取英文版本之json資料檔案，因為中文版之處理方式較麻煩 (需斷詞)，故分成兩種版本之函式
def read_json_en():
    # 我們要一次處理多個 json 檔案
    file_name = ['diploma+inflation_0602', 'degree+inflation_0602', 'credential+inflation_0602', 'grade+inflation_0608', 'Academic+Inflation_0608']
    json_data_list = list() # 把所有讀進來的JSON檔案存進一個list內
    for name in file_name:
        if os.path.exists(name):
            with open(name + '/' + 'search_result.json', 'r') as input_file:
                tmp_json_data = json.load(input_file)
                json_data_list.extend(tmp_json_data)
        else:
            print('檔案名稱 %s 應該有誤，請檢查' % (name))
    # print(json_data_list)
    # print(len(json_data_list))  # 看一下讀進了幾條新聞

    global title_keywords_en, text_keywords_en
    title_keywords_en = []  # 所有標題關鍵字
    text_keywords_en = []   # 所有內文摘要
    for news in json_data_list:
        # 首先處理新聞標題
        tmp = []
        for char in news['news_title'].lower().split():  # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
            if char not in stop_word_list:
               tmp.append(char)
        title_keywords_en.append(tmp)

        # 處理內文
        tmp = []
        for char in news['news_text'].lower().split():  # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
            if char not in stop_word_list:
                tmp.append(char)
        text_keywords_en.append(tmp)

    # print(title_keywords_en)
    # print(text_keywords_en)


# 讀取中文版本之json資料檔案，因為中文版之處理方式較麻煩 (需斷詞)，故分成兩種版本之函式
def read_json_ch():
    # 我們要一次處理多個 json 檔案
    file_name = ['學歷貶值_0608', '學歷通膨_0602', '學歷氾濫_0608', '學歷不值錢_0608', '畢業即失業_0608']
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
    for news in json_data_list:
        # 處理新聞標題
        title = news['news_title']                   # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        title = Converter('zh-hans').convert(title)  # 繁體中文轉換成簡體中文，這樣斷詞的效果比較好
        # print(title)
        seg_list = jieba.cut(title, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(title, HMM=True)   # 搜尋引擎模式，好像沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        title_keywords_ch.append(split_word)

        # 處理內文
        text = news['news_text']                    # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        text = Converter('zh-hans').convert(text)   # 繁體中文轉換成簡體中文，這樣斷詞的效果比較好
        # print(text)
        seg_list = jieba.cut(text, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(text, HMM=True)   # 搜尋引擎模式，不知道有沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        text_keywords_ch.append(split_word)

    # 將斷詞過後的中文字串弄成適合作Apriori的資料格式 (list)，故使用到tmp, tmp2
    # print(title_keywords_ch)
    # print(text_keywords_ch)
    tmp = []
    for sentence in title_keywords_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                word = Converter('zh-hant').convert(word)  # 最後轉換回繁體中文
                tmp2.append(word)
        tmp.append(tmp2)
    title_keywords_ch = tmp

    tmp = []
    for sentence in text_keywords_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                word = Converter('zh-hant').convert(word) # 最後轉換回繁體中文
                tmp2.append(word)
        tmp.append(tmp2)
    text_keywords_ch = tmp
    # 轉換結束
    # print(title_keywords_ch)
    # print(text_keywords_ch)


# 輸出frequent pattern
def freq_pat_analy(data):
    # print(data)
    association_rules = apriori(data)
    association_results = list(association_rules)
    freq_pat_result = []
    for i in association_results:
        freq_pat_result.append(i)
    return freq_pat_result

# 由於Frequent Pattern效果不好，故嘗試關鍵字頻率分析
def frequency_statistics(data):
    # print(data)
    frequency_count = {}
    for news_title in data:
        for word in news_title:
            if word not in frequency_count and word not in stop_word_list:
                frequency_count[word] = 1
            elif word in frequency_count and word not in stop_word_list:
                frequency_count[word] += 1

    # print(frequency_count)
    sorted_frequency_count = sorted(frequency_count.items(), key=lambda x: x[1], reverse=True)
    freq_count_result = []
    for i in sorted_frequency_count:
        if len(i[0]) >= 2 and i[1] >= 25:
            freq_count_result.append( (i[0], i[1]) )

    return freq_count_result


# 方便 print list用的
def print_data(data):
    for i in data:
        print(i)


# 將分析出來的 Frequent Pattern 以及 頻率統計 輸出成兩個檔案，以供將來做成文字雲
def output_analysis_result(freq_pattern, freq_count):
    pass


# 將統計出來的資料視覺化成文字雲
def text_cloud():
    pass

if __name__ == '__main__':
    read_json_en() # 讀取JSON檔案，並存進 title_keywords_en, text_keywords_en 兩個全域的list
    read_json_ch() # 讀取JSON檔案，並存進 title_keywords_ch, text_keywords_ch 兩個全域的list

    print('--------------- 開始英文版Frequent Pattern分析 ---------------')
    freq_pat_of_title_en = freq_pat_analy(title_keywords_en)
    print_data(freq_pat_of_title_en)
    print(' - - - - - - - - - - - - - - - - - - - - - -  ')
    freq_pat_of_text_en = freq_pat_analy(text_keywords_en)
    print_data(freq_pat_of_text_en)
    print('--------------- 英文版Frequent Pattern分析結束 ---------------')
    print('--------------- 開始中文版Frequent Pattern分析 ---------------')
    freq_pat_of_title_ch = freq_pat_analy(title_keywords_ch)
    print_data(freq_pat_of_title_ch)
    print(' ==========================================  ')
    freq_pat_of_text_ch = freq_pat_analy(text_keywords_ch)
    print_data(freq_pat_of_text_ch)
    print('--------------- 中文版Frequent Pattern分析結束 ---------------')

    print('--------------- 開始英文版 字母頻率 分析 ---------------')
    freq_count_of_title_en = frequency_statistics(title_keywords_en)
    print_data(freq_count_of_title_en)
    print(' ==========================================  ')
    freq_count_of_text_en = frequency_statistics(text_keywords_en)
    print_data(freq_count_of_text_en)
    print('--------------- 英文版 字母頻率 分析結束 ---------------')
    print('--------------- 開始中文版 字母頻率 分析 ---------------')
    freq_count_of_title_ch = frequency_statistics(title_keywords_ch)
    print_data(freq_count_of_title_ch)
    print(' ==========================================  ')
    freq_count_of_text_ch = frequency_statistics(text_keywords_ch)
    print_data(freq_count_of_text_ch)
    print('--------------- 中文版 字母頻率 分析結束 ---------------')

    # output_analysis_result()
