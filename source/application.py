import concurrent.futures
from PIL import Image  # picture handling library: https://pillow.readthedocs.io/en/5.1.x/index.html
import io
import requests


# Retrieve a single image and resize down to max 100x100 pixels
# resizing is done to scale by Pillow.
# Doing this does endanger a mis-marking of most common pixel colors
# but the performance increase out-weight those dangers.
def load_url(url, timeout):
    size = 150, 150
    url_string = requests.get(url).content
    img = Image.open(io.BytesIO(url_string))
    img.thumbnail(size, Image.ANTIALIAS)
    pixels = list(img.getdata())
    return pixels


# This method takes in the image array and finds the top 3 most
# most prevalent colors. It runs in O(n) speed - iterating over
# the image array once.
def rank_top_colors(image):
    color_count_map = {}
    first = second = third = ("", 0)

    for pixel in image:
        color = '#%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])  # converts RGB values to Hexadecimal

        if color in color_count_map:
            color_count_map[color] += 1
        else:
            color_count_map[color] = 1
        color_count = color_count_map[color]

        if color_count > first[1]:
            if color != first[0]:
                if color != second[0]:
                    third = second
                second = first
            first = (color, color_count)
        elif color_count > second[1]:
            if color != second[0]:
                third = second
            second = (color, color_count)
        elif color_count > third[1]:
            third = (color, color_count)

    return first, second, third


# Downloading images is I/O bound, thus, even with a single CPU environment
# it is optimal to fetch the images into memory w/ a thread pool
# while preforming the array parsing to find the top 3 colors.
# Without async image fetch, we would experience a ~1 second * number of URL's
# delay depending on internet speed & image download size
# there is also a timeout - eg if you cant load an image, after 10 seconds the thread
# will stop and the image will be skipped - it will not be written to the csv.
def fetch_images(urls_in):
    # We can use a with statement to ensure threads are cleaned up promptly
    csv_file = open('processed_images.csv', 'w')
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_url, url, 10): url for url in
                         urls_in}  # call load_url() on each URL passed in
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                # timeout or exception when trying to load the URL
                print('%r generated an exception: %s' % (url, exc))
            else:
                # once URL loads, if successful, rank top 3 and write to CSV
                most_prevalent = rank_top_colors(data)
                csv_file.write(f"{url}, {most_prevalent[0][0]}, {most_prevalent[1][0]}, {most_prevalent[2][0]}\n")
        csv_file.close()
        print('finished batch')


# import urls from the file, do so in chunks as the url list can
# run into the billions - thus do not want to move all the URL's to
# a single list. The chunk of URL's are then fetched with the thread pool.
def import_urls_from_file(url_dir):
    with open(url_dir, 'r') as urls:
        chunk = []
        for url in urls:
            chunk.append(url.rstrip())
            if len(chunk) >= 1000:
                fetch_images(chunk)
                chunk = []


# handle user input for path to URL's text file
def process_urls():
    url_in = input("Enter directory where URL file is stored: \n")
    while True:
        try:
            with open(url_in, 'r') as urls:
                urls.close()
                print("Starting processing images...")

                import_urls_from_file(url_in)

                print("Completed image processing, see processed_images.csv for output.")
                break
        except Exception as ex:
            url_in = input("Could not find that directory, please try again: \n")


process_urls()
