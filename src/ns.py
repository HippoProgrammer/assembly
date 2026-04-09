import aiohttp # HTTP requests
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
            return proposals

def parse_coauthor(coauthor:etree._Element):
    if len(coauthor) == 0:
        return []
    else: 
        return coauthor[0].text.split(',')

async def parse_proposals(council: int):
    xml = await query_proposals(council)
    parsed_xml = []
    for element in xml:
        parsed_element = wa.Proposal().fromAttributeValues(
            id = element.xpath('./ID')[0].text,
            council = council,
            name = element.xpath('./NAME')[0].text,
            category = element.xpath('./CATEGORY')[0].text,
            author = element.xpath('./PROPOSED_BY')[0].text,
            coauthors = parse_coauthor(element.xpath('./COAUTHOR')),
            legal = (len(element.xpath('./GENSEC/LEGAL/*')) > (len(element.xpath('./GENSEC/ILLEGAL/*')) + len(element.xpath('./GENSEC/DISCARD/*'))))
        )
        parsed_xml.append(parsed_element)
    return parsed_xml