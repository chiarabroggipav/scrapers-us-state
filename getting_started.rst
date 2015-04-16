
Setting up your development environ
===================================

1. Clone the state scraper repo from Github

``git clone https://github.com/influence-usa/scrapers-us-state.git``

2. Make a new virtualenv

``mkvirtualenv --python=$(which python3) <name>``

3. Use ``pip`` to install requirements

``pip install -r requirements.txt``

4. If you don't see a folder for the state you're working on, run the
   following:

``(iusa-scrape)$>pupa init arizona     no pupa_settings on path, using defaults     jurisdiction name (e.g. City of Seattle): Arizona     division id (e.g. ocd-division/country:us/state:wa/place:seattle): ocd-division/country:us/state:az     classification (can be: government, legislature, executive, school_system): government     official URL: http://www.az.gov/     create disclosures scraper? [Y/n]: Y     create bills scraper? [y/N]: n     create events scraper? [y/N]: y     create votes scraper? [y/N]: n     create people scraper? [y/N]: y``

...what this did was create a new folder for the state. In this example,
the state was Arizona (``arizona``).

``(iusa-scrape)$>tree     .     ├── ak     │   └── __init__.py     ├── al     │   ├── __init__.py     │   └── people.py     ├── arizona     │   ├── disclosures.py     │   ├── events.py     │   ├── __init__.py     │   └── people.py     ├── md     │   └── __init__.py     ├── README.md     ├── requirements.txt     ├── Untitled.ipynb     └── utils         ├── __init__.py         └── lxmlize.py``

To follow the broader pupa convention, we'll change the directory name
to ``az``:

::

        (iusa-scrape)$>mv arizona az
        (iusa-scrape)$>tree
        tree
        .
        ├── ak
        │   └── __init__.py
        ├── al
        │   ├── __init__.py
        │   └── people.py
        ├── az
        │   ├── disclosures.py
        │   ├── events.py
        │   ├── __init__.py
        │   └── people.py
        ├── md
        │   └── __init__.py
        ├── README.md
        ├── requirements.txt
        ├── Untitled.ipynb
        └── utils
            ├── __init__.py
            └── lxmlize.py

    5 directories, 13 files

Because we told it to in the questions asked above, it also created the
starter code for our scrapers: there's one each for disclosures, events
and people.

Also interesting is the ``__init__.py`` file in our state's directory.
It used the answers to our questions to build a ``Jurisdiction`` object
that represents the state government:

.. code:: python

    class Arizona(Jurisdiction):
        division_id = "ocd-division/country:us/state:az"
        classification = "government"
        name = "Arizona"
        url = "https://az.gov/"
        scrapers = {
            "events": ArizonaEventScraper,
            "people": ArizonaPersonScraper,
            "disclosures": ArizonaDisclosureScraper,
        }

        def get_organizations(self):
            yield Organization(name=None, classification=None)

Version control
===============

This is a good time to add and commit our changes so far.

``terminal (iusa-scrape)$>git add az (iusa-scrape)$>git commit -m "initialized arizona" [master 3e622ef] initialized arizona  4 files changed, 47 insertions(+)  create mode 100644 az/__init__.py  create mode 100644 az/disclosures.py  create mode 100644 az/events.py  create mode 100644 az/people.py``

Where is the data?
==================

Creating global authority organizations
=======================================

Create the Secretary of State
-----------------------------

The ``get_organizations`` method of the ``Jurisdiction`` class lets us
define some global organizations for all of the data that we'll be
scraping from Arizona's sites. For campaign finance disclosures, we'll
have to define the Arizona Secretary of State's Office.

.. code:: python

    def get_organizations(self):                                        

First, initialize using the ``Organization`` class.

``python     secretary_of_state = Organization(                                             name="Office of the Secretary of State, State of Arizona",                 classification="office"                                                )``

Here, we're able to set particular attributes using ``kwargs``. To get a
sense of which attributes you can set at this point, check out the
`source <https://github.com/influence-usa/pupa/blob/disclosures/pupa/scrape/popolo.py#L132-L182>`__.

Now, we can add other attribtues, using the helper methods found on the
``Organization`` class:

.. code:: python

        secretary_of_state.add_contact_detail(                                
            type="voice",                                                     
            value="602-542-4285"                                              
        )                    

        secretary_of_state.add_contact_detail(                                
            type="address",                                                   
            value="1700 W Washington St Fl 7, Phoenix AZ 85007-2808"          
        )                                                                     
        secretary_of_state.add_link(                                          
            url="http://www.azsos.gov/",                                      
            note="Home page"                                                  
        )                                                                     

We should add the organization we've created to the ``Jurisdiction``
object as a semi-private property. This is useful, beacuse the
``Jurisdiction`` object will essentially always be accessible to all of
our scrapers. Whenever we want to refer to the AZ Secretary of State, we
can always access it from ``Arizona`` jurisdiction object.

.. code:: python

        self._secretary_of_state = secretary_of_state                   

Finally, yield the organization we created. This is beacause
``get_organizations`` is actually the first scraper that we'll run each
time we run Arizona scrapers of any kind.

.. code:: python

        yield secretary_of_state                                          

Test what we have so far!
-------------------------

Cool, let's try out what we have so far. From the project root
(``scrapers-us-state``), run the command:

::

    (iusa-scrape)$>pupa update az disclosures --scrape

This will throw a ``ScrapeError`` because we haven't written any of the
main scrapers yet, but before it does we'll see that it creates our
``Jurisdiction`` object, and the ``Organization`` representing the
Arizona Secretary of State.

::

    no pupa_settings on path, using defaults
    az (scrape)
      events: {}
      people: {}
      disclosures: {}
    Not checking sessions...
    13:30:10 INFO pupa: save jurisdiction Arizona as jurisdiction_ocd-jurisdiction-country:us-state:az-government.json
    13:30:10 INFO pupa: save organization Office of the Secretary of State, State of Arizona as organization_1e330580-e20b-11e4-a4f5-e90fe0697b56.json

Starting a new scraper
======================

Now it's time to start writing the real meat and potatoes of our
scraping code.

Locate the source of the data
-----------------------------

Check out the `Big
Board <https://docs.google.com/spreadsheets/d/18-MvVJXg8TkUUNhtBmWoCEPUWEMf7F6-YVV6x7CWrg4/pubhtml>`__
to see which URL you should use to start. Explore the links on that page
until you find the data you're looking for.

For this example, we'll look at the Arizona Super PAC list.

.. code:: python

    PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"
Adding new scrape routines
--------------------------

We're going to add our code to ``az/disclosures.py``.

.. code:: python

    class ArizonaDisclosureScraper(Scraper):
                                               
        def scrape_super_pacs(self):           
            pass                               
                                               
        def scrape(self):                      
            # needs to be implemented          
            yield from self.scrape_super_pacs()

When we're through, the ``pupa`` CLI commands will call the ``scrape``
command. It's good practice to follow this pattern to break down that
command into a series of subroutines, one for each type of data you're
returning. The pupa software actually doesn't care, though, it just
expects a stream of Open Civic Data scrape objects (``Person``,
``Organizaton``, ``Event``, etc).

Developing your scraper
-----------------------

At this point, you might want to move to a REPL (or, even better, to an
IPython notebook) so that you can start figuring out how to obtain the
target data. You'll

In this example, things are fairly straightforward. There's a
``<table>`` element in the middle of the page that has all the
information we need to generate the ``Organization`` objects that we
want.

.. code:: python

    from lxml import etree
    from lxml.html import HTMLParser
    
    import scrapelib
The scraper we'll eventually write is a subclass of
``scrapelib.Scraper()`` (see the ``Scraper`` class in
`pupa/pupa/scrape/base.py <https://github.com/influence-usa/pupa/blob/disclosures/pupa/scrape/base.py>`__),
and working with the parent class will be close enough to reality when
we're undergoing trial and error at first.

.. code:: python

    my_scraper = scrapelib.Scraper()
.. code:: python

    _, resp = my_scraper.urlretrieve(PAC_LIST_URL)
.. code:: python

    resp.content



