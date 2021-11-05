import requests
from urllib.parse import urlparse
from os.path import join
import re


def download(url, directory):
    parsed_url = urlparse(url)
    filename = re.sub(r'[^A-Za-z0-9]',
                      '-',
                      parsed_url.netloc + parsed_url.path) + '.html'
    filepath = join(directory, filename)
    content = requests.get(url).text
    with open(filepath, 'w') as file:
        file.write(content)
    return filepath
