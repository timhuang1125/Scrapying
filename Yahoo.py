from numpy import random
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import pandas as pd

#隨機秒數休息
def sleeptime(multiply = 1):
    sleept = random.uniform(1, 5)
    time.sleep(sleept * multiply)
scroll_step = 100
#等待頁面讀取完成
def driverwait(xpath):
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, xpath)))

#......變數......#
prd_count = 0
ans_index = 0
firm_name = '無資料'
firm_add = '無資料'
firm_id = '無資料'
firm_idx = '無資料'
prd_link_list = []
prd_key_list = ['豆皮', '豆腐', '豆干', '豆包', '豆花',
                '豆漿', '豆奶', '豆乳', '豆醬', '豆棗',
                '腐竹', '素肉', '素雞', '干絲', '醬油',
                '油膏', '味噌', '納豆', '豆腐乳', '豆瓣醬']
#...............#

#開啟網頁
driver = webdriver.Firefox()
csvfile = open('Yahoo_' + str(time.strftime('%Y%m%d%H%M')) + '.csv', 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)
writer.writerow(['產品名稱', '廠商名稱', '廠商地址', '食品業者登錄字號'])
for prd_key in prd_key_list:
    prd_link_list = []
    driver.get('https://tw.buy.yahoo.com/search/product?cid=4419983&p=' + prd_key + '&pg=')
    driver.maximize_window()
    driver.refresh()
#計算分頁數
    search_sum = driver.find_element_by_xpath('//*[@id="isoredux-root"]/div[2]/div/div[2]/div/div[1]/span')
    prd_sum = search_sum.text.strip(' 筆結果')
    print(prd_key, '共有', prd_sum, '筆')
    if int(prd_sum) % 60 == 0:
        next_btn = int(prd_sum) / 60
    elif int(prd_sum) < 60:
        next_btn = 1
    else:
        next_btn = int(prd_sum) // 60 + 1
#抓取符合關鍵字之連結
    for count_page in range(next_btn):
        count_page = count_page + 1
        driver.get('https://tw.buy.yahoo.com/search/product?cid=4419983&p=' + prd_key + '&pg=' + str(count_page))
        driverwait('//*[@id="isoredux-root"]/div[2]/div/div[2]/div/div[1]/span')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_link = soup.find_all('a', class_='BaseGridItem__content___3LORP BaseGridItem__hover___3UlCS')
        for prd_detail in prd_link:
            if prd_key in prd_detail.get_text():
                prd_link_list.append(prd_detail.get('href'))
#前往各產品頁面
    for prd_link_get in prd_link_list:
        driver.get(prd_link_get)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_name = soup.find('h1', class_='HeroInfo__title___57Yfg HeroInfo__textTooLong___BXk8j')
        if prd_name == None:
            continue
#滾動更新頁面
        for search_more in range(150):
            scroll_step = 100
            driver.execute_script("window.scrollBy(0," + str(scroll_step) + ")")
            scroll_step = scroll_step + 50
            time.sleep(0.01)
#抓取產品資訊表格
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_info = soup.find(class_='ProductHtmlDetail__dangerouslyContent___3ovQ9 ProductHtmlDetail__spec___pa_3-')
        try:
            prd_info_df = pd.read_html(str(prd_info))
            prd_info_df = prd_info_df[0]
        except:
            continue
        for prd_table in prd_info_df[0]:
            if prd_table == '廠商名稱':
                firm_name = (prd_info_df[1][ans_index])
            if prd_table == '廠商地址':
                firm_add = (prd_info_df[1][ans_index])
            if prd_table == '食品業者登錄字號':
                firm_id = (prd_info_df[1][ans_index])
            if prd_table == '其他揭露事項':
                firm_idx = (prd_info_df[1][ans_index])
                if '食品業者登錄字號' in firm_idx:
                    firm_id = firm_idx
            ans_index = ans_index + 1
        prd_count = prd_count + 1
        print(prd_count, prd_name.text, firm_name, firm_add, firm_id)
        writer.writerow([str(prd_name.text), firm_name, firm_add, firm_id])
        ans_index = 0
        firm_name = '無資料'
        firm_add = '無資料'
        firm_id = '無資料'
        firm_idx = '無資料'
print('已將資料寫入csv')
csvfile.close()
driver.close()
