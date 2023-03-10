import re
from typing import Tuple
from bs4 import BeautifulSoup, NavigableString

regex_string_length = '[a-zA-Z]{6,}'


def parse_html(html: str) -> Tuple[str, str]:
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.head.title
    body = soup.find('body')
    # menu in newcomments section above username
    comments_links = body.find_all('span', class_='comhead')
    pagetop = body.find('span', class_='pagetop')  # main menu
    hnmore = body.find_all('span', class_='hnmore')

    if not title:
        title = 'Сервер не предоставил title для этой страницы'
    else:
        title = title.string

    for script in soup(["script", "style", "head"]):
        script.extract()

    for tag in body.find_all(True):
        tagname = tag.name
        text = tag.text.split(' ')
        new_text = []

        if tagname == 'a':

            if tag.attrs.get('class') != None and tag.attrs.get('class')[0] == 'morelink':
                href = tag.attrs.get('href')
                href = href.split('?')[1:][0]
                tag.attrs['href'] = f'?{href}'

            elif tag.parent.attrs.get('class') != None and tag.parent.attrs.get('class')[0] == 'yclinks':
                if not ('github' in tag.attrs['href'] or 'mailto' in tag.attrs['href'] or 'ycombinator' in tag.attrs['href']):
                    tag.attrs['href'] = 'https://news.ycombinator.com/' + \
                        tag.attrs['href']

            else:
                """To replace links in main content"""

                if tag.attrs.get('class') == ['hnpast']:
                    tag.attrs['href'] = f"{tag.attrs['href']}"
                
                if 'hide' in tag.attrs.get('href') or \
                   'item' in tag.attrs.get('href') or \
                   'user' in tag.attrs.get('href') or \
                   'fave' in tag.attrs.get('href') or \
                   'shownew' in tag.attrs.get('href'):
                    tag.attrs['href'] = f"/{tag.attrs['href']}"
                
                if 'showhn' in tag.attrs.get('href'):
                    tag.attrs['href'] = f"https://news.ycombinator.com/{tag.attrs['href']}"

                tag.attrs['_blank'] = True

        if tagname == 'img':
            tag.attrs['src'] = 'https://news.ycombinator.com/' + \
                tag.attrs['src']
        
        if tagname == 'form':
            tag.attrs['action'] = tag.attrs['action'][1:]

        for elem in text:
            s = re.search(regex_string_length, elem)
            if s:
                new_text.append(s.group(0) + '™')
            else:
                new_text.append(elem)

        if tag.string:
            tag.string.replace_with(NavigableString(' '.join(new_text)))

    for reply_btn in body.find_all('div', class_='reply'):
        link = reply_btn.find('a')
        if link:
            link['href'] = 'https://news.ycombinator.com' + link['href']
            link['_blank'] = True

    for comment_link in comments_links:
        for nav in comment_link.find_all('a'):
            if nav and not nav.attrs['href'][0] == '/':
                nav.attrs['href'] = '/' + nav.attrs['href']

    for span in hnmore:
        link = span.find('a')
        link.attrs['href'] = f'/{link.attrs["href"]}'

    if pagetop:
        for link in pagetop.find_all('a'):
            if not link.attrs['href'].startswith('/'):
                link.attrs['href'] = '/' + link.attrs['href']

    return soup.prettify(), title
