# 10720CS_570100_DataScience
清大資工所 資料科學 作業

開發用作業系統為Windwos, IDE為PyCharm


## HW1
本次作業是到 https://arxiv.org/ 進行論文爬蟲(爬前100篇, sort by relevance)，要將連結、標題、作者爬回來，並且統計前50個常出現的關鍵字
使用方法有兩種:
  1. 直接修改crawler裡面的關鍵字，並執行主程式
  2. cd到專案資料夾，於令命列輸入 python crawler.py data+science   <--- 關鍵字範例，空白記得用+號連接

## HW2
本次作業是實作frequent pattern mining 演算法之 Apriori
使用方法:
  cd到專案資料夾，於令命列輸入 python frequent_pattern.py sample_in.txt out1.txt 50   <--- 關鍵字範例
  P.S. 當minimum support要求愈小、input txt愈大時程式會執行愈久哦~
