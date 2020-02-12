# -*- coding: utf-8-sig -*-
#writers: Lee sanjin (berry2971@hanmail.net), Jo Eunkyoung(jek.cl.nlp@gmail.com)
#usage info: This code works only in Windows OS.

import os, platform, sys, re
import time, random, math
import selenium, sqlite3, warnings
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread

# settings
SCRAP_OPTION = 0                        # 스크래핑 옵션
MAX_PAGE_CUR = 0                        # 진행 중 청원 페이지 시작 번호
MAX_PAGE_EXP = 0                        # 만료 된 청원 페이지 시작 번호
MIN_PAGE_CUR = 0                        # 진행 중 청원 페이지 끝 번호
MIN_PAGE_EXP = 0                        # 만료 된 청원 페이지 끝 번호
MAX_SLEEP_SEC = 1.3                     # 호스트로부터의 차단 방지를 위한 최대 대기 시간
LOAD_TIMEOUT = 10                       # 페이지 로드 타임아웃 경계
SCRIPT_TIMEOUT = 10                     # 스크립트 실행 타임아웃 경계
WAIT_CONDITION = 10                     # EC만족까지 최대 대기 시간
REFRESH_TIME = 3                        # 새로고침 대기 시간
MAX_RETRY_NO = 5                        # 새로고침 최대 횟수
RESULT_DB_NAME = "result_petitions"     # 결과 파일명([RESULT_DB_NAME]_YYMMDDhhmmss.db)

# global variables
onlyList = list()
driver = list()
init = True
tries = 0
conn = None

########## 임의의 시간 동안 동작 중지
def sleep_random():
    rand = random.random() * MAX_SLEEP_SEC
    time.sleep(rand)

########## 임의의 시간 동안 동작 중지
def sleep_refresh():
    time.sleep(REFRESH_TIME)

########## 브라우저 로드
def load_browser():
    global driver
    global init

    plf = platform.system()
    if plf == 'Windows':    # Windows
        try:
            if init:
                print("Welcome! Petitions Scraper... running on Windows")
                init = False
            driver1 = webdriver.PhantomJS(os.path.dirname(os.path.abspath(__file__)) + r"\phantomjs.exe")
            driver1.set_page_load_timeout(LOAD_TIMEOUT)
            driver1.set_script_timeout(SCRIPT_TIMEOUT)
            driver2 = webdriver.PhantomJS(os.path.dirname(os.path.abspath(__file__)) + r"\phantomjs.exe")
            driver2.set_page_load_timeout(LOAD_TIMEOUT)
            driver2.set_script_timeout(SCRIPT_TIMEOUT)
            driver3 = webdriver.PhantomJS(os.path.dirname(os.path.abspath(__file__)) + r"\phantomjs.exe")
            driver3.set_page_load_timeout(LOAD_TIMEOUT)
            driver3.set_script_timeout(SCRIPT_TIMEOUT)
            driver4 = webdriver.PhantomJS(os.path.dirname(os.path.abspath(__file__)) + r"\phantomjs.exe")
            driver4.set_page_load_timeout(LOAD_TIMEOUT)
            driver4.set_script_timeout(SCRIPT_TIMEOUT)
            driver5 = webdriver.PhantomJS(os.path.dirname(os.path.abspath(__file__)) + r"\phantomjs.exe")
            driver5.set_page_load_timeout(LOAD_TIMEOUT)
            driver5.set_script_timeout(SCRIPT_TIMEOUT)
            driver.append("")
            driver.append(driver1)
            driver.append(driver2)
            driver.append(driver3)
            driver.append(driver4)
            driver.append(driver5)
        except FileNotFoundError:
            print("Cannot find driver.")
            input()
            sys.exit()
    elif plf == 'Darwin':   # Mac
        try:
            if init:
                print("Welcome! Petitions Scraper... running on Mac OS")
                init = False
        except FileNotFoundError:
            print("Cannot find driver.")
            input()
            sys.exit()
    elif plf == 'Linux':    # Linux
        print("Sorry!\nscraping-petitions doesn't run on Linux")
        sys.exit()
    else:                   # Other
        print("Sorry!\nscraping-petitions runs on Windows OS only")
        sys.exit()