.. parsed-literal::

    b'\r\n\r\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head id="ctl00_ctl00_PageHead"><title>\r\n\tSuperPAC Committees List\r\n</title>\r\n    \r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="Content-Style-Type" content="text/css" /><meta name="title" content="Arizona Secretary of State" /><meta name="description" content="Secretary of State" /><meta name="originatorJurisdiction" content="Arizona Secretary of State" /><meta name="govType" content="State Government" /><meta name="medium" content="Web page" /><meta name="accessConstraints" content="none" /><link href="/css/apps-style-newazsos.css" rel="stylesheet" type="text/css" media="all" /><link href="/css/SiteMasterStyles.css" rel="stylesheet" type="text/css" media="all" /><link href="App_Themes/defaultTheme/default.css" type="text/css" rel="stylesheet" /></head>\r\n<body id="ctl00_ctl00_mybody">\r\n    <div id="header-wrapper">\r\n    <div id="header-logo-wrapper" style="padding-top:15px;">\r\n\t\t    <a href="http://www.azsos.gov" title="Arizona Secretary of State"><img src="/images/site-logo.png" alt="site logo"  style="float:left;"/></a>\r\n\t\t    <div id="toplinks" style="float:right;">\r\n\t<span style="float:right;"><a href="http://www.azsos.gov/contact" title="Email Us" target="_blank"><img alt="email icon" src="/images/email.png" style="height:32px;padding-top:2px;padding-right:5px;" /></a><a href="https://twitter.com/SecretaryReagan" title="Follow us on Twitter" target="_blank"><img alt="twitter icon" src="/images/twitter.png" style="height:32px;padding-top:2px;padding-right:5px;" /></a><a href="https://www.facebook.com/AZSecretaryofState" title="Follow us on Facebook" target="_blank"><img alt="facebook icon" src="/images/facebook.png" style="height:32px;padding-top:2px;padding-right:5px;" /></a><a href="http://www.youtube.com/user/AZSecState" title="Watch us on YouTube" target="_blank"><img alt="youtube icon" src="/images/youtube.png" style="height:32px;padding-top:2px;" /></a><br /><a href="http://az.gov/" title="Visit the official website of the State of Arizona" target="_blank"><img alt="az.gov logo" src="/images/azdotgov-logo.png" style="height:32px;padding-top:9px;float:right;" class="hide-on-mobile" /></a></span>\r\n\t\t    </div>\r\n    </div>\r\n</div>\t\t\r\n<div id="navigation">\r\n<div id="primary_nav_wrap">\r\n<ul>\r\n\t<li class="current-menu-item"><a href="http://www.azsos.gov/elections">Elections</a>\r\n\t\t<ul>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/elections-calendar-upcoming-events">Elections Calendar &amp; Upcoming Events</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/voting-election">Voting In This Election</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/campaign-finance-reporting">Campaign Finance &amp; Reporting</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/running-office">Running for Office</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/equal/">Sign a Candidate Petition or Give $5 Qualifying Petition</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/information-about-recognized-political-parties">Information about Recognized Political Parties</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/initiative-referendum-and-recall">Initiative, Referendum &amp; Recall</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/requirements-paid-non-resident-circulators">Requirements for Paid &amp; Non-Resident Circulators</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/voter-registration-historical-election-data">Voter Registration &amp; Historical Data</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/arizona-election-laws-publications">Arizona Election Laws &amp; Publications</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/elections/lobbyists">Lobbyists</a></li>\t\t\t\r\n\t\t</ul>\r\n\t</li>\r\n\t<li><a href="http://www.azsos.gov/business">Business</a>\r\n\t\t<ul>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/trade-names-and-trademarks" title="">Trade Names &amp; Trademarks</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/notary-public">Notary Public</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/charities">Veterans Charities Organizations</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/uniform-commercial-code-ucc">Uniform Commercial Code (UCC)</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/partnerships">Partnerships</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/telephonic-seller-registration">Telephonic Seller Registration</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/corporations">Corporations</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/professional-employment-organizations-peo">Professional Employment Organizations (PEO)</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/business/dance-studios">Dance Studios</a></li>\r\n\t\t</ul>\r\n\t</li>\r\n\t<li><a href="http://www.azsos.gov/services">Services</a>\r\n\t\t<ul>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/acp">Address Confidentiality Program</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/authentication-and-apostille">Document Authentication and Apostille</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/advanced-directives">Advanced Directives</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/athlete-agents">Athlete Agents</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/legislative-filings">Legislative Filings</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/public-information">Public Information</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/out-state-landlord-agents-service">Out-of-State Landlord Agents for Service</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/services/no-trespass-registration-and-public-notice">No Trespass Registration &amp; Public Notice</a></li>\r\n\t\t</ul>\r\n\t</li>\r\n\t<li><a href="http://www.azsos.gov/rules">Rules</a>\r\n\t\t<ul>\r\n\t\t\t<li><a href="http://www.azsos.gov/rules/arizona-administrative-code">Arizona Administrative Code</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/rules/arizona-administrative-register">Arizona Administrative Register</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/rules/semiannual-index">Semiannual Index</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/rules/annual-regulatory-agenda">Annual Regulatory Agenda</a></li>\r\n\t\t</ul>\r\n\t</li>\r\n\t<li><a href="http://www.azlibrary.gov">State Library</a>\r\n\t\t\t<ul>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/talkingbooks">Arizona Talking Book Library</a></li>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/sla">State Library of Arizona</a></li>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/azcm">Arizona Capitol Museum</a></li>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/arm">Archives &amp; Records Management</a></li>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/libdev">Library Development</a></li>\r\n\t\t\t<li><a href="http://www.azlibrary.gov/about">About State Library</a></li>\t\t\t\r\n\t\t</ul>\r\n\r\n\t</li>\t\r\n\t<li><a href="http://www.azsos.gov/about-office">About the Office</a>\r\n\t\t<ul>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/about-secretary">About the Secretary</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/secretaries-since-statehood">Secretaries Since Statehood</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/events">Current and Upcoming Events</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/media-center">Media Center</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/great-seal-arizona">State Seal</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/annual-report">Annual Report</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/executive-staff">Executive Staff</a></li>\r\n\t\t\t<li><a href="http://www.azsos.gov/about-office/contact-us">Contact Us</a></li>\r\n\t\t</ul>\r\n\t</li>\r\n\t\r\n</ul>\r\n   \r\n\t\t</div>\r\n\t\t\r\n \r\n\t\t</div>\r\n\r\n    <div class="content_wrapper">\r\n        <div id="main1">\r\n            <div id="main2">\r\n                <form name="aspnetForm" method="post" action="SuperPACList.aspx" id="aspnetForm">\r\n<input type="hidden" name="ctl00_ctl00_ScriptManager1_HiddenField" id="ctl00_ctl00_ScriptManager1_HiddenField" value="" />\r\n<input type="hidden" name="__VIEWSTATEGUID" id="__VIEWSTATEGUID" value="a0bd59a4-0c44-442c-8ab3-7ef3ff064057" />\r\n<input type="hidden" name="__VIEWSTATE" id="\r\n__VIEWSTATE" value="" />\r\n\r\n\r\n<script src="/apps/election/cfs/search/ScriptResource.axd?d=T9M0dbj5_oxRw_kXIz2P_jOlnfSFIc_VkcMQtNnE1TnR-vp9RnQMYjyw0M7C4A1B1r8BHdeqDVH4ccRT_5O4fBb-Vzllgjj1AKNiBBd3hH598oPtAkxNalCgQNb5FOzRy5Cixg2&amp;t=ffffffffec54f2d7" type="text/javascript"></script>\r\n<script type="text/javascript">\r\n//<![CDATA[\r\nif (typeof(Sys) === \'undefined\') throw new Error(\'ASP.NET Ajax client-side framework failed to load.\');\r\n//]]>\r\n</script>\r\n\r\n                    <input type="hidden" name="ctl00$ctl00$ScriptManager1" id="ctl00_ctl00_ScriptManager1" />\r\n                    <div id="right_column">\r\n                        \r\n                    </div>\r\n\r\n                    \r\n                    <div id="content">\r\n                        <table width="100%" cellpadding="0" cellspacing="0" border="0">\r\n                            <tr>\r\n                                <td id="ctl00_ctl00_PageHeadingCell" class="pagetitle">\r\n                                    <script type="text/javascript">document.write(document.title)</script>\r\n                                </td>\r\n                                <td class="pagetitlehelp" id="four">\r\n                                    \r\n                                </td>\r\n                            </tr>\r\n                        </table>\r\n                        <div id="ctl00_ctl00_MainPanel">\r\n\t\r\n                            \r\n    \r\n    \r\n\r\n<table cellpadding="8" class="thinborder">\r\n<tr><th>Filer ID</th><th>Name & Address</th> <th>Phone #</th><th>Begin Date</th><th>End Date</th></tr>\r\n\r\n<tr>\r\n\r\n<td>1066</td>\r\n<td>AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC)<br />345 E PALM LN<br />PHOENIX, AZ 85004 </td>\r\n<td>(602) 264-1774</td>\r\n<td>06/09/2014</td>\r\n<td>06/08/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1354</td>\r\n<td>AFSCME PEOPLE<br />1625 L ST NW<br />WASHINGTON, DC 20036 </td>\r\n<td>(202) 429-1088</td>\r\n<td>04/02/2014</td>\r\n<td>04/01/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200602733</td>\r\n<td>ARIZONA CHAMBER POLITICAL ACTION COMMITTEE<br />3200 N CENTRAL AVE, STE 1125<br />PHOENIX, AZ 85012 </td>\r\n<td>(602) 248-9172</td>\r\n<td>02/14/2014</td>\r\n<td>02/13/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200602848</td>\r\n<td>ARIZONA FAMILIES UNITED FOR STRONG COMMUNITIES- PROJECT OF SEIU COPE<br />3707 N 7TH ST, STE 100<br />PHOENIX, AZ 85014 </td>\r\n<td>(602) 279-8016</td>\r\n<td>07/21/2014</td>\r\n<td>07/20/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>201000081</td>\r\n<td>Arizona List P.A.C.<br />PO BOX 42294<br />TUCSON, AZ 85733 </td>\r\n<td>(520) 327-0520</td>\r\n<td>01/25/2015</td>\r\n<td>01/24/2019</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1100</td>\r\n<td>Arizona Lodging & Tourism Super PAC<br />1240 E MISSOURI AVE<br />PHOENIX, AZ 85014 </td>\r\n<td>(602) 604-0729</td>\r\n<td>05/15/2013</td>\r\n<td>05/14/2015</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1227</td>\r\n<td>Arizona Pipe Trades 469<br />3109 N 24TH ST<br />PHOENIX, AZ 85016 </td>\r\n<td>(602) 626-8805</td>\r\n<td>02/10/2014</td>\r\n<td>02/09/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1065</td>\r\n<td>AZ DENTAL POLITICAL ACTION COMMITTEE<br />3193 N DRINKWATER BLVD<br />SCOTTSDALE, AZ 85251 </td>\r\n<td>(480) 344-5777</td>\r\n<td>12/15/2013</td>\r\n<td>12/14/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1129</td>\r\n<td>AZ MULTIHOUSING ASSN PAC<br />818 N 1ST ST<br />PHOENIX, AZ 85004 </td>\r\n<td>(602) 296-6200</td>\r\n<td>12/05/2013</td>\r\n<td>12/04/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>2109</td>\r\n<td>BNSF Railway Company RAILPAC<br />PO BOX 961039<br />FORT WORTH, TX 76161 </td>\r\n<td>(202) 347-8662</td>\r\n<td>10/16/2014</td>\r\n<td>10/15/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200002272</td>\r\n<td>CWA COMMUNICATIONS WORKERS OF AMERICA /AZ COMMITTEE  ON POLITICAL EDUCATION (COPE)<br />1951 W CAMELBACK RD, STE 335<br />PHOENIX, AZ 85015 </td>\r\n<td>(602) 266-2620</td>\r\n<td>10/10/2013</td>\r\n<td>10/09/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200202405</td>\r\n<td>Enterprise Holdings, Inc. Political Action Committee<br />600 CORPORATE PARK DR<br />SAINT LOUIS, MO 63105 </td>\r\n<td>(314) 512-5000</td>\r\n<td>11/17/2014</td>\r\n<td>11/16/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1140</td>\r\n<td>GREATER PHOENIX CHAMBER OF COMMERCE POLITICAL ACTION COMMITTEE<br />201 N CENTRAL AVE, FL 27<br />PHOENIX, AZ 85004 </td>\r\n<td>(602) 495-6474</td>\r\n<td>12/21/2013</td>\r\n<td>12/20/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1452</td>\r\n<td>HOME BUILDERS ASSN OF CENTRAL AZ POLITICAL ACTION COMMITTEE<br />7740 N 16TH ST, STE 385<br />PHOENIX, AZ 85020 </td>\r\n<td>(602) 274-6545</td>\r\n<td>05/15/2013</td>\r\n<td>05/14/2015</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>201000325</td>\r\n<td>Honeywell International Political Action Committee Arizona-(HIPAC AZ)<br />101 CONSTITUTION AVE. NW, SUITE 500 WEST<br />WASHINGTON, DC 20001 </td>\r\n<td>(202) 662-2644</td>\r\n<td>01/03/2014</td>\r\n<td>01/02/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1233</td>\r\n<td>JPMORGAN CHASE & CO ARIZONA PAC<br />601 PENNSYLVANIA AVE NW, FL 7<br />WASHINGTON, DC 20004 </td>\r\n<td>(202) 585-3750</td>\r\n<td>02/10/2014</td>\r\n<td>02/09/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1663</td>\r\n<td>PARADISE VALLEY FUND FOR CHILDREN IN PUBLIC EDUCATION (PV ED & SUPPORT EMPL ASSN PAC)<br />345 E PALM LN<br />PHOENIX, AZ 85004 </td>\r\n<td>(602) 407-2380</td>\r\n<td>04/03/2014</td>\r\n<td>04/02/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1016</td>\r\n<td>PINNACLE WEST CAPITAL CORPORATION POLITICAL ACTION COMMITTEE<br />C/O BOB EKSTROM, 801 PENNSYLVANIA AVE NW, SUITE 214<br />WASHINGTON, DC 20004 </td>\r\n<td>(202) 293-2655</td>\r\n<td>02/25/2014</td>\r\n<td>02/24/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1155</td>\r\n<td>REALTORS OF AZ PAC (RAPAC)<br />255 E OSBORN RD, STE 200<br />PHOENIX, AZ 85012 </td>\r\n<td>(602) 248-7787</td>\r\n<td>09/23/2013</td>\r\n<td>09/22/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1206</td>\r\n<td>SALT RIVER VALLEY WATER USERS ASSN POLITICAL INVOLVEMENT COMMITTEE<br />CORPORATE TAXES,  ISB336  PO BOX 52025<br />PHOENIX, AZ 85207 </td>\r\n<td>(602) 236-2070</td>\r\n<td>01/07/2014</td>\r\n<td>01/06/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>201200346</td>\r\n<td>The Political Committee of Planned Parenthood Advocates of Arizona<br />5651 N 7TH ST<br />PHOENIX, AZ 85014 </td>\r\n<td>(602) 263-4215</td>\r\n<td>06/09/2014</td>\r\n<td>06/08/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200802906</td>\r\n<td>UNITE HERE TIP CAMPAIGN COMMITTEE<br />275 SEVENTH AVENUE, 11TH FLOOR<br />NEW YORK, NY 10001 </td>\r\n<td>(212) 265-7000</td>\r\n<td>07/16/2013</td>\r\n<td>07/15/2015</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>1797</td>\r\n<td>UNITED FOOD & COMMERCIAL WORKERS ACTIVE BALLOT CLUB (UFCW)<br />1775 K ST NW<br />WASHINGTON, DC 20006 </td>\r\n<td>(202) 223-3111</td>\r\n<td>04/09/2014</td>\r\n<td>04/08/2018</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>2083</td>\r\n<td>UNITED FOOD & COMMERCIAL WORKERS UNION OF AZ LOCAL 99<br />2401 N CENTRAL AVE<br />PHOENIX, AZ 85004 </td>\r\n<td>(602) 626-8805</td>\r\n<td>10/03/2013</td>\r\n<td>10/02/2017</td>\r\n</tr>\r\n\r\n<tr>\r\n\r\n<td>200402535</td>\r\n<td>United Services Automobile Assn Employee PAC<br />9800 FREDERICKSBURG RD<br />SAN ANTONIO, TX 78288 </td>\r\n<td>(210) 498-0736</td>\r\n<td>02/22/2015</td>\r\n<td>02/21/2019</td>\r\n</tr>\r\n\r\n</table>\r\n\r\n    \r\n\r\n\r\n                            \r\n                        \r\n</div>\r\n                        <br />\r\n                        \r\n                        <br />\r\n                    </div>\r\n                \r\n\r\n<script type="text/javascript">\r\n//<![CDATA[\r\n(function() {var fn = function() {$get("ctl00_ctl00_ScriptManager1_HiddenField").value = \'\';Sys.Application.remove_init(fn);};Sys.Application.add_init(fn);})();\r\nSys.Application.setServerId("ctl00_ctl00_ScriptManager1", "ctl00$ctl00$ScriptManager1");\r\n\r\nSys.Application._enableHistoryInScriptManager();\r\nSys.Application.initialize();\r\n//]]>\r\n</script>\r\n</form>\r\n            </div>\r\n        </div>\r\n        <div id="footer" style="clear:both;">\r\n\r\n    <div style="clear:both;"><br /><br /></div>\r\n    \r\n\t\t<a href="http://www.azsos.gov/website-policies" title="Website Policies" style="color: #9B918B;text-decoration: none;text-align: center;font-size: 13px;padding-right: 6px;">Website Policies</a>\r\n\t\t<a href="http://www.azsos.gov/about-office/contact-us" title="Contact Us" style="color: #9B918B;border-left: 1px solid #9B918B;padding-left: 6px;text-decoration: none;text-align: center;font-size: 13px;padding-right: 6px;">Contact Us</a>\t\r\n    <br />\r\n <span style="color: #9B918B;text-decoration: none;text-align: center;font-size: 11px;line-height:2.2em;padding-top:10px;margin-bottom:10px;">\r\n          &copy;<script type="text/javascript">\r\n\r\n                    today = new Date();\r\n                    yr = today.getFullYear();\r\n                    document.write(yr);\r\n\r\n\t\t  </script> \r\n         Arizona Secretary of State, All Rights Reserved</span>\r\n          \r\n</div>\r\n    </div>\r\n</body>\r\n</html>\r\n'



