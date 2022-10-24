import re
import os
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from unicodedata import normalize
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.logging import LoggingApp
from models.productAmazon import ProductAmazon

basedir = os.path.dirname(__file__)

def normalize_text(text):
    text_norm = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", text), 0, re.I
    )
    text_norm = normalize('NFC', text_norm)

    return text_norm

class ScrapeAmazon():
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=os.path.join(basedir, 'chromedriver.exe'))
        self.logging = LoggingApp()
        self.products_array = []
    def scrape_amazon_products(self, product_name, pages, pbar_signal):
        url = f"https://www.amazon.com/s?k={product_name}"
        arr_href = []
        products_count = 0

        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, 's-skipLinkTargetForMainSearchResults')))
            max_pagination_number = self.driver.find_element(By.XPATH, "//div[contains(@class, 's-pagination-container')]//span[contains(@class, 's-pagination-disabled')][2]").text
            product_items = self.driver.find_elements(By.CLASS_NAME, "s-product-image-container")
            max_pagination_number = int(max_pagination_number)

            if pages != 'Max':
                max_pagination_number = int(pages)

            estimated_products = len(product_items) * max_pagination_number

            for i in range(0, max_pagination_number):
                url = f"https://www.amazon.com/s?k={product_name}&page={i+1}"
                self.driver.get(url)
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, 's-skipLinkTargetForMainSearchResults')))
                product_items = self.driver.find_elements(By.CLASS_NAME, "s-product-image-container")

                if len(product_items) > 0:
                    for product in product_items:
                        try:
                            a_tag = product.find_element(By.TAG_NAME, "a")
                            href = a_tag.get_attribute('href')
                            arr_href.append(href)
                        except Exception as e:
                            self.logging.reg_log(str(self.driver.current_url) + "\n" + str(e), "warning")
                            continue

                if len(arr_href) > 0:
                    for hrf in arr_href:
                        self.scrape_product_details(hrf)
                        products_count=products_count+1
                        estimated_percent_advance = round((products_count / estimated_products) * 100)
                        if estimated_percent_advance < 100:
                            pbar_signal.emit(estimated_percent_advance)

                self.driver.close()
                return {
                    "products": self.products_array
                }

        except Exception as e:
            self.logging.reg_log(str(self.driver.current_url) + "\n" + str(e), "error")
            self.driver.close()

    def scrape_product_details(self, url):
        product = ProductAmazon()
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, 'productTitle')))
            title = self.driver.find_elements(By.ID, 'productTitle')
            if len(title) > 0:
                product.name = title[0].text
            # Using beautifulSoup for the others tags
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            #   Price
            span_price = soup.findAll("span", {"class": "priceToPay"})
            if len(span_price) > 0:
                span_price_value = span_price[0].find("span", {"class": "a-offscreen"})
                if len(span_price_value) > 0:
                    product.price = span_price_value.text
            else:
                #   Price range
                span_price_range = soup.findAll("span", {"class": "a-price-range"})
                if len(span_price_range) > 0:
                    span_price_range = span_price_range[0].findAll("span", {"class": "a-offscreen"})
                    if len(span_price_range) > 0:
                        product.price = span_price_range[0].text + "-" + span_price_range[1].text


            self.products_array.append(product)

        except Exception as e:
            self.logging.reg_log(str(self.driver.current_url) + "\n" + str(e), "error")
            self.driver.close()