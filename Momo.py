from numpy import random
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import csv

#隨機秒數休息
def sleeptime(multiply = 1):
    sleept = random.uniform(1, 5)
    time.sleep(sleept * multiply)
#等待頁面讀取完成
def driverwait(xpath):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

#......變數......#
prd_count = 0
ans_index = 0
prd_all = '無資料'
prd_link_list = []
prd_key_list = ['豆皮', '豆腐', '豆干', '豆包', '豆花',
                '豆漿', '豆奶', '豆乳', '豆醬', '豆棗',
                '腐竹', '素肉', '素雞', '干絲', '醬油',
                '油膏', '味噌', '納豆', '豆腐乳', '豆瓣醬']
#...............#

#開啟網頁
driver = webdriver.Firefox()
csvfile = open('momo_' + str(time.strftime('%Y%m%d%H%M')) + '.csv', 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)
writer.writerow(['產品名稱', '產品資訊'])
driver.get('https://www.momoshop.com.tw/main/Main.jsp')
for prd_key in prd_key_list:
    prd_link_list = []
    driver.get('https://www.momoshop.com.tw/search/searchShop.jsp?keyword=' + prd_key + '&searchType=1&curPage=1&_isFuzzy=0&showType=chessboardType')
    sleeptime()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        search_sum = soup.select_one('div dl dt span b').text
        print(prd_key, '共', search_sum, '筆資料')
    except:
        print(prd_key, '無資料')
        continue
#計算分頁數
    if int(search_sum) % 30 == 0:
        next_btn = int(search_sum) / 30
    elif int(search_sum) < 30:
        next_btn = 1
    else:
        next_btn = int(search_sum) // 30 + 1
    print(prd_key, '共', next_btn, '頁資料')
    for count_page in range(next_btn):
        driver.get('https://www.momoshop.com.tw/search/searchShop.jsp?keyword=' + prd_key + '&searchType=1&curPage=' + str(count_page + 1) + '&_isFuzzy=0&showType=chessboardType')
        driverwait('/html/body/div[1]/div[4]/div[5]/div[4]/ul/li[1]/a/div/h3')
        sleeptime()
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_link = soup.select('a.goodsUrl')
        for prd_detail in prd_link:
            if prd_key in prd_detail.get_text():
                prd_link_list.append('https://www.momoshop.com.tw' + prd_detail.get('href'))
#前往各產品頁面
    for prd_link_get in prd_link_list:
        driver.get(prd_link_get)
        sleeptime()
        try:
            driverwait('/html/body/div[1]/div[3]/div[3]/form/div[2]/div[1]/h3')
        except:
            continue
#滾動更新頁面
        for search_more in range(150):
            scroll_step = 100
            driver.execute_script("window.scrollBy(0," + str(scroll_step) + ")")
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[3]/form/div[2]/ul/li[2]/span').click()
                break
            except:
                pass
            scroll_step = scroll_step + 50
            time.sleep(0.01)
        sleeptime()
        soup = BeautifulSoup(driver.page_source, 'lxml')
#抓取產品資訊表格
        prd_name = soup.select_one('div.prdnoteArea h3')
        try:
            prd_info_df = pd.read_html(str(soup))
            sleeptime()
        except:
            continue
        for prd_df_search in prd_info_df:
            ans_index = 0
            try:
                for prd_table in prd_df_search[0]:
                    if prd_table == '商品規格':
                        prd_all = (prd_df_search[1][ans_index])
                    ans_index = ans_index + 1
            except:
                continue
                ans_index = ans_index + 1
        prd_count = prd_count + 1
        print(prd_count, prd_name.text, prd_all)
        writer.writerow([str(prd_name.text), prd_all])
        ans_index = 0
        prd_all = '無資料'
print('已將資料寫入csv')
csvfile.close()
driver.close()