.. code:: python

    d = etree.fromstring(resp.content, parser=HTMLParser())
The easiest thing to do is just look for the table we're interested by
writing an xpath query. The ``<table>``

.. code:: python

    d.xpath('//table')



.. parsed-literal::

    [<Element table at 0x7fc07468e368>, <Element table at 0x7fc07468e3b8>]



Hm, looks like there's more than one, so we're going to have to narrow
our XPath query. Here's where we can cheat: using Chrome/Chromium, we
can right click on the table, and select "Inspect Element" from the
dropdown. This opens Developer Tools and shows us where in the page's
source that object is. Right click on the ``<table>`` tag and select
"Copy XPath". Now paste the results into a text editor. What you'll see
is:

::

    //*[@id="ctl00_ctl00_MainPanel"]/table

Chrome DevTools does its best to find a short-ish query that uniquely
identifies the node you've selected. The results of this query will be
more targeted.

.. code:: python

    d.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')



.. parsed-literal::

    [<Element table at 0x7fc07468e3b8>]



Notice that this is still a list. To access it we'll need to select the
object by indexing with ``[0]``.

We know that the information we need is in this table, and using IPython
we can test out scripts that scrape the data.

.. code:: python

    target_table = d.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]
The ``table`` element can, in turn, be queried with an XPath query. We
can get all of the rows with ``tbody/tr``.

.. code:: python

    rows = target_table.xpath('tr')
    len(rows)



.. parsed-literal::

    26



.. code:: python

    rows[0]



.. parsed-literal::

    <Element tr at 0x7fc07468e728>



.. code:: python

    def find_the_table(html_document):
        return d.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]
To see what the original HTML string of any element looks like, use:

.. code:: python

    etree.tostring(rows[5])



.. parsed-literal::

    b'<tr>&#13;\n&#13;\n<td>201000081</td>&#13;\n<td>Arizona List P.A.C.<br />PO BOX 42294<br />TUCSON, AZ 85733 </td>&#13;\n<td>(520) 327-0520</td>&#13;\n<td>01/25/2015</td>&#13;\n<td>01/24/2019</td>&#13;\n</tr>&#13;\n&#13;\n'



Now we can write functions to query for, and parse each table. It can be
helpful when debugging to break up your scraper's code into small
functions, so that when (not if ;) something goes wrong, it's easier to
tell where and why.

.. code:: python

    def scrape_table_first_draft(table_element):
        scraped_rows = []
        for row in table_element.xpath('tr'):
            _data = {}
            columns = row.xpath('td')
            _data['org_id'] = columns[0].text_content()
            _data['org_name_and_address'] = columns[1].text_content()
            _data['org_phone'] = columns[2].text_content()
            _data['org_begin_date'] = columns[3].text_content()
            _data['org_end_date'] = columns[4].text_content()
            scraped_rows.append(_data)
        return scraped_rows
.. code:: python

    scrape_table_first_draft(target_table)

::


    ---------------------------------------------------------------------------

    IndexError                                Traceback (most recent call last)

    <ipython-input-25-fd2553283391> in <module>()
    ----> 1 scrape_table_first_draft(target_table)
    

    <ipython-input-24-c1bb3e62f865> in scrape_table_first_draft(table_element)
          4         _data = {}
          5         columns = row.xpath('td')
    ----> 6         _data['org_id'] = columns[0].text_content()
          7         _data['org_name_and_address'] = columns[1].text_content()
          8         _data['org_phone'] = columns[2].text_content()


    IndexError: list index out of range


Oops! Let's look at what happened. We got an ``IndexError`` when looking
for item ``0`` in the list ``columns``. Expect to see a lot of these
kinds of errors when writing ``lxml`` scrapers. It usually means that an
XPath query returned an empty list. Let's make use our ``"td"`` query is
working on each row:

.. code:: python

    [row.xpath("td") for row in target_table.xpath('tr')]



