import os

from pytest import fixture, raises
from requests_mock import Mocker
from tempfile import TemporaryDirectory
from page_loader.download import download
from bs4 import BeautifulSoup
import requests


@fixture
def mocker():
    mocker = Mocker()
    with open('tests/fixtures/raw_data.html') as page:
        mocker.register_uri('GET', 'http://ru.hexlet.io/courses', text=page.read())
        mocker.register_uri('GET', 'http://ru.hexlet.io/assets/professions/nodejs.png')
        mocker.register_uri('GET', 'https://ru.hexlet.io/packs/js/runtime.js')
        mocker.register_uri('GET', 'http://ru.hexlet.io/assets/application.css')
    return mocker


@fixture
def mocker404():
    mocker404 = Mocker()
    mocker404.register_uri('GET', 'http://ru.hexlet.io/courses', status_code=404)
    return mocker404


def test_download_filepath(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://ru.hexlet.io/courses', tmpdir)
            assert r == tmpdir + '/ru-hexlet-io-courses.html'


def test_download_file_content(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://ru.hexlet.io/courses', tmpdir)
            with open(r, 'r') as file:
                with open('tests/fixtures/parsed_data.html') as parsed_page:
                    soup = BeautifulSoup(parsed_page.read(), 'html.parser')
                    assert file.read() == soup.prettify()


def test_download_404(mocker404):
    with mocker404:
        with TemporaryDirectory() as tmpdir:
            assert raises(requests.exceptions.HTTPError, download, 'http://ru.hexlet.io/courses', tmpdir)


def test_download_resources(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            download('http://ru.hexlet.io/courses', tmpdir)
            assert len(os.listdir(os.path.join(tmpdir, 'ru-hexlet-io-courses_files'))) == 4
