from gc import callbacks
import scrapy


# XPATH:
LINKS = "//a[starts-with(@href,'collection/') and (parent::h3|parent::h2)]/@href"
HEADING = "//h1[@class='documentFirstHeading']/text()"
PARAGRAPH = "//div[@class='field-item even']//p[not(@class)]/text()"


class CiaSpider(scrapy.Spider):
    name = 'cia'
    start_urls = ['https://www.cia.gov/readingroom/historical-collections']
    custom_settings = {'FEED_URI': 'cia.json',
                       'FEED_FORMAT': 'json',
                       'MEMUSAGE_LIMIT_MB': 1024,
                       'FEED_EXPORT_ENCODING': 'utf-8',
                       'USER_AGENT':'Learning scrapy please dont put me on jails'
    }
    f = open(custom_settings['FEED_URI'], 'w').close()

    def parse(self, response):
        links = response.xpath(LINKS).getall()


        for link in links:
            yield response.follow(link, callback=self.parse_link, cb_kwargs={'url': response.urljoin(link)})
    

    def parse_link(self, response, **kwargs):
        link = kwargs['url']
        title = response.xpath(HEADING).get()
        paragraph = response.xpath(PARAGRAPH).getall()
        paragraph = '\n'.join(map(str,paragraph))

        yield {
            'url': link,
            'title': title,
            'body': paragraph
        }