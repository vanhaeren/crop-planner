from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from agrosemens.items import AgrosemensItem
import re


class AgrosemensSpider(CrawlSpider):
    name = 'www.agrosemens.com'
    allowed_domains = ['www.agrosemens.com']
    start_urls = ['http://www.agrosemens.com']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@id="categories_block_left"]//li/a'), callback='parse_item',
             follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[@class="product_img_link"]'), callback='parse_item_detail',
             follow=True),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        pass

    def parse_item_detail(self, response):
        item = AgrosemensItem()
        variety = response.xpath('//div[@id="idTab1"]//text()').re(r'\w.*\w')[0]
        # Category = first variety word
        item['href'] = response.url
        item['category'] = variety.split(' ')[0]
        item['variety'] = variety
        item['taxon'] = response.xpath('//div[@id="idTab1"]//text()').re(r'\w.*\w')[1]
        sections = response.xpath('//div[@id="idTab1"]//span[contains(@style,"color: #993300")]//text()').re(r'\w.*\w')
        fields = response.xpath('//div[@id="idTab1"]//span[contains(@style,"font-size: 10pt")]/strong/text()').re(
            '\w.*\w')
        details = response.xpath('//div[@id="idTab1"]//text()').re('\w.*\w')
        # We want all seed details in a structure json divided in section and fields. We can't map this directly in
        # mysql since these can vary
        try:
            # Strip Taxon.We have this already
            all_details = re.match('.*?Descriptif(.*)', '|'.join(details)).group(1)
            self.logger.info('Debug sections = %s', sections)
            self.logger.info('Debug re = %s', '|'.join(sections[sections.index("Descriptif"):]))
            # split into sections
            details_by_section = re.compile('|'.join(sections[sections.index("Descriptif"):])).split(all_details)
            self.logger.info('Debug details by section = %s', details_by_section)
            self.logger.info('Debug fields = %s', fields)
            description = {}
            fieldmatcher = {'plantingDistance' : ['densité\s*:|distance.*?:', '\d{1,2}\s*x\s*\d{1,2}'],
                            'grainesInGram': ['.*\sde\sgraines/g','\d+'],
                            'dose' : ['[D-d]ose|quantité.*:','\d{1,4}.*?\s*/(?<=hect)are|(?<=h)a|m2'],
                            'sowingPlanting' : ['semis\set\splantation','.*'],
                            'sowingOpenAir' : ['(semis\sen\s)?plein champ','.*'] ,
                            'sowingGreenhouse': ['abri','.*'],
                            'averageSeedWeight' : ['PMG','\d+,?\.?\d*'],
                            'soilPreparation' : ['Préparation du sol','.*'],
                            'plantingDepth': ['Profondeur','\d+'],
                        'plantingPeriod' : ['Semis et plantation','.*'],
                        'harvestPeriod' : ['Récolte','.*'],
                        'germinationPeriod' : ['Levée','.*'],
                        'germinationCapacity' : ['Faculté germinative','.*'],
                        'natrium' : ['N','\d+'],
                        'phosphor' : ['P','\d+'],
                        'kalium' : ['K','\d+'],
                        'furtilizerNeed' : ['Apport','.*t/ha'],
                        'yield' : ['Rendement','.*t/ha'],
            }
            for i, section in enumerate(sections[sections.index("Descriptif"):]):
                description[sanitize_key(section)] = {}
                for field in fields:
                    # split section into fields
                    field_content = re.match(r'.*?\|' + field + '\|(.*?)\|', details_by_section[i]).group(1)
                    self.logger.info('Debug detail split by %s = %s', field, field_content)
                    if field_content :
                       description[sanitize_key(section)][sanitize_key(field)] += field_content
                else:
                    key = 'Descriptif'
                    for line in details_by_section[i].split('|'):
                        try:
                          (key,value) = line.split(':',1)
                        except ValueError:
                          value = line
                        try:
                            description[sanitize_key(section)][sanitize_key(key)] += value + ' '
                        except KeyError:
                            description[sanitize_key(section)][sanitize_key(key)] = value

            item['description'] = description
            return item
        except AttributeError:
            pass

def sanitize_key(keyname):
    return re.sub('\.+|\$+','',keyname)

