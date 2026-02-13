
from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080/index.html")

        # Wait for page load logic to start
        page.wait_for_timeout(1000)

        # 1. Verify Dark Mode Toggle
        # Click the toggle
        toggle = page.locator("#themeToggle")
        if toggle.is_visible():
            toggle.click()
            # Verify body class
            classes = page.eval_on_selector("body", "el => el.className")
            if "dark-mode" in classes:
                print("Dark mode toggled successfully.")
            else:
                print("Dark mode failed to toggle.")
        else:
            print("Theme toggle not found.")

        # 2. Verify Favorites Tab
        fav_tab = page.locator("#tab-favorites")
        if fav_tab.is_visible():
            print("Favorites tab is visible.")
        else:
            print("Favorites tab is missing.")

        # Take screenshot of Dark Mode Home
        page.screenshot(path="verification/home_dark.png")

        # 3. Open a book to test Reader UI
        # We manually trigger openBook since data loading might be slow or depend on external file
        page.evaluate("""
            // Mock books array if empty so openBook finds it or we pass object directly
            // openBook accepts object
            openBook({title: "Test Book", textUrl: "test_url", author: "Test Author", cover: ""});
        """)

        # Wait for reader to be visible
        reader = page.locator("#reader")
        reader.wait_for(state="visible", timeout=5000)

        # Click Settings
        settings_btn = page.locator("#readerSettingsToggle")
        settings_btn.click()

        # Wait for panel
        panel = page.locator("#readerSettingsPanel")
        panel.wait_for(state="visible", timeout=2000)

        # Take screenshot of Reader with Settings
        page.screenshot(path="verification/reader_settings.png")
        print("Reader settings verification complete.")

        browser.close()

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"Error: {e}")
