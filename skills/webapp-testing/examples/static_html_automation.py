# Adapted from anthropics/skills (Apache License 2.0); output paths made portable.
from playwright.sync_api import sync_playwright
from pathlib import Path

# Example: Automating interaction with static HTML files using file:// URLs

file_url = Path('path/to/your/file.html').resolve().as_uri()  # works on Windows too

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # Navigate to local HTML file
    page.goto(file_url)

    # Take screenshot
    page.screenshot(path='static_page.png', full_page=True)

    # Interact with elements
    page.click('text=Click Me')
    page.fill('#name', 'John Doe')
    page.fill('#email', 'john@example.com')

    # Submit form
    page.click('button[type="submit"]')
    page.wait_for_timeout(500)

    # Take final screenshot
    page.screenshot(path='after_submit.png', full_page=True)

    browser.close()

print("Static HTML automation completed!")