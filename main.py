import time
import random
import requests
import os
import io

from bs4 import BeautifulSoup

ROOT_URL = 'http://www.overmundo.com.br'

INITIAL_PATH = '/arquivo_usuario/daniel-duende'


def random_sleep():
    time.sleep(random.randint(15, 20))


def get_page(url):
    # random_sleep()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.content
    raise Exception


def savefile(name, content):
    io.open(name, 'wb').write(content)
    return content


def gen_file_name(url):
    return './cache-' + url.replace('/', '-').replace(':', '-')


def cachedurl(url):
    name = gen_file_name(url)
    if os.path.exists(name):
        return True, io.open(name, 'rb').read()
    else:
        return False, savefile(name, get_page(url))


def download_path(path):
    url = f"{ROOT_URL}{path}"
    _, content = cachedurl(url)
    return content


def scrape_page(page):
    print(page.select_one('h1').text)
    print(page.select_one('div#conteudo div.conteudo').text)


def scrape_doc(page):
    print(page.select_one('h1').text)
    download_link = page.select_one('div.botao.baixar a')
    download_path(download_link.get('href'))
    text_object = (
        page.select_one('div#conteudo div.obraTexto') or
        page.select_one('div#conteudo div.conteudo'))
    print(text_object.text)



def parse_page(path):
    content = download_path(path)
    page = BeautifulSoup(content, 'html.parser')
    if path.startswith('/banco'):
        scrape_doc(page)
    else:
        scrape_page(page)


def parse_root():
    page = BeautifulSoup(download_path(INITIAL_PATH), 'html.parser')
    for link in page.select('div[class=colaboracoes] h3 a'):
        parse_page(link.get('href'))


if __name__ == '__main__':
    parse_root()