.. parsed-literal::

    [[],
     [<Element td at 0x7fc07469f4a8>,
      <Element td at 0x7fc07469f408>,
      <Element td at 0x7fc07469f138>,
      <Element td at 0x7fc07469f958>,
      <Element td at 0x7fc07469f9a8>],
     [<Element td at 0x7fc07469f9f8>,
      <Element td at 0x7fc07469fa48>,
      <Element td at 0x7fc07469fa98>,
      <Element td at 0x7fc07469fae8>,
      <Element td at 0x7fc07469fb38>],
     [<Element td at 0x7fc07469fb88>,
      <Element td at 0x7fc07469fbd8>,
      <Element td at 0x7fc07469fc28>,
      <Element td at 0x7fc07469fc78>,
      <Element td at 0x7fc07469fcc8>],
     [<Element td at 0x7fc07469fd18>,
      <Element td at 0x7fc07469fd68>,
      <Element td at 0x7fc07469fdb8>,
      <Element td at 0x7fc07469fe08>,
      <Element td at 0x7fc07469fe58>],
     [<Element td at 0x7fc07469fea8>,
      <Element td at 0x7fc07469fef8>,
      <Element td at 0x7fc07469ff48>,
      <Element td at 0x7fc07469ff98>,
      <Element td at 0x7fc0746b1048>],
     [<Element td at 0x7fc0746b1098>,
      <Element td at 0x7fc0746b10e8>,
      <Element td at 0x7fc0746b1138>,
      <Element td at 0x7fc0746b1188>,
      <Element td at 0x7fc0746b11d8>],
     [<Element td at 0x7fc0746b1228>,
      <Element td at 0x7fc0746b1278>,
      <Element td at 0x7fc0746b12c8>,
      <Element td at 0x7fc0746b1318>,
      <Element td at 0x7fc0746b1368>],
     [<Element td at 0x7fc0746b13b8>,
      <Element td at 0x7fc0746b1408>,
      <Element td at 0x7fc0746b1458>,
      <Element td at 0x7fc0746b14a8>,
      <Element td at 0x7fc0746b14f8>],
     [<Element td at 0x7fc0746b1548>,
      <Element td at 0x7fc0746b1598>,
      <Element td at 0x7fc0746b15e8>,
      <Element td at 0x7fc0746b1638>,
      <Element td at 0x7fc0746b1688>],
     [<Element td at 0x7fc0746b16d8>,
      <Element td at 0x7fc0746b1728>,
      <Element td at 0x7fc0746b1778>,
      <Element td at 0x7fc0746b17c8>,
      <Element td at 0x7fc0746b1818>],
     [<Element td at 0x7fc0746b1868>,
      <Element td at 0x7fc0746b18b8>,
      <Element td at 0x7fc0746b1908>,
      <Element td at 0x7fc0746b1958>,
      <Element td at 0x7fc0746b19a8>],
     [<Element td at 0x7fc0746b19f8>,
      <Element td at 0x7fc0746b1a48>,
      <Element td at 0x7fc0746b1a98>,
      <Element td at 0x7fc0746b1ae8>,
      <Element td at 0x7fc0746b1b38>],
     [<Element td at 0x7fc0746b1b88>,
      <Element td at 0x7fc0746b1bd8>,
      <Element td at 0x7fc0746b1c28>,
      <Element td at 0x7fc0746b1c78>,
      <Element td at 0x7fc0746b1cc8>],
     [<Element td at 0x7fc0746b1d18>,
      <Element td at 0x7fc0746b1d68>,
      <Element td at 0x7fc0746b1db8>,
      <Element td at 0x7fc0746b1e08>,
      <Element td at 0x7fc0746b1e58>],
     [<Element td at 0x7fc0746b1ea8>,
      <Element td at 0x7fc0746b1ef8>,
      <Element td at 0x7fc0746b1f48>,
      <Element td at 0x7fc0746b1f98>,
      <Element td at 0x7fc0746b2048>],
     [<Element td at 0x7fc0746b2098>,
      <Element td at 0x7fc0746b20e8>,
      <Element td at 0x7fc0746b2138>,
      <Element td at 0x7fc0746b2188>,
      <Element td at 0x7fc0746b21d8>],
     [<Element td at 0x7fc0746b2228>,
      <Element td at 0x7fc0746b2278>,
      <Element td at 0x7fc0746b22c8>,
      <Element td at 0x7fc0746b2318>,
      <Element td at 0x7fc0746b2368>],
     [<Element td at 0x7fc0746b23b8>,
      <Element td at 0x7fc0746b2408>,
      <Element td at 0x7fc0746b2458>,
      <Element td at 0x7fc0746b24a8>,
      <Element td at 0x7fc0746b24f8>],
     [<Element td at 0x7fc0746b2548>,
      <Element td at 0x7fc0746b2598>,
      <Element td at 0x7fc0746b25e8>,
      <Element td at 0x7fc0746b2638>,
      <Element td at 0x7fc0746b2688>],
     [<Element td at 0x7fc0746b26d8>,
      <Element td at 0x7fc0746b2728>,
      <Element td at 0x7fc0746b2778>,
      <Element td at 0x7fc0746b27c8>,
      <Element td at 0x7fc0746b2818>],
     [<Element td at 0x7fc0746b2868>,
      <Element td at 0x7fc0746b28b8>,
      <Element td at 0x7fc0746b2908>,
      <Element td at 0x7fc0746b2958>,
      <Element td at 0x7fc0746b29a8>],
     [<Element td at 0x7fc0746b29f8>,
      <Element td at 0x7fc0746b2a48>,
      <Element td at 0x7fc0746b2a98>,
      <Element td at 0x7fc0746b2ae8>,
      <Element td at 0x7fc0746b2b38>],
     [<Element td at 0x7fc0746b2b88>,
      <Element td at 0x7fc0746b2bd8>,
      <Element td at 0x7fc0746b2c28>,
      <Element td at 0x7fc0746b2c78>,
      <Element td at 0x7fc0746b2cc8>],
     [<Element td at 0x7fc0746b2d18>,
      <Element td at 0x7fc0746b2d68>,
      <Element td at 0x7fc0746b2db8>,
      <Element td at 0x7fc0746b2e08>,
      <Element td at 0x7fc0746b2e58>],
     [<Element td at 0x7fc0746b2ea8>,
      <Element td at 0x7fc0746b2ef8>,
      <Element td at 0x7fc0746b2f48>,
      <Element td at 0x7fc0746b2f98>,
      <Element td at 0x7fc0746b3048>]]



Ah, the first row has no ``td`` elements! Let's look at it again:

.. code:: python

    etree.tostring(target_table.xpath('tr')[0])



.. parsed-literal::

    b'<tr><th>Filer ID</th><th>Name &amp; Address</th> <th>Phone #</th><th>Begin Date</th><th>End Date</th></tr>&#13;\n&#13;\n'



