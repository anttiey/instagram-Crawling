from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import time
import pandas as pd

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) # Chromedriver PATH

## 인스타그램 접속
driver.get('https://www.instagram.com/accounts/login/')
driver.maximize_window()

time.sleep(5)

## 인스타그램 계정 로그인
username = 'yourID'
password = 'yourPW'

user_id = driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(1) > div > label > input')
user_id.send_keys(username)
time.sleep(5)

user_pw = driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(2) > div > label > input')
user_pw.send_keys(password)
time.sleep(5)

driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(3) > button').click()
time.sleep(10)

time.sleep(5)

## 정보 등록 나중에 하기
driver.find_element(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf.x10cihs4.x1t2pt76.x1n2onr6.x1ja2u2z > section > main > div > div > div > div > button').click()
time.sleep(5)

## 페이지로 이동
driver.get('https://www.instagram.com/pageUrl')

## 해시태그 검색 후 페이지로 이동
driver.get('https://www.instagram.com/explore/tags/태그이름/')

time.sleep(10) # 페이지 로딩 때문에 Error 발생해 지연 걸어줌

## 추출 데이터

post_contents = []
post_days = []
post_likes = []
post_imgs = []
post_comments = []

## results = []

## 목표 게시물 수
target = 2

## 첫번째 게시물 클릭
driver.find_element(By.CSS_SELECTOR, 'div._aabd._aa8k._aanf').click()

time.sleep(5)

for i in range(target):

    ## 현재 게시글 html
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    ## 1. 본문 내용
    try:
        content = soup.select('div._a9zs > span')[0].text
    except:
        content = ''

    ## 2. 작성 일자
    try: 
        date = soup.select('time._aaqe')[0]['datetime'][:10]
    except:
        date = ''

    ## 3. 좋아요 수
    try:
        like = soup.select('div._aacl._aaco._aacw._aacx._aada._aade > span')[0].text  
    except:
        like = 0

    time.sleep(2)

    imgSrcs = []

    ## 4. 포스트 이미지
    try:
        image = driver.find_element(By.CSS_SELECTOR, 'div._aagu._aato > div._aagv > img._aagt')
        imgSrc = image.get_attribute('src')
        imgSrcs.append(imgSrc)
    except:
        image = driver.find_element(By.CSS_SELECTOR, 'div._ab8w._ab94._ab99._ab9f._ab9m._ab9p._abcf._abcg._abch._abck._abcl._abcm > div > div > div > ul > li:nth-child(2) > div > div > div > div > div._aagv > img._aagt')
        imgSrc = image.get_attribute('src')
        imgSrcs.append(imgSrc)

        driver.find_element(By.CSS_SELECTOR, 'button._aahi').click()
        time.sleep(3)

        while True:
            try:
                image = driver.find_element(By.CSS_SELECTOR, 'div._ab8w._ab94._ab99._ab9f._ab9m._ab9p._abcf._abcg._abch._abck._abcl._abcm > div > div > div > ul > li:nth-child(3) > div > div > div > div > div._aagv > img._aagt')
                imgSrc = image.get_attribute('src')
                imgSrcs.append(imgSrc)
                print(imgSrc)

                driver.find_element(By.CSS_SELECTOR, 'button._aahi').click()
                time.sleep(3)
            except:
                break
    
    ## 5. 댓글
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, 'div._ae2s._ae3v._ae3w > div._ae5q._ae5r._ae5s > ul > li > div > button').click()
        except:
            break

    buttons = driver.find_elements(By.CSS_SELECTOR, 'li > ul > li > div > button')
    time.sleep(5)

    for button in buttons:
        button.send_keys(Keys.ENTER)
        time.sleep(3)

    comments = driver.find_elements(By.CSS_SELECTOR, 'ul > ul > div > li > div > div > div._a9zr > div._a9zs > span')
    time.sleep(5)

    for i in comments:
        comment = i.text.strip()
        post_comments.append(comment)

    replys = driver.find_elements(By.CSS_SELECTOR, ' ul > ul > li > ul > div > li > div > div > div._a9zr > div._a9zs > span')
    time.sleep(5)

    for i in replys:
        reply = i.text.strip()
        post_comments.append(reply)

    ## 6. 저장하기
    post_contents.append(content)
    post_days.append(date)
    post_likes.append(like)
    post_imgs.append(imgSrcs)

    # result = [content, date, like, imgSrcs]
    # results.append(result)

    time.sleep(3)

    ## 다음 포스트로 이동

    driver.find_element(By.CSS_SELECTOR, 'div._aaqg._aaqh > button').click()
    time.sleep(3)

## 데이터 저장
file_name="instagram_extract"

insta_info_df = pd.DataFrame({"content":post_contents, "date":post_days, "like":post_likes, "imgs":post_imgs})
insta_info_df.to_csv("{}.csv".format(file_name), index=False)
insta_info_df.to_json("{}.json".format(file_name), force_ascii=False, orient = 'index')

file_name="instagram_comments"

insta_comment_df = pd.DataFrame({"comments":post_comments})
insta_comment_df.to_csv("{}.csv".format(file_name), index=False)
insta_comment_df.to_json("{}.json".format(file_name), index=False)

'''
results_df = pd.DataFrame(results, columns = ['content','date','like', 'imgs'])
results_df.to_json("{}.json".format(file_name), force_ascii=False, orient = 'index')
'''

driver.close()
driver.quit()
