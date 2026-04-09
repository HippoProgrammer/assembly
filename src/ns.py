import aiohttp # HTTP requests
import os, sys # general os-level functionality
import asyncio # async functionality
from lxml import etree # XML parsing
import wa



async def query_proposals(council: int):
    council = str(council) # convert to string for URL
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=proposals') as response:
            xmlstr = await response.text()
            xmltree = etree.fromstring(xmlstr)
            proposals = xmltree.xpath('/WA/PROPOSALS/PROPOSAL')