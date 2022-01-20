import requests
import os
from urllib.parse import urlparse
from os.path import join, splitext, split
import re
from bs4 import BeautifulSoup
import logging
from progress.bar import Bar
import sys


LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, stream=sys.stderr)
logger = logging.getLogger()
logger.debug('Test logger')


def download(url, directory):
    """Downloads page and its resources to specified local folder"""
    parsed_url = urlparse(url)
    # define page file name
    filename = re.sub(r'[^A-Za-z0-9]',
                      '-',
                      parsed_url.netloc + parsed_url.path) + '.html'
    # define directory name for files
    resource_directory = join(directory, splitext(filename)[0] + '_files')
    # define page filepath
    filepath = join(directory, filename)
    # get page
    try:
        page = requests.get(url)
        page.raise_for_status()
    except requests.exceptions.RequestException as error:
        logger.error('Request went wrong')
        raise error
    # get page files
    soup = BeautifulSoup(page.text, 'html.parser')
    download_resources(soup, resource_directory, url)
    # update links in page
    with open(filepath, 'w') as file:
        file.write(soup.prettify())
    return filepath


def download_resources(soup, resource_directory, page_url):
    """Downloads images and scripts of html
document to specified local folder and updates links to them"""
    create_dir(resource_directory)
    bar = Bar('Processing', max=20)
    for resource in find_resources(soup):
        src = resource.get('src', resource.get('href'))
        if src and is_local(src, page_url):
            name = name_file(src, page_url)
            filepath = join(resource_directory, name)
            resource_url = build_resource_url(src, page_url)
            resource_src = join(split(resource_directory)[1], name)
            download_resource(resource_url, filepath, resource.name)
            if resource.name in ('img', 'script'):
                resource['src'] = resource_src
            else:
                resource['href'] = resource_src
        bar.next()
    bar.finish()


def find_resources(soup):
    return soup.findAll('img') + soup.findAll('script') + soup.findAll('link')


def is_local(src, page_url):
    # не учитывается поддомен
    page_host = urlparse(page_url).netloc
    resource_host = urlparse(src).netloc
    if resource_host == page_host or resource_host == '':
        return True


def build_resource_url(src, page_url):
    if urlparse(src).netloc:
        return src
    else:
        return urlparse(page_url).scheme + '://' \
            + urlparse(page_url).netloc + src


def create_dir(resource_directory):
    try:
        os.mkdir(resource_directory)
    except OSError as error:
        logger.error('OS Error')
        raise error


def name_file(resource_url, page_url):
    """Generates file name for resource in local folder"""
    page_host = urlparse(page_url).netloc
    resource_host = urlparse(resource_url).netloc
    extension = splitext(resource_url)[1]
    if extension == '':
        extension = '.html'
    url_after_host = re.sub(r'[^A-Za-z0-9]', '-',
                            urlparse(splitext(resource_url)[0]).path) \
        + extension
    if resource_host == '':
        return re.sub(r'[^A-Za-z0-9]', '-', page_host) + url_after_host
    return re.sub(r'[^A-Za-z0-9]', '-', resource_host) + url_after_host


def download_resource(url, filepath, resource_name):
    payload = get_resource_payload(url)
    if resource_name == 'img' or 'link':
        with open(filepath, 'wb') as file:
            file.write(payload.content)
    else:
        with open(filepath, 'w') as file:
            file.write(payload.text)


def get_resource_payload(resource_url):
    try:
        payload = requests.get(resource_url)
        payload.raise_for_status()
        return payload
    except requests.exceptions.RequestException as error:
        logger.error('Request went wrong')
        raise error


def update_links(soup, directory, page_url):
    """Updates links in html"""
    for link in soup.findAll("link"):
        page_host = urlparse(page_url)
        href = urlparse(link['href'])
        if page_host.netloc == href.netloc or href.netloc == '':
            name = re.sub(r'[^A-Za-z0-9]', '-', urlparse(page_url).netloc) + \
                re.sub(r'[^A-Za-z0-9]', '-', splitext(link['href'])[0])
            extension = splitext(link['href'])[1]
            if extension == '':
                extension = '.html'
            link['href'] = join(directory, name) + extension
