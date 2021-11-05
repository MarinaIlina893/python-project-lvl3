from pytest import fixture
from requests_mock import Mocker
from tempfile import TemporaryDirectory
from page_loader.page_loader import download


@fixture
def mocker():
    mocker = Mocker()
    mocker.register_uri('GET', 'http://test.com', text='data')
    return mocker


def test_download(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://test.com', tmpdir)
            assert r == tmpdir + '/test-com.html'


def test_file_content(mocker):
    with mocker:
        with TemporaryDirectory() as tmpdir:
            r = download('http://test.com', tmpdir)
            with open(r, 'r') as file:
                assert file.read() == 'data'