Of course: the first row is a header row, and only contains ``<th>``
tags. (Actually, this is bad HTML. The ``th`` tags should be inside of a
``<thead>`` tag, and ``tr`` tags should be in a separate ``tbody`` tag,
but that's not what was on the page). Let's make sure that there are 5
``td`` tags when parsing a row.

.. code:: python

    def scrape_table_second_draft(table_element):
        scraped_rows = []
        for row in table_element.xpath('tr'):
            _data = {}
            columns = row.xpath('td')
            if len(columns) == 5:
                _data['org_id'] = columns[0].text_content()
                _data['org_name_and_address'] = columns[1].text_content()
                _data['org_phone'] = columns[2].text_content()
                _data['org_begin_date'] = columns[3].text_content()
                _data['org_end_date'] = columns[4].text_content()
                scraped_rows.append(_data)
        return scraped_rows
            
.. code:: python

    result = scrape_table_second_draft(target_table)
.. code:: python

    result



.. parsed-literal::

    [{'org_begin_date': '06/09/2014',
      'org_end_date': '06/08/2018',
      'org_id': '1066',
      'org_name_and_address': 'AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC)345 E PALM LNPHOENIX, AZ 85004 ',
      'org_phone': '(602) 264-1774'},
     {'org_begin_date': '04/02/2014',
      'org_end_date': '04/01/2018',
      'org_id': '1354',
      'org_name_and_address': 'AFSCME PEOPLE1625 L ST NWWASHINGTON, DC 20036 ',
      'org_phone': '(202) 429-1088'},
     {'org_begin_date': '02/14/2014',
      'org_end_date': '02/13/2018',
      'org_id': '200602733',
      'org_name_and_address': 'ARIZONA CHAMBER POLITICAL ACTION COMMITTEE3200 N CENTRAL AVE, STE 1125PHOENIX, AZ 85012 ',
      'org_phone': '(602) 248-9172'},
     {'org_begin_date': '07/21/2014',
      'org_end_date': '07/20/2018',
      'org_id': '200602848',
      'org_name_and_address': 'ARIZONA FAMILIES UNITED FOR STRONG COMMUNITIES- PROJECT OF SEIU COPE3707 N 7TH ST, STE 100PHOENIX, AZ 85014 ',
      'org_phone': '(602) 279-8016'},
     {'org_begin_date': '01/25/2015',
      'org_end_date': '01/24/2019',
      'org_id': '201000081',
      'org_name_and_address': 'Arizona List P.A.C.PO BOX 42294TUCSON, AZ 85733 ',
      'org_phone': '(520) 327-0520'},
     {'org_begin_date': '05/15/2013',
      'org_end_date': '05/14/2015',
      'org_id': '1100',
      'org_name_and_address': 'Arizona Lodging & Tourism Super PAC1240 E MISSOURI AVEPHOENIX, AZ 85014 ',
      'org_phone': '(602) 604-0729'},
     {'org_begin_date': '02/10/2014',
      'org_end_date': '02/09/2018',
      'org_id': '1227',
      'org_name_and_address': 'Arizona Pipe Trades 4693109 N 24TH STPHOENIX, AZ 85016 ',
      'org_phone': '(602) 626-8805'},
     {'org_begin_date': '12/15/2013',
      'org_end_date': '12/14/2017',
      'org_id': '1065',
      'org_name_and_address': 'AZ DENTAL POLITICAL ACTION COMMITTEE3193 N DRINKWATER BLVDSCOTTSDALE, AZ 85251 ',
      'org_phone': '(480) 344-5777'},
     {'org_begin_date': '12/05/2013',
      'org_end_date': '12/04/2017',
      'org_id': '1129',
      'org_name_and_address': 'AZ MULTIHOUSING ASSN PAC818 N 1ST STPHOENIX, AZ 85004 ',
      'org_phone': '(602) 296-6200'},
     {'org_begin_date': '10/16/2014',
      'org_end_date': '10/15/2018',
      'org_id': '2109',
      'org_name_and_address': 'BNSF Railway Company RAILPACPO BOX 961039FORT WORTH, TX 76161 ',
      'org_phone': '(202) 347-8662'},
     {'org_begin_date': '10/10/2013',
      'org_end_date': '10/09/2017',
      'org_id': '200002272',
      'org_name_and_address': 'CWA COMMUNICATIONS WORKERS OF AMERICA /AZ COMMITTEE  ON POLITICAL EDUCATION (COPE)1951 W CAMELBACK RD, STE 335PHOENIX, AZ 85015 ',
      'org_phone': '(602) 266-2620'},
     {'org_begin_date': '11/17/2014',
      'org_end_date': '11/16/2018',
      'org_id': '200202405',
      'org_name_and_address': 'Enterprise Holdings, Inc. Political Action Committee600 CORPORATE PARK DRSAINT LOUIS, MO 63105 ',
      'org_phone': '(314) 512-5000'},
     {'org_begin_date': '12/21/2013',
      'org_end_date': '12/20/2017',
      'org_id': '1140',
      'org_name_and_address': 'GREATER PHOENIX CHAMBER OF COMMERCE POLITICAL ACTION COMMITTEE201 N CENTRAL AVE, FL 27PHOENIX, AZ 85004 ',
      'org_phone': '(602) 495-6474'},
     {'org_begin_date': '05/15/2013',
      'org_end_date': '05/14/2015',
      'org_id': '1452',
      'org_name_and_address': 'HOME BUILDERS ASSN OF CENTRAL AZ POLITICAL ACTION COMMITTEE7740 N 16TH ST, STE 385PHOENIX, AZ 85020 ',
      'org_phone': '(602) 274-6545'},
     {'org_begin_date': '01/03/2014',
      'org_end_date': '01/02/2018',
      'org_id': '201000325',
      'org_name_and_address': 'Honeywell International Political Action Committee Arizona-(HIPAC AZ)101 CONSTITUTION AVE. NW, SUITE 500 WESTWASHINGTON, DC 20001 ',
      'org_phone': '(202) 662-2644'},
     {'org_begin_date': '02/10/2014',
      'org_end_date': '02/09/2018',
      'org_id': '1233',
      'org_name_and_address': 'JPMORGAN CHASE & CO ARIZONA PAC601 PENNSYLVANIA AVE NW, FL 7WASHINGTON, DC 20004 ',
      'org_phone': '(202) 585-3750'},
     {'org_begin_date': '04/03/2014',
      'org_end_date': '04/02/2018',
      'org_id': '1663',
      'org_name_and_address': 'PARADISE VALLEY FUND FOR CHILDREN IN PUBLIC EDUCATION (PV ED & SUPPORT EMPL ASSN PAC)345 E PALM LNPHOENIX, AZ 85004 ',
      'org_phone': '(602) 407-2380'},
     {'org_begin_date': '02/25/2014',
      'org_end_date': '02/24/2018',
      'org_id': '1016',
      'org_name_and_address': 'PINNACLE WEST CAPITAL CORPORATION POLITICAL ACTION COMMITTEEC/O BOB EKSTROM, 801 PENNSYLVANIA AVE NW, SUITE 214WASHINGTON, DC 20004 ',
      'org_phone': '(202) 293-2655'},
     {'org_begin_date': '09/23/2013',
      'org_end_date': '09/22/2017',
      'org_id': '1155',
      'org_name_and_address': 'REALTORS OF AZ PAC (RAPAC)255 E OSBORN RD, STE 200PHOENIX, AZ 85012 ',
      'org_phone': '(602) 248-7787'},
     {'org_begin_date': '01/07/2014',
      'org_end_date': '01/06/2018',
      'org_id': '1206',
      'org_name_and_address': 'SALT RIVER VALLEY WATER USERS ASSN POLITICAL INVOLVEMENT COMMITTEECORPORATE TAXES,  ISB336  PO BOX 52025PHOENIX, AZ 85207 ',
      'org_phone': '(602) 236-2070'},
     {'org_begin_date': '06/09/2014',
      'org_end_date': '06/08/2018',
      'org_id': '201200346',
      'org_name_and_address': 'The Political Committee of Planned Parenthood Advocates of Arizona5651 N 7TH STPHOENIX, AZ 85014 ',
      'org_phone': '(602) 263-4215'},
     {'org_begin_date': '07/16/2013',
      'org_end_date': '07/15/2015',
      'org_id': '200802906',
      'org_name_and_address': 'UNITE HERE TIP CAMPAIGN COMMITTEE275 SEVENTH AVENUE, 11TH FLOORNEW YORK, NY 10001 ',
      'org_phone': '(212) 265-7000'},
     {'org_begin_date': '04/09/2014',
      'org_end_date': '04/08/2018',
      'org_id': '1797',
      'org_name_and_address': 'UNITED FOOD & COMMERCIAL WORKERS ACTIVE BALLOT CLUB (UFCW)1775 K ST NWWASHINGTON, DC 20006 ',
      'org_phone': '(202) 223-3111'},
     {'org_begin_date': '10/03/2013',
      'org_end_date': '10/02/2017',
      'org_id': '2083',
      'org_name_and_address': 'UNITED FOOD & COMMERCIAL WORKERS UNION OF AZ LOCAL 992401 N CENTRAL AVEPHOENIX, AZ 85004 ',
      'org_phone': '(602) 626-8805'},
     {'org_begin_date': '02/22/2015',
      'org_end_date': '02/21/2019',
      'org_id': '200402535',
      'org_name_and_address': 'United Services Automobile Assn Employee PAC9800 FREDERICKSBURG RDSAN ANTONIO, TX 78288 ',
      'org_phone': '(210) 498-0736'}]



Hm, let's see if we can do a better job with that
``org_name_and_address`` field. We're going to want to separate them.

.. code:: python

    rows = target_table.xpath('tr')
    row = rows[7]
.. code:: python

    cell = row.xpath('td')[1]
.. code:: python

    etree.tostring(cell)



.. parsed-literal::

    b'<td>Arizona Pipe Trades 469<br />3109 N 24TH ST<br />PHOENIX, AZ 85016 </td>&#13;\n'



The first part of the cell can be extracted using the ``text`` property.
Unlike ``text_content``, it will only return the text up until the first
``<br/>`` tag.

.. code:: python

    cell.text



.. parsed-literal::

    'Arizona Pipe Trades 469'



We can take advantage of the ``<br />`` elements, by using their
``tail`` properties. This property returns text that follows the
element, stopping before the next element encountered.

.. code:: python

    for br in cell.xpath('br'):
        print('tail: "{}"'.format(br.tail))

.. parsed-literal::

    tail: "3109 N 24TH ST"
    tail: "PHOENIX, AZ 85016 "


.. code:: python

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
                _data['org_begin_date'] = columns[3].text_content()
                _data['org_end_date'] = columns[4].text_content()
                scraped_rows.append(_data)
        return scraped_rows
.. code:: python

    results = scrape_table(target_table)
.. code:: python

    results



.. parsed-literal::

    [{'org_address': '345 E PALM LN, PHOENIX, AZ 85004 ',
      'org_begin_date': '06/09/2014',
      'org_end_date': '06/08/2018',
      'org_id': '1066',
      'org_name': 'AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC)',
      'org_phone': '(602) 264-1774'},
     {'org_address': '1625 L ST NW, WASHINGTON, DC 20036 ',
      'org_begin_date': '04/02/2014',
      'org_end_date': '04/01/2018',
      'org_id': '1354',
      'org_name': 'AFSCME PEOPLE',
      'org_phone': '(202) 429-1088'},
     {'org_address': '3200 N CENTRAL AVE, STE 1125, PHOENIX, AZ 85012 ',
      'org_begin_date': '02/14/2014',
      'org_end_date': '02/13/2018',
      'org_id': '200602733',
      'org_name': 'ARIZONA CHAMBER POLITICAL ACTION COMMITTEE',
      'org_phone': '(602) 248-9172'},
     {'org_address': '3707 N 7TH ST, STE 100, PHOENIX, AZ 85014 ',
      'org_begin_date': '07/21/2014',
      'org_end_date': '07/20/2018',
      'org_id': '200602848',
      'org_name': 'ARIZONA FAMILIES UNITED FOR STRONG COMMUNITIES- PROJECT OF SEIU COPE',
      'org_phone': '(602) 279-8016'},
     {'org_address': 'PO BOX 42294, TUCSON, AZ 85733 ',
      'org_begin_date': '01/25/2015',
      'org_end_date': '01/24/2019',
      'org_id': '201000081',
      'org_name': 'Arizona List P.A.C.',
      'org_phone': '(520) 327-0520'},
     {'org_address': '1240 E MISSOURI AVE, PHOENIX, AZ 85014 ',
      'org_begin_date': '05/15/2013',
      'org_end_date': '05/14/2015',
      'org_id': '1100',
      'org_name': 'Arizona Lodging & Tourism Super PAC',
      'org_phone': '(602) 604-0729'},
     {'org_address': '3109 N 24TH ST, PHOENIX, AZ 85016 ',
      'org_begin_date': '02/10/2014',
      'org_end_date': '02/09/2018',
      'org_id': '1227',
      'org_name': 'Arizona Pipe Trades 469',
      'org_phone': '(602) 626-8805'},
     {'org_address': '3193 N DRINKWATER BLVD, SCOTTSDALE, AZ 85251 ',
      'org_begin_date': '12/15/2013',
      'org_end_date': '12/14/2017',
      'org_id': '1065',
      'org_name': 'AZ DENTAL POLITICAL ACTION COMMITTEE',
      'org_phone': '(480) 344-5777'},
     {'org_address': '818 N 1ST ST, PHOENIX, AZ 85004 ',
      'org_begin_date': '12/05/2013',
      'org_end_date': '12/04/2017',
      'org_id': '1129',
      'org_name': 'AZ MULTIHOUSING ASSN PAC',
      'org_phone': '(602) 296-6200'},
     {'org_address': 'PO BOX 961039, FORT WORTH, TX 76161 ',
      'org_begin_date': '10/16/2014',
      'org_end_date': '10/15/2018',
      'org_id': '2109',
      'org_name': 'BNSF Railway Company RAILPAC',
      'org_phone': '(202) 347-8662'},
     {'org_address': '1951 W CAMELBACK RD, STE 335, PHOENIX, AZ 85015 ',
      'org_begin_date': '10/10/2013',
      'org_end_date': '10/09/2017',
      'org_id': '200002272',
      'org_name': 'CWA COMMUNICATIONS WORKERS OF AMERICA /AZ COMMITTEE  ON POLITICAL EDUCATION (COPE)',
      'org_phone': '(602) 266-2620'},
     {'org_address': '600 CORPORATE PARK DR, SAINT LOUIS, MO 63105 ',
      'org_begin_date': '11/17/2014',
      'org_end_date': '11/16/2018',
      'org_id': '200202405',
      'org_name': 'Enterprise Holdings, Inc. Political Action Committee',
      'org_phone': '(314) 512-5000'},
     {'org_address': '201 N CENTRAL AVE, FL 27, PHOENIX, AZ 85004 ',
      'org_begin_date': '12/21/2013',
      'org_end_date': '12/20/2017',
      'org_id': '1140',
      'org_name': 'GREATER PHOENIX CHAMBER OF COMMERCE POLITICAL ACTION COMMITTEE',
      'org_phone': '(602) 495-6474'},
     {'org_address': '7740 N 16TH ST, STE 385, PHOENIX, AZ 85020 ',
      'org_begin_date': '05/15/2013',
      'org_end_date': '05/14/2015',
      'org_id': '1452',
      'org_name': 'HOME BUILDERS ASSN OF CENTRAL AZ POLITICAL ACTION COMMITTEE',
      'org_phone': '(602) 274-6545'},
     {'org_address': '101 CONSTITUTION AVE. NW, SUITE 500 WEST, WASHINGTON, DC 20001 ',
      'org_begin_date': '01/03/2014',
      'org_end_date': '01/02/2018',
      'org_id': '201000325',
      'org_name': 'Honeywell International Political Action Committee Arizona-(HIPAC AZ)',
      'org_phone': '(202) 662-2644'},
     {'org_address': '601 PENNSYLVANIA AVE NW, FL 7, WASHINGTON, DC 20004 ',
      'org_begin_date': '02/10/2014',
      'org_end_date': '02/09/2018',
      'org_id': '1233',
      'org_name': 'JPMORGAN CHASE & CO ARIZONA PAC',
      'org_phone': '(202) 585-3750'},
     {'org_address': '345 E PALM LN, PHOENIX, AZ 85004 ',
      'org_begin_date': '04/03/2014',
      'org_end_date': '04/02/2018',
      'org_id': '1663',
      'org_name': 'PARADISE VALLEY FUND FOR CHILDREN IN PUBLIC EDUCATION (PV ED & SUPPORT EMPL ASSN PAC)',
      'org_phone': '(602) 407-2380'},
     {'org_address': 'C/O BOB EKSTROM, 801 PENNSYLVANIA AVE NW, SUITE 214, WASHINGTON, DC 20004 ',
      'org_begin_date': '02/25/2014',
      'org_end_date': '02/24/2018',
      'org_id': '1016',
      'org_name': 'PINNACLE WEST CAPITAL CORPORATION POLITICAL ACTION COMMITTEE',
      'org_phone': '(202) 293-2655'},
     {'org_address': '255 E OSBORN RD, STE 200, PHOENIX, AZ 85012 ',
      'org_begin_date': '09/23/2013',
      'org_end_date': '09/22/2017',
      'org_id': '1155',
      'org_name': 'REALTORS OF AZ PAC (RAPAC)',
      'org_phone': '(602) 248-7787'},
     {'org_address': 'CORPORATE TAXES,  ISB336  PO BOX 52025, PHOENIX, AZ 85207 ',
      'org_begin_date': '01/07/2014',
      'org_end_date': '01/06/2018',
      'org_id': '1206',
      'org_name': 'SALT RIVER VALLEY WATER USERS ASSN POLITICAL INVOLVEMENT COMMITTEE',
      'org_phone': '(602) 236-2070'},
     {'org_address': '5651 N 7TH ST, PHOENIX, AZ 85014 ',
      'org_begin_date': '06/09/2014',
      'org_end_date': '06/08/2018',
      'org_id': '201200346',
      'org_name': 'The Political Committee of Planned Parenthood Advocates of Arizona',
      'org_phone': '(602) 263-4215'},
     {'org_address': '275 SEVENTH AVENUE, 11TH FLOOR, NEW YORK, NY 10001 ',
      'org_begin_date': '07/16/2013',
      'org_end_date': '07/15/2015',
      'org_id': '200802906',
      'org_name': 'UNITE HERE TIP CAMPAIGN COMMITTEE',
      'org_phone': '(212) 265-7000'},
     {'org_address': '1775 K ST NW, WASHINGTON, DC 20006 ',
      'org_begin_date': '04/09/2014',
      'org_end_date': '04/08/2018',
      'org_id': '1797',
      'org_name': 'UNITED FOOD & COMMERCIAL WORKERS ACTIVE BALLOT CLUB (UFCW)',
      'org_phone': '(202) 223-3111'},
     {'org_address': '2401 N CENTRAL AVE, PHOENIX, AZ 85004 ',
      'org_begin_date': '10/03/2013',
      'org_end_date': '10/02/2017',
      'org_id': '2083',
      'org_name': 'UNITED FOOD & COMMERCIAL WORKERS UNION OF AZ LOCAL 99',
      'org_phone': '(602) 626-8805'},
     {'org_address': '9800 FREDERICKSBURG RD, SAN ANTONIO, TX 78288 ',
      'org_begin_date': '02/22/2015',
      'org_end_date': '02/21/2019',
      'org_id': '200402535',
      'org_name': 'United Services Automobile Assn Employee PAC',
      'org_phone': '(210) 498-0736'}]



Adding to the DisclosureScraper object
--------------------------------------

After we think that we're able to scrape the data we want, we should add
the code to our scraper object.

.. code:: python

    class ArizonaDisclosureScraper(Scraper):

        def scrape_super_pacs(self):
        
            def find_the_table(html_document):
                return d.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]
        
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
                        _data['org_begin_date'] = columns[3].text_content()
                        _data['org_end_date'] = columns[4].text_content()
                        scraped_rows.append(_data)
                return scraped_rows
                
            PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"
            
            resp = self.urlretrieve(PAC_LIST_URL)
            
            html_document = etree.fromstring(resp, parser=HTMLParser())
            
            target_table = find_the_table(html_document)
            
            results = scrape_the_table(target_table)

        def scrape(self):                      
            # needs to be implemented          
            yield from self.scrape_super_pacs()