########## 초기 화면
def init_state():
    global onlyList
    global SCRAP_OPTION
    global MIN_PAGE_CUR
    global MIN_PAGE_EXP
    global MAX_PAGE_CUR
    global MAX_PAGE_EXP

    print()

    if SCRAP_OPTION not in [1, 2, 3]:
        print("-----SCRAP OPTIONS-----")
        print("1. 진행 중 청원만")
        print("2. 만료 된 청원만")
        print("3. 진행 중 청원과 만료 된 청원 모두")
        print()
        print("0. 페이지 설정 없이 모든 청원 스크랩")
        print("-----------------------")
        SCRAP_OPTION = int(input("스크랩 옵션 선택: "))

    if SCRAP_OPTION == 0:
        MIN_PAGE_CUR = 1
        MIN_PAGE_EXP = 1
        get_max_page(1)
        get_max_page(2)

    while SCRAP_OPTION not in [0, 1, 2, 3]:
        print("잘못된 옵션 번호입니다!")
        SCRAP_OPTION = int(input("스크랩 옵션 선택: "))

    if SCRAP_OPTION in [1, 3]:
        MIN_PAGE_CUR = int(input("페이지 시작 범위 입력(진행 중 청원): "))
        while MIN_PAGE_CUR < 1:
            print("잘못된 페이지 번호입니다!")
            MIN_PAGE_CUR = int(input("페이지 시작 범위 입력(진행 중 청원): "))
        MAX_PAGE_CUR = int(input("페이지 종료 범위 입력(진행 중 청원): "))
        while MAX_PAGE_CUR < 1:
            print("잘못된 페이지 번호입니다!")
            MAX_PAGE_CUR = int(input("페이지 종료 범위 입력(진행 중 청원): "))
    if SCRAP_OPTION in [2, 3]:
        MIN_PAGE_EXP = int(input("페이지 시작 범위 입력(만료 된 청원): "))
        while MIN_PAGE_EXP < 1:
            print("잘못된 페이지 번호입니다!")
            MIN_PAGE_EXP = int(input("페이지 시작 범위 입력(만료 된 청원): "))
        MAX_PAGE_EXP = int(input("페이지 종료 범위 입력(만료 된 청원): "))
        while MAX_PAGE_EXP < 1:
            print("잘못된 페이지 번호입니다!")
            MAX_PAGE_EXP = int(input("페이지 종료 범위 입력(만료 된 청원): "))

    if MIN_PAGE_CUR == 99999:
        MIN_PAGE_CUR = 1
    if MIN_PAGE_EXP == 99999:
        MIN_PAGE_EXP = 1
    if MAX_PAGE_CUR == 99999:
        get_max_page(1)
    if MAX_PAGE_EXP == 99999:
        get_max_page(2)

    if SCRAP_OPTION == 1:
        onlyList = [1]
        print("<진행 중 청원>만 " + str(MIN_PAGE_CUR) + " - " + str(MAX_PAGE_CUR) + "페이지 스크랩합니다.\n")
    elif SCRAP_OPTION == 2:
        onlyList = [2]
        print("<만료 된 청원>만 " + str(MIN_PAGE_EXP) + " - " + str(MAX_PAGE_EXP) + "페이지 스크랩합니다.\n")
    elif SCRAP_OPTION in [0, 3]:
        onlyList = [1, 2]
        print("<진행 중 청원> " + str(MIN_PAGE_CUR) + " - " + str(MAX_PAGE_CUR) + "페이지")
        print("<만료 된 청원> " + str(MIN_PAGE_EXP) + " - " + str(MAX_PAGE_EXP) + "페이지\n")

    print()

