import urllib2

background_urls = [
    "http://publicdomainarchive.com/wp-content/uploads/2014/12/public-domain-images-free-stock-photos-high-quality-resolution-downloads-public-domain-archive-8-1000x662.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2016/01/public-domain-images-free-stock-photos-002-1000x667.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2015/03/public-domain-images-free-stock-photos-autumn-1000x662.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/12/public-domain-images-free-stock-photos-high-quality-resolution-downloads-public-domain-archive-7-1000x665.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/12/public-domain-images-free-stock-photos-high-quality-resolution-downloads-public-domain-archive-1-1000x667.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/10/public-domain-images-free-stock-photos-high-quality-resolution-downloads-nashville-tennessee-17-1000x666.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/09/public-domain-images-free-stock-photos-Brussels-gallery-Architecture-shopping-1000x666.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/09/public-domain-images-free-stock-photos-beach-sun-Cliff-sea-sand-1000x666.jpg",
    "http://publicdomainarchive.com/wp-content/uploads/2014/06/public-domain-images-free-stock-photos-high-quality-resolution-downloads-unsplash0073-1000x666.jpg"
]

def download_background(url, file_name):

    request_headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "http://thewebsite.com",
    "Connection": "keep-alive" 
    }

    request = urllib2.Request(url, headers=request_headers)
    u = urllib2.urlopen(request)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + "\b" * (len(status) + 1)
        print status,

    f.close()