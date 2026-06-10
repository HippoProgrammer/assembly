'''This file is part of assembly.
Copyright (C) 2026 HippoProgrammer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.'''

import aiohttp # HTTP requests
import asyncio # async functionality
import xml.etree.ElementTree as etree # XML parsing
import classes
from .env import load_useragent_from_envvars
import logging

# set up a logger
logger = logging.getLogger('assembly.customio.ns') # get the logger for this script

class HTTPResponseException(Exception):
    pass

class QueryException(Exception):
    pass
class API:
    def __init__(self) -> None:
        self.rate_limited = False
        self.headers = {
            "User-Agent": f"assembly/0.1.0-a1, source https://github.com/HippoProgrammer/assembly, author idinist_imauggland, used_by {load_useragent_from_envvars()}"
        }

    async def setup_all(self) -> None:
        self.clientsession = aiohttp.ClientSession(headers=self.headers)

    async def cleanup(self) -> None:
        await self.clientsession.close()

    async def _make_request(self, uri:str) -> str:
        if not self.rate_limited:
            async with self.clientsession.get(uri) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:
                    self.rate_limited = True
                    raise HTTPResponseException(f'Error {response.status}: {response.reason}. NS API rate limited. No retry will be attempted.')
                    headers = response.headers
                    await asyncio.sleep(int(headers['Retry-After']))
                    self.rate_limited = False
                else:
                    raise HTTPResponseException(f'Error {response.status}: {response.reason}')
        else:
            raise QueryException('Rate limited. Request blocked.')

    async def _query_proposals(self, council: int) -> etree.ElementTree:
        council = str(council) # convert to string for URL
        try:
            xmlstr = await self._make_request(f'http://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=proposals')
            xmltree = etree.fromstring(xmlstr)
            proposals = xmltree.findall('./PROPOSALS/PROPOSAL')
            return proposals
        except HTTPResponseException as e:
            raise QueryException(str(e))

    async def _parse_coauthor(self,coauthor:etree.Element) -> list[str | None]:
        if len(coauthor) == 0:
            return []
        else: 
            return coauthor[0].text.split(',')

    async def _get_quorum(self) -> int:
        try:
            xmlstr = await self._make_request('http://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=numdelegates')
            xmltree = etree.fromstring(xmlstr)
            numdelegates = int(xmltree.findall('./NUMDELEGATES')[0].text)
            quorum = round(numdelegates * 0.06, 1)
            return quorum
        except HTTPResponseException as e:
            raise QueryException(str(e))

    async def _parse_approvals(self,approval:etree.Element) -> list[str | None]:
        if approval[0].text == None:
            return []
        else:
            return approval[0].text.split(':')

    async def parse_proposals(self, council: int) -> list[classes.wa.Proposal]:
        xml = await self._query_proposals(council)
        parsed_xml = []
        for element in xml:
            parsed_element = classes.wa.Proposal().fromAttributeValues(
                id = element.findall('./ID')[0].text,
                council = council,
                name = element.findall('./NAME')[0].text,
                category = element.findall('./CATEGORY')[0].text,
                author = element.findall('./PROPOSED_BY')[0].text,
                coauthors = await self._parse_coauthor(element.findall('./COAUTHOR')),
                legal = (len(element.findall('./GENSEC/LEGAL/*')) > (len(element.findall('./GENSEC/ILLEGAL/*')) + len(element.findall('./GENSEC/DISCARD/*')))),
                quorum = len(await self._parse_approvals(element.findall('./APPROVALS'))) > await self._get_quorum()
            )
            parsed_xml.append(parsed_element)
        return parsed_xml

    async def _query_atvote(self,council:int) -> etree.ElementTree:
        council = str(council) # convert to string for URL
        try:
            xmlstr = await self._make_request(f'http://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=resolution')
            xmltree = etree.fromstring(xmlstr)
            resolution_elements = xmltree.findall('./RESOLUTION/')
            if len(resolution_elements) == 0:
                return None
            else:
                return resolution_elements
        except HTTPResponseException as e:
            raise QueryException(str(e))
    
    async def parse_atvote(self, council:int):
        xml = await self._query_atvote(council)
        parsed_xml = classes.wa.Proposal().fromAttributeValues(
            id = 0,
            council = 0,
            name = '',
            category = '',
            author = '',
            legal = True,
            quorum = True,
            coauthors = []
        )
        return parsed_xml
