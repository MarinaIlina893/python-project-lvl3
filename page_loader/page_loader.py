import requests
import os
from urllib.parse import urlparse
from os.path import join, splitext, split
import re
from bs4 import BeautifulSoup
import logging

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, filename='log.log')
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
    content = requests.get(url).text
    # get page files
    soup = BeautifulSoup(content, 'html.parser')
    download_resources(soup, resource_directory, url)
    update_links(soup,
                 split(resource_directory)[1],
                 url)
    # update links to resources in page
    with open(filepath, 'w') as file:
        file.write(soup.prettify())
    return filepath


def download_resources(soup, resource_directory, page_url):
    """Downloads images and scripts of html
document to specified local folder"""
    os.mkdir(resource_directory)
    for resource in (soup.findAll('img') + soup.findAll('script')):
        resource_url = resource['src']
        resource_host = urlparse(resource['src']).netloc
        page_host = urlparse(page_url).netloc
        if resource.get('src'):
            if resource_host == page_host or resource_host == '':
                name = name_file(resource_url, page_url)
                extension = splitext(resource_url)[1]
                filepath = join(resource_directory, name) + extension
                resource_absolute_url = urlparse(page_url).scheme + '://' \
                    + urlparse(page_url).netloc + resource_url
                if resource.name == ['img']:
                    download_image(resource_absolute_url, filepath)
                if resource.name == ['script']:
                    download_script(resource_absolute_url, filepath)
                resource['src'] = join(split(resource_directory)[1], name)


def name_file(resource_url, page_url):
    """Generates file name for resource in local folder"""
    page_host = urlparse(page_url).netloc
    if urlparse(resource_url).netloc == page_host or \
            urlparse(resource_url) is None:
        return re.sub(r'[^A-Za-z0-9]', '-', page_host) + \
               re.sub(r'[^A-Za-z0-9]',
                      '-',
                      urlparse(splitext(resource_url)[0]).path) \
               + splitext(resource_url)[1]
    return re.sub(r'[^A-Za-z0-9]', '-', page_host) + \
        re.sub(r'[^A-Za-z0-9]',
               '-',
               splitext(resource_url)[0]) + splitext(resource_url)[1]


def download_image(image_url, filepath):
    """Downloads image  from url to specified folder"""
    with open(filepath, 'wb') as file:
        file.write(requests.get(image_url).content)


def download_script(script_url, filepath):
    """Downloads script  from url to specified folder"""
    with open(filepath, 'w') as file:
        file.write(requests.get(script_url).text)


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
