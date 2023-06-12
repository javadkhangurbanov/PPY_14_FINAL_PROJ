from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# Class to store state
class Condition:
    def __init__(self):
        self.last_link_text = None
        self.links = None

    def __call__(self, d):
        self.links = d.find_elements(By.XPATH, '//a[@href]')
        # print(self.last_link_text, self.links[-1].text)
        if self.last_link_text is None or self.links[-1].text != self.last_link_text:
            self.last_link_text = self.links[-1].text
            return True
        else:
            # print('RETURNED FALSE')
            return False


def get_search_results(search_term):
    from urllib.parse import quote
    search_url = 'https://podcastindex.org/search?q=' + quote(search_term)

    options = Options()
    options.add_experimental_option('detach', True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(search_url)

    body = driver.find_element(By.TAG_NAME, 'body')

    # Wait for the page to be loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component "))
    )
    last_height = 0
    new_height = driver.execute_script("return document.body.scrollHeight")

    condition = Condition()

    while last_height < new_height:
        print('test')
        # Calculate new scroll height and compare with last scroll height
        last_height = new_height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 2).until(condition)
        except TimeoutException:
            # If a timeout occurs, check if the page height has changed
            last_height = new_height
            new_height = driver.execute_script("return document.body.scrollHeight")
            # If the page height has not changed, break the loop
            print(last_height, new_height)
            if new_height == last_height:
                break
            # Otherwise, continue with the loop
            continue
        # Record the new height after WebDriverWait - after the lazy loading is complete
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

    return condition.links

# print('end')
# [print(item.text) for item in condition.links]
