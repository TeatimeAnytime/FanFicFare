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

class StarsLibraryNetAdapter(BaseEfictionAdapter):

    @staticmethod
    def getSiteDomain():
        return 'starslibrary.net'

    @classmethod
    def getProtocol(self):
        return "https"

    ## starslibrary.net is a replacement for pre-existing twcslibrary.net.
    @classmethod
    def getConfigSections(cls):
        "Only needs to be overriden if has additional ini sections."
        return super(StarsLibraryNetAdapter, cls).getConfigSections()+['www.'+cls.getConfigSection(),'www.twcslibrary.net']

    @classmethod
    def getAcceptDomains(cls):
        return [cls.getSiteDomain(),'www.' + cls.getSiteDomain(),
                'www.twcslibrary.net','twcslibrary.net']

    @classmethod
    def getSiteURLPattern(self):
        return r"https?://(%s)?%s/%s\?sid=(?P<storyId>\d+)" % ('|'.join(self.getAcceptDomains()), self.getPathToArchive(), self.getViewStoryPhpName())

    @classmethod
    def getSiteAbbrev(self):
        return 'stars'

    @classmethod
    def getDateFormat(self):
        return "%d %b %Y"
    
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
        if 'TWCS Romance Contest' in key:
            for val in re.split(r"\s*,\s*", value):
                self.story.addToList('contest', val)
        elif 'Language' in key:
            self.story.addToList('language', value)
        else:
            super(StarsLibraryNetAdapter, self).handleMetadataPair(key, value)


def getClass():
    return StarsLibraryNetAdapter
