from urllib.parse import urlsplit

import base64
import os


def url_to_file_name(url):
    return url.replace("https://", "").replace("http://", "").replace("/", "").replace(".", "").replace("?",
                                                                                                        "").replace("=",
                                                                                                                    "").replace(
        "&", "").replace(":", "").replace("-", "").replace("_", "").replace("!", "").replace(";", "").replace(",",
                                                                                                              "").replace(
        " ", "").replace("%", "").replace("#", "").replace("@", "")


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
    url = url.strip()
    return url[:url.find("/", 8)]
    # return urlsplit(url).netloc


def storage_path():
    if not os.path.exists("storage"):
        os.mkdir("storage")

    return f"storage"


def test_extract_base_url():
    url = "https://sananes.co.il/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-spc"

    base = extract_base_url(url)
    print(base)


if __name__ == '__main__':
    test_extract_base_url()
