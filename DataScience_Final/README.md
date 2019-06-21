## 目的

資料科學的期末專案，我們這組主要想探討學歷通膨與教育不平等的問題。

我這邊負責到Google News爬蟲，存成JSON以及txt檔案，並做資料視覺化 (輸出文字雲圖)

## 使用說明

終端機 cd 到專案資料夾，接著輸入關鍵字即可自動爬蟲 (每個關鍵字約爬300篇新聞): 

```python=
  python crawler.py 香港 ch
  python crawler.py 反送中 ch
  python crawler.py 六四 ch
  python crawler.py Hong+Kong en
  python crawler.py Anti+Extradition+Law en
  python crawler.py Tiananmen en
```

接著我們到 show_data.py 這個檔案內，找到 read_json_en 、 read_json_ch 這兩個函式，手動設定下面的 "file_name" 這個變數，設定他要讀取的資料夾們
再來執行 show_data.py 這個檔案，即可自動輸出txt檔案以及文字雲圖囉~ 

```python=
python show_data.py
```

P.S. 可於show_data.py程式碼內，設定stop_word_list來過濾不想要顯示的字
