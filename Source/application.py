import concurrent.futures
from PIL import Image  # picture handling library: https://pillow.readthedocs.io/en/5.1.x/index.html
import io
import requests


def import_urls_from_file(url_dir):
    with open(url_dir, 'r') as urls:
        chunk = []
        for url in urls:
            chunk.append(url.rstrip())
            if len(chunk) >= 1000:
                fetch_image(chunk)
                chunk = []


def rbg_to_hex(r, g, b):
    # converts RBG values into hexidecimal
    return '#%02x%02x%02x' % (r, g, b)


# Retrieve a single page and report the url and contents
def load_url(url, timeout):
    size = 100, 100
    url_string = requests.get(url).content
    img = Image.open(io.BytesIO(url_string))
    img.thumbnail(size, Image.ANTIALIAS)
    pixels = list(img.getdata())
    return pixels


def get_three_most_prevalent(img):
    pix_prev = {}
    first = second = third = (0, "")
    for x in img:
        hex_val = rbg_to_hex(x[0], x[1], x[2])
        if hex_val in pix_prev:
            pix_prev[hex_val] += 1
        else:
            pix_prev[hex_val] = 1
        if pix_prev[hex_val] > first[0]:
            first = (pix_prev[hex_val], hex_val)
        elif second[0] < pix_prev[hex_val] < first[0]:
            second = (pix_prev[hex_val], hex_val)
        elif third[0] < pix_prev[hex_val] < second[0] and pix_prev[hex_val] < first[0]:
            third = (pix_prev[hex_val], hex_val)
    return first, second, third


def fetch_image(urls_in):
    # We can use a with statement to ensure threads are cleaned up promptly
    csv_file = open('processed_images.csv','w')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_url, url, 10): url for url in urls_in}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                most_prevalent = get_three_most_prevalent(data)
                csv_file.write(f"{url}, {most_prevalent[0][1]}, {most_prevalent[1][1]}, {most_prevalent[2][1]}\n")
        csv_file.close()
        print('finished batch')


def process_urls():
    url_in = input("Enter directory where URL file is stored: \n")
    while True:
        try:
            with open(url_in, 'r') as urls:
                urls.close()
                print("Starting image processing...")
                import_urls_from_file(url_in)
                print("Completed image processing, see processed_images.csv for output.")
                break
        except Exception as exc:
            url_in = input("Could not find that directory, please try again: \n")


process_urls()