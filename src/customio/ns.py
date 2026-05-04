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

headers = {
    "User-Agent": f"assembly/0.1.0-a1, source https://github.com/HippoProgrammer/assembly, author idinist_imauggland, used_by {load_useragent_from_envvars()}"
}

async def _query_proposals(council: int):
    council = str(council) # convert to string for URL
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=proposals') as response:
            xmlstr = await response.text()
            xmltree = etree.fromstring(xmlstr)
            proposals = xmltree.findall('/WA/PROPOSALS/PROPOSAL')
            return proposals

async def _parse_coauthor(coauthor:etree._Element):
    if len(coauthor) == 0:
        return []
    else: 
        return coauthor[0].text.split(',')

async def _get_quorum():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=numdelegates') as response:
            xmlstr = await response.text()
            xmltree = etree.findall(xmlstr)
            numdelegates = int(xmltree.findall('/WA/NUMDELEGATES')[0].text)
            quorum = round(numdelegates * 0.06, 1)
            return quorum

async def _parse_approvals(approval:etree._Element):
    if approval[0].text == None:
        return []
    else:
        return approval[0].text.split(':')

async def parse_proposals(council: int):
    xml = await _query_proposals(council)
    parsed_xml = []
    for element in xml:
        parsed_element = classes.wa.Proposal().fromAttributeValues(
            id = element.findall('./ID')[0].text,
            council = council,
            name = element.findall('./NAME')[0].text,
            category = element.findall('./CATEGORY')[0].text,
            author = element.findall('./PROPOSED_BY')[0].text,
            coauthors = await _parse_coauthor(element.findall('./COAUTHOR')),
            legal = (len(element.findall('./GENSEC/LEGAL/*')) > (len(element.findall('./GENSEC/ILLEGAL/*')) + len(element.findall('./GENSEC/DISCARD/*')))),
            quorum = len(await _parse_approvals(element.findall('./APPROVALS'))) > await _get_quorum()
        )
        parsed_xml.append(parsed_element)
    return parsed_xml

async def _query_atvote(council:int):
    council = str(council) # convert to string for URL
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=resolution') as response:
            xmlstr = await response.text()
            xmltree = etree.fromstring(xmlstr)
            resolutions = xmltree.findall('/WA/RESOLUTION')
            if len(resolutions) == 0:
                return None
            else:
                return resolutions
