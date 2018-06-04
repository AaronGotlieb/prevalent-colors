# prevalent-colors
Takes a list of URL jpg images, returns a csv of the link, and the top 3 most prevalent colors


LOGIC:
This application works to find the 3 most prevalent pixel colors in an image.

It starts by taking a user input for the directory of the URL text file.

It then batches URL's into groups of 1000, and creates a list.
The URL list could be well into the billions so its best to batch into smaller groups.

The URL batches are then fetched with an asynchronous call via request.
The image fetch is I/O bound, vs the image processing is CPU bound. 
Because we only have one CPU, threading out the image processing would not give us better results. The URL fetch on the other hand, being I/O bound, will benefit greatly from using a multithreaded approach. Thus, we fetch images, and whenever we get responses, we start processing them synchronously.

The image processing takes an image, scales it down to 150x150px, and then iterates over the image array finding the 3 most common pixel colors. 

Shrinking down greatly increases process time - but it does open us up to being inaccurate on our 3 most common read. The speed benefit makes this worthwhile. Otherwise, we could remove the compression for a 100% accurate result. I chose 150x150 as in my tests, it was accurate, and going smaller did not give us that great of a speed up. 

Finally, the result is printed into a CSV file titled: 'processed_images.csv'
The CSV is formatted: URL, first, second, third\n
eg:
https://i.redd.it/ihczg3pmle3z.jpg, #a4ad9c, #afb8a7, #b0b9a8
