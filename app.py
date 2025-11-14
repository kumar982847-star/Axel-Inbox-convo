import subprocess
subprocess.run("playwright install", shell=True)
from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def send_messages(chat_id, messages, delay, cookies_raw):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Add cookies if provided
        if cookies_raw.strip():
            cookie_items = cookies_raw.split(";")
            cookies_list = []
            for c in cookie_items:
                if "=" in c:
                    name, value = c.split("=", 1)
                    cookies_list.append({
                        "name": name.strip(),
                        "value": value.strip(),
                        "domain": ".facebook.com",
                        "path": "/"
                    })
            await context.add_cookies(cookies_list)

        page = await context.new_page()
        await page.goto(f"https://www.facebook.com/messages/t/{chat_id}")
        await page.wait_for_timeout(5000)

        # Send each message
        for msg in messages:
            box = await page.wait_for_selector("div[contenteditable='true']", timeout=15000)
            await box.click()
            await box.type(msg)
            await box.press("Enter")
            await page.wait_for_timeout(delay * 1000)

        await browser.close()


@app.route("/send", methods=["POST"])
def send():
    data = request.json
    chat_id = data.get("chat_id")
    cookies = data.get("cookies", "")
    messages = data.get("messages", [])
    delay = int(data.get("delay", 20))

    # Run Playwright
    asyncio.run(send_messages(chat_id, messages, delay, cookies))
    return jsonify({"status": "done", "messages_sent": len(messages)})


@app.route("/")
def home():
    return "Facebook Auto Message Server Running"


if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
