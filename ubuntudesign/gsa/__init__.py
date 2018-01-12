# Core modules
try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

# Third party modules
import requests
from lxml import etree


def xml_text(root_element, child_tag):
    if root_element.xpath(child_tag):
        return root_element.xpath(child_tag)[0].text


class GSAClient:
    """
    Query the Google Search Appliance and return results
    as a python dictionary.

    Usage:

    search_client = GSAClient(base_url="http://gsa.example.com/search")
    results = search_client.search("hello world")
    total = search_client.total_results("hello world")
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def search(
        self, query,
        start=0, num=10, domains=[], language="", timeout=30
    ):
        """
        Query the GSA to get response in XML format
        which it will then parse into a dictionary.
        """

        query_string = query.decode()

        # Filter by domains, if specified
        if domains:
            domain_filters = ['site:' + domain for domain in domains]
            query_string += ' ( ' + " | ".join(domain_filters) + ' )'

        # Build the GSA URL
        query_parameters = urlencode({
            'q': query_string,
            'num': str(num),
            'start': str(start),
            'lr': language
        })
        search_url = self.base_url + '?' + query_parameters

        response = requests.get(search_url, timeout=timeout)

        xml_tree = etree.fromstring(response.content)

        # We're now going to parse the XML items into a hopefully
        # more meaningful dictionary object.
        # To understand the layout of the XML document, see here:
        # https://www.google.com/support/enterprise/static/gsa/docs/admin/70/gsa_doc_set/xml_reference/results_format.html

        results = {
            'estimated_total_results': xml_text(xml_tree, '/GSP/RES/M'),
            'document_filtering': bool(xml_text(xml_tree, '/GSP/RES/FI')),
            'next_url': xml_text(xml_tree, '/GSP/RES/NB/NU'),
            'previous_url': xml_text(xml_tree, '/GSP/RES/NB/PU'),
            'items': []
        }

        item_elements = xml_tree.xpath('/GSP/RES/R')

        for item_element in item_elements:
            item = {
                'index': int(item_element.attrib.get('N')),
                'url': xml_text(item_element, 'U'),
                'encoded_url': xml_text(item_element, 'UE'),
                'title': xml_text(item_element, 'T'),
                'relevancy': int(xml_text(item_element, 'RK')),
                'appliance_id': xml_text(item_element, 'ENT_SOURCE'),
                'summary': xml_text(item_element, 'S'),
                'language': xml_text(item_element, 'LANG'),
                'details': {},
                'link_supported': bool(item_element.xpath('HAS/L')),
                'cache': None
            }

            detail_elements = item_element.xpath('FS')

            for detail in detail_elements:
                item['details'][detail.attrib['NAME']] = detail.attrib['VALUE']

            cache_elements = item_element.xpath('HAS/C')

            if cache_elements:
                item['cache'] = {
                    'size': cache_elements[0].attrib.get('SZ'),
                    'cache_id': cache_elements[0].attrib.get('CID'),
                    'encoding': cache_elements[0].attrib.get('ENC')
                }

            results['items'].append(item)

        return results
