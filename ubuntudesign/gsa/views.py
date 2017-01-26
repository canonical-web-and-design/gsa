# Core modules
try:
    from urllib.parse import urlparse
    from urllib.error import URLError
except:
    from urlparse import urlparse
    from urllib2 import URLError
import socket
from requests import ConnectionError

# Third party modules
from django.conf import settings
from django.views.generic import TemplateView

# Local modules
from . import GSAClient


def is_ipv4(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False


class SearchView(TemplateView):
    '''
    A Django view for querying search results from the Google Search Appliance
    and passing them to a Django template.

    Requests should be formatted: <url>?q=<string>&offset=<num>&limit=<num>

    I've used "offset" and "limit" for pagination,
    following the "Web API Design" standard:
    https://pages.apigee.com/web-api-design-ebook.html

    This expects to find the search server URL
    in the SEARCH_SERVER_URL Django setting.

    E.g.: SEARCH_SERVER_URL = 'http://my-server.com/search'
    '''

    def get_context_data(self, **kwargs):
        """
        Extend TemplateView.get_context_data to parse query parameters
        and return search results from the Google Search Appliance (GSA)

        E.g.: http://example.com/search?q=juju&limit=10&offset=10

        Query parameters:
        - q: the search query to be passed to the GSA
        - limit: number of results to return, "page size" (default: 10)
        - offset: where to start results at (default: 0)
        """

        search_server_url = settings.SEARCH_SERVER_URL
        search_host = urlparse(search_server_url).netloc
        search_client = GSAClient(search_server_url)

        query = self.request.GET.get('q', '').encode('utf-8')
        limit = int(self.request.GET.get('limit', '10'))
        offset = int(self.request.GET.get('offset', '0'))
        results = {}
        error = None

        # return self.context
        try:
            # Check we can find the host
            if is_ipv4(search_host):
                socket.gethostbyaddr(search_host)
            else:
                socket.gethostbyname(search_host)

            server_results = search_client.search(
                query, start=offset, num=limit
            )
            items = server_results['items']

            total = search_client.total_results(query)
            start = None
            end = None

            remainder = total % limit
            if remainder == 0:
                last_page_offset = total - offset
            else:
                last_page_offset = total - remainder

            results = {
                'items': items,
                'total': total,
            }

            if total > 0:
                start = items[0]['index']
                end = items[-1]['index']

                results.update({
                    'start': start,
                    'end': end,
                    'next_offset': offset + limit,
                    'previous_offset': offset - limit,
                    'last_page_offset': last_page_offset,
                    'last_page': start > last_page_offset,
                    'penultimate_page': (
                        start < last_page_offset and
                        start >= last_page_offset - limit
                    ),
                    'first_page': start == 1,
                    'second_page': start > 1 and start <= (limit + 1)
                })

        except URLError:
            error = 'request error'
        except ConnectionError:
            error = 'connection error'
        except socket.error:
            error = 'host error'

        # Import context from parent
        template_context = super(SearchView, self).get_context_data(**kwargs)

        template_context['results'] = results
        template_context['query'] = query
        template_context['limit'] = limit
        template_context['offset'] = offset
        template_context['error'] = error

        return template_context
