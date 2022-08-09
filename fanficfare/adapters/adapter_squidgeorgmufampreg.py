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
import re
from .base_efiction_adapter import BaseEfictionAdapter

class SquidgeOrgMufaMpregAdapter(BaseEfictionAdapter):

    @staticmethod
    def getSiteDomain():
        return 'www.squidge.org'

    @classmethod
    def getPathToArchive(self):
        return '/mufa-mpreg'

    @classmethod
    def getConfigSection(cls):
        "Overriden because [domain/path] section for multiple-adapter domain."
        return cls.getSiteDomain()+cls.getPathToArchive()

    @classmethod
    def getSiteAbbrev(self):
        return 'smfmp'

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
        labels = listbox.find_all('a')
        #logger.debug(listbox)
        a_url = labels[-1]
        rating = a_url.next_sibling.string
        rating = rating.split('[')[1]
        rating = rating.split(']')[0]
        self.story.setMetadata('rating',rating)

            
#        def handleMetadataPair(self, key, value):
#            if 'Categories' in key:
#                for val in re.split(r"\s*,\s*", value):
#                    for val2 in re.split(r"\s*>\s*", val):
#                        self.story.addToList('category', val2)
#            elif 'Pairing Type' in key:
#                for val in re.split(r"\s*,\s*", value):
#                    self.story.addToList('shipstype', val)
#            elif 'File Type' in key:
#                for val in re.split(r"\s*,\s*", value):
#                    self.story.addToList('filetype', val)
#            else:
#                super(SquidgeOrgMufaMpregAdapter, self).handleMetadataPair(key, value)


def getClass():
    return SquidgeOrgMufaMpregAdapter

