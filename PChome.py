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
prd_countt = 0
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
csvfile = open('PChome_' + str(time.strftime('%Y%m%d%H%M')) + '.csv', 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)
writer.writerow(['產品名稱', '廠商名稱', '廠商地址', '食品業者登錄字號'])
driver.get('https://24h.pchome.com.tw/')
for prd_key in prd_key_list:
    prd_link_list = []
    driver.get('https://ecshweb.pchome.com.tw/search/v3.3/?q=' + prd_key)
    driverwait('/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div/span/span')
    soup = BeautifulSoup(driver.page_source, 'lxml')
    prd_count = soup.select_one('div.msg_box span span')
    prd_sum = int(prd_count.text)
    print(prd_key, '共', prd_sum, '筆資料')
#計算分頁數
    if prd_sum <= 20:
        scroll_sum = 3
    elif prd_sum > 20 and prd_sum % 20 == 0:
        scroll_sum = prd_sum // 20 + 2
    else:
        scroll_sum = prd_sum // 20 + 3
    for search_more in range(scroll_sum): #scroll_sum
        driver.execute_script("window.scrollBy(0, 10000)")
        time.sleep(0.5)
    print('共滾動', scroll_sum, '次')
    soup = BeautifulSoup(driver.page_source, 'lxml')
#抓取符合關鍵字之連結
    prd_link = soup.select('h5 a')
    a = 1
    for prd_detail in prd_link:
        if prd_key in prd_detail.get_text():
            if 'https' in prd_detail.get('href'):
                prd_link_list.append(prd_detail.get('href'))
            else:
                prd_link_list.append('https:' + prd_detail.get('href'))
#前往各產品頁面
    for prd_link_get in prd_link_list:
        driver.get(prd_link_get)
        sleeptime()
        try:
            driverwait('//*[@id="NickContainer"]')
        except:
            continue
#滾動更新頁面
        for search_more in range(150):
            scroll_step = 100
            driver.execute_script("window.scrollBy(0," + str(scroll_step) + ")")
            scroll_step = scroll_step + 50
            time.sleep(0.01)
        sleeptime()
        soup = BeautifulSoup(driver.page_source, 'lxml')
#抓取產品資訊表格
        prd_name = soup.select_one('div.left h5.nick')
        try:
            prd_info_df = pd.read_html(str(soup))
            sleeptime()
        except:
            continue
        for prd_df_search in prd_info_df:
            ans_index = 0
            try:
                for prd_table in prd_df_search[0]:
                    if prd_table == '廠商名稱':
                        firm_name = (prd_df_search[1][ans_index])
                    if prd_table == '廠商地址':
                        firm_add = (prd_df_search[1][ans_index])
                    if prd_table == '食品業者登錄字號':
                        firm_id = (prd_df_search[1][ans_index])
                    if prd_table == '其他揭露事項':
                        firm_idx = (prd_df_search[1][ans_index])
                        if '食品業者登錄字號' in firm_idx:
                            firm_id = firm_idx
                    ans_index = ans_index + 1
            except:
                continue
                ans_index = ans_index + 1
        prd_countt = prd_countt + 1
        print(prd_countt, prd_name.text, firm_name, firm_add, firm_id)
        writer.writerow([str(prd_name.text), firm_name, firm_add, firm_id])
        ans_index = 0
        firm_name = '無資料'
        firm_add = '無資料'
        firm_id = '無資料'
        firm_idx = '無資料'
print('已將資料寫入csv')
csvfile.close()
driver.close()
