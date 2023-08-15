import re
import httpx
from scrapy import Selector


def htmlTagClean(html):
    cleaner = re.compile('<.*?>')
    return cleaner.sub('', html)


class FacebookParser(object):
    """Facebook public post parser."""
    def __init__(self) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'viewport-width': 1466
        }
    
    def parse_html(self, html) -> dict[str, str]:
        soup = Selector(text=html)
        title = soup.xpath('//*[@id="facebook"]/head/title')
        meta = soup.xpath('//*[@id="facebook"]/head/meta')
        description = ""
        for i in meta:
            for key in i.attrib.keys():
                if key == "name":
                    if i.attrib[key] == "description":
                        description = i.attrib["content"]
        return {
            "author": htmlTagClean(title.extract()[0]).split(" - ")[0],
            "title": htmlTagClean(title.extract()[0]).split(" - ")[1],
            "description": description
        }


    async def parse(self, url) -> dict[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return self.parse_html(html=response.text)