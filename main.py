import time
import random
import requests
import os
import io
import jinja2

from bs4 import BeautifulSoup

ROOT_URL = 'http://www.overmundo.com.br'

INITIAL_PATH = '/arquivo_usuario/daniel-duende'


# ---- Teeny lil silly retrieve & cache system ----


def random_sleep():
    time.sleep(random.randint(15, 20))


def get_page(url):
    random_sleep()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.content
    raise Exception


def save_file(name, content):
    io.open(name, 'wb').write(content)
    return content


def gen_file_name(url, cache):
    name = url.replace('/', '-').replace(':', '-')
    return f'./cache/cache-{name}' if cache else f'./docs/{name}'


def cached_url(url, into_cache):
    name = gen_file_name(url, into_cache)
    if os.path.exists(name):
        return name, io.open(name, 'rb').read()
    else:
        return name, save_file(name, get_page(url))


def download(path, into_cache):
    url = f"{ROOT_URL}{path}"
    return cached_url(url, into_cache)


def download_content(path):
    _, content = download(path, into_cache=True)
    return content


# ---- Templatery ----


TMPL_OUT = os.path.join(os.path.dirname(__file__), 'docs')
TMPL_PATH = os.path.join(os.path.dirname(__file__), 'tmpl')
TMPL_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TMPL_PATH),
    autoescape=jinja2.select_autoescape(['html', 'xml']))
TMPL_ENV.trim_blocks = True
TMPL_ENV.lstrip_blocks = True

def do_template(tmpl, name=None, **kwargs):
    output = os.path.join(TMPL_OUT, name or tmpl)
    template = TMPL_ENV.get_template(tmpl)
    io.open(output, 'w').write(template.render(**kwargs))


# ---- Process Content ---


def scrape_page(path, page):
    title = page.select_one('h1').text
    date = page.select_one('.extra').text.strip().split('\r')[0]
    content = page.select_one('div#conteudo div.conteudo')
    del content['class']
    do_template(
        'page.html',
        link_path(path),
        title=title,
        date=date,
        content=content)


def scrape_doc(path, page):
    title = page.select_one('h1').text
    date = page.select_one('.extra').text.strip().split('\r')[0]
    download_link = page.select_one('div.botao.baixar a').get('href')
    download_name, _ = download(download_link, into_cache=False)
    content = (
        page.select_one('div#conteudo div.obraTexto') or
        page.select_one('div#conteudo div.conteudo'))
    do_template(
        'page.html',
        link_path(path),
        title=title,
        date=date,
        content=content,
        download_link=link_path(download_name, ''))


def do_page(path):
    content = download_content(path)
    page = BeautifulSoup(content, 'html.parser')
    if path.startswith('/banco'):
        scrape_doc(path, page)
    else:
        scrape_page(path, page)


def link_path(path, ext='.html'):
    return f"{path.split('/')[-1]}{ext}"


def page_attrs(page_url, page_title):
    return {"url": link_path(page_url), "title": page_title}


def do_root():
    root_page = BeautifulSoup(download_content(INITIAL_PATH), 'html.parser')
    pages = []
    for link in root_page.select('div[class=colaboracoes] h3 a'):
        page_url = link.get('href')
        do_page(page_url)
        pages.append(page_attrs(page_url, link.text))
    do_template('index.html', pages=pages)


if __name__ == '__main__':
    do_root()
