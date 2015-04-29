# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .people import MoPersonScraper


class Mo(Jurisdiction):
    division_id = "ocd-division/country:us"
    classification = "government"
    name = "Missouri State Government"
    url = ""
    scrapers = {
        "people": MoPersonScraper,
    }

    def get_organizations(self):
        yield Organization(name=None, classification=None)
