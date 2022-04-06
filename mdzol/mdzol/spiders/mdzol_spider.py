import scrapy

# xpath valid for mdzol.com:
NEWS_LINK = "//h2[@class='news__title']/a/@href"
NEWS_TEXT = "//h2[@class='news__title']/a/text()"
BAN_LINKS = ['/estilo', 'https:/www.quever']


class MdzolSpider(scrapy.Spider):
    name = 'mdzol'
    start_urls = ['http://mdzol.com/']
    custom_settings = {'FEED_URI': 'mdzol.json',
                       'FEED_FORMAT': 'json',
                       'MEMUSAGE_LIMIT_MB': 1024,
                       'FEED_EXPORT_ENCODING': 'utf-8'}

    open(custom_settings['FEED_URI'], 'w').close()


    def parse(self, response):
        nnews = {}
        nlink = response.xpath(NEWS_LINK).getall()
        ntext = response.xpath(NEWS_TEXT).getall()

        filters = getattr(self, 'filters', None)
        filters = filters.split(',')

        for k, text in enumerate(ntext):
            discard = False

            for ban_startswith in BAN_LINKS:
                if nlink[k].startswith(ban_startswith):
                    discard = True

            if discard: continue

            for filter in filters:
                if text.lower().find(filter) != -1:
                    nnews[k] = {
                        "text": text,
                        "link": nlink[k]
                    }

        yield nnews

