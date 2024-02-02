from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def highlight_dark_patterns(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Example: Highlight elements with a specific class name
    dark_pattern_elements = soup.find_all(class_=['a-section as-title-block','vl-card-header__header-container clearfix','discount-price strike'])
    for element in dark_pattern_elements:
        # Add a CSS class for highlighting only to the specified class
        element['class'] = element.get('class', []) + ['highlighted-ad']

    return str(soup)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def detect_ads():
    url = request.form['url']

    # Use Selenium to open the website in a headless browser
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to the provided URL
        driver.get(url)

        # Wait for the page to load (adjust the conditions as needed)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        logging.info(f"Successfully loaded the page for URL: {url}")

        # Get the modified HTML content after JavaScript execution
        modified_html = driver.page_source

        # Highlight dark patterns
        modified_html_highlighted = highlight_dark_patterns(modified_html)

        return render_template('index.html', url=url, modified_html=modified_html_highlighted)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return render_template('index.html', url=url, modified_html="Error occurred during ad detection")

    finally:
        # Close the browser
        driver.quit()
        logging.info("Browser closed")

if __name__ == '__main__':
    app.run(debug=True)
