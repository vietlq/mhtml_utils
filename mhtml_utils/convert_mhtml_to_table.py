#!/usr/bin/env python3

import pandas as pd
from datetime import datetime

from .convert_mhtml_to_html import get_utf8_content_of_mht
from .convert_mhtml_to_pandas import dataframe_from_content

# https://datatables.net/examples/data_sources/js_array.html
# https://datatables.net/download/index
# http://tabulator.info/
# https://www.kryogenix.org/code/browser/sorttable/
# https://ourcodeworld.com/articles/read/619/top-7-best-table-sorter-javascript-and-jquery-plugins
# https://www.jqueryscript.net/table/Paginate-Sort-Filter-Table-Sortable.html


def main():
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"results_{suffix}.xlsx"

    with pd.ExcelWriter(excel_file_name) as writer:
        for result in get_utf8_content_of_mht():
            result_df = dataframe_from_content(result.raw)
            result_df.to_excel(writer, sheet_name=result.orig_key)


if __name__ == "__main__":
    # Run: python3 -m mhtml_utils.convert_mhtml_to_table
    main()