Use scraped data to build Open Civic Data objects
-------------------------------------------------

Let's look at how we can use the PAC data we scraped to build an
``Organization`` object.

.. code:: python

    result = results[0]
    
    result



.. parsed-literal::

    {'org_address': '345 E PALM LN, PHOENIX, AZ 85004 ',
     'org_begin_date': '06/09/2014',
     'org_end_date': '06/08/2018',
     'org_id': '1066',
     'org_name': 'AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC)',
     'org_phone': '(602) 264-1774'}



If we import the ``Organization`` scraper model, this becomes very easy:

.. code:: python

    from pupa.scrape.popolo import Organization
.. code:: python

    my_org = Organization(
        name=result['org_name'],
        classification='political action committee',
        founding_date=result['org_begin_date'],
        dissolution_date=result['org_end_date']
    )
That's actually more information than we needed. Only the ``name`` and
``classification`` properties were required.

To add other information, like contact details and identifiers, we can
use special helper functions that come with the ``Organization`` class:

.. code:: python

    my_org.add_identifier(
        identifier=result['org_id'],
        scheme='urn:az-state:committee'
        )
.. code:: python

    my_org.add_contact_detail(
        type='address',
        value=result['org_address']
    )
.. code:: python

    my_org.add_contact_detail(
        type='voice',
        value=result['org_phone']
    )
To see your organization as a ``dict``, use the ``as_dict`` method:

.. code:: python

    my_org.as_dict()



.. parsed-literal::

    {'_id': '0e683e08-e46e-11e4-a4f5-e90fe0697b56',
     'classification': 'political action committee',
     'contact_details': [{'note': '',
       'type': 'address',
       'value': '345 E PALM LN, PHOENIX, AZ 85004 '},
      {'note': '', 'type': 'voice', 'value': '(602) 264-1774'}],
     'dissolution_date': '06/08/2018',
     'extras': {},
     'founding_date': '06/09/2014',
     'identifiers': [{'identifier': '1066', 'scheme': 'urn:az-state:committee'}],
     'image': '',
     'links': [],
     'name': 'AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC)',
     'other_names': [],
     'parent_id': None,
     'source_identified': False,
     'sources': []}



Ah! That reminds me: We have to be sure to do two things to all
``Person`` and ``Organization`` objects returned by our scraper.

First, Make sure ``source_identified`` is ``True``

.. code:: python

    my_org.source_identified = True
Next, make sure you include the source (ie, the URL that you found the
organization at)

.. code:: python

    my_org.add_source(url=PAC_LIST_URL)
Yielding your new objects
-------------------------

Adding the new code to our scraper:

.. code:: python

    class ArizonaDisclosureScraper(Scraper):

        def scrape_super_pacs(self):

            def find_the_table(html_document):
                return d.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]

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
                        _data['org_begin_date'] = columns[3].text_content()
                        _data['org_end_date'] = columns[4].text_content()
                        scraped_rows.append(_data)
                return scraped_rows

            PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"

            _, resp = self.urlretrieve(PAC_LIST_URL)

            html_document = etree.fromstring(resp, parser=HTMLParser())

            target_table = find_the_table(html_document)

            results = scrape_the_table(target_table)
            
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
            # needs to be implemented          
            yield from self.scrape_super_pacs()

Finished!
---------

You don't need to worry about anything after this point. After doing the
hard work of writing your scraper code, you can hand off the rest
(validation, database storage, deduplication) to the ``pupa`` framework.

Running your new scraper
========================

Okay, time to see how well it works! Run:

::

    (iusa-scrape)$>pupa update az disclosures --scrape

Uh oh.

