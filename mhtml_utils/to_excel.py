#!/usr/bin/env python3

import pandas as pd
from datetime import datetime

from .to_stream import get_utf8_content_of_mht
from .to_pandas import dataframe_from_content


def main():
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"results_{suffix}.xlsx"

    with pd.ExcelWriter(excel_file_name) as writer:
        for result in get_utf8_content_of_mht():
            result_df = dataframe_from_content(result.raw)
            result_df.to_excel(writer, sheet_name=result.orig_key)

    print(f"Check the output file: {excel_file_name}")


if __name__ == "__main__":
    # Run: python3 -m mhtml_utils.convert_mhtml_to_excel
    main()
