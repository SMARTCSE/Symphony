import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
import pandas as pd

def abstract_cleaner(abstract):
    """Converts all the sup and sub script when passing the abstract block as html"""
    conversion_tags_sub = BeautifulSoup(str(abstract), 'html.parser').find_all('sub')
    conversion_tags_sup = BeautifulSoup(str(abstract), 'html.parser').find_all('sup')
    abstract_text = str(abstract).replace('<.', '< @@dot@@')
    for tag in conversion_tags_sub:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    for tag in conversion_tags_sup:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    abstract_text = sup_sub_encode(abstract_text)
    abstract_text = BeautifulSoup(abstract_text, 'html.parser').text
    abstract_text = sup_sub_decode(abstract_text)
    abstract_text = re.sub('\\s+', ' ', abstract_text)
    text = re.sub('([A-Za-z])(\\s+)?(:|\\,|\\.)', r'\1\3', abstract_text)
    text = re.sub('(:|\\,|\\.)([A-Za-z])', r'\1 \2', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(</su(p|b)>)', r'\3\1\4\5', text)
    text = re.sub('(<su(p|b)>)(\\w+)(\\s+)(</su(p|b)>)', r'\1\3\5\4', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(\\s+)(</su(p|b)>)', r'\3\1\4\6\5', text)
    abstract_text = re.sub('\\s+', ' ', text)
    abstract_text = abstract_text.replace('< @@dot@@', '<.')
    return abstract_text.strip()

def sup_sub_encode(html):
    """Encodes superscript and subscript tags"""
    encoded_html = html.replace('<sup>', 's#p').replace('</sup>', 'p#s').replace('<sub>', 's#b').replace('</sub>',
                                                                                                         'b#s') \
        .replace('<Sup>', 's#p').replace('</Sup>', 'p#s').replace('<Sub>', 's#b').replace('</Sub>', 'b#s')
    return encoded_html


def sup_sub_decode(html):
    """Decodes superscript and subscript tags"""
    decoded_html = html.replace('s#p', '<sup>').replace('p#s', '</sup>').replace('s#b', '<sub>').replace('b#s',
                                                                                                         '</sub>')
    return decoded_html

if __name__ == '__main__':
    all_data = []
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Cookie': '_gcl_au=1.1.564658388.1720501694; _gid=GA1.2.693927908.1720501697; _clck=17hqd72%7C2%7Cfnb%7C0%7C1651; _hjSessionUser_2698532=eyJpZCI6IjhlODYzNmYwLWZlZjUtNTgwNC1hMzNjLThkOWQwMjllMmQ3MCIsImNyZWF0ZWQiOjE3MjA1MDE2OTc2MTgsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_2698532=eyJpZCI6IjRjYTU1MDU3LTZmNjItNGQyZS04OTkxLTBmMjIwOWZhYWJlMiIsImMiOjE3MjA1MDE2OTc2MjAsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _fbp=fb.1.1720501698075.927248504664451367; _ga_1VL8M2RE06=GS1.1.1720501693.1.1.1720501758.58.0.0; _ga=GA1.2.1192009283.1720501694; _clsk=4bdo5b%7C1720502390456%7C5%7C1%7Cw.clarity.ms%2Fcollect',
        'Priority': 'u=0, i',
        'Referer': 'https://symphonylimited.com/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    main_url = 'https://symphonyventicool.com/'
    url = 'https://symphonyventicool.com/project.php'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find('div', class_='row')
    content = data.find_all('div', class_='project-one__arrow')
    for links in content:
        link = links.find('a')['href']
        data_link = 'https://symphonyventicool.com/' + link
        data_link_response = requests.get(data_link, headers=header)
        data_soup = BeautifulSoup(data_link_response.text, 'html.parser')
        Data = data_soup.find('div', class_='page-header__inner').find('h1')
        Data_title = abstract_cleaner(Data)
        abstract = data_soup.find('div', class_='project-details__right')
        abstracts = abstract_cleaner(abstract)
        all_dict = {'TITLE': Data_title, 'URL': data_link, 'Success_Abstract': abstracts}
        all_data.append(all_dict)
        df = pd.DataFrame(all_data)
        df.to_csv('Symphony_output.csv', index=False)
        print(abstracts)