::

        no pupa_settings on path, using defaults
        az (scrape)
          disclosures: {}
        Not checking sessions...
        21:45:21 INFO pupa: save jurisdiction Arizona as jurisdiction_ocd-jurisdiction-country:us-state:az-government.json
        21:45:21 INFO pupa: save organization Office of the Secretary of State, State of Arizona as organization_4b266268-e250-11e4-a4f5-e90fe0697b56.json
        21:45:21 INFO scrapelib: GET - http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx
        Traceback (most recent call last):
          File "/home/blannon/.virtualenvs/iusa-scrape/bin/pupa", line 9, in <module>
            load_entry_point('pupa==0.4.1', 'console_scripts', 'pupa')()
          File "/home/blannon/.virtualenvs/iusa-scrape/src/pupa/pupa/cli/__main__.py", line 71, in main
            subcommands[args.subcommand].handle(args, other)
          File "/home/blannon/.virtualenvs/iusa-scrape/src/pupa/pupa/cli/commands/update.py", line 241, in handle
            report['scrape'] = self.do_scrape(juris, args, scrapers)
          File "/home/blannon/.virtualenvs/iusa-scrape/src/pupa/pupa/cli/commands/update.py", line 123, in do_scrape
            report[scraper_name] = scraper.do_scrape(**scrape_args)
          File "/home/blannon/.virtualenvs/iusa-scrape/src/pupa/pupa/scrape/base.py", line 104, in do_scrape
            for obj in self.scrape(**kwargs) or []:
          File "/home/blannon/dev/ocd/scrapers-us-state/az/disclosures.py", line 78, in scrape
            yield from self.scrape_super_pacs()
          File "/home/blannon/dev/ocd/scrapers-us-state/az/disclosures.py", line 41, in scrape_super_pacs
            html_document = etree.fromstring(resp, parser=HTMLParser())
          File "lxml.etree.pyx", line 3094, in lxml.etree.fromstring (src/lxml/lxml.etree.c:70505)
          File "parser.pxi", line 1827, in lxml.etree._parseMemoryDocument (src/lxml/lxml.etree.c:106328)
        ValueError: can only parse strings

Looks like something's wrong. Let's run it again, except this time we'll
tell ``pupa`` to drop us into ``pdb`` when it fails. If you're not
familiar with ``pdb``, check out @claytron's `excellent
talk <https://speakerdeck.com/claytron/so-you-think-you-can-pdb>`__ from
this year's PyCon.

::

    (iusa-scrape)$>pupa --debug pdb update az disclosures --scrape

Now, when it crashes, we're launched into the Python debugger.

::

    (Pdb) u
    > /home/blannon/dev/ocd/scrapers-us-state/lxml.etree.pyx(3094)lxml.etree.fromstring (src/lxml/lxml.etree.c:70505)()
    (Pdb) u
    > /home/blannon/dev/ocd/scrapers-us-state/az/disclosures.py(41)scrape_super_pacs()
    -> html_document = etree.fromstring(resp, parser=HTMLParser())
    (Pdb) resp
    ('/tmp/tmpy2r8olmk', <Response [200]>)
    (Pdb) l
     36     
     37             PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"
     38     
     39             resp = self.urlretrieve(PAC_LIST_URL)
     40     
     41  ->         html_document = etree.fromstring(resp, parser=HTMLParser())
     42     
     43             target_table = find_the_table(html_document)
     44     
     45             results = scrape_the_table(target_table)
     46     

...ah ha! On line 41, we incorrectly assumed that ``urlretrieve`` would
return an HTML string. Instead, it returned a tuple including the
location of the temporary file and a ``Response`` object. We'll have to
change that line:

.. code:: diff

    diff --git a/az/disclosures.py b/az/disclosures.py
    index 64ebf1b..a10695b 100644
    --- a/az/disclosures.py
    +++ b/az/disclosures.py
    @@ -36,9 +36,9 @@ class ArizonaDisclosureScraper(Scraper):
     
             PAC_LIST_URL = "http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx"
     
    -        resp = self.urlretrieve(PAC_LIST_URL)
    +        tmp, resp = self.urlretrieve(PAC_LIST_URL)
     
    -        html_document = etree.fromstring(resp, parser=HTMLParser())
    +        html_document = etree.fromstring(resp.content, parser=HTMLParser())
     
             target_table = find_the_table(html_document)

Now, let's re-run!

::

    (iusa-scrape)$>pupa --debug pdb update az disclosures --scrape

We'll get another error:

::

    validictory.validator.ValidationError: validation of Organization 46282b8b-e254-11e4-a4f5-e90fe0697b56 failed: Value '06/08/2018' for field '<obj>.dissolution_date' does not match regular expression '(^[0-9]{4})?(-[0-9]{2}){0,2}$'
    > /home/blannon/.virtualenvs/iusa-scrape/src/pupa/pupa/scrape/base.py(191)validate()
    -> self.__class__.__name__, self._id, ve)
    (Pdb) 

This time, ``validictory``, the schema validation library, is telling us
that our dates aren't formatted correctly. Let's go back and fix that,
with a ``reformat_date`` function:

.. code:: diff

    diff --git a/az/disclosures.py b/az/disclosures.py
    index 7d33214..40d585d 100644
    --- a/az/disclosures.py
    +++ b/az/disclosures.py
    @@ -5,11 +5,17 @@ from pupa.scrape.popolo import Organization
     from lxml import etree
     from lxml.html import HTMLParser
     
    +from datetime import datetime
    +
     
     class ArizonaDisclosureScraper(Scraper):
     
         def scrape_super_pacs(self):
     
    +        def reformat_date(datestring):
    +            dt = datetime.strptime(datestring, '%m/%d/%Y')
    +            return dt.strftime('%Y-%m-%d')
    +
             def find_the_table(html_document):
                 return html_document.xpath('//*[@id="ctl00_ctl00_MainPanel"]/table')[0]
     
    @@ -29,8 +35,8 @@ class ArizonaDisclosureScraper(Scraper):
                         _data['org_name'] = _name
                         _data['org_address'] = _address
                         _data['org_phone'] = columns[2].text_content()
    -                    _data['org_begin_date'] = columns[3].text_content()
    -                    _data['org_end_date'] = columns[4].text_content()
    +                    _data['org_begin_date'] = reformat_date(columns[3].text_content())
    +                    _data['org_end_date'] = reformat_date(columns[4].text_content())
                         scraped_rows.append(_data)
                 return scraped_rows

Okay, I got a good feeling about this one:

::

    (iusa-scrape)$>pupa --debug pdb update az disclosures --scrape

Output looks great!

::

    (iusa-scrape)$>pupa --debug pdb update az disclosures --scrape
    no pupa_settings on path, using defaults
    az (scrape)
      disclosures: {}
    Not checking sessions...
    22:22:17 INFO pupa: save jurisdiction Arizona as jurisdiction_ocd-jurisdiction-country:us-state:az-government.json
    22:22:17 INFO pupa: save organization Office of the Secretary of State, State of Arizona as organization_73f49f2a-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO scrapelib: GET - http://apps.azsos.gov/apps/election/cfs/search/SuperPACList.aspx
    22:22:17 INFO pupa: save organization AEA FUND FOR PUBLIC EDUCATION (FORMERLY) AZ PAC (AZ EDUCATION ASSN PAC) as organization_73f49f2b-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization AFSCME PEOPLE as organization_73f49f2c-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization ARIZONA CHAMBER POLITICAL ACTION COMMITTEE as organization_73f49f2d-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization ARIZONA FAMILIES UNITED FOR STRONG COMMUNITIES- PROJECT OF SEIU COPE as organization_73f49f2e-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization Arizona List P.A.C. as organization_73f49f2f-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization Arizona Lodging & Tourism Super PAC as organization_73f49f30-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization Arizona Pipe Trades 469 as organization_73f49f31-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization AZ DENTAL POLITICAL ACTION COMMITTEE as organization_73f49f32-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization AZ MULTIHOUSING ASSN PAC as organization_73f49f33-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization BNSF Railway Company RAILPAC as organization_73f49f34-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization CWA COMMUNICATIONS WORKERS OF AMERICA /AZ COMMITTEE  ON POLITICAL EDUCATION (COPE) as organization_73f49f35-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization Enterprise Holdings, Inc. Political Action Committee as organization_73f49f36-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization GREATER PHOENIX CHAMBER OF COMMERCE POLITICAL ACTION COMMITTEE as organization_73f49f37-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization HOME BUILDERS ASSN OF CENTRAL AZ POLITICAL ACTION COMMITTEE as organization_73f49f38-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization Honeywell International Political Action Committee Arizona-(HIPAC AZ) as organization_73f49f39-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization JPMORGAN CHASE & CO ARIZONA PAC as organization_73f49f3a-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization PARADISE VALLEY FUND FOR CHILDREN IN PUBLIC EDUCATION (PV ED & SUPPORT EMPL ASSN PAC) as organization_73f49f3b-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization PINNACLE WEST CAPITAL CORPORATION POLITICAL ACTION COMMITTEE as organization_73f49f3c-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization REALTORS OF AZ PAC (RAPAC) as organization_73f49f3d-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization SALT RIVER VALLEY WATER USERS ASSN POLITICAL INVOLVEMENT COMMITTEE as organization_73f49f3e-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization The Political Committee of Planned Parenthood Advocates of Arizona as organization_73f49f3f-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization UNITE HERE TIP CAMPAIGN COMMITTEE as organization_73f49f40-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization UNITED FOOD & COMMERCIAL WORKERS ACTIVE BALLOT CLUB (UFCW) as organization_73f49f41-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization UNITED FOOD & COMMERCIAL WORKERS UNION OF AZ LOCAL 99 as organization_73f49f42-e255-11e4-a4f5-e90fe0697b56.json
    22:22:17 INFO pupa: save organization United Services Automobile Assn Employee PAC as organization_73f49f43-e255-11e4-a4f5-e90fe0697b56.json
    az (scrape)
      disclosures: {}
    disclosures scrape:
      duration:  0:00:00.396384
      objects:
        organization: 25
    jurisdiction scrape:
      duration:  0:00:00.001806
      objects:
        jurisdiction: 1
        organization: 1

Modeling OCD Types
==================

The following examples are abstract, and they assume that the target
data has already been obtained. They're meant to show you how to use the
OCD Scrape Objects and their helper functions.

Person
------

.. code:: python

    from pupa.scrape.popolo import Person
