from pupa.scrape import Scraper
from pupa.scrape import Disclosure
from pupa.scrape.popolo import Organization
from lxml import etree
from lxml.html import HTMLParser
import scrapelib
#from datetime import datetime

class VirginiaDisclosureScraper(Scraper):

    def scrape_committees(self):
        SEARCH_COMMITTEES_URL="http://cfreports.sbe.virginia.gov/"
        my_scraper = scrapelib.Scraper()
        _, resp = my_scraper.urlretrieve(SEARCH_COMMITTEES_URL)
        d = etree.fromstring(resp.content, parser=HTMLParser())
        number_of_result_pages=int(d.xpath('//span[@id="PagingTotalPages"]/text()')[0])
        number_of_results=int(d.xpath('//span[@id="PagingTotalRecords"]/text()')[0])

        scraped_rows = []
        for index in range(number_of_result_pages):
        #for index in range(2):
            _, resp = my_scraper.urlretrieve(SEARCH_COMMITTEES_URL+
                                             '?page='+str(index+1))
            d = etree.fromstring(resp.content, parser=HTMLParser())
            target_table = d.xpath('//table/tbody')[0]
            for row in target_table.xpath('tr'):
                columns = row.xpath('td')
                name = columns[0].text_content().strip()
                candidate = columns[1].text_content().strip()
                committee_type = columns[2].text_content().strip()
                anchors = columns[3].xpath('a')
                try:
                    reports_link = anchors[0].attrib['href']
                except IndexError:
                    reports_link = None
                if not (name == ""):
                    data_dict = {}
                    data_dict['org_name'] = name
                    data_dict['org_type'] = committee_type
                    if(committee_type == "Candidate Campaign Committee"):
                        data_dict['org_candidate'] = candidate
                    data_dict['org_reports_link'] = reports_link 
                    scraped_rows.append(data_dict)

        assert len(scraped_rows) == number_of_results 

        for result in scraped_rows:
            org = Organization(
                name=result['org_name'],
                classification='political action committee',
            )
            org.add_source(url=SEARCH_COMMITTEES_URL)
            org.source_identified = True
            yield org 

    def scrape(self):
        yield from self.scrape_committees()
