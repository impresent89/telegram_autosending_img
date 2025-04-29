import subprocess
from PIL import Image
import telegram
import schedule
import time
import random
import datetime
import asyncio
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO

# 설정
TEST_MODE = True
BOT_TOKEN = '8065976731:AAGlFpQF_eUEkodhftNq_CwXn3J5qSQqhAo'
CHAT_ID = '-4638489793'
URL = 'https://weather.naver.com/today/02135105'

async def send_telegram_photo(bot_token, chat_id, photo_path):
    try:
        bot = telegram.Bot(token=bot_token)
        async with bot:
            await bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))
        print("텔레그램 전송 성공")
        return True
    except FileNotFoundError:
        print("오류: weather_screenshot.png 파일을 찾을 수 없습니다.")
    except telegram.error.TelegramError as e:
        print(f"텔레그램 API 오류: {e}")
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
    return False

async def job():
    try:
        # 크롬 브라우저 설정
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--start-maximized')

        # 웹드라이버 실행
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 네이버 날씨 페이지 열기
        driver.get(URL)
        
        # 특정 element 대기 및 찾기 (날씨 정보를 포함하는 div)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'section_center '))
        )
        
        # element의 스크린샷 찍기
        element_png = element.screenshot_as_png
        
        # 이미지 처리 및 저장
        img = Image.open(BytesIO(element_png))
        img.save("weather_screenshot.png")
        print("스크린샷 촬영 성공")
        
        # 브라우저 종료
        driver.quit()
        
        # 텔레그램으로 전송
        success = await send_telegram_photo(BOT_TOKEN, CHAT_ID, 'weather_screenshot.png')
        return success
    
    except Exception as e:
        print(f"작업 실행 중 오류 발생: {e}")
    
    return False

def run_job():
    success = asyncio.run(job())
    if success:
        print("작업 성공. 프로그램을 종료합니다.")
        sys.exit(0)
    else:
        print("작업 실패. 프로그램을 종료합니다.")
        sys.exit(1)

def schedule_job():
    if TEST_MODE:
        # 테스트 모드: 5초에서 10초 사이의 랜덤한 시간 후 실행
        seconds = random.randint(5, 10)
        execution_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    else:
        # 실전 모드: 오전 8:00에서 8:30 사이의 랜덤한 시간에 실행
        today_at_8 = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        random_minutes = random.randint(0, 30)
        execution_time = today_at_8 + datetime.timedelta(minutes=random_minutes)
        
        if datetime.datetime.now() > execution_time:
            execution_time += datetime.timedelta(days=1)
    
    print(f"실행 예정 시간: {execution_time}")
    return execution_time

# 실행 시간 계산
execution_time = schedule_job()

# 실행 대기
while datetime.datetime.now() < execution_time:
    time.sleep(1)

# 작업 실행
run_job()