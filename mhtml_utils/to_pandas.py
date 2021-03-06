#!/usr/bin/env python3

import parsel
import re
from bs4 import BeautifulSoup
import pandas as pd

# https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html
# https://stackoverflow.com/questions/52677769/extract-text-from-div-class-with-scrapy
# https://stackoverflow.com/questions/293482/how-do-i-fix-wrongly-nested-unclosed-html-tags/293558
# https://stackoverflow.com/questions/614797/xpath-find-a-node-that-has-a-given-attribute-whose-value-contains-a-string
# https://developer.mozilla.org/en-US/docs/Web/XPath/Introduction_to_using_XPath_in_JavaScript
# https://lxml.de/xpathxslt.html
# https://lxml.de/parsing.html
# https://stackoverflow.com/questions/25221023/select-a-node-with-xpath-whose-child-node-contains-a-specific-inner-text
# https://stackoverflow.com/questions/103325/what-is-the-correct-xpath-for-choosing-attributes-that-contain-foo
# https://cssselect.readthedocs.io/en/latest/
# https://www.w3schools.com/jsref/met_document_queryselector.asp
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html
# Make sure `openpyxl` is installed

_STR_XPATH_PARENT_SPAN = '//{parent}[span[contains(text(), " v ")]]'
_STR_CHILD_SPAN_WITH_V = "./span[contains(text(), ' v ')]"
_STR_HTML_NS = "http://www.w3.org/TR/REC-html40"


def extract_text(elem):
    return re.sub(
        r"[\r\n\s]+", " ", " ".join([x for x in elem.xpath(".//text()").extract()]).strip()
    )


def extract_spans_with_v(elem):
    return [extract_text(sub_elem) for sub_elem in elem.xpath(_STR_CHILD_SPAN_WITH_V)]


def extract_parent_and_spans_with_v(top_elem, parent, redact_cases=True):
    results = [
        (extract_spans_with_v(parent_elem), extract_text(parent_elem))
        for parent_elem in top_elem.xpath(_STR_XPATH_PARENT_SPAN.format(parent=parent))
    ]
    # Redact case names for challenge
    output = []
    for (spans_with_v, parent_elem) in results:
        for span in spans_with_v:
            parent_elem = parent_elem.replace(span, "****_guess_it_****")
        output.extend([(span, parent_elem) for span in spans_with_v])

    return pd.DataFrame(data=output, columns=["case_name", "details"])


def dataframe_from_content(raw_content, redact_cases=True):
    soup = BeautifulSoup(raw_content, "html5lib")
    # Export a valid and prettified HTML document
    html = soup.prettify()
    doc = parsel.Selector(text=html)
    return pd.concat(
        [
            extract_parent_and_spans_with_v(doc, parent=parent, redact_cases=redact_cases)
            for parent in ["li", "p"]
        ]
    )
