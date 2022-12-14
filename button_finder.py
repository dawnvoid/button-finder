# Use base conda env for now.

import sys
import urllib.parse
import requests
import requests.exceptions
import bs4
from PIL import ImageFile
# import multiprocessing

FLAG_VERBOSE: bool = False
FLAG_DEBUG: bool = False

def get_image_size(image_url: str) -> int:
    result = None
    try:
        # Gets the filesize in bytes of an image:
        data = requests.get(image_url, stream = True)
    except requests.sessions.InvalidSchema as err:
        print(f'ERROR: Could not determine size of image {image_url} ({err})')
    else:
        if 'Content-length' in data.headers:
            result = data.headers['Content-length']
            result = int(result)
    return result

def get_image_dimensions(image_url: str) -> tuple[int, int]:
    result = None
    # Gets the dimensions in pixels of an image:
    resume_header = {'Range': 'bytes=0-2000000'}    ## the amount of bytes you will downloadj
    data = requests.get(image_url, stream = True, headers = resume_header).content

    p = ImageFile.Parser()
    p.feed(data)    ## feed the data to image parser to get photo info from data headers
    if p.image:
        result = p.image.size
    return result

def get_root_url(url: str):
    domain = urllib.parse.urlparse(url).netloc
    root_url = 'https://' + domain
    return root_url

def get_parent_url(url: str):
    while len(url) > 0:
        if url[-1] == '/':
            break
        url = url[:-1]
    return url

def endswith_any(url: str, extensions: list[str]):
    for extension in extensions:
        if url.endswith(extension):
            return True
    return False

def has_extension(url: str):
    while len(url) > 0:
        if url[-1] == '/':
            return False
        elif url[-1] == '.':
            return True
        url = url[:-1]
    return False

def find_links_in_js(js_contents: str) -> list[str]:
    results = []
    # if FLAG_VERBOSE:
        # print(js_contents)
    return results

def is_button(url: str):
    image_size = get_image_size(url)
    if image_size is None:
        # Image size is unknown
        return False
    elif image_size >= 500000: # < 5kb is reasonable right?
        # Image is too big
        return False
    image_dimensions = get_image_dimensions(url)
    if image_dimensions == (88, 31):
        return True
    return False

def process_page(url: str):
    root_url = get_root_url(url)

    try:
        response = requests.get(url)

        # Raise error if status != 200 (OK):
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        print(f'ERROR: HTTP error occurred ({http_error})')
        # Don't do anything lol.
        pass
    except Exception as exception:
        print(f'ERROR: Other exception occurred ({exception})')
    else:
        # print(response.text)
        # print(response.content) # Gets raw bytes.

        # file_name = url
        # file_name = file_name.replace('https://', '')
        # file_name = file_name.replace('http://', '')
        # file_name = file_name.replace('/', '.')
        # file_path = 'buttons/' + file_name
        # with open(file_path, "wb") as binary_file:
        #     binary_file.write(response.content)

        # if url.endswith('.js'):
        #     print(f'{url} is a javascript file')

        #     return [], [], []

        html = response.text
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        links = []
        link_tags = soup.find_all('a')
        for link_tag in link_tags:
            if not link_tag.has_attr('href'):
                continue
            href: str = link_tag['href'].strip()
            # if href.startswith('https://'):
            #     links.append(href)
            # elif href.startswith('http://'):
            #     links.append(href)
            # elif href.startswith('/'):
            #     href = root_url + href
            #     links.append(href)
            # else:
            #     # Get parent folder path:
            #     parent = get_parent_url(url)
            #     # href = url + href
            #     href = parent + href
            #     links.append(href)
            href = urllib.parse.urljoin(url, href)
            links.append(href)
        
        images = []
        image_tags = soup.find_all('img')
        for image_tag in image_tags:
            if not image_tag.has_attr('src'):
                continue
            src: str = image_tag['src'].strip()
            # if src.startswith('https://'):
            #     links.append(src)
            # elif src.startswith('http://'):
            #     links.append(src)
            # elif src.startswith('/'):
            #     src = root_url + src
            #     images.append(src)
            # else:
            #     src = url + src
            #     images.append(src)
            src = urllib.parse.urljoin(url, src)
            images.append(src)
        
        scripts = []
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            # The script could be in an src attribute or inside the tag itself.
            # js = script_tag.text.strip()
            src = ''
            if script_tag.has_attr('src'):
                src = script_tag['src'].strip()
            if src == '':
                continue
            # elif src.startswith('https://'):
            #     scripts.append(src)
            # elif src.startswith('http://'):
            #     scripts.append(src)
            # elif src.startswith('/'):
            #     src = root_url + src
            #     scripts.append(src)
            # else:
            #     src = url + src
            #     scripts.append(src)
            src = urllib.parse.urljoin(url, src)
            scripts.append(src)
        
        embed_tags = soup.find_all('embed')
        for embed_tag in embed_tags:
            if not embed_tag.has_attr('src'):
                continue
            src = embed_tag['src']
            src = urllib.parse.urljoin(url, src)
            links.append(src)
        
        object_tags = soup.find_all('object')
        for object_tag in object_tags:
            if not object_tag.has_attr('data'):
                continue
            data = object_tag['data']
            data = urllib.parse.urljoin(url, data)
            links.append(data)
        
        iframe_tags = soup.find_all('iframe')
        for iframe_tag in iframe_tags:
            if not iframe_tag.has_attr('src'):
                continue
            src = iframe_tag['src']
            src = urllib.parse.urljoin(url, src)
            links.append(src)

            
                    
            # print(f'{script_tag} {s1 = } {s2 = }')

        return links, images, scripts
    return [], [], []

def process_image(url: str):
    pass

