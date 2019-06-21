# 10720CS_570100_DataScience
清大資工所 資料科學 作業

開發用作業系統為Windwos, IDE為PyCharm

## Final Project
### 目的

資料科學的期末專案，我們這組主要想探討學歷通膨與教育不平等的問題。

我這邊負責到Google News爬蟲，存成JSON以及txt檔案，並做資料視覺化 (輸出文字雲圖)

### 使用說明

終端機 cd 到專案資料夾，接著輸入關鍵字即可自動爬蟲 (每個關鍵字約爬300篇新聞): 

```python=
  python crawler.py 香港 ch
  python crawler.py 反送中 ch
  python crawler.py 六四 ch
  python crawler.py Hong+Kong en
  python crawler.py Anti+Extradition+Law en
  python crawler.py Tiananmen en
```

接著我們到 show_data.py 這個檔案內，找到 **read_json_en** 、 **read_json_ch** 這兩個函式，手動設定下面的 "**file_name**" 這個變數，設定他要讀取的資料夾們
再來執行 show_data.py 這個檔案，即可自動輸出txt檔案以及文字雲圖囉~ 

```python=
python show_data.py
```

P.S. 可於show_data.py程式碼內，設定stop_word_list來過濾不想要顯示的字

langconv.py 以及 zh_wiki.py 僅為簡繁轉換用

msyh.ttf 則是為了支援中文文字雲所用到的字型

示意圖，無關上面的關鍵字:

![image](https://github.com/shawn2000100/10720CS_570100_DataScience/blob/master/DataScience_Final/word_count_text_ch_revised.png?raw=true)

![image](https://github.com/shawn2000100/10720CS_570100_DataScience/blob/master/DataScience_Final/word_count_text_en_revised.png)

---

## HW1
本次作業是到 https://arxiv.org/ 進行論文爬蟲(爬前100篇, sort by relevance)，要將連結、標題、作者爬回來，並且統計前50個常出現的關鍵字
使用方法有兩種:
  1. 直接修改crawler裡面的關鍵字，並執行主程式
  2. cd到專案資料夾，於令命列輸入 python crawler.py data+science   <--- 關鍵字範例，空白記得用+號連接

---

## HW2
本次作業是實作frequent pattern mining 演算法之 Apriori
使用方法:
  cd到專案資料夾，於令命列輸入 python frequent_pattern.py sample_in.txt out1.txt 50   <--- 關鍵字範例
  P.S. 當minimum support要求愈小、input txt愈大時程式會執行愈久哦~

---

## HW3
這次的作業3是到kaggle參加一個課堂競賽

https://www.kaggle.com/c/nthuds2019hw3/leaderboard

---

## HW4
這次的作業與HW3差不多，也是一個Kaggle競賽。 主要在學習填補Missing Value

https://www.kaggle.com/c/ds2019hw4/leaderboard

---

## HW5

---

## HW6

---

## practice_1 
這是一個爬蟲汽車拍賣網站，並作分析的練習

網址: https://www.findcar.com.tw/

---

## practice_2
這是一個介紹各種Classification模型及資料前處理的練習，可以學到很多重要的基本概念。 
最後面的Feature Selection及Pipeline我還是沒有弄得很懂
