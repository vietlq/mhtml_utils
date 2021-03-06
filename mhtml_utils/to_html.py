#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import pkgutil
import os
import logging
import json

from .to_stream import get_utf8_content_of_mht, _STR_UTF8
from .to_pandas import dataframe_from_content

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger("mht2html")

# https://datatables.net/examples/data_sources/js_array.html
# https://datatables.net/download/index
# http://tabulator.info/
# https://www.kryogenix.org/code/browser/sorttable/
# https://ourcodeworld.com/articles/read/619/top-7-best-table-sorter-javascript-and-jquery-plugins
# https://www.jqueryscript.net/table/Paginate-Sort-Filter-Table-Sortable.html
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
# https://mdbootstrap.com/docs/jquery/tables/sort/


HTML_TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>Sortable</title>
    <meta charset="UTF-8">
    <!--
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" type="text/css"
          href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css">
    -->
    <style>%(style)s</style>
    <script>%(script)s</script>
</head>

<body>

<h1>Cases and details</h1>

<div>
    <table id="sortable_cases" class="display">
    </table>
</div>

<script>
var dataSet = %(json_values)s;

$(document).ready(function() {
    $('#sortable_cases').DataTable( {
        data: dataSet,
        columns: [
            { title: "source" },
            { title: "case_name" },
            { title: "details" }
        ]
    } );
} );
</script>

</body>

</html>
"""


def main():
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_dir = f"html_results_{suffix}"
    # TODO: Consider using index.html when exporting images
    html_file_name = os.path.join(html_dir, f"results_{suffix}.html")
    dataframes = []
    bad_cases = []

    for result in get_utf8_content_of_mht():
        try:
            result_df = dataframe_from_content(result.raw)
            result_df["source"] = result.orig_key
            dataframes.append(result_df)
        except:
            bad_cases.append(result.target_file)
            logger.exception(f"An error occurred when processing {result.target_file}")

    final_df = pd.concat(dataframes)
    final_df = final_df.loc[:, ["source", "case_name", "details"]]
    json_values = json.loads(final_df.to_json(orient="values"))
    json_values = json.dumps(json_values, indent=2)

    os.makedirs(html_dir, exist_ok=True)
    with open(html_file_name, "wb") as html_fh:
        script_str = pkgutil.get_data(__name__, "DataTables/datatables.min.js")
        style_str = pkgutil.get_data(__name__, "DataTables/datatables.min.css")
        contents = HTML_TEMPLATE % dict(
            {
                "script": script_str.decode(_STR_UTF8),
                "style": style_str.decode(_STR_UTF8),
                "json_values": json_values,
            }
        )
        html_fh.write(contents.encode(_STR_UTF8))

    print(f"Could not process these files: {bad_cases}")
    print(f"Check the output file: {html_file_name}")


if __name__ == "__main__":
    # Run: python3 -m mhtml_utils.to_html
    main()
