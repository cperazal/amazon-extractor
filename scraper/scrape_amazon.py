import re
import os
import time
import random
import subprocess
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from unicodedata import normalize
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.logging import LoggingApp
from models.productAmazon import ProductAmazon
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome import options
import config

basedir = os.path.dirname(__file__)

def normalize_text(text):
    text_norm = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", text), 0, re.I
    )
    text_norm = normalize('NFC', text_norm)

    return text_norm

def kill_chrome_processes():
    """Kill all chromedriver processes"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    time.sleep(1)  # Esperar a que los procesos se cierren

class ScrapeAmazon():
    def __init__(self):
        kill_chrome_processes()

        self.chrome_options = options.Options()

        # Modo headless controlado por config.HEADLESS_MODE
        if config.HEADLESS_MODE:
            self.chrome_options.headless = True
            self.chrome_options.add_argument('--headless=new')

        # Opciones para navegador invisible
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument(f'--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}')

        # Opciones anti-detección de bot
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        # User-Agent desde config
        self.chrome_options.add_argument(f'user-agent={config.USER_AGENT}')

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        self.logging = LoggingApp()
        self.products_array = []
        self.amazon_sold = 0
        self.amazon_ships = 0
        self.request_delay_min = config.REQUEST_DELAY_MIN
        self.request_delay_max = config.REQUEST_DELAY_MAX

    def scrape_amazon_products(self, product_name, pages, pbar_signal, amazon_sold, amazon_ships, amazon_stars,
                               price_min, price_max, check_price):
        url = f"https://www.amazon.com/s?k={product_name}"
        products_count = 0
        self.amazon_sold = amazon_sold
        self.amazon_ships = amazon_ships
        self.amazon_stars = amazon_stars
        self.price_min = price_min
        self.price_max = price_max
        self.check_price = check_price

        try:
            # Intentar acceder a la página principal con reintentos (MAX_RETRIES)
            loaded = False
            for attempt in range(config.MAX_RETRIES):
                try:
                    self.driver.get(url)
                    time.sleep(random.uniform(3, 5))  # Espera inicial mayor
                    WebDriverWait(self.driver, config.WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.ID, 's-skipLinkTargetForMainSearchResults')))
                    loaded = True
                    break
                except Exception as retry_e:
                    self.logging.reg_log(
                        f"Intento {attempt + 1}/{config.MAX_RETRIES} fallido: {retry_e}", "warning")
                    if attempt < config.MAX_RETRIES - 1:
                        time.sleep(config.RETRY_DELAY)

            if not loaded:
                self.logging.reg_log("No se pudo cargar la página después de los reintentos.", "error")
                self.driver.close()
                return []

            max_pagination_number = self.driver.find_element(By.XPATH, "//*[@class='s-pagination-strip']/ul/span[2]").text
            product_items = self.driver.find_elements(By.CLASS_NAME, "s-product-image-container")
            max_pagination_number = int(max_pagination_number)

            if pages != 'Max':
                max_pagination_number = int(pages)

            estimated_products = len(product_items) * max_pagination_number

            for i in range(0, max_pagination_number):
                # Delay aleatorio entre solicitudes
                delay = random.uniform(self.request_delay_min, self.request_delay_max)
                time.sleep(delay)

                url = f"https://www.amazon.com/s?k={product_name}&page={i+1}"

                # Reintentos por página
                page_loaded = False
                for attempt in range(config.MAX_RETRIES):
                    try:
                        self.driver.get(url)
                        time.sleep(random.uniform(2, 3))
                        WebDriverWait(self.driver, config.WAIT_TIMEOUT).until(
                            EC.presence_of_element_located((By.ID, 's-skipLinkTargetForMainSearchResults')))
                        page_loaded = True
                        break
                    except Exception as retry_e:
                        self.logging.reg_log(
                            f"Página {i+1} - Intento {attempt + 1}/{config.MAX_RETRIES} fallido: {retry_e}", "warning")
                        if attempt < config.MAX_RETRIES - 1:
                            time.sleep(config.RETRY_DELAY)

                if not page_loaded:
                    self.logging.reg_log(f"No se pudo cargar la página {i+1}, se omite.", "warning")
                    continue

                product_items = self.driver.find_elements(By.CLASS_NAME, "s-product-image-container")
                arr_href = []

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
        # Delay aleatorio antes de acceder a la página de detalles
        time.sleep(random.uniform(self.request_delay_min, self.request_delay_max))
        self.driver.get(url)
        time.sleep(random.uniform(1, 2))  # Espera después de cargar
        try:
            WebDriverWait(self.driver, config.PRODUCT_DETAILS_TIMEOUT).until(
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
            span_price = soup.find("span", {"id": "apex-pricetopay-accessibility-label"})
            if len(span_price) > 0:
                product.price = span_price.text
            else:
                #   Price range
                span_price_range = soup.findAll("span", {"class": "a-price-range"})
                if len(span_price_range) > 0:
                    span_price_range = span_price_range[0].findAll("span", {"class": "a-offscreen"})
                    if len(span_price_range) > 0:
                        product.price = span_price_range[0].text + "-" + span_price_range[1].text
            # iff don't have price, try to find the deal
            if product.price == "":
                span_price = soup.findAll("span", {"class": "apexPriceToPay"})
                if len(span_price) > 0:
                    span_price_value = span_price[0].find("span", {"class": "a-offscreen"})
                    if len(span_price_value) > 0:
                        product.price = span_price_value.text
            if product.price !="":
                product.price = product.price.replace(",", "")
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
            div_soldby = soup.find("a", {"id": "sellerProfileTriggerId"})
            if div_soldby:                  #   'SHIPS FROM AND SOLD BY AMAZON.COM' in span_soldby.text.upper()
                product.seller = div_soldby.text

            else:
                div_soldby = soup.findAll("div", {"tabular-attribute-name": "Sold by"})
                if len(div_soldby) > 0:
                    span_soldby = div_soldby[1].find("span")
                    if span_soldby:
                        product.seller = span_soldby.text

            div_ships_from = soup.find("div", {"id": "fulfillerInfoFeature_feature_div"})
            if len(div_ships_from) > 0:
                span_ships = div_ships_from.findAll("span")
                if span_ships:
                    product.shipsFrom = span_ships[1].text

            #   Validate sold and ships from ama zon
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

            # Validate price range
            if self.check_price == 2 and product.price != "":
                if len(span_price) > 0:
                    price = re.findall("\d+\.\d+", product.price)[0]
                    if float(self.price_min) <= float(price) and float(price) <= float(self.price_max):
                        pass
                    else:
                        return
                else:
                    price_range = re.findall("\d+\.\d+", product.price)
                    price_1 = float(price_range[0])
                    price_2 = float(price_range[1])
                    if price_1 >= float(self.price_min) and price_2 <= float(self.price_max):
                        pass
                    else:
                        return

            if product.to_dict() not in self.products_array:
                self.products_array.append(product.to_dict())

        except Exception as e:
            self.logging.reg_log(str(self.driver.current_url) + "\n" + str(e), "error")