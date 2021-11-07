from page_loader.page_loader import download
import argparse
import sys


parser = argparse.ArgumentParser('page_loader', description='Save page ')
parser.add_argument("url", help="Enter page url")
parser.add_argument("directory", help='Will save page to this directory')
args = parser.parse_args()


class KnownError(Exception):
    pass


try:
    def main():
        print(download(args.url, args.directory))
except KnownError:
    sys.exit(1)

if __name__ == '__main__':
    main()