def process_site(url: str):
    if not url.endswith('/'):
        url = url + '/'
    root_url = get_root_url(url)

    frontier = [url]
    checked_pages = []

    total_links: list[str] = []
    total_images: list[str] = []
    total_scripts: list[str] = []
    total_buttons: list[str] = []

    while len(frontier) > 0:
        # page = frontier.pop()
        current_url = frontier.pop(0)

        if current_url in checked_pages:
            continue

        # current_url = urllib.parse.urljoin('https://', current_url)
        checked_pages.append(current_url)

        # print(f'Checking {page}... {len(checked_pages)}/{len(frontier) + len(checked_pages)}')
        print(f'Checking {current_url}...')

        if FLAG_DEBUG:
            print('\tFrontier:')
            for item in frontier:
                print(f'\t{item}')
            print()
            print('\tChecked pages:')
            for item in checked_pages:
                print(f'\t{item}')
            print()
        
        if endswith_any(current_url, ['.png', '.jpg', 'jpeg', '.gif', '.bmp', '.tiff', '.webp']):
            # This is probably an image file.
            process_image(current_url)
        elif endswith_any(current_url, ['.html', '.htm', '.com', '.org', '.net']) or not has_extension(current_url):
            # This is probably an html file.
            try:
                links, images, scripts = process_page(current_url)
            except requests.exceptions.HTTPError as http_error:
                print(f'ERROR: HTTP error occurred ({http_error})')
            # except Exception as exception:
                # print(f'ERROR: Other exception occurred ({exception})')
            else:
                for link in links:
                    if not link in total_links:
                        total_links.append(link)
                for image in images:
                    if not image in total_images:
                        total_images.append(image)
                for script in scripts:
                    if not script in total_scripts:
                        total_scripts.append(script)

                if FLAG_VERBOSE:
                    print('\tLinks:')
                    if len(links) == 0:
                        print('\tNone')
                    else:
                        for link in links:
                            print(f'\t{link}')
                    print()

                    print('\tImages:')
                    if len(images) == 0:
                        print('\tNone')
                    else:
                        for image in images:
                            print(f'\t{image}')
                    print()

                    print('\tScripts:')
                    if len(scripts) == 0:
                        print('\tNone')
                    else:
                        for script in scripts:
                            print(f'\t{script}')
                    print()

                # Add pages to the frontier.
                for link in links:
                    # If the link isn't an html page, ignore it.
                    # if not (link.endswith('.html') or link.endswith('.htm') or link.endswith('.js')):
                        # continue
                    # If the link is external, ignore it.
                    if not link.startswith(root_url):
                        # print(f'{link} is external')
                        continue
                    # If link was already checked, ignore it.
                    elif link in checked_pages:
                        # print(f'{link} was already visited')
                        continue
                    frontier.append(link)

                # TODO: Do this in parallel when there's a lot of images, it's too slow.
                buttons = []
                for image in images:
                    if is_button(image):
                        buttons.append(image)
                
                for button in buttons:
                    if not button in total_buttons:
                        total_buttons.append(button)

                if FLAG_VERBOSE:
                    print(f'\tPotential buttons ({len(buttons)}):')
                    for button in buttons:
                        print(f'\t{image}')
                
                for script in scripts:
                    response = requests.get(script)
                    js = response.text
                    find_links_in_js(js)

    print('Done!')
    print()
    
    if FLAG_VERBOSE:
        print(f'Links ({len(total_links)}):')
        for link in total_links:
            print(link)
        print()
        print(f'Images ({len(total_images)}):')
        for image in total_images:
            print(image)
        print()
        print(f'Scripts ({len(total_scripts)}):')
        for script in total_scripts:
            print(script)
        print()

    print(f'Valid pages ({len(checked_pages)}):')
    for checked_page in checked_pages:
        print(checked_page)
    print()

    print(f'Possible buttons ({len(total_buttons)}):')
    for button in total_buttons:
        print(f'{button}')
    print()


url = 'https://dawnvoid.neocities.org'
# url = 'https://dawnvoid.neocities.org/home.html'
# url = 'https://dawnvoid.neocities.org/page/media/media.html'
# url = 'https://dawnvoid.neocities.org/page/buttons/buttons.html'
# url = 'https://koyo.neocities.org/koy19/home.html'
# url = 'https://fauux.neocities.org'
# url = 'https://scarbyte.com'
# url = 'https://kry.pt'
# url = 'https://hosma.neocities.org'
# url = 'https://google.com'
# url = 'https://wikipedia.org/'
# url = 'https://dawnvoid.neocities.org/assets/angel.gif'
# url = 'https://arandomsite.neocities.org'
# url = 'http://127.0.0.1:5500/tests/test.html' # Tests don't work right now, won't connect to localhost :/

if len(sys.argv) > 1:
    url = sys.argv[1]
process_site(url)

# response = requests.get(url)
# soup = bs4.BeautifulSoup(response.content, 'html.parser')
# script_tags = soup.find_all('script')
# for script_tag in script_tags:
#     # The script could be in an src attribute or inside the tag itself.
#     js = script_tag.text.strip()
#     if js == '':
#         if script_tag.has_attr('src'):
#             src = script_tag['src']
#             try
#     print(f'{script_tag} {s1 = } {s2 = }')


# https?:\/\/|\/?[A-Za-z0-9\.\-\_]+\.[A-Za-z0-9\.\-\_]+
# ["'](https:\/\/[A-Za-z0-9\.\-\_\/]+\.[A-Za-z0-9\.\-\_\/]+\.[A-Za-z0-9]+)['"]

# response = requests.get(url)
# print(response.text)
# soup = bs4.BeautifulSoup(response.content, 'html.parser')
# print(soup.find_all('a'))