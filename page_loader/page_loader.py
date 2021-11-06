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
        file.write(update_resource_links(content,
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


def download_scripts(content, directory, page_url):
    soup = BeautifulSoup(content, 'html.parser')
    scripts = soup.findAll('script')
    for script in scripts:
        u = urlparse(page_url)
        if script.get('src') is not None:
            src = urlparse(script['src'])
            if src.netloc == u.netloc:
                url = script['src']
                name = re.sub(r'[^A-Za-z0-9]',
                              '-',
                              u.netloc + splitext(script['src'])[0])
                extension = splitext(url)[1]
                filepath = join(directory, name) + extension
                with open(filepath, 'w') as file:
                    script_url = u.scheme + '://' + u.netloc + url
                    file.write(requests.get(script_url).content)


def update_resource_links(content, directory, page_url):
    soup = BeautifulSoup(content, 'html.parser')
    parsed_url = urlparse(page_url)
    for image in soup.findAll("img"):
        name = re.sub(r'[^A-Za-z0-9]', '-', parsed_url.netloc) + \
            re.sub(r'[^A-Za-z0-9]', '-', splitext(image['src'])[0])
        extension = splitext(image['src'])[1]
        image['src'] = join(directory, name) + extension
    for script in soup.findAll("script"):
        if script.get('src') is not None:
            src = urlparse(script['src'])
            page_host = urlparse(page_url).netloc
            if src.netloc == page_host:
                name = re.sub(r'[^A-Za-z0-9]', '-', parsed_url.netloc) + \
                    re.sub(r'[^A-Za-z0-9]',
                           '-',
                           urlparse(splitext(script['src'])[0]).path)
                extension = splitext(script['src'])[1]
                script['src'] = join(directory, name) + extension
    for link in soup.findAll("link"):
        page_host = urlparse(page_url)
        href = urlparse(link['href'])
        if page_host.netloc == href.netloc or href.netloc == '':
            name = re.sub(r'[^A-Za-z0-9]', '-', parsed_url.netloc) + \
                re.sub(r'[^A-Za-z0-9]', '-', splitext(link['href'])[0])
            extension = splitext(link['href'])[1]
            if extension == '':
                extension = '.html'
            link['href'] = join(directory, name) + extension
    return soup.prettify()


def download_links(content, directory, page_url):
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.findAll('link')
    for link in links:
        u = urlparse(page_url)
        if link.get('src') is not None:
            href = urlparse(link['href'])
            if href.netloc == u.netloc:
                url = link['href']
                name = re.sub(r'[^A-Za-z0-9]',
                              '-',
                              u.netloc + splitext(link['href'])[0])
                extension = splitext(url)[1]
                filepath = join(directory, name) + extension
                with open(filepath, 'w') as file:
                    link_href = u.scheme + '://' + u.netloc + url
                    file.write(requests.get(link_href).content)
