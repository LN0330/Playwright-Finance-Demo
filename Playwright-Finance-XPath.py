from playwright.sync_api import sync_playwright, TimeoutError

def get_dow_jones_change(page):
    # 嘗試方法 1：根據中文文字內容尋找
    try:
        print("嘗試使用文字定位...")
        # 找到含有「道瓊工業平均指數」的項目，然後往下找百分比區塊
        row = page.locator('text=道瓊工業平均指數').first
        change_element = row.locator('xpath=../../../../div[4]/span/div/div')
        change_text = change_element.text_content(timeout=3000)
        print("文字定位成功！")
        if change_text:
            return change_text.strip()
    except TimeoutError:
        print("文字定位失敗，嘗試使用 XPath...")

    # 嘗試方法 2：使用備用 XPath
    try:
        print("嘗試使用 XPath 定位...")
        fallback_xpath = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[4]/div[3]/div[1]/div/div[1]/ul/li[2]/a/div/div/div[4]/span/div/div'
        change_text = page.locator(f'xpath={fallback_xpath}').text_content(timeout=3000)
        print("XPath 定位成功！")
        if change_text:
            return change_text.strip()
    except TimeoutError:
        print("XPath 定位也失敗。")

    return None

# 主程式執行區塊
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 載入頁面
    page.goto('https://www.google.com/finance/markets/indexes', wait_until="load")

    # 抓取道瓊工業平均指數漲跌百分比
    change = get_dow_jones_change(page)

    if change:
        print("道瓊工業平均指數漲跌百分比:", change)
    else:
        print("❌ 無法取得道瓊工業平均指數的漲跌百分比。")

    browser.close()
