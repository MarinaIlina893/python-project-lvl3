from page_loader.download import download
import argparse
import sys


parser = argparse.ArgumentParser('page_loader', description='Save page ')
parser.add_argument("url", help="Enter page url")
parser.add_argument("directory", help='Will save page to this directory')
args = parser.parse_args()


class KnownError(Exception):
    pass


def main():
    try:
        print(download(args.url, args.directory))
    except KnownError:
        sys.exit()


if __name__ == '__main__':
    main()
