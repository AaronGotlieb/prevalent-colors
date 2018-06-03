import concurrent.futures
from PIL import Image  # picture handling library: https://pillow.readthedocs.io/en/5.1.x/index.html
import io
import requests


URLS = ['https://i.redd.it/d8021b5i2moy.jpg', 'https://i.redd.it/d8021b5i2moy.jpg', 'http://i.imgur.com/TKLs9lo.jpg']

# configuration variables
URL_FILE_DIR = 'urls.txt'

# private helper variables
img_urls = []


def import_urls_from_file():
    with open(URL_FILE_DIR, 'r') as urls:
        for url in urls:
            img_urls.append(url.rstrip())


def rbg_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)


# Retrieve a single page and report the url and contents
def load_url(url, timeout):
    size = 150, 150
    url_string = requests.get(url).content
    img = Image.open(io.BytesIO(url_string))
    img.thumbnail(size, Image.ANTIALIAS)
    pixels = list(img.getdata())
    return pixels


def get_three_most_prevalent(img):
    pix_prev = {}
    first = second = third = (0, "")
    for x in img:
        hexval = rbg_to_hex(x[0], x[1], x[2])
        if hexval in pix_prev:
            pix_prev[hexval] += 1
        else:
            pix_prev[hexval] = 1
        if pix_prev[hexval] > first[0]:
            first = (pix_prev[hexval], hexval)
        elif pix_prev[hexval] > second[0] and pix_prev[hexval] < first[0]:
            second = (pix_prev[hexval], hexval)
        elif pix_prev[hexval] > third[0] and pix_prev[hexval] < second[0] and pix_prev[hexval] < first[0]:
            third = (pix_prev[hexval], hexval)
    return (first, second, third)


import_urls_from_file()

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in img_urls}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print(get_three_most_prevalent(data))
