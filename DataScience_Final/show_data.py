#encoding=utf-8
import os
import json
from apyori import apriori  # Frequent Pattern 分析用
import jieba                # 中文斷詞用
from langconv import*       # 繁體轉簡體用，為了讓 結巴 的中文斷詞表現更好
from wordcloud import WordCloud

# 有些字我們不在乎，只要一碰到就可以去掉它...
stop_word_list = [', ', ',', '...', '的', '\xa0', ' ', '「', '」', '。', '，', '、', '（', '）', '：', '.', '...', '】', '【', '....', '”',
                  'a', 'is', 'of', 'the', 'an', 'to', 'as', 'at', 'by', 'in', 'on', 'with', 'for', 'and', 'are', 'that', 'have', 'has', 'had', 'we',
                  '-', '—', 'your', 'its', '', '“', '／', '；', '》', '《', '“', 'he', 'they', 'was', 'or', 'be', 'this', 'how', 'his', 'per',
                  'it\'s', 'so', 'who', 'were', 'their', 'it', 'what', 'you', 'our', 'she', 'my', 'say', 10, 20]

# 讀取 英文 版本JSON檔，並將所有檔案整合成一份 txt 檔並輸出，接著再做資料處理  (老實說，模組化寫得不好... 較無彈性...)
# 因為中文版處理方式較麻煩 (需斷詞)，故分成兩種版本
def read_json_en(keywords_of_title_en, keywords_of_text_en):
    # 將所有爬到的 English新聞 們整合成一份 txt 檔案，以便將來討論某個特定關鍵字的成因
    def aggregate_news_en(json_file):
        with open('aggregated_news_en.txt', 'w') as f:
            for data in json_file:
                f.write('news_title: ')
                f.write(str(data['news_title'].encode(encoding="utf-8")))
                f.write('\n')
                f.write('news_text: ')
                f.write(str(data['news_text'].encode(encoding="utf-8")))
                f.write('\n')
                f.write('news_link: ')
                f.write(str(data['news_link'].encode(encoding="utf-8")))
                f.write('\n\n')


    # 我們要一次處理多個 json 檔案，這邊要 ***手動*** 設定資料夾名稱，並放在project的同一個資料夾內 (或者用絕對路徑)
    file_name = ['Anti+Extradition+Law_0622', 'Hong+Kong_0622', 'Tiananmen_0622']
    # 把所有讀進來的JSON檔案存進一個list內
    json_data_list = list()
    for name in file_name:
        if os.path.exists(name):
            print(name + '/' + name[:-5] + '.json')
            with open(name + '/' + name[:-5] + '.json', 'r') as input_file:
                tmp_json_data = json.load(input_file)
                json_data_list.extend(tmp_json_data)
        else:
            print('資料夾名稱: %s 應該有誤，請檢查' % (name))
    # print(json_data_list)
    # print(len(json_data_list))      # 看一下讀進了幾條新聞
    aggregate_news_en(json_data_list) # 將所有讀進來的 英文 新聞整合成一份txt檔

    # 開始把句子中的單字拆出來，順便去除stop_word，未來要做資料分析用
    for news in json_data_list:
        # 處理標題
        tmp = []
        for char in news['news_title'].lower().split():  # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
            if char not in stop_word_list:
               tmp.append(char)
        keywords_of_title_en.append(tmp)

        # 處理內文
        tmp = []
        for char in news['news_text'].lower().split():  # 記得要一律轉成小寫，不然之後會分析不出frequent pattern
            if char not in stop_word_list:
                tmp.append(char)
        keywords_of_text_en.append(tmp)


