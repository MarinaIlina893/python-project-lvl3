import requests
import os
from urllib.parse import urlparse
from os.path import join, splitext, split
import re
from bs4 import BeautifulSoup


def download(url, directory):
    parsed_url = urlparse(url)
    filename = re.sub(r'[^A-Za-z0-9]',
                      '-',
                      parsed_url.netloc + parsed_url.path) + '.html'
    resource_directory = join(directory, splitext(filename)[0] + '_files')
    filepath = join(directory, filename)
    content = requests.get(url).text
    download_images(content, resource_directory, url)
    with open(filepath, 'w') as file:
        file.write(update_image_links(content,
                                      split(resource_directory)[1],
                                      url))
    return filepath


def download_images(content, directory, page_url):
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.findAll('img')
    for image in images:
        u = urlparse(page_url)
        url = image['src']
        name = re.sub(r'[^A-Za-z0-9]',
                      '-',
                      u.netloc + splitext(image['src'])[0])
        extension = splitext(url)[1]
        os.mkdir(directory)
        filepath = join(directory, name) + extension
        with open(filepath, 'wb') as file:
            image_url = u.scheme + '://' + u.netloc + url
            file.write(requests.get(image_url).content)


def update_image_links(content, directory, page_url):
    soup = BeautifulSoup(content, 'html.parser')
    parsed_url = urlparse(page_url)
    for image in soup.findAll("img"):
        name = re.sub(r'[^A-Za-z0-9]', '-', parsed_url.netloc) + \
            re.sub(r'[^A-Za-z0-9]', '-', splitext(image['src'])[0])
        extension = splitext(image['src'])[1]
        image['src'] = join(directory, name) + extension
    return soup.prettify()
