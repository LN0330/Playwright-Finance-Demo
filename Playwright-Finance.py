import asyncio
import csv
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def fetch_google_finance_text(raw_text_path, screenshot_path):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.google.com/finance/")
        await page.wait_for_timeout(1000)  # 等待頁面載入完成
        await page.get_by_role("link", name="市場指數").click()
        await page.wait_for_url(
            "https://www.google.com/finance/markets/indexes")
        await page.wait_for_timeout(3000)

        # 擷取整個頁面並儲存為圖片
        await page.screenshot(path=screenshot_path, full_page=True)

        # 取得整個頁面文字
        content = await page.locator("body").inner_text()

        # 儲存 raw_text.txt
        with open(raw_text_path, "w", encoding="utf-8") as f:
            f.write(content)

        await browser.close()


def parse_and_save_csv(raw_text_path, output_csv_path):
    with open(raw_text_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    data = []
    region = ""
    i = 0
    while i < len(lines):
        line = lines[i]

        if line in ["美洲", "歐洲、中東和非洲地區", "亞太地區"]:
            region = line  # 用於記住目前是哪個區域
            i += 1
            continue

        # 指數名稱、當前指數值、漲跌數值、漲跌百分比是連續的4行
        if line == "指數" and i + 4 < len(lines):
            name = lines[i + 1]  # 指數名稱
            value = lines[i + 2]  # 當前指數值
            change = lines[i + 3]  # 漲跌數值
            change_percent = lines[i + 4] # 漲跌百分比

            data.append([region, name, value, change, change_percent])

            if region == "亞太地區" and "S&P Asia 50" in name:
                break

            i += 5
        else:
            i += 1

    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["地區", "指數名稱", "指數值", "漲跌", "漲跌幅"])
        writer.writerows(data)


def main():
    # 用 pathlib 取得與 .py 檔案相同的路徑
    current_dir = Path(__file__).resolve().parent
    raw_text_path = current_dir / "raw_text.txt"
    output_csv_path = current_dir / "filtered_indexes.csv"
    screenshot_path = current_dir / "screenshot.png"

    asyncio.run(fetch_google_finance_text(raw_text_path, screenshot_path))

    parse_and_save_csv(raw_text_path, output_csv_path)
    print(f"資料擷取儲存於：{output_csv_path}\n截圖儲存於：{screenshot_path}")


if __name__ == "__main__":
    main()
