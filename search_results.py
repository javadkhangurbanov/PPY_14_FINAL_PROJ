from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from podcast import Podcast
from PyQt5.QtCore import QThread, pyqtSignal


def get_search_results(search_term):
    from urllib.parse import quote
    search_url = 'https://podcastindex.org/search?q=' + quote(search_term)

    options = Options()
    options.add_experimental_option('detach', True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(search_url)

    body = driver.find_element(By.TAG_NAME, 'body')

    # Wait for the page to be loaded
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component "))
        )
    except:
        driver.quit()
        raise NoResultsException(f'No results for search term: {search_term}')

    last_height = 0
    new_height = driver.execute_script("return document.body.scrollHeight")

    #  Dynamic wait time, increments by 0.5 seconds, max wait time is 5 seconds
    base_wait_time = 0.5
    max_wait_time = 1
    wait_time = base_wait_time

    while True:
        print('test')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(wait_time)  # wait for the page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            wait_time += 0.5
            print(wait_time)
            if wait_time > max_wait_time:
                break
        else:
            # Reset the wait time to base to make the overall wait time smaller
            wait_time = base_wait_time
        last_height = new_height
        print(last_height, new_height)

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    results_container = soup.find('div', {'class': 'infinite-scroll-component'})

    results = results_container.find_all('div', {'class': 'result'})

    podcasts = []

    for result in results:
        result_row = result.find('div', {'class': 'result-row'})
        # Get the whole text of the div without going in its' nested classes
        podcast_title = result_row.find('div', {'class': 'result-title'}).get_text(strip=True)
        podcast_author = result_row.find_all('p', class_=False)[0].text
        podcast_categories = [item.get_text(strip=True) for item in
                              result_row.find_all('div', {'class': 'result-category'})]
        podcast_description = result.find('p', {'class': 'result-description'})
        if podcast_description is None:
            podcast_description = 'No description'
        podcast_image = result_row.find_all('img')[0]['src']
        pi_link = 'https://podcastindex.org' + result_row.find('a').get('href')

        podcast = Podcast(podcast_title, podcast_author, podcast_categories, podcast_description, podcast_image,
                          pi_link)
        podcasts.append(podcast)

    driver.quit()
    return podcasts


class WebsiteRetriever(QThread):
    finished = pyqtSignal(str)

    def __init__(self, pi_link):
        QThread.__init__(self)
        self.pi_link = pi_link

    def run(self):
        options = Options()
        options.add_experimental_option('detach', True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(self.pi_link)

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "podcast-header-external-links"))
        )

        html = driver.page_source
        original_website_soup = BeautifulSoup(html, 'html.parser')
        original_website_link_tag = original_website_soup.find('a', {'title': 'Podcast Website'})

        if original_website_link_tag is not None:
            original_website = original_website_link_tag.get('href')
        else:
            original_website = None

        driver.quit()
        self.finished.emit(original_website)


class NoResultsException(Exception):
    pass
