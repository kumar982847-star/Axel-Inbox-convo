import os
from flask import Flask, request
import asyncio
from playwright.async_api import async_playwright, Browser

app = Flask(__name__)
browser_instance: Browser = None

async def get_browser():
    global browser_instance
    if browser_instance is None:
        pw = await async_playwright().start()
        browser_instance = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )
    return browser_instance


@app.route("/")
def home():
    return "Server OK | Playwright Ready"


@app.route("/send", methods=["POST"])
async def send_msg():
    data = request.json

    cookies = data.get("cookies")
    hater_name = data.get("hater_name")
    thread_id = data.get("thread_id")
    message = data.get("message")

    if not cookies or not message:
        return {"error": "Missing Required Fields"}, 400

    browser = await get_browser()
    page = await browser.new_page()

    # Load cookies
    await page.context.add_cookies(cookies)

    # Go to Facebook
    await page.goto("https://www.facebook.com/messages/t/" + thread_id)

    # →→ TU APNA SEND MESSAGE KA CODE YAHA DAL SAKTA HAI ←←

    # Example:
    await page.fill("div[aria-label='Message']", message)
    await page.keyboard.press("Enter")

    return {"status": "Message Sent!", "to": hater_name}
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
