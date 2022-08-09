# -*- coding: utf-8 -*-

# Copyright 2018 FanFicFare team
# Copyright 2018 FanFicFare team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Software: eFiction
##################################################################################
### Rewritten by: GComyn on November, 06, 2016
### Original was adapter_fannation.py
##################################################################################
from __future__ import absolute_import
import logging
logger = logging.getLogger(__name__)
from ..htmlcleanup import stripHTML
import re
from .base_efiction_adapter import BaseEfictionAdapter

class ValentChamberComAdapter(BaseEfictionAdapter):

    @staticmethod
    def getSiteDomain():
        return 'valentchamber.com'

    @classmethod
    def getSiteAbbrev(self):
        return 'vccom'

    @classmethod
    def getProtocol(self):
        """
        Some, but not all site now require https.
        """
        return "https"

    @classmethod
    def getDateFormat(self):
        # The date format will vary from site to site.
        # http://docs.python.org/library/datetime.html#strftime-strptime-behavior
        return "%B %d %Y"
    
    def getRatingFromTOC(self):
        # In many eFiction sites, the Rating is not included in
        # print page, but is on the TOC page.  At least one site's rating
        # (libraryofmoriacom) differs enough to be problematic.
        toc = self.url + "&index=1"
        soup = self.make_soup(self.get_request(toc))
        #logger.debug(soup)
        listbox = soup.find("div", attrs={"class": "listbox"})
        labels = listbox.find_all(class_=re.compile("label"))
        #logger.debug(listbox)
        for label in labels:
            #logger.debug(label)
            if 'Rated:' in label or 'Rating:' in stripHTML(label):
                rating = stripHTML(label.next_sibling)
                if rating.endswith(' ['):
                    rating = rating[:-2]
                self.story.setMetadata('rating',rating)
                break
            
    def handleMetadataPair(self, key, value):
        if 'Classification' in key:
            for val in re.split(r"\s*,\s*", value):
                self.story.addToList('class', val)
        else:
            super(ValentChamberComAdapter, self).handleMetadataPair(key, value)

##################################################################################
### The Efiction Base Adapter uses the Bulk story to retrieve the metadata, but
### on this site, the Rating is not present in the Bulk page... 
### so it is not retrieved.
##################################################################################
        
def getClass():
    return ValentChamberComAdapter
