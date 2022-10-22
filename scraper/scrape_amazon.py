import json
import requests
import re
from urllib.parse import urljoin
import lxml.html
from bs4 import BeautifulSoup
import os
from unicodedata import normalize


xpath_array = ["//a[starts-with(@href, 'tel')"]
regex_prefix_array = [r'[+][0-9]{2,3}', r'[+][(][0-9]{2,3}']
contact_paths = ['Contact us', 'Contact', 'Contactanos', 'Contacto', 'Contactenos']
regex_array = [
    r'\(?\d{1}\)?[\s-]\d{3}[\s-]\d{3}[\s-]\d{4}',
    r'\(?\d{1}\)?[\s.]\d{3}[\s.]\d{3}[\s.]\d{4}',
    r'\+\(?\d{1,3}\)?[\s.-]?\d{1,9}[\s.-]?\d{1,9}[\s.-]?\d{1,9}',
    r'(?:\d{1,9}){4,9}[\s.-](?:\d{1,9}){4,9}',
    r'\+?\(?:?\d{1,3}\)?[-]\d{1,9}[-]\d{1,9}[-]\d{4,9}',
    r'\+?\(?:?\d{1,3}\)?[\s]\d{1,9}[\s]\d{1,9}[\s]\d{4,9}',
    r'\+?\(?:?\d{1,3}\)?[\s.-]?\d{1,9}[\s.-]?\d{1,9}[\s.-]?\d{1,9}[\s.-]?\d{1,9}'
]
phones = set()
basedir = os.path.dirname(__file__)

def search_by_regex(response):
    arr_regn = []
    for regex in regex_array:
        try:
            reg_match = re.findall(regex, response.text)
            if len(reg_match) > 0:
                for rm in reg_match:
                    if len(rm) >= 8:
                        arr_regn.append(rm)
                if len(arr_regn) > 0:
                    phones.update(reg_match)
                    break
        except:
            return None

def search_by_xpath(response):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tel_element = soup.find("a", href=re.compile("^tel"))
        a_tel_text = a_tel_element.text
        if len(a_tel_text) > 0:
            phones.update([a_tel_text])
    except:
        return None

def search_by_prefix(response):
    tree = lxml.html.fromstring(response.text)
    try:
        with open(os.path.join(basedir, 'country_phone_code.json')) as f:
            data = json.load(f)
            for c_code in data:
                nodos = tree.xpath(f"//*[starts-with(text(),'+{c_code['code']}')]")
                if len(nodos) > 0:
                    for node in nodos:
                        if len(node.text) > 4:
                            phone = str(node.text)
                            phones.update([phone])
                            break

    except Exception as e:
        print(e)
        return None

def normalize_text(text):
    text_norm = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", text), 0, re.I
    )
    text_norm = normalize('NFC', text_norm)

    return text_norm

def extract_product_by_url(url):

    try:
        phones.clear()
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
        response = requests.get(url, headers=headers)
        search_by_xpath(response) # search level 1 by xpath
        soup = BeautifulSoup(normalize_text(response.text.upper()), 'html.parser')

    except:
        return None

    return phones

def get_url_products(product_name):
    url = f"https://www.amazon.com/s?k={product_name}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(response)
