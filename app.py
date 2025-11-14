import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import json
import time

st.title("Facebook Auto Messenger (Playwright Version)")

chat_id = st.text_input("Chat / Conversation ID")
delay = st.number_input("Delay (seconds)", min_value=5, max_value=600, value=30)
cookies_text = st.text_area("Facebook Cookies (Paste RAW cookies here)")
messages_text = st.text_area("Messages (one per line)")


async def send_messages(chat_id, messages, delay, cookies_raw):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context()

        # Add cookies if provided
        if cookies_raw.strip():
            cookies_list = []
            for c in cookies_raw.split(";"):
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

        # Open chat page
        await page.goto(f"https://www.facebook.com/messages/t/{chat_id}")

        await page.wait_for_timeout(5000)

        for msg in messages:
            try:
                # Message input box
                box = await page.wait_for_selector("div[contenteditable='true']", timeout=15000)

                await box.click()
                await box.type(msg)
                await box.press("Enter")

                st.write(f"Sent: {msg}")
                await page.wait_for_timeout(delay * 1000)

            except Exception as e:
                st.error(f"Error sending message: {e}")

        await browser.close()


# Start Button
if st.button("Start Automation"):
    if not chat_id or not messages_text:
        st.error("Chat ID aur messages dono chahiye.")
        st.stop()

    messages = messages_text.strip().split("\n")
    cookies = cookies_text.strip()

    st.write("⏳ Starting automation...")

    asyncio.run(send_messages(chat_id, messages, delay, cookies))

    st.success("✅ Automation Completed!")