# 讀取 中文 版本JSON檔，並將所有檔案整合成一份 txt 檔並輸出，接著再做資料處理  (老實說，模組化寫得不好... 較無彈性...)
# 因為中文版處理方式較麻煩 (需斷詞)，故分成兩種版本
def read_json_ch(keywords_of_title_ch, keywords_of_text_ch):
    # 將所有爬到的新聞們整合成一份 txt 檔案，中文版需處理編碼問題，比較麻煩
    def aggregate_news_ch(json_file):
        with open('aggregated_news_ch.txt', 'wb') as f:  # 這邊要記得用wb
            for data in json_file:
                f.write('news_title: '.encode('utf8'))
                f.write(data['news_title'].encode('utf8'))
                f.write('\n'.encode('utf8'))
                f.write('news_text: '.encode('utf8'))
                f.write(data['news_text'].encode(encoding="utf-8"))
                f.write('\n'.encode('utf8'))
                f.write('news_link: '.encode('utf8'))
                f.write(data['news_link'].encode(encoding="utf-8"))
                f.write('\n\n'.encode('utf8'))


    # 我們要一次處理多個 json 檔案，這邊要 ***手動*** 設定資料夾名稱，並放在project的同一個資料夾內 (或者用絕對路徑)
    file_name = ['六四_0622', '香港_0622', '反送中_0622']
    json_data_list = list()
    for name in file_name:
        if os.path.exists(name):
            with open(name + '/' + name[:-5] + '.json', 'r') as input_file:
                tmp_json_data = json.load(input_file)
                json_data_list.extend(tmp_json_data)
        else:
            print('檔案名稱: %s 應該有誤，請檢查' % (name))
    # print(json_data_list)
    # print(len(json_data_list)) # 看一下讀進了幾條新聞
    aggregate_news_ch(json_data_list)  # 將所有讀進來的 中文 新聞整合成一份txt檔

    # 開始把句子中的字拆出來 (中文斷詞)，順便去除stop_word，未來要做資料分析用
    for news in json_data_list:
        # 處理標題
        title = news['news_title']                   # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        title = Converter('zh-hans').convert(title)  # 繁體中文轉換成簡體中文，這樣斷詞的效果比較好
        # print(title)
        seg_list = jieba.cut(title, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(title, HMM=True)   # 搜尋引擎模式，好像沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        keywords_of_title_ch.append(split_word)

        # 處理內文
        text = news['news_text']                    # 中文比較麻煩，沒辦法用split來切。 需使用 結巴 函式庫
        text = Converter('zh-hans').convert(text)   # 繁體中文轉換成簡體中文，這樣斷詞的效果比較好
        # print(text)
        seg_list = jieba.cut(text, cut_all=False, HMM=True) # 預設精準模式
        # seg_list = jieba.cut_for_search(text, HMM=True)   # 搜尋引擎模式，不知道有沒有比較厲害?
        split_word = "/".join(seg_list)
        # print(split_word)
        keywords_of_text_ch.append(split_word)

    # 將斷詞過後的中文 標題 弄成適合作Apriori的資料格式 (list)，故使用到tmp, tmp2 (外層list包一堆內層list)
    tmp = []
    for sentence in keywords_of_title_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                word = Converter('zh-hant').convert(word)  # 最後轉換回繁體中文
                tmp2.append(word)
        tmp.append(tmp2)
    keywords_of_title_ch[:] = tmp # 這麼做超級重要!! 因為 keywords_of_text_ch[] = tmp 只是改變local的指標，當函數結束就被回收了 (所以不會真的變動到...)

    # 將斷詞過後的中文 內文 弄成適合作Apriori的資料格式 (list)，故使用到tmp, tmp2 (外層list包一堆內層list)
    tmp = []
    for sentence in keywords_of_text_ch:
        words = sentence.split('/')
        tmp2 = []
        for word in words:
            if word not in stop_word_list:
                word = Converter('zh-hant').convert(word) # 最後轉換回繁體中文
                tmp2.append(word)
        tmp.append(tmp2)
    keywords_of_text_ch[:] = tmp # 這麼做超級重要!! 因為 keywords_of_text_ch[] = tmp 只是改變local的指標，當函數結束就被回收了 (所以不會真的變動到...)


# 回傳frequent pattern分析後的結果 (frozen set)
def frequent_pattern_analyze(data):
    print('----- 開始Frequent Pattern分析... (Apriori) -----')
    # print(data)
    association_rules = apriori(data)
    association_results = list(association_rules)
    frequent_pattern_result = []
    for i in association_results:
        frequent_pattern_result.append(i)
    print('----- Frequent Pattern分析完成! -----')
    return frequent_pattern_result


# 由於Frequent Pattern效果不好，故嘗試關鍵字頻率分析
def frequency_statistics(data):
    frequency_count = {}
    for news_title in data:
        for word in news_title:
            if word not in frequency_count and word not in stop_word_list:
                frequency_count[word] = 1
            elif word in frequency_count and word not in stop_word_list:
                frequency_count[word] += 1

    # 依照出現頻率由大到小排序
    sorted_frequency_count = sorted(frequency_count.items(), key=lambda x: x[1], reverse=True)
    # 這邊再進一步處理，把一些 單一字 或 頻率太低的字過濾掉 (e.g., '我': 14)
    freq_count_result = []
    for i in sorted_frequency_count:
        if len(i[0]) >= 2 and i[1] >= 15:  # len(i[0]) 是中文詞長度、len(i[1]) 是出現頻率 (原則上我們對單一中文字沒興趣，故過濾)
            freq_count_result.append( (i[0], i[1]) )
    return freq_count_result


# 方便 print list用的
def print_data(data):
    print(' --- print data... ---')
    for i in data:
        print(i)
    print(' --- print finished! ---')

# 將分析出來的 頻率統計 輸出成4個txt檔案，以供將來做成文字雲
def output_frequency_count(word_count_title_en, word_count_text_en,
                           word_count_title_ch, word_count_text_ch):
    with open('word_count_title_en.txt', 'w') as f:
        for tuple in word_count_title_en:
            for i in range(tuple[1]):
                f.write(tuple[0] + ' ')
            f.write('\n')
    with open('word_count_text_en.txt', 'w') as f:
        for tuple in word_count_text_en:
            for i in range(tuple[1]):
                f.write(tuple[0] + ' ')
            f.write('\n')
    with open('word_count_title_ch.txt', 'w') as f:
        for tuple in word_count_title_ch:
            for i in range(tuple[1]):
                f.write(tuple[0] + ' ')
            f.write('\n')
    with open('word_count_text_ch.txt', 'w') as f:
        for tuple in word_count_text_ch:
            for i in range(tuple[1]):
                f.write(tuple[0] + ' ')
            f.write('\n')


# 將統計出來的資料視覺化成文字雲 共4張圖片，不輸出frequent pattern (沒有找到明顯的pattern, 且格式比較難處理)
def output_word_cloud():
    # 這邊要 ***手動*** 設定txt檔案名稱，並放在project的同一個資料夾內 (或者用絕對路徑)
    for file_name in ['word_count_title_en', 'word_count_text_en', 'word_count_title_ch', 'word_count_text_ch']:
        text = open( file_name + ".txt", 'r').read()
        wc = WordCloud(background_color="white",
                       width=1000,
                       height=860,
                       margin=2,
                       font_path='msyh.ttf', # 引入一個支援中文的字型，建議字型放在同一個資料夾內
                       collocations=False,   # 這行超重要!!!，不然字體會重複出現多次
                       max_words=100,
                       max_font_size=150,
                       min_font_size=32)
        wc.generate(text)
        wc.to_file(file_name + '.png')


if __name__ == '__main__':
    # 首先宣告list，未來要存新聞 標題&內文 關鍵詞用的
    keywords_of_title_en, keywords_of_text_en = list(), list()
    keywords_of_title_ch, keywords_of_text_ch = list(), list()

    # 讀取 English JSON檔案，並存進 keywords_of_title_en, keywords_of_text_en 兩個list
    read_json_en(keywords_of_title_en, keywords_of_text_en)
    print_data(keywords_of_title_en)
    print_data(keywords_of_text_en)

    # 讀取 中文 JSON檔案，並存進 keywords_of_title_ch, keywords_of_text_ch 兩個list
    read_json_ch(keywords_of_title_ch, keywords_of_text_ch)
    print_data(keywords_of_title_ch)
    print_data(keywords_of_text_ch)

    # 開始做 英文版 Frequent Pattern 分析
    frequent_pattern_of_title_en = frequent_pattern_analyze(keywords_of_title_en)
    print_data(frequent_pattern_of_title_en)
    frequent_pattern_of_text_en = frequent_pattern_analyze(keywords_of_text_en)
    print_data(frequent_pattern_of_text_en)

    # 開始做 中文版 Frequent Pattern 分析
    frequent_pattern_of_title_ch = frequent_pattern_analyze(keywords_of_title_ch)
    print_data(frequent_pattern_of_title_ch)
    frequent_pattern_of_text_ch = frequent_pattern_analyze(keywords_of_text_ch)
    print_data(frequent_pattern_of_text_ch)

    # 開始做 English版 字彙頻率 分析
    frequency_count_of_title_en = frequency_statistics(keywords_of_title_en)
    print_data(frequency_count_of_title_en)
    frequency_count_of_text_en = frequency_statistics(keywords_of_text_en)
    print_data(frequency_count_of_text_en)

    # 開始做 中文版 字彙頻率 分析
    frequency_count_of_title_ch = frequency_statistics(keywords_of_title_ch)
    print_data(frequency_count_of_title_ch)
    frequency_count_of_text_ch = frequency_statistics(keywords_of_text_ch)
    print_data(frequency_count_of_text_ch)

    # 開始輸出 字母頻率 統計，共4個txt檔案
    output_frequency_count(frequency_count_of_title_en, frequency_count_of_text_en, frequency_count_of_title_ch, frequency_count_of_text_ch)
    # 開始輸出 文字雲 ，會讀取上一步驟之4個txt檔案 (或者你自己準備其他txt檔案也可以啦...)
    output_word_cloud()