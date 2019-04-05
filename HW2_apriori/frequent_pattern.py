from sys import argv
import re


# 掃描Dataset，建立出 "單一元素" 之集合，以便未來進行join...等運算, 稱之C1
def create_C1(data_set):
    C1 = set()
    for trans in data_set:  # 遍歷每筆Transaction
        for item in trans:  # 遍歷Transaction裡的所有keyword
            item_set = frozenset([item]) # 由於我們的frequent pattern words是成對出現的，所以需要用frozenset來一次存一群Keywords...
            C1.add(item_set)
    return C1

# 使用Downward Closure Property剪枝，加快程式執行
def is_apriori(Ck_item, Lk_previous):
    for item in Ck_item:
        sub_Ck = Ck_item - frozenset([item])
        if sub_Ck not in Lk_previous:
            return False
    return True

# 從Lk-1生出Ck, k表示關鍵詞數量
def create_Ck(Lk_previous, k):
    Ck = set()
    len_Lk_previous = len(Lk_previous)
    list_Lk_previous = list(Lk_previous)
    for i in range(len_Lk_previous):
        for j in range(1, len_Lk_previous):
            trans1 = list(list_Lk_previous[i])
            trans2 = list(list_Lk_previous[j])
            trans1.sort()
            trans2.sort()
            # 判斷假如兩個transactions至倒數第二個字一樣，就union他們
            # 例如: C, B UNION C, E  =>  C, B, E
            if trans1[0:k-2] == trans2[0:k-2]:
                Ck_item = list_Lk_previous[i] | list_Lk_previous[j]
                # pruning，使用到downward closure property
                if is_apriori(Ck_item, Lk_previous):
                    Ck.add(Ck_item)
    return Ck

# 計算Candidate i 及對應之support number 產生出 Lk (趁機去掉不滿足support number的組合)
def generate_Lk_by_Ck(data_set, Ck, min_support, support_data):
    Lk = set()
    item_count = {}
    for trans in data_set:
        # 這邊簡單來說就是在統計所有 Ck 的關鍵字組合們，在整個Database裡出現的次數
        for item in Ck:
            if item.issubset(trans):
                if item not in item_count:
                    item_count[item] = 1
                else:
                    item_count[item] += 1
    # 計算完Ck內所有字彙的出現次數(support number)後，我們要儲存 >= sup 要求的frozenset(Lk) 及support number(support_data)
    for item in item_count:
        if item_count[item] >= min_support:
            Lk.add(item)
            support_data[item] = item_count[item]
    return Lk

# apriori實作
def apriori_implement(data_set, max_trans_len, min_support):
    C1 = create_C1(data_set)            # 生成Candidate level_1
    support_data = {}                   # 空字典，到時候會將frozenset(關鍵字們) : support_value 的組合return
    L1 = generate_Lk_by_Ck(data_set, C1, min_support, support_data)  # 統計C1們的出現次數，只記錄 >= support_number的結果
    Li_previous = L1.copy() # 之後會需要暫存前一回合之Li-1
    # 繼續進行C2 -> L2, C3 -> L3, C4 -> L4...之過程。迭代次數不會超過max_trans_len
    for i in range(2, max_trans_len + 1):
        Ci = create_Ck(Li_previous, i)                                  # 首先依據Li-1，生成關鍵詞組，Ci
        Li = generate_Lk_by_Ck(data_set, Ci, min_support, support_data) # 判斷Ci的support_number，只存 >= support_number之組合
        # 假如此回合Li計算出來為空集合，後面都不用繼續算了，代表Li-1為最大之frequent pattern集合
        if len(Li) == 0:
            break
        Li_previous = Li.copy()

    return support_data

