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

# Software: eFiction
from __future__ import absolute_import
from ..htmlcleanup import stripHTML
import logging
logger = logging.getLogger(__name__)
import re
from .base_efiction_adapter import BaseEfictionAdapter

class AmotheaSlashcityComAdapter(BaseEfictionAdapter):

    @staticmethod
    def getSiteDomain():
        return 'amothea.slashcity.com'

    @classmethod
    def getPathToArchive(self):
        return '/db'

    @classmethod
    def getSiteAbbrev(self):
        return 'ascaa'

    @classmethod
    def getDateFormat(self):
        return "%m/%d/%Y"
    
    @classmethod
    def getProtocol(self):
        """
        Some, but not all site now require https.
        """
        return "https"
    
    def getRatingFromTOC(self):
        # In many eFiction sites, the Rating is not included in
        # print page, but is on the TOC page.  At least one site's rating
        # (libraryofmoriacom) differs enough to be problematic.
        toc = self.url + "&index=1"
        soup = self.make_soup(self.get_request(toc))
        #logger.debug(soup)
        listbox = soup.find("div", attrs={"id": "pagetitle"})
        labels = listbox.find_all(class_=re.compile("label"))
        #logger.debug(listbox)
        for label in labels:
            logger.debug(label)
            if 'Rated:' in label or 'Rating:' in stripHTML(label):
                rating = stripHTML(label.next_sibling)
                if rating.endswith(' ['):
                    rating = rating[:-2]
                self.story.setMetadata('rating',rating)
            #elif 'Pairing Type' in label:
            #    shipstype = stripHTML(label.next_sibling)
            #    self.story.addToList('shipstype', shipstype)
                break
             
    def handleMetadataPair(self, key, value):
        #logger.debug(key.string)
        if 'Categories' in key:
            for val in re.split(r"\s*,\s*", value):
                for val2 in re.split(r"\s*>\s*", val):
                    self.story.addToList('category', val2)
        else:
            super(AmotheaSlashcityComAdapter, self).handleMetadataPair(key, value)

def getClass():
    return AmotheaSlashcityComAdapter

