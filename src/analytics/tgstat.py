"""Module for parsing Telegram channel category using tgstat.ru"""
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

def get_request(url: str, headers: dict[str, str], retry_count: int = 3) -> str:
    """
    Function to make a GET request to the given URL.

    Args:
        url (str): URL to make a GET request

    Returns:
        str: response text
    """
    if retry_count == 0:
        return ""
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        # with open("/app/sessions/tgstat", "w") as f:
        #     f.write(response.text)
        return response.text
    except requests.exceptions.RequestException:
        return get_request(url, headers, retry_count - 1)

def get_channel_category_tgstat(channel_username: str) -> str | None:
    """
    Function to get the category of the given Telegram channel using tgstat.ru.

    Args:
        channel_username (str): username of the channel

    Returns:
        str: category of the channel
    """
    url = f'https://tgstat.ru/ru/channel/@{channel_username}'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'cookie': 'cookie: tgstat_sirk=gqsfj6vfp4j8ckhfipka1pdi63; tgstat_idrk=0434d3a489f997bd01130a9dc48fe27f40526241bdeb8694a8357dbcbcad21d0a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22tgstat_idrk%22%3Bi%3A1%3Bs%3A52%3A%22%5B4317046%2C%22pcSFU6ocT73apak4JTeXZmX-E_IFiBIv%22%2C2592000%5D%22%3B%7D; _tgstat_csrk=605e9648cd79f0c2ae845e5c6b7e98d2e526f1bbfd1c6e467f19dc0361ff912aa%3A2%3A%7Bi%3A0%3Bs%3A12%3A%22_tgstat_csrk%22%3Bi%3A1%3Bs%3A32%3A%22Kwtf0Jr1shrghdZNID-9nez7nKsS_vqJ%22%3B%7D; tgstat_settings=5e815a3abb1a3a16da63fe270615d2fa16f010829ce07e95b4fa539a2b23b564a%3A2%3A%7Bi%3A0%3Bs%3A15%3A%22tgstat_settings%22%3Bi%3A1%3Bs%3A19%3A%22%7B%22fp%22%3A%2207v2GeUhnV%22%7D%22%3B%7D'
    }

    response = get_request(url, headers)

    soup = BeautifulSoup(response, 'html.parser')

    query_selector_1 = "body > div > div > div.content.p-0.col > div.container-fluid.px-2.px-md-3 > div:nth-child(2) > div:nth-child(1) > div > div > div.col-12.col-sm-7.col-md-8.col-lg-6 > div.d-none.d-sm-block.d-lg-none.mt-2.mb-n2 > div:nth-child(3) > a"
    query_selector_2 = "body > div > div > div.content.p-0.col > div.container-fluid.px-2.px-md-3 > div:nth-child(1) > div > div > div > div.col-12.col-sm-7.col-md-8.col-lg-6 > div.d-none.d-sm-block.d-lg-none.mt-2.mb-n2 > div:nth-child(3) > a"
    query_selector_3 = ".d-none.d-sm-block.d-lg-none.mt-2.mb-n2 a"
    query_selector_4 = "b + a"

    element = (
        soup.select_one(query_selector_1) or
        soup.select_one(query_selector_2) or
        soup.select_one(query_selector_3) or
        soup.select_one(query_selector_4)
    )

    if element is None:
        return None
    return element.get_text().strip()

# print(get_channel_category_tgstat("durov_russia"))
# print(get_channel_category_tgstat("difhel_b"))
# print(get_channel_category_tgstat("ayugramchat"))
