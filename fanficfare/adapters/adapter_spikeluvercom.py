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
from ..htmlcleanup import stripHTML
import re
# Software: eFiction
import logging
logger = logging.getLogger(__name__)
from .base_efiction_adapter import BaseEfictionAdapter

class SpikeluverComAdapter(BaseEfictionAdapter):

    @classmethod
    def getProtocol(self):
        """
        Some, but not all site now require https.
        """
        return "https"

    @staticmethod
    def getSiteDomain():
        return 'spikeluver.com'

    @classmethod
    def getPathToArchive(self):
        return '/SpuffyRealm'

    @classmethod
    def getSiteAbbrev(self):
        return 'slc'

    @classmethod
    def getDateFormat(self):
        return "%m/%d/%Y"

    def getRatingFromTOC(self):
        # In many eFiction sites, the Rating is not included in
        # print page, but is on the TOC page.  At least one site's rating
        # (libraryofmoriacom) differs enough to be problematic.
        toc = self.url + "&index=1"
        soup = self.make_soup(self.get_request(toc))
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
        labels = soup.findAll('span',{'class':'label'})
        for labelspan in labels:
#            value = labelspan.nextSibling
            label = labelspan.string
            if 'Categories' in label:
                cats = labelspan.parent.findAll('a',href=re.compile(r'browse.php\?type=categories'))
                for cat in cats:
                    logger.debug(cat)
                    logger.debug(cat['href'])
                    link = cat['href']
                    catid = link.split('catid=')[1]
                    logger.debug(catid)
                    logger.debug(cat.string)
                    self.story.addToList('category',cat.string)
                    Spuffy_Fantasy = ['3','4','27']
                    Spuffy_International = ['13','14','24','26','25']
                    Spuffy_General = ['5','6','7','8']
                    Spuffy_Hardcore = ['9','17','28','10']
                    Crossovers = ['19','20']
                    Challenges = ['22','23']
                    if catid in Spuffy_Fantasy:
                        self.story.addToList('category','Spuffy Fantasy/AU')
                    if catid in Spuffy_International:
                        self.story.addToList('category','Spuffy International')
                    if catid in Spuffy_General:
                        self.story.addToList('category','Spuffy General/Canon')
                    if catid in Spuffy_Hardcore:
                        self.story.addToList('category','Spuffy Hardcore/Smut')
                    if catid in Crossovers:
                        self.story.addToList('category','Crossovers')
                    if catid in Challenges:
                        self.story.addToList('category','Challenges')
                break
        
    def handleMetadataPair(self, key, value):
        if 'Categories' in key:
            pass
        else:
            super(SpikeluverComAdapter, self).handleMetadataPair(key, value)

def getClass():
    return SpikeluverComAdapter
