#!/usr/bin/env python3

import logging
import os
from datetime import datetime

import pandas as pd

from .to_stream import get_utf8_content_of_mht
from .to_pandas import dataframe_from_content

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger("mht2html")


def main():
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"results_{suffix}.xlsx"
    bad_cases = []

    with pd.ExcelWriter(excel_file_name) as writer:
        for result in get_utf8_content_of_mht():
            try:
                result_df = dataframe_from_content(result.raw)
                result_df.to_excel(writer, sheet_name=result.orig_key)
            except:
                bad_cases.append(result.target_file)
                logger.exception(f"An error occurred when processing {result.target_file}")

    print(f"Could not process these files: {bad_cases}")
    print(f"Check the output file: {excel_file_name}")


if __name__ == "__main__":
    # Run: python3 -m mhtml_utils.convert_mhtml_to_excel
    main()
