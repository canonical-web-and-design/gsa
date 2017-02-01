# Core modules
import math
try:
    from urllib.error import URLError
except:
    from urllib2 import URLError
import requests

# Third party modules
from django.conf import settings
from django.views.generic import TemplateView

# Local modules
from . import GSAClient


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
        search_client = GSAClient(search_server_url)

        query = self.request.GET.get('q', '').encode('utf-8')
        domains = (
            self.request.GET.getlist('domain') or
            getattr(settings, "SEARCH_DOMAINS", [])
        )
        language = (
            self.request.GET.get('language') or
            getattr(settings, "SEARCH_LANGUAGE", '')
        )
        timeout = (
            self.request.GET.get('language') or
            getattr(settings, "SEARCH_TIMEOUT", 30)
        )
        limit = int(self.request.GET.get('limit', '10'))
        offset = int(self.request.GET.get('offset', '0'))
        results = {}
        error = None

        if query:
            try:
                server_results = search_client.search(
                    query,
                    start=offset,
                    num=limit,
                    domains=domains,
                    language=language,
                    timeout=timeout
                )
                items = server_results['items']

                total = search_client.total_results(
                    query,
                    domains=domains,
                    language=language
                )

                results = {
                    'items': items,
                    'total': total,
                }

                if total > 0:
                    start = items[0]['index']
                    end = items[-1]['index']
                    last_page = int(math.ceil(float(total) / limit))
                    penultimate_page = last_page - 1
                    current_page = int(math.ceil(float(end) / limit))
                    last_page_offset = limit * penultimate_page
                    next_offset = offset + limit
                    previous_offset = offset - limit
                    if next_offset >= total:
                        next_offset = None
                    if previous_offset < 0:
                        previous_offset = None

                    results.update({
                        'start': start,
                        'end': end,
                        'next_offset': next_offset,
                        'previous_offset': previous_offset,
                        'last_page_offset': last_page_offset,
                        'last_page': last_page,
                        'penultimate_page': penultimate_page,
                        'current_page': current_page
                    })

                    if offset + limit < total:
                        results['next_offset'] = offset + limit
                    if offset - limit >= 0:
                        results['previous_offset'] = offset - limit

            except URLError:
                error = 'URL error'
            except requests.ConnectionError:
                error = 'connection error'
            except requests.Timeout:
                error = 'timeout error'
            except requests.RequestException:
                error = 'general request error'

        # Import context from parent
        template_context = super(SearchView, self).get_context_data(**kwargs)

        template_context['results'] = results
        template_context['query'] = query
        template_context['limit'] = limit
        template_context['offset'] = offset
        template_context['error'] = error

        return template_context
