# selenium을 이용해 spotify Global Weekly 주간 차트 csv파일을 크롤링하는 코드
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path
from datetime import datetime, timedelta
import time

# 시작일과 종료일 사이의 주간 기준 날짜(1주 간격)를 리스트로 생성
# 2024년, 2025년 모두 이 함수를 그대로 사용하고 start/end만 바꿔 실행함
def generate_weekly_dates(start="2025-01-09", end="2025-10-30"):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(weeks=1)

    return dates


# spotify 차트 csv를 저장할 로컬 다운로드 폴더
download_dir = Path(r"C:\Users\ptopj\spotify_2024_crawler\downloads")
download_dir.mkdir(parents=True, exist_ok=True)

# 크롬 다운로드 설정 (지정한 폴더로 자동 저장되도록 설정)
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": str(download_dir),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
}
options.add_experimental_option("prefs", prefs)

# 크롬 드라이버 실행
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


# 페이지 로딩 후 특정 버튼이 나타날 때까지 최대 20초 동안 기다리도록 설정
wait = WebDriverWait(driver, 20)

try:
    # spotify 차트 페이지 접속한 후 여기서 직접 계정 로그인
    driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")
    print("브라우저 열림 → 로그인하세요.")
    input("로그인 완료 후 엔터를 누르세요...")

    print("로그인 세션 유지 상태에서 다운로드를 시작합니다.")

    # 주간 차트 기준 날짜 리스트 생성
    dates_2024 = generate_weekly_dates()
    print("다운로드할 날짜 개수:", len(dates_2024))

    # 생성된 각 날짜에 대해 해당 주간 차트 페이지로 이동 후 csv 다운로드
    for d in dates_2024:
        url = f"https://charts.spotify.com/charts/view/regional-global-weekly/{d}"
        print(f"\n[{d}] 이동 중 → {url}")
        driver.get(url)

        time.sleep(5)  # 페이지 로딩 대기

        try:
            # csv 다운로드 버튼(aria-labelledby='csv_download')이 클릭 가능해질 때까지 대기
            csv_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[aria-labelledby='csv_download']")
                )
            )
            csv_button.click()
            print(f"[{d}] CSV 다운로드 성공")
            time.sleep(5)  # 다운로드 시간 대기

        except Exception as e:
            print(f"[{d}] CSV 다운로드 실패: {e}")

finally:
    driver.quit()
