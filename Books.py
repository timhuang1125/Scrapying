from numpy import random
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

#隨機秒數休息
def sleeptime(multiply = 1):
    sleept = random.uniform(1, 5)
    time.sleep(sleept * multiply)
scroll_step = 100
#等待頁面讀取完成
def driverwait(xpath):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
#等待頁面可正常讀取
def errorsleep(driver, current_link, xpath):
    time_count = 0
    for wait_ok in range(100):
        time.sleep(30)
        driver.close()
        driver = webdriver.Firefox()
        driver.get(current_link)
        time_count = time_count + 30
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
            print('已可成功抓取資料')
            break
        except:
            print('休息' + str(time_count) + '秒後依舊無法抓取資料,繼續休息')
            continue

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
csvfile = open('Books_' + str(time.strftime('%Y%m%d%H%M')) + '.csv', 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)
writer.writerow(['產品名稱', '廠商名稱', '廠商地址', '食品業者登錄字號'])
for prd_key in prd_key_list:
    prd_link_list = []
    driver.get('https://search.books.com.tw/search/query/cat/5/key/' + prd_key + '/qsub/K08/sort/1/page/1/v/0/')
    try:
        sleeptime()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="key"]')))
    except:
        print('抓取第', prd_key, '資料失敗,等待重啟瀏覽器')
        driver.close()
        driver = webdriver.Firefox()
        driver.get('https://search.books.com.tw/search/query/cat/5/key/' + prd_key + '/qsub/K08/sort/1/page/1/v/0/')
        current_link = 'https://search.books.com.tw/search/query/cat/5/key/' + prd_key + '/qsub/K08/sort/1/page/1/v/0/'
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="key"]')))
        except:
            errorsleep(driver, current_link, '//*[@id="key"]')
#計算分頁數
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        search_sum = soup.select('div.page span')
        search_sum = search_sum[0].string
    except:
        search_sum = 1
    print(prd_key, '共有', search_sum, '頁')
#抓取符合關鍵字之連結
    for count_page in range(int(search_sum)):
        count_page = count_page + 1
        driver.get('https://search.books.com.tw/search/query/cat/5/key/' + prd_key +'/qsub/K08/sort/1/page/' + str(count_page) + '/v/0/')
        try:
            sleeptime()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="key"]')))
        except:
            print('抓取第', prd_key, '資料失敗,等待重啟瀏覽器')
            driver.close()
            driver = webdriver.Firefox()
            driver.get('https://search.books.com.tw/search/query/cat/5/key/' + prd_key + '/qsub/K08/sort/1/page/1/v/0/')
            current_link = 'https://search.books.com.tw/search/query/cat/5/key/' + prd_key + '/qsub/K08/sort/1/page/1/v/0/'
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="key"]')))
            except:
                errorsleep(driver, current_link, '//*[@id="key"]')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_link = soup.find_all('a', rel='mid_name')
        for prd_detail in prd_link:
            if prd_key in prd_detail.get_text():
                prd_link_list.append(prd_detail.get('href'))
#前往各產品頁面
    for prd_link_get in prd_link_list:
        driver.get('https:' + prd_link_get)
        try:
            sleeptime()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/div/h1')))
        except:
            print('抓取第', prd_count + 1, '筆資料失敗,等待重啟瀏覽器')
            driver.close()
            driver = webdriver.Firefox()
            driver.get('https:' + prd_link_get)
            current_link = 'https:' + prd_link_get
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/div/h1')))
            except:
                errorsleep(driver, current_link, '/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/div/h1')
            sleeptime()
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_name = soup.find('h1')
#滾動更新頁面
        for search_more in range(150):
            scroll_step = 100
            driver.execute_script("window.scrollBy(0," + str(scroll_step) + ")")
            scroll_step = scroll_step + 50
            time.sleep(0.01)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prd_info = soup.find(class_='cnt_product02')
        prd_info = prd_info.text.split('【')
#抓取產品資訊表格
        for prd_table in prd_info:
            if '廠商名稱' in prd_table:
                firm_name = (prd_table)
            if '廠商地址' in prd_table:
                firm_add = (prd_table)
            if '食品業者登錄字號' in prd_table:
                firm_id = (prd_table)
            ans_index = ans_index + 1
        prd_count = prd_count + 1
        print(prd_count, prd_name.text, firm_name, firm_add, firm_id)
        sleeptime()
        writer.writerow([str(prd_name.text), firm_name, firm_add, firm_id])
        ans_index = 0
        firm_name = '無資料'
        firm_add = '無資料'
        firm_id = '無資料'
        firm_idx = '無資料'
print('已將資料寫入csv')
csvfile.close()
driver.close()
