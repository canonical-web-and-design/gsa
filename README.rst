ubuntudesign.gsa: Python GSA client
===================================

.. image:: https://travis-ci.org/ubuntudesign/ubuntudesign.gsa.svg?branch=master
   :alt: build status
   :target: https://travis-ci.org/ubuntudesign/ubuntudesign.gsa

A client library for the `Google Search Appliance <https://enterprise.google.com/search/products/gsa.html>`_, to make retrieving search results in Python easier.

Installation
------------

This module is in PyPi as :code:`ubuntudesign.gsa`. You should be able to install it simply with:

.. code:: bash

    pip install ubuntudesign.gsa

GSAClient
---------

This is a basic client for querying a Google Search Appliance.

Making queries
~~~~~~~~~~~~~~

You can query the GSA using the :code:`search` method.

.. code:: python

    search_client = GSAClient(base_url="http://gsa.example.com/search")

    first_ten_results = search_client.search("hello world")

    first_thirty_results = search_client.search("hello world", num=30)

    results_twenty_to_forty = search_client.search(
      "hello world", start=20, num=20
    )

This will set the `q <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1089652>`_,
`start <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1076971>`_ (default: 0) and
`num <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1076882>`_ (default: 10) and
`lr <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1076879>`_ (default: '') parameters.
No other `search parameters <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1086546>`_,
will be provided, so they will all fall back to their defaults.

The returned results object will attempt to map each of the GSA's
`standard result XML tags <https://www.google.com/support/enterprise/static/gsa/docs/admin/70/gsa_doc_set/xml_reference/results_format.html#1078461>`_
into a more readable format:

.. code:: python

    {
        'estimated_total_results': int,  # "M": GSA's estimate, see below
        'document_filtering': bool,      # "FI": Is filtering enabled?
        'next_url': str,                 # "NU": GSA URL for querying the next set of results, if available
        'previous_url': str,             # "PU": Ditto for previous set of results
        'items': [
            {
                'index': int,            # "R[N]": The number of this result in the index of all results
                'url': str,              # "U": The URL of the resulting page
                'encoded_url': str,      # "UE": The above URL, encoded
                'title': str,            # "T": The page title
                'relevancy': int,        # "RK": How relevant is this result to the query? From 0 to 10
                'appliance_id': str,     # "ENT_SOURCE": The serial number of the GSA
                'summary': str,          # "S": Summary text for this result
                'language': str,         # "LANG": The language of the page
                'details': {}            # "FS": Name:value pairs of any extra info
                'link_supported': bool,  # "L": “link:” special query term is supported,
                'cache': {               # "C": Dictionary, or "None" if cache is not available
                    'size': str,         # "C[SZ]": Human readable size of cached page
                    'cache_id': str,     # "C[CID]": ID of document in GSA's cache
                    'encoding': str      # "C[ENC]": The text encoding of the cached page
                }
            },
            ...
        ]
    }

Filtering by domain or language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can filter your search results by specifying specific domains or a
`specific language <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1077439>`_.

.. code:: python

    english_results = search_client.search("hello world", language="lang_en")
    non_english_results = search_client.search("hello world", language="-lang_en")
    domain_specific_results = search_client.search(
        "hello world",
        domains=["site1.example.com", "site2.example.com"]
    )

*NB:* If no search results are found with the specified ``language``, the GSA will fall back to returning any results it finds in all languages.

Getting accurate totals
~~~~~~~~~~~~~~~~~~~~~~~

At the time of writing, the Google Search Appliance will return an "estimate" of
the total number of results with each query, but this estimate is usually wildly
inaccurate, sometimes out by more than a factor of 10! This is true even with
`rc <https://www.google.com/support/enterprise/static/gsa/docs/admin/72/gsa_doc_set/xml_reference/request_format.html#1076946>`_
enabled.

With the :code:`total_results` method, the client will attempt to request results
990 - 1000. This will usually result in the GSA returning the last page of
results, which allows us to find the actual total number of results.

.. code:: python

    total = search_client.total_results("hello world", domains=[], language='')

Django view
-----------

To simplify usage of the GSA client with Django, a Django view is included
with this module.

Usage
~~~~~

At the minimum, need to provide the :code:`SEARCH_SERVER_URL` setting to tell the view
where to find the GSA:

.. code:: python

    # settings.py
    SEARCH_SERVER_URL = 'http://gsa.example.com/search'  # Required: GSA location
    SEARCH_DOMAINS = ['site1.example.com']               # Optional: By default, limit results to this set of domains
    SEARCH_LANGUAGE = 'lang_zh-CN'                       # Optional: By default, limit results to this language

    # urls.py
    from ubuntudesign.gsa.views import SearchView
    urlpatterns += [url(r'^search/?$', SearchView.as_view(template_name="search.html"))]

This view will then be available to be queried:

- :code:`example.com/search?q=my+search+term`
- :code:`example.com/search?q=my+search+term&domain=example.com&domain=something.example.com`  (overrides :code:`SEARCH_DOMAINS`)
- :code:`example.com/search?q=my+search+term&language=-lang_zh-CN`  (exclude results in Chinese, overrides :code:`SEARCH_LANGUAGE`)

After retrieving search results, the view will pass the context object to the specified :code:`template_name` (in this case :code:`search.html`).

The context object will be structured as follows:

.. code:: python

    {
        'query': str,       # The value of the `q` parameters passed to the view
        'limit': int,       # The value of the `limit` parameter, or the default of 10
        'offset': int,      # The value of the `offset` parameter, or the default of 0
        'error': None|str,  # None, or a description of the error if one occurred
        'results': {
            'items': [],    # The list of items as returned from the GSAClient (see above)
            'total': int,   # The exact total number of results available
            'start': int,   # The index of the first result in the set
            'end': int,     # The index of the last result in the set
            'next_offset': int|None,      # The offset for the next page of results, if available
            'previous_offset': int|None,  # The offset for the previous page of results, if available
            'last_page_offset': int,      # The offset for the last page of results
            'last_page': int,             # The final page number (calculated from "limit" and "total")
            'current_page': int,          # The current page number (calculated from "limit" and "end")
            'penultimate_page': int       # The second-to-last page
    }
