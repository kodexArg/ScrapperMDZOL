import scrapy


# xpath valid for mdzol.com:
NEWS_LINK = "//h2[@class='news__title']/a/@href"
NEWS_TEXT = "//h2[@class='news__title']/a/text()"
NEWS_EPIGRAPH = "//p[starts-with(@class,'epigraph')]/text()"
NEWS_BODY = "//div[@class='modules-container']//p[not(@class)]//text()"
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

        filters = getattr(self, 'filters', None).split(',')

        for k, text in enumerate(ntext):
            discard = False

            for ban_startswith in BAN_LINKS:
                if nlink[k].startswith(ban_startswith):
                    discard = True
            if discard:
                continue

            for filter in filters:
                if text.lower().find(filter) != -1:
                    nnews = {
                        "text": text,
                        "link": nlink[k]
                    }

                    yield response.follow(nlink[k], callback=self.parse_link, cb_kwargs=nnews)


    def parse_link(self, response, **kwargs):
        nnews = kwargs

        epigraph = response.xpath(NEWS_EPIGRAPH).get()
        epigraph = epigraph.replace('\n', '')
        nnews['epigraph'] = epigraph

        # it's not possible to get the paragraph with <p></p>, so the body's div needs parsing:
        body = response.xpath(NEWS_BODY).getall()
        body = ''.join(body) #
        for k, _ in enumerate(body):
            if len(body) > k + 3:
                if body[k] == "." and body[k+1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ":
                    body = body[:k] + ".\n" + body[k + 1:]
        nnews['body'] = body.replace(" "," ").replace("\n\n","\n")

        yield nnews