########## 99999 눌렀을 때만 실행: 페이지 수 불러오기(양 가늠, 1번글 못찾았을 때도 프로그램 종료할 수 있도록)
def get_max_page(only):
    global tries
    global driver
    global MAX_PAGE_CUR
    global MAX_PAGE_EXP
    curUrl = 'https://www1.president.go.kr/petitions/?c=0&only=1&page=1&order=1'
    expUrl = 'https://www1.president.go.kr/petitions/?c=0&only=2&page=1&order=1'

    try:
        if only == 1:
            driver[1].get(curUrl)
        elif only == 2:
            driver[1].get(expUrl)

        time.sleep(1)

        html = driver[1].execute_script("return document.documentElement.innerHTML;")
        soup = bs(html, "html.parser")
        ul = soup.find("ul", class_ = "petition_list")
        wrap = ul.find("div", class_ = "bl_wrap")

        number_of_wraps = wrap.find("div", class_ = "bl_no").text
        number_of_wraps = int(re.search("번호 (.*)", number_of_wraps).group(1))
                            # re.search("번호 (.*)", number_of_wraps).group(1)   ->   "3600"
                            # int(문자열)  ->   정수로 변환
                            # 가장 마지막 게시물의 게시물번호를 따온거

        if only == 1:
            MAX_PAGE_CUR = math.ceil(number_of_wraps / 15)
        elif only == 2:
            MAX_PAGE_EXP = math.ceil(number_of_wraps / 15)
    except Exception as e:
        if tries >= MAX_RETRY_NO:  # MAX_RETRY_NO: 최대 재시도 횟수...  이걸 넘어가면
            tries = 0
            if only == 1:
                MAX_PAGE_CUR = 50
            elif only == 2:
                MAX_PAGE_EXP = 50000
            return
        tries = tries + 1
        print("ERROR: 페이지 수를 불러오던 중... 재실행 횟수: " + str(tries) + "/" + str(MAX_RETRY_NO))
        print(e)
        get_max_page(only)

########## 게시판 불러오기(게시글 목록 불러오기)
def get_wraps(url, thread_no): # input: String 게시글 목록 주소
    global tries
    global driver
    checkLast = False # 게시판에 마지막 글이 있는지를 확인

    try:
        driver[thread_no].get(url)

        wait = WebDriverWait(driver[thread_no], 10)
        wait.until(\
            EC.element_to_be_clickable((By.XPATH, "//ul[@class='petition_list']//div[@class='bl_wrap']/div[@class='bl_subject']/a[@class='cb relpy_w']")))

        html = driver[thread_no].execute_script("return document.documentElement.innerHTML;")
        soup = bs(html, "html.parser")
        uls = soup.find("ul", class_ = "petition_list")
        wraps = uls.find_all("div", class_ = "bl_wrap")

        for wrap in wraps:
            checkLast = getWrapInfo(wrap, thread_no)
            if checkLast == True:
                break
        conn.commit()

        return checkLast
    # except selenium.common.exceptions.TimeoutException:
    # driver.refresh()
    except Exception as e:
        if tries >= MAX_RETRY_NO:
            tries = 0
            return checkLast
        tries = tries + 1
        print("ERROR: 게시판을 불러오던 중...  재실행 횟수: " + str(tries) + "/" + str(MAX_RETRY_NO))
        print(e)
        get_wraps(url, thread_no)

########## 게시글 불러오기(게시글 정보 불러오기)
def getWrapInfo(wrap, thread_no):   # input: String 게시판 목록 중 하나의 오브젝트
    global tries
    global driver
    checkLast = False

    sleep_random()

    number = int(re.search("번호 (.*)", wrap.find("div", class_ = "bl_no").text).group(1))
    if (number == 1):
        checkLast = True

    category = re.search("분류 (.*)", wrap.find("div", class_ = "bl_category ccategory cs wv_category").text).group(1)
    title = re.search("제목 (.*)", wrap.find("div", class_ = "bl_subject").text).group(1)
    href = "https://www1.president.go.kr" + wrap.find("a").get("href")
    content = getText(href, thread_no)
    #import pdb; pdb.set_trace()
    date = re.search("청원 종료일 (.*)", wrap.find("div", class_ = "bl_date light").text).group(1) #JEK
    num_agree = re.search("참여인원 (.*)", wrap.find("div", class_ = "bl_agree cs").text).group(1) #JEK
    print("\t쓰레드"+str(thread_no)+" 글 번호:" + re.findall('\d+', href)[1] + " 종료일:" + date + "참여수:" + num_agree + " 글 제목:" + title.strip()[:50] )

    try:
        if content != None:
            content = content.strip()
            conn.execute("""
            INSERT INTO petitions (HREF, CATEGORY, TITLE, CONTENT, DATE, NUM_AGREE) VALUES (?, ?, ?, ?, ?, ?)""",
            [href, category, title, content, date, num_agree]) #JEK
            return checkLast
    except Exception as e:
        print("데이터베이스 오류", e)
        getWrapInfo(wrap, thread_no)

