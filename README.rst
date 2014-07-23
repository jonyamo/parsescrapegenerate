ParseScrapeGenerate
===================

Generate XML documents using data scraped from HTML documents. In other words:
*parse*, *scape*, and *generate* XML feeds.

Introduction
------------

Using site-specific config files, ``parsescrapegenerate`` will scrape the given
site looking for entries matching the defined rules. Once all the data is
collected the resulting XML data will be written to STDOUT.  Existing XML data
can be read from STDIN, in which case, all entries will be extracted and added
to the resulting output (duplicates will be ignored).

Installation
------------

.. code-block:: bash

    $ git clone https://github.com/jonyamo/parsescrapegenerate.git
    $ cd parsescrapegenerate
    $ python setup.py install

Usage
-----

Command line:

.. code-block:: bash

    parsescrapegenerate CONFIG_FILE < existing_feed.xml > new_feed.xml

As a module:

.. code-block:: python

    from parsescrapegenerate import main

    >>> old_feed = parse(existing_feed)
    >>> new_feed = scrape(config, old_feed)
    >>> generate(new_feed)

Configuration
-------------

In order for ``parsescrapegenerate`` to work you must first define a config file.
This file will define what site to scrape as well as the rules that will be
used to extract the necessary data. Each site you would like to scrape will
have its own config file. The files are defined using `YAML <http://yaml.org>`_.

.. code-block:: yaml

    title:  "Sample Feed Config"           # Optional. If not set, will attempt to extract from site.
    lang:   "en"                           # Optional. If not set, will attempt to extract from site.
    format: "atom"                         # Optional. If not set, will default to RSS.
    path:   "http://example.com/page.html" # Required. Where to find data to scrape. Can be URL or path to file.

    entry:
      templates:                          # Optional. Available keys: title, link, content.
                                          # Data extracted from below xpath rules will be interpolated using Jinja2.
        link:    "http://example.com{{ entry.link }}"
        content: "<span title='{{ entry.title }}'>{{ entry.content }}</span>"

      xpath:                              # Required if you want to actually extract any data.
                                          # Required keys: context.
        context: "//div[@class='entry']"
        title:   "h2[@class='title']/a/text()"
        link:    "h2[@class='title']/a/@href"
        content: "div[@class='content']/text()"

Acknowledgements
----------------

`XPath2RSS <https://github.com/jareware/xpath2rss>`_ - Similar tool written in PHP.
