from pupa.scrape import Scraper
from pupa.scrape import Disclosure
from pupa.scrape.popolo import Organization

from lxml import etree
from lxml.html import HTMLParser

from datetime import datetime


class ArizonaDisclosureScraper(Scraper):

    def scrape_super_pacs(self):

        def reformat_date(datestring):
            dt = datetime.strptime(datestring, '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')

        def find_the_table(html_document):
            return html_document.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]

        def separate_name_and_address(cell):
            name = cell.text
            address = ', '.join([br.tail for br in cell.xpath('br')])
            return name, address

        def scrape_table(table_element):
            scraped_rows = []
            for row in table_element.xpath('tr'):
                _data = {}
                columns = row.xpath('td')
                if len(columns) == 5:
                    _data['org_id'] = columns[0].text_content()
                    _name, _address = separate_name_and_address(columns[1])
                    _data['org_name'] = _name
                    _data['org_address'] = _address
                    _data['org_phone'] = columns[2].text_content()
                    _data['org_begin_date'] = reformat_date(columns[3].text_content())
                    _data['org_end_date'] = reformat_date(columns[4].text_content())
                    scraped_rows.append(_data)
            return scraped_rows

        PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"

        tmp, resp = self.urlretrieve(PAC_LIST_URL)

        html_document = etree.fromstring(resp.content, parser=HTMLParser())

        target_table = find_the_table(html_document)

        results = scrape_table(target_table)

        for result in results:

            _org = Organization(
                name=result['org_name'],
                classification='political action committee',
                founding_date=result['org_begin_date'],
                dissolution_date=result['org_end_date']
            )

            _org.add_identifier(
                identifier=result['org_id'],
                scheme='urn:az-state:committee'
            )

            _org.add_contact_detail(
                type='address',
                value=result['org_address']
            )

            _org.add_contact_detail(
                type='voice',
                value=result['org_phone']
            )

            _org.add_source(url=PAC_LIST_URL)

            _org.source_identified = True

            yield _org

    def scrape(self):
        yield from self.scrape_super_pacs()