Let's assume that this is data we've managed to pull out of an online
source:

.. code:: python

    person_data = {
        'person_name': 'Sheldon Adelson',
        'person_aliases': [
            'Shelly A',
            'The Shelster',
            'Sheldon G Adelson',
            'Sheldon Gary Adelson',
        ],
        'birth_date': '1993-08-04',
        'biography': "Sheldon Gary Adelson (pronounced /ˈædəlsən/; born August 4, 1933) is an American business magnate, investor, and philanthropist. He is the chairman and chief executive officer of the Las Vegas Sands Corporation, which owns the Marina Bay Sands in Singapore and is the parent company of Venetian Macao Limited which operates The Venetian Resort Hotel Casino and the Sands Expo and Convention Center. He also owns the Israeli daily newspaper Israel HaYom. Adelson, a lifelong donor and philanthropist to a variety of causes, founded with his wife's initiative the Adelson Foundation. As of July 2014, Adelson was listed by Forbes as having a fortune of $36.4 billion, and as the 8th richest person in the world. Adelson is also a major contributor to Republican Party candidates, which has resulted in his gaining significant influence within the party.",
        'summary': 'Casino owner and large-dollar donor',
        'image': 'http://upload.wikimedia.org/wikipedia/commons/0/0f/Sheldon_Adelson_21_June_2010.jpg',
        'gender': 'male',
        'national_identity': 'USA',
        'address': '3355 Las Vegas Blvd S, LAS VEGAS, NV 89109',
        'fec_identifier': 'A0035', # Not real, just for demonstration!
    }
Initializing the object
~~~~~~~~~~~~~~~~~~~~~~~

When we initialize a ``Person`` object, we can set a lot of these
properties using keyword arguments. Usually, you won't have this much
information, but Shelly's pretty well known.

.. code:: python

    _person = Person(
        name=person_data['person_name'],
        birth_date=person_data['birth_date'],
        biography=person_data['biography'],
        summary=person_data['summary'],
        image=person_data['image'],
        gender=person_data['gender'],
        national_identity=person_data['national_identity'],
        source_identified=True
    )
Adding multivalued properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we've initialized the person object, we can use its helper
functions to add other properties like contact details, sources,
identifiers and other names (aliases). If you're curious about what's
possible, many of these helper functions are implemented using the
mixins found on
`pupa/pupa/scrape/base.py <https://github.com/influence-usa/pupa/blob/disclosures/pupa/scrape/base.py#L213-L320>`__.

.. code:: python

    _person.add_contact_detail(
        type="address",
        value=person_data['address'],
    )
.. code:: python

    for alias_name in person_data['person_aliases']:
        _person.add_name(name=alias_name)
.. code:: python

    _person.add_source(
        url="http://www.example.com/disclosure/?DocumentID=21459sadgljs85102h235naosudgyy7",
        note="F342_contributions"
    )
Namespaced Identifiers
~~~~~~~~~~~~~~~~~~~~~~

Identifiers can be added in the same way, but you'll need to include a
`namespace <http://en.wikipedia.org/wiki/Namespace>`__ for them.
Namespaces keep identifiers from different sources separate. For
instance, the namespace ``"urn:sopr:registrant"`` is and identifier
namespace that covers identifiers assigned to lobbying disclosure
registrants by the Senate Office of Public Record. The House Clerk's
office also assigns identifiers to many lobbying firms, and they might
clash with SOPR's identifiers, so we assign it to a different namespace,
which is ``"urn:house-clerk:registrant"``.

If you don't see an existing namespace that is an obvious fit for the
data you're scraping, feel free to make one up. It might get changed in
the future, but that's okay.

.. code:: python

    _person.add_identifier(
        identifier=person_data['fec_identifier'],
        scheme='urn:fec:individual'
    )
Viewing the object as a dict
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    _person.as_dict()



.. parsed-literal::

    {'_id': '13de4c60-e46e-11e4-a4f5-e90fe0697b56',
     'biography': "Sheldon Gary Adelson (pronounced /ˈædəlsən/; born August 4, 1933) is an American business magnate, investor, and philanthropist. He is the chairman and chief executive officer of the Las Vegas Sands Corporation, which owns the Marina Bay Sands in Singapore and is the parent company of Venetian Macao Limited which operates The Venetian Resort Hotel Casino and the Sands Expo and Convention Center. He also owns the Israeli daily newspaper Israel HaYom. Adelson, a lifelong donor and philanthropist to a variety of causes, founded with his wife's initiative the Adelson Foundation. As of July 2014, Adelson was listed by Forbes as having a fortune of $36.4 billion, and as the 8th richest person in the world. Adelson is also a major contributor to Republican Party candidates, which has resulted in his gaining significant influence within the party.",
     'birth_date': '1993-08-04',
     'contact_details': [{'note': '',
       'type': 'address',
       'value': '3355 Las Vegas Blvd S, LAS VEGAS, NV 89109'}],
     'death_date': '',
     'extras': {},
     'gender': 'male',
     'identifiers': [{'identifier': 'A0035', 'scheme': 'urn:fec:individual'}],
     'image': 'http://upload.wikimedia.org/wikipedia/commons/0/0f/Sheldon_Adelson_21_June_2010.jpg',
     'links': [],
     'name': 'Sheldon Adelson',
     'national_identity': 'USA',
     'other_names': [{'name': 'Shelly A'},
      {'name': 'The Shelster'},
      {'name': 'Sheldon G Adelson'},
      {'name': 'Sheldon Gary Adelson'}],
     'source_identified': True,
     'sources': [{'note': 'F342_contributions',
       'url': 'http://www.example.com/disclosure/?DocumentID=21459sadgljs85102h235naosudgyy7'}],
     'summary': 'Casino owner and large-dollar donor'}



Organization
------------

(see above)

Event
-----

.. code:: python

    from pupa.scrape import Event
Let's assume that this is data we've managed to pull out of an online
source:

.. code:: python

    event_data = {
        "name": "Sidley Austin LLP - New Client for Existing Registrant, Vifor Pharma",
        "description": "Form LD-1: registration of a lobbying firm and the client they represent.",
        "start_time": "2012-03-01",
        "end_time": None,
        "classification": "registration",
        "location": "United States",
        "timezone":"America/New_York"
    }
A few notes:

-  If we don't know the end time, that's fine: the ``end_time`` can be
   left null.
-  When entering times, enter as much detail as you have available. If
   you know the event's time down to the second, feel free to specify
   that, but if you only know the month in which it occurs, something
   like ``"2014-01"`` is fine
-  Location can also be described as specifically or generally as
   possible

Initializing the object
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    _event = Event(
        name=event_data["name"],
        description=event_data["description"],
        start_time=event_data["start_time"],
        classification=event_data["classification"],
        location=event_data["location"],
        timezone=event_data["timezone"]
    )
**protip**: notice how the keys of the ``event_data`` dict are the same
as the kwargs that we assign them to? a shorter (though admittedly less
explicit) way of initializing the object would be:

.. code:: python

    _quicker_event = Event(**event_data)
Adding Participants
~~~~~~~~~~~~~~~~~~~

Participants in an event can be either of class ``Organization`` or
``Person``, and they can be added using the helper function
``add_participant``. When adding them, it's helpful to characterize
their participation using the ``note`` field:

.. code:: python

    _lobbying_org = Organization(
        name="Sidley Austin LLP",
        classification='company',
    )
    
    _client = Organization(
        name="Vifor Pharma",
        classification="company",
    )
    
    _event.add_participant(
        type=_lobbying_org._type,
        id=_lobbying_org._id,
        name=_lobbying_org.name,
        note="registrant"
    )
    
    _event.add_participant(
        type=_client._type,
        id=_client._id,
        name=_client.name,
        note="client"
    )
As you'll see, the ``participant`` list becomes a list of the entities
that you added. Actually, they are stubs of those objects, rather than
the full objects. They give you an identifier that allows you to resolve
to find the full object, however.

.. code:: python

    _event.participants



.. parsed-literal::

    [{'entity_type': 'organization',
      'id': 'dc6f38d8-e470-11e4-a4f5-e90fe0697b56',
      'name': 'Sidley Austin LLP',
      'note': 'registrant'},
     {'entity_type': 'organization',
      'id': 'dc6f38d9-e470-11e4-a4f5-e90fe0697b56',
      'name': 'Vifor Pharma',
      'note': 'client'}]



Agenda Items
~~~~~~~~~~~~

When describing events, we can give a more organized account of what
happened than just summarizing in the ``description`` property. We can
also model the details of the event using the ``EventAgendaItem`` class.
Agenda items can describe things like the subjects of meetings, the
issues discussed by lobbying firms or the intended agenda of an event.
If you'd like, you can also reflect the order of items in the agenda by
specifying them.

.. code:: python

    _agenda_item = _event.add_agenda_item("issues lobbied on")
Unlike many of the other helper functions, this one adds the item and
also returns it. That makes it possible to make further changes to the
agenda item:

.. code:: python

    for subject in ["HCR", "TAX", "ACC", "LBR"]:
        _agenda_item.add_subject(subject)
    
    _agenda_item['notes'].append("Regulation of complex large-molecule drugs by the Food and Drug Administration")
Because the object that was returned by ``add_agenda_item`` is the same
object that is stored in ``_event``'s ``agenda`` property, making these
changes on ``_agenda_item`` is equivalent to making changes to the
corresponding object inside of ``_event``.

.. code:: python

    _event.agenda



.. parsed-literal::

    [{'description': 'issues lobbied on',
      'media': [],
      'notes': ['Regulation of complex large-molecule drugs by the Food and Drug Administration'],
      'order': '0',
      'related_entities': [],
      'subjects': ['HCR', 'TAX', 'ACC', 'LBR']}]



.. code:: python

    _agenda_item



.. parsed-literal::

    {'description': 'issues lobbied on',
     'media': [],
     'notes': ['Regulation of complex large-molecule drugs by the Food and Drug Administration'],
     'order': '0',
     'related_entities': [],
     'subjects': ['HCR', 'TAX', 'ACC', 'LBR']}



That means that you don't need to ``yield`` the ``EventAgendaItem``
objects. When you yield the ``Event`` object, you'll be yielding the
agenda items that it contains for free.


Modeling Relationships
======================

Memberships
-----------

.. code:: python

    import webbrowser
