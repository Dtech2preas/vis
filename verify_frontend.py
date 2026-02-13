
import os
import time
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 1. Load Index
    print("Navigating to index.html...")
    page.goto("http://localhost:8080/index.html")

    # 2. Verify Valentine Modal
    print("Checking Valentine Modal...")
    try:
        page.wait_for_selector("#valentineModal", state="visible", timeout=5000)
        page.screenshot(path="valentine_modal.png")
        print("Valentine Modal visible. Screenshot taken.")

        # 3. Close Modal
        print("Closing modal...")
        page.click("button.v-btn")
        page.wait_for_selector("#valentineModal", state="hidden")
    except:
        print("Valentine modal did not appear (maybe already shown?). Clearing storage and retrying.")
        page.evaluate("localStorage.clear()")
        page.reload()
        page.wait_for_selector("#valentineModal", state="visible")
        page.click("button.v-btn")

    # 4. Wait for Books (wait for loading to finish)
    print("Waiting for books to load...")
    try:
        # Wait for loading indicator to disappear implies loading is done
        page.wait_for_selector("#loadingProgress", state="hidden", timeout=30000)
        page.wait_for_selector(".book-card", timeout=5000)
        print("Books loaded and stable.")
    except Exception as e:
        print(f"Books load issue: {e}")
        page.screenshot(path="index_debug.png")
        # Force a book if needed
        page.evaluate("""
            const b = {title:'Test Book', textUrl:'https://www.gutenberg.org/files/11/11-0.txt', author:'Lewis Carroll', cover:''};
            books = [b];
            renderHomePage(books);
        """)
        page.wait_for_selector(".book-card")

    # 5. Click a Book
    print("Clicking first book...")
    # Add a small delay to ensure event listeners are attached
    time.sleep(1)
    page.click(".book-card >> nth=0")

    # 6. Verify Navigation to Reader
    print("Waiting for navigation to reader.html...")
    page.wait_for_url("**/reader.html*")

    # 7. Verify Reader Elements
    print("Verifying reader elements...")
    page.wait_for_selector(".reader-container")

    # Wait for title to populate (even if 'Loading Book...')
    page.wait_for_selector("#bookTitle")

    title = page.text_content("#bookTitle")
    print(f"Reader Title: {title}")

    # 8. Take Screenshot of Reader
    # Wait a bit for potential layout render
    time.sleep(1)
    page.screenshot(path="reader_page.png")
    print("Reader screenshot taken.")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
