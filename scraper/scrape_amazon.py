import json
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
        self.amazon_sold = 0
        self.amazon_ships = 0
    def scrape_amazon_products(self, product_name, pages, pbar_signal, amazon_sold, amazon_ships, amazon_stars):
        url = f"https://www.amazon.com/s?k={product_name}"
        arr_href = []
        products_count = 0
        self.amazon_sold = amazon_sold
        self.amazon_ships = amazon_ships
        self.amazon_stars = amazon_stars

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
                return self.products_array

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
            #   url
            product.url = self.driver.current_url
            #   name
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
            #   stars
            span_stars = soup.findAll("span", {"id": "acrPopover"})
            if len(span_stars) > 0:
                stars = span_stars[0].find("span", {"class": "a-icon-alt"}).text
                if len(stars) > 0:
                    product.stars = stars
            #   ratings
            span_ratings = soup.find("span", {"id": "acrCustomerReviewText"})
            if span_ratings:
                product.ratings = span_ratings.text
            #   colors
            colors_array = []
            div_colors = soup.find("div", {"id": "variation_color_name"})
            if div_colors:
                ul = div_colors.find("ul")
                if ul:
                    li_elements = ul.findAll("li")
                    for li in li_elements:
                        color = li.find("img")["alt"]
                        colors_array.append(color)
                    product.colors = ";".join(colors_array)
            #   features
            features_array = []
            div_features = soup.find("div", {"id": "feature-bullets"})
            if div_features:
                ul = div_features.find("ul")
                if ul:
                    li_elements = ul.findAll("li")
                    for li in li_elements:
                        feature = li.find("span").text
                        features_array.append(feature)
                    product.features = ";".join(features_array)
            #   details
            details_array = []
            div_details = soup.find("div", {"id": "productOverview_feature_div"})
            if div_details:
                table = div_details.find("table")
                if table:
                    tr_elements = table.findAll("tr")
                    for tr in tr_elements:
                        td_elements = tr.findAll("td")
                        td_title = td_elements[0].find("span").text
                        td_value = td_elements[1].find("span").text
                        detail = str(td_title) + " " + str(td_value)
                        details_array.append(detail)
                    product.details = ";".join(details_array)
            #   note
            div_note = soup.find("div", {"id": "universal-product-alert"})
            if div_note:
                spans = div_note.findAll("span")
                if len(spans) > 0:
                    product.note = spans[1].text
            #   Sold by and ships from
            div_soldby = soup.find("div", {"id": "shipsFromSoldByMessage_feature_div"})
            if div_soldby:                  #   'SHIPS FROM AND SOLD BY AMAZON.COM' in span_soldby.text.upper()
                span_soldby = div_soldby.find("span")
                if span_soldby:
                    product.seller = span_soldby.text
            else:
                div_soldby = soup.findAll("div", {"tabular-attribute-name": "Sold by"})
                if len(div_soldby) > 0:
                    span_soldby = div_soldby[1].find("span")
                    if span_soldby:
                        product.seller = span_soldby.text

                div_ships_from = soup.findAll("div", {"tabular-attribute-name": "Ships from"})
                if len(div_ships_from) > 0:
                    span_ships = div_ships_from[1].find("span")
                    if span_ships:
                        product.shipsFrom = span_ships.text

            #   Validate sold and ships from amazon
            if self.amazon_sold == 2 and 'AMAZON' not in product.seller.upper():
                return
            if self.amazon_ships == 2 and 'AMAZON' not in product.shipsFrom.upper():
                return

            #   Validate stars
            if self.amazon_stars != 'All':
                stars_numbers = re.findall(r'\d+', product.stars)
                if len(stars_numbers) > 0:
                    star_num = stars_numbers[0]
                    star_selected = re.findall(r'\d+', self.amazon_stars)[0]
                    if float(star_num) < float(star_selected):
                        return
                else:
                    return

            self.products_array.append(product.to_dict())

        except Exception as e:
            self.logging.reg_log(str(self.driver.current_url) + "\n" + str(e), "error")