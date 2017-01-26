Python GSA
==========

A client library for the Google Search Appliance, to make retrieving search results in Python easier.

Usage
----

.. code:: python 

    search_client = GSAClient(base_url="http://gsa.example.com/search")
    results = search_client.search("hello world")
    total = search_client.total_results("hello world")

Django view
---

There is also a view for using this with Django:

.. code:: python

    # settings.py
    SEARCH_SERVER_URL = 'http://gsa.example.com/search'

    # urls.py
    from ubuntudesign.gsa.views import SearchView
    urlpatterns += [url(r'^search/?$', SearchView.as_view(template_name="search.html"))]

