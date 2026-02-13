from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Index Page - Stats Tab
        page.goto("http://localhost:8080/index.html")

        # Inject some stats AND prevent valentine modal
        page.evaluate("""
            localStorage.setItem('gutenberg:stats', JSON.stringify({
                totalTime: 3665,
                pagesTurned: 42
            }));
            localStorage.setItem('gutenberg:lastpage:testbook', '10');
            localStorage.setItem('owami_valentine_shown', 'true');
        """)

        page.reload()
        page.click('#tab-stats')
        time.sleep(1)
        page.screenshot(path="index_stats.png")

        # 2. Index Page - Collections Tab & Creation
        page.click('#tab-collections')
        time.sleep(1)

        # Handle prompt for collection creation
        def handle_dialog(dialog):
            dialog.accept("My Favorites")
        page.on("dialog", handle_dialog)

        page.click("text=+ New Collection")
        time.sleep(1)
        page.screenshot(path="index_collections.png")

        # 3. Reader Page
        # Use a dummy book url
        page.goto("http://localhost:8080/reader.html?url=http://www.gutenberg.org/files/11/11-0.txt&title=Alice%20in%20Wonderland")
        time.sleep(2) # wait for load
        page.screenshot(path="reader_page.png")

        browser.close()

if __name__ == "__main__":
    run()
