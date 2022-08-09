# -*- coding: utf-8 -*-

# Copyright 2011 Fanficdownloader team, 2018 FanFicFare team
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

from __future__ import absolute_import
import logging
logger = logging.getLogger(__name__)
from ..htmlcleanup import stripHTML
import re
# Software: eFiction
from .base_efiction_adapter import BaseEfictionAdapter

class StarskyHutchArchiveNetSiteAdapter(BaseEfictionAdapter):

    @staticmethod
    def getSiteDomain():
        return 'www.starskyhutcharchive.net'

    @classmethod
    def getSiteAbbrev(self):
        return 'shan'

    @classmethod
    def getDateFormat(self):
        return "%m/%d/%Y"
    
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
    
def getClass():
    return StarskyHutchArchiveNetSiteAdapter
