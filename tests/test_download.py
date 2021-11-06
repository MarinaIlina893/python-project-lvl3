from pytest import fixture
from requests_mock import Mocker
from tempfile import TemporaryDirectory
from page_loader.page_loader import download
from bs4 import BeautifulSoup


@fixture
def mocker():
    mocker = Mocker()
    with open('tests/fixtures/raw_data.html') as page:
        mocker.register_uri('GET', 'http://test.com', text=page.read())
        mocker.register_uri('GET', 'http://test.com/assets/professions/nodejs.png')
    return mocker


def test_download_filepath(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://test.com', tmpdir)
            assert r == tmpdir + '/test-com.html'


def test_download_file_content(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://test.com', tmpdir)
            with open(r, 'r') as file:
                with open('tests/fixtures/parsed_data.html') as parsed_page:
                    soup = BeautifulSoup(parsed_page.read(),  'html.parser')
                    assert file.read() == soup.prettify()