def getText(url, thread_no):   # input: String 게시글 주소 return: String 게시글 본문
    global tries

    try:
        driver[thread_no].get(url)

        WebDriverWait(driver[thread_no], 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "petitionsView_write"))
        )

        html = driver[thread_no].page_source
        soup = bs(html, "html.parser")
        return soup.find("div", class_ = "View_write").text
    except Exception as e:
        if tries >= MAX_RETRY_NO:
            tries = 0
            print("ERROR: 텍스트를 불러오던 중...  재실행 횟수: " + str(tries) + "/" + str(MAX_RETRY_NO))
            print(e)
            return None
        tries = tries + 1
        getText(url, thread_no)

def inside_run(thread_no):
    global tries

    exp_pages_no = MAX_PAGE_EXP - MIN_PAGE_EXP + 1
    exp_pages_per_thread = int(exp_pages_no / 4)

    if thread_no == 1:
        start_page = MIN_PAGE_CUR
        end_page = MAX_PAGE_CUR
        only = 1
    else:
        start_page = MIN_PAGE_EXP + (exp_pages_per_thread*(thread_no-2))
        end_page = start_page + exp_pages_per_thread
        only = 2

    url1 = "https://www1.president.go.kr/petitions/?c=0&only=" + str(only)

    page = start_page

    while True:
        # 게시판 목록이 보여지는 페이지의 주소
        url2 = url1 + "&page=" + str(page) + "&order=1"

        # 진행상황 표시
        if only == 1: print('"진행 중 청원" 스크랩 중... 페이지: ' + str(page))
        elif only == 2: print('"만료 된 청원" 스크랩 중... 페이지: ' + str(page))

        tries = 0
        if get_wraps(url2, thread_no) == True:
            print("더 이상 글이 없습니다.")
            break
        page = page + 1

        # 게시판 페이지 번호가 MAX를 넘어가면 break
        if thread_no == 1 and page > end_page: break
        elif page > end_page: break

def run(onlyList):
    global tries

    t1 = Thread(target = inside_run, args = (1,))
    t1.start()
    if 2 in onlyList:
        t2 = Thread(target = inside_run, args = (2,))
        t3 = Thread(target = inside_run, args = (3,))
        t4 = Thread(target = inside_run, args = (4,))
        t5 = Thread(target = inside_run, args = (5,))
        t2.start()
        t3.start()
        t4.start()
        t5.start()

def create_database():
    global conn

    try:
        import datetime
        x = datetime.datetime.now()
        cur_time = x.strftime('%Y%m%d-%H%M%S') #JEK

        if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"\\result"):
            os.makedirs(os.path.dirname(os.path.abspath(__file__))+"\\result")

        fileName = RESULT_DB_NAME+"_"+cur_time+".db"
        sourcePath = os.path.dirname(os.path.abspath(__file__))
        db = sourcePath + "\\result\\" + fileName

        conn = sqlite3.connect(db, timeout = 10, check_same_thread=False)

        conn.execute("""\
            CREATE TABLE petitions if not exists
            (HREF TEXT NOT NULL,
            CATEGORY TEXT NOT NULL,
            TITLE TEXT NOT NULL,
            CONTENT TEXT NOT NULL,
            DATE DATE Not Null,
            NUM_AGREE TEXT Not Null, Primary Key(HREF))""") #JEK
    except:
        print("Failed to create DB!")
        sys.exit()
####################################################################################################

load_browser() # 브라우저 실행, 브라우저-timeout 설정
init_state() # 스크래핑 옵션 설정, 페이지 범위 설정
create_database() # db 파일 만들고, 프로그램과 연결, 테이블 만들고, attribute(항목) 만들기

try:
    run(onlyList)
except Exception as e:
    print(e)
    input()
finally:
    input()
