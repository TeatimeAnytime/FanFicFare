# -*- coding: utf-8 -*-

# Copyright 2020 FanFicFare team
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
import re
#from bs4.element import Tag
from .. import exceptions as exceptions
from ..htmlcleanup import stripHTML

# py2 vs py3 transition
#from ..six import text_type as unicode

from .base_adapter import BaseSiteAdapter,  makeDate

def getClass():
    return SilmarillionWritersGuildOrgAdapter

# Class name has to be unique.  Our convention is camel case the
# sitename with Adapter at the end.  www is skipped.
class SilmarillionWritersGuildOrgAdapter(BaseSiteAdapter):

    def __init__(self, config, url):
        BaseSiteAdapter.__init__(self, config, url)

        self.username = "NoneGiven" # if left empty, site doesn't return any message at all.
        self.password = ""
        self.is_adult=False

        # get storyId from url--url validation guarantees query is only sid=1234
        #logger.debug(self.parsedUrl.path.split('/')[2])
        self.story.setMetadata('storyId',self.parsedUrl.path.split('/')[2])

        # normalized story URL.
        self._setURL('https://' + self.getSiteDomain() + '/node/'+self.story.getMetadata('storyId'))

        # Each adapter needs to have a unique site abbreviation.
        self.story.setMetadata('siteabbrev','swg')

        # The date format will vary from site to site.
        # http://docs.python.org/library/datetime.html#strftime-strptime-behavior
        self.dateformat = "%d %B %Y"

    @staticmethod # must be @staticmethod, don't remove it.
    def getSiteDomain():
        # The site domain.  Does have www here, if it uses it.
        return 'www.silmarillionwritersguild.org'

    @classmethod
    def getSiteExampleURLs(cls):
        return "https://"+cls.getSiteDomain()+"/node/123"

    def getSiteURLPattern(self):
        return r"https?://"+re.escape(self.getSiteDomain()+"/node/")+r"\d+$"

    ## Getting the chapter list and the meta data
    def extractChapterUrlsAndMetadata(self):

        url = self.url
        logger.debug("URL: "+url)

        data = self.get_request(url)

        soup = self.make_soup(data)

        #check if the link is even a story, as the website stores other multimedia with no differece to urls
        type_check = soup.body['class']
        #logger.debug(type_check)
        if 'page-node-type-writing' in type_check:
            logger.debug('Content check passed.')
            pass
        else:
            logger.debug('Content check failed.')
            raise exceptions.FailedToDownload("Node is not a story at URL: %s " % self.url)
        
        ## Title and author

        # find story header
        a = soup.find('h1')

        titleLinks = a.find_all('a')
        authorLink= titleLinks[1]

        self.story.setMetadata('authorId',authorLink['href'].split('/')[2])
        self.story.setMetadata('authorUrl','https://'+self.host+authorLink['href'])
        self.story.setMetadata('author',authorLink.string)
        titleurl = titleLinks[0]
        self.story.setMetadata('title',titleurl.string)

        # Parse the infobox
        ## The site doesn't give categories, so set default in default.ini
        infobox = soup.find('table').find('tbody').findAll('tr')
        labelsbox = infobox[0:2]
        for box in labelsbox:
            labelSpans = box.find_all('strong')
            #logger.debug(labelSpans)
            for labelSpan in labelSpans:
                #logger.debug(labelSpan)
                label = labelSpan.string
                if label is None:
                    label = stripHTML(labelSpan)
                #logger.debug(label)
                if 'Summary' in label:
                    valueHTML = labelSpan.parent.next_sibling
                    nextEl = valueHTML.next_sibling
                    valueHTML2 = str(valueHTML)
                    while nextEl is not None and '<strong>' not in str(nextEl):
                        valueHTML2 = valueHTML2 + str(nextEl)
                        nextEl = nextEl.next_sibling
                    self.setDescription(self.url, valueHTML2)
                else:
                    values = labelSpan.parent.find_all('a')
                    if 'Major Characters' in label:
                        for value in values:
                            self.story.addToList('characters', value.string)
                    elif 'Major Relationships' in label:
                        for value in values:
                            self.story.addToList('ships', value.string)
                    elif 'Genre' in label:
                        for value in values:
                            self.story.addToList('genre', value.string)
                    elif 'Rating' in label:
                        for value in values:
                            self.story.setMetadata('rating', value.string)
                    elif 'Warnings' in label:
                        for value in values:
                            self.story.addToList('warnings', value.string)
                    elif 'Chapters' in label:
                        value = labelSpan.next_sibling.string.strip()
                        self.story.addToList('numChapters', int(value))
                    elif 'Word Count' in label:
                        value = labelSpan.next_sibling.string.strip()
                        self.story.setMetadata('numWords', value)
        
        datebox = infobox[2]
        dates = datebox.find_all('td')
        for date in dates:
            date = date.string
            date = date.split(' on ')
            if date[0] == 'Posted':
                self.story.setMetadata('datePublished', makeDate(date[1], self.dateformat))
            elif date[0] == 'Updated':
                self.story.setMetadata('datePublished', makeDate(date[1], self.dateformat))
        status_box = infobox[3]
        status = status_box.td.p.string
        if status == 'This fanwork is complete.':
            self.story.setMetadata('status', 'Completed')
        elif status == 'This fanwork is a work in progress.':
            self.story.setMetadata('status', 'In-Progress')
            
        ## Series parse
        #technically, there can be more than one series, but I really can't be bothered.
        box1 = infobox[0]                
        series_check = box1.find('span',{'class':'series-empty'})
        if series_check is None:
            try:
                series_full = box1.find('span',{'class':'field-content'}).find('a')
                
                seriesName = series_full.string
                #logger.debug(seriesName)
                seriesUrl = 'https://'+self.host+series_full['href']
                logger.debug(seriesUrl)
                self.story.setMetadata('seriesUrl',seriesUrl)
                #making soup from series page just to find the index, Oh MY!
                seriesPageSoup = self.make_soup(self.get_request(seriesUrl))
                
                #seriesStoryList = []
                storyHeaders = seriesPageSoup.findAll('h4')
                #logger.debug(storyHeaders)
                i=1
                for storyHeader in storyHeaders:
                    seriesPagePageStoryUrl = storyHeader.find('a',href=re.compile(r'\/node\/\d+$'))
                    #logger.debug(seriesPagePageStoryUrl)
                    if seriesPagePageStoryUrl is None:
                        pass
                    else:
                        if seriesPagePageStoryUrl['href'] == ('/node/'+self.story.getMetadata('storyId')):
                            #logger.debug("Series Name: "+ seriesName)
                            #logger.debug("Series Index: "+i)
                            self.setSeries(seriesName, i)
                            raise StopIteration("Break out of series parsing loops")
                        i+=1
            except StopIteration:
                # break out of both loops, don't need to fetch further
                # pages after story found.
                pass
            except Exception as e:
                logger.warning("series parsing failed(%s)"%e) 
        #getting storynotes
        notesbox = soup.find('h4')
        if notesbox.string == 'Fanwork Notes':
            valueHTML = notesbox.next_sibling.next_sibling
            nextEl = valueHTML.next_sibling.next_sibling
            valueHTML2 = str(valueHTML)
            while nextEl is not None and '<p>' in str(nextEl):
                valueHTML2 = valueHTML2 + str(nextEl)
                nextEl = nextEl.next_sibling
            #logger.debug(valueHTML2)
            self.story.setMetadata('storynotes', stripHTML(valueHTML2))
    
        # Find the chapters by regexing urls
        chapters=soup.findAll('a', href=re.compile(r'^/node/'+self.story.getMetadata('storyId')+r"/single\?page\=\d+$"))

        for chapter in chapters:
            # logger.debug("Added Chapter: "+chapter.string)
            self.add_chapter(chapter,'https://'+self.host+chapter['href'])
            

    # grab the text for an individual chapter.
    def getChapterText(self, url):

        logger.debug('Getting chapter text from: %s' % url)

        data = self.get_request(url)
        soup = self.make_soup(data)

        listing = soup.find('div',{'class':"fanwork-listing"})
        if None == listing:
            raise exceptions.FailedToDownload("Error downloading Chapter: %s!  Missing required element!" % url)
        # remove useless elements
        listing.div.decompose()
        listing.h1.decompose()
        listing.h3.decompose()
        #check for footnote
        footnote_check = False
        maybe_footnotes = listing.find_all('h4')
        for maybe in maybe_footnotes:
            if maybe.string == 'Chapter End Notes':
                footnote_check = True
                listing.h4.decompose()
            else:
                pass
        if self.getConfig("include_author_notes",True):
            firstline = listing.find('hr')
            para = firstline.next_sibling
            firstline.decompose()
            while para is not None and'<p>' not in str(para):
                para = para.next_sibling
                if '<hr/>' in str(para):
                    firstline = listing.find('hr')
                    firstline.decompose()
                    break
            #logger.debug(listing)
            chapter_content = listing
        else:
            logger.debug('here')
            #remove frontonte
            firstline = listing.find('hr')
            para = firstline.next_sibling
            if '<hr/>' not in str(para):
                nextEl = para.next_sibling
                para.replace_with('')
                while nextEl is not None and '<hr/>' not in str(nextEl):
                    para = nextEl
                    nextEl = nextEl.next_sibling
                    para.replace_with('')
            firstline.decompose()
            listing.find('hr').decompose()
            #remove footnote if present
            if footnote_check == True:
                lines = listing.find_all('hr')
                lastline = lines[-1]
                para = lastline.next_sibling
                nextEl = para.next_sibling
                para.replace_with('')
                while nextEl is not None and '<hr/>' not in str(nextEl):
                    para = nextEl
                    nextEl = nextEl.next_sibling
                    para.replace_with('')
                lastline.decompose()
            chapter_content = listing

        return self.utf8FromSoup(url,chapter_content)
