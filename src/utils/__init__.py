from urllib.parse import urlsplit

import base64


def url_path_to_filename(url: str):
    return base64.urlsafe_b64encode(url.encode()).decode()


def filename_to_url_path(filename: str):
    return base64.urlsafe_b64decode(filename.encode()).decode()


def test_url_path_to_filename():
    url = "https://www.calcalist.co.il/finance/articles/0,7340,L-3888751,00.html"
    filename = url_path_to_filename(url)
    print(url)
    print(filename)
    n_url = filename_to_url_path(filename)
    print(n_url)
    assert url == n_url



def url_to_filename(url):
    return url.split("//")[1].split("/")[0].replace(".", "_")


def extract_base_url(url):
    # from beginning to first slash that is not part of http:// or https://
    return url[:url.find("/", 8)]
    # return urlsplit(url).netloc
