from pupa.scrape import Scraper
from pupa.scrape import Person
import lxml.html

class MoPersonScraper(Scraper):

    def scrape(self):
        url = 'http://www.mec.mo.gov/EthicsWeb/CampaignFinance/CF11_SearchComm.aspx'

        
        for letter in ['e', 'i', 'o', 'u', 'y', 'a']:

            print("Searching '{}'".format(letter))
            initial = self.get(url).text
            parsed = lxml.html.fromstring(initial)        

            page_n = 0

            data = get_input_data(parsed, first_time=True)
            data['ctl00$ContentPlaceHolder$txtCandLast'] = letter
            
            while True:
                page_n += 1
            
                print("Page: {}".format(page_n))
            
                r = self.post(url, data=data, cookies=dict(PageIndex=str(1)))
                    
                output = lxml.html.fromstring(r.text)
            
                seeks = output.xpath('//*[@id="ctl00_ContentPlaceHolder_grvSearch"]/tr[2]/td[3]')
                if len(seeks):
                    print(seeks[0].text_content())
                            
                if not output.xpath("//*[@id='ctl00_ContentPlaceHolder_grvSearch_ctl28_lbtnNextPage']"):
                    print(output.xpath("//*[@id='ctl00_ContentPlaceHolder_grvSearch_ctl28_lbtnNextPage']"))
                    break
            
                data = get_input_data(output)
                        
        
def get_input_data(parsed_xml, first_time=False):
    input_names = [
        '__LASTFOCUS', 
        '__EVENTTARGET', 
        '__EVENTARGUMENT', 
        '__VIEWSTATE', 
        '__SCROLLPOSITIONX', 
        '__SCROLLPOSITIONY', 
        '__EVENTVALIDATION', 
        'ctl00$txtLoginNonIE', 
        'ctl00$ContentPlaceHolder$txtCandLast', 
        'ctl00$ContentPlaceHolder$txtCommName', 
        'ctl00$ContentPlaceHolder$txtMECID', 
        'ctl00$ContentPlaceHolder$ddCommType', 
        'ctl00$ContentPlaceHolder$ddCommStatus',
        ] 
    
    data = {}
    
    for name in input_names:
        values = parsed_xml.xpath("//*[@name='{}']".format(name))
        if len(values):
            data[name] = values[0].value

    if first_time:
        data['ctl00$ContentPlaceHolder$btnSearch'] = 'Search'
        data['ctl00$ContentPlaceHolder$grvSearch$ctl28$lbtnNextPage'] = 'Search'
    else:
        data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$grvSearch$ctl28$lbtnNextPage'
        
    # print(data)
    
    return data
    