# 負責讀進input file(原始摘要集)，並作字串前處理，最後輸出database
def read_input_and_preprocess(transactions, input_file_name):
    # 讀取stop word list
    with open('stop_words.txt', 'r') as f:
        words = f.readlines()
        stop_words = []  # 用來存所有的stop words
        for word in words:
            stop_words.append(word.strip('\n'))
        stop_words.extend(['.', ',', '?']) # 為了以後不讓浮點數 (0.xxx)被亂拆，我們先將. , ?加進stop word list裡面
    # 讀取 摘要們 (input file)
    with open(input_file_name, 'r') as f:
        abstracts = f.readlines()  # 把一堆摘要讀進來，並塞進list

    # 準備開始剖析所有abstract，先拆成各自的句子，再接著細分出transaction
    max_trans_len = 44     # 預設值，到時候會變大
    for abs in abstracts:  # 到摘要池中依序抓摘要出來，並準備拆分出句子
        abs = abs.lower()                              # 摘要全部轉成小寫
        abs = re.sub('[\\n]', ' ', abs)                # 將摘要後面的換行字元替換掉
        abs = re.sub('[!@\\#$%^&*()\\n$:;]+', '', abs) # 替換掉某些不必要之字元
        sentences = re.split('(?<![0-9])([\.,?])', abs)
        # print(sentences)
        for sentence in sentences:
            word = sentence.strip().split(' ')  # 把一個sentence拆成好幾個words
            # 上一步將sentence拆成words還不夠，需接著再處理stop word跟空字串
            word_item = []
            for w in word:
                if w not in stop_words and len(w) >= 1:
                    word_item.append(w)
            if len(word_item) >= 1:  # 需做這一檢查是因為有可能word_item = [] (完全沒加進任何東西)
                transactions.append(word_item)
                # print(word_item)
                max_trans_len = max(max_trans_len, len(word_item)) # 單筆交易最大的單詞數量

    return max_trans_len, transactions

# 排序freq_pat，順便將型態從dict轉成list
# 例如 dict:
# { frozenset({'learning'}): 246,
#   frozenset({'data'}): 163,
#   frozenset({'networks'}): 101 }
# 轉換成 list:
# [ [['data'], 163],
#   [['learning'], 246],
#   [['model'], 125] ]
def  sort_pattern(freq_pat):
    new_type_of_freq = []
    for i in freq_pat:
        new_list = []         # 連frozenset及support值一起存進去
        keywords = []         # 只存frozenset的keywords
        sup_val = freq_pat[i] # frozenset對應的support值

        # 依序迭代frozenset，把裡面的keywords string加進同一個list
        for j in i:
            keywords.append(j)
        keywords.sort() # 順便sort裡面的keywords

        # 這邊會將 [ ['keyword1', '2', '3'], 100 ] 這整行list再加進一個大list裡面 (如同Database)
        new_list.append(keywords)
        new_list.append(sup_val)
        new_type_of_freq.append(new_list)

    new_type_of_freq.sort() # 實在想不太到好的sorting辦法了，只好靠這招來sort外部(整體資料庫)
    return new_type_of_freq

# 輸出txt檔
# 此時收到的freq_pat已成為list型態，例如:
# [ [['data'], 163],
#   [['learning'], 246],
#   [['model'], 125] ]
def output_file(freq_pat, output_name):
    with open(output_name, 'w') as f:
        for i in freq_pat:
            sup_num = i[1]

            # 這行純粹只為處理那討厭的 '-'
            if len(i[0]) == 1 and i[0][0] == '-':
                continue

            for j in i[0]:
                f.write(str(j) + ' ')
            f.write(str(sup_num))
            f.write('\n')

# 主程式
if __name__ == '__main__':
    # 需在命令列模式執行 e.g., python frequent_pattern.py sample_in.txt out1.txt 10
    if len(argv) != 4:
        print('請在命令列模式執行 (e.g., python frequent_pattern.py sample_in.txt out1.txt 80)')
    else:
        input_name = argv[1]                # 欲讀取之input檔案
        output_name = argv[2]               # 欲輸出之frequent pattern之檔案名稱
        minimum_support_num = int(argv[3])  # 指定minimum support
        max_trans_len = 44                  # 紀錄單筆交易最大的詞彙量，可減少apriori迴圈執行次數
        transactions = []                   # 初始化，空的字彙資料庫

        # 前處理input檔案，回傳單筆最大之words數以及單詞資料庫
        # 例如:
        # [ ['deep', 'reinforcement', 'learning', 'enabled', 'control', 'increasingly', 'complex', 'high-dimensional', 'problems'],
        #   ['however'],
        #   ['need', 'vast', 'amounts', 'data', 'reasonable', 'performance', 'attained', 'prevents', 'widespread', 'application'] ]
        # max_trans_len = 9
        max_trans_len, transactions = read_input_and_preprocess(transactions, input_name)
        # print(transactions)

        # 使用上一步處理好之Database來執行apriori演算法計算frequent pattern
        freq_pat = apriori_implement(transactions, max_trans_len, minimum_support_num)
        # print(freq_pat)
        # print(type(freq_pat))

        # 接著依照Output Format來排序處理好之frequent pattern結果(其實沒有完全排正確...
        # 另外，此步驟會順便轉換資料型態 (由dict 轉成 list
        sorted_freq_pat = sort_pattern(freq_pat)
        # print(sorted_freq_pat)
        # print(type(sorted_freq_pat))

        # 排序完成，依照argv[2] 及 [3] 輸出txt檔
        output_file(sorted_freq_pat, output_name)