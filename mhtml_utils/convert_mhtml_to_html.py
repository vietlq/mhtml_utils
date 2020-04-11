#!/usr/bin/env python3

import base64
import logging
import os
import re

from datetime import datetime
from os import listdir
from os.path import isfile, splitext
from email.parser import Parser
from email.quoprimime import body_decode
from urllib.parse import urlparse
from collections import namedtuple
from typing import Generator

import chardet

_STR_ASCII = "ascii"
_STR_UTF8 = "utf-8"
_STR_CTE = "Content-Transfer-Encoding"
_STR_QPRI = "quoted-printable"
_STR_BASE64 = "base64"
_STR_CLOC = "Content-Location"
_STR_CTYPE = "Content-Type"


ParseResult = namedtuple("ParseResult", "orig_key target_dir target_file raw")


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger("mht2html")


def handle_multipart(mht_file, export_utf8_mht=False):
    with open(mht_file, "rb") as fh:
        contents = fh.read()

    # Detect encoding and convert to UTF-8 if required
    # https://pypi.org/project/chardet/
    encoding_dict = chardet.detect(contents)
    logger.info(f"The encoding of the file [{mht_file}] is {encoding_dict}")
    guessed_encoding = encoding_dict["encoding"]
    try:
        text_contents = contents.decode(guessed_encoding, errors="strict")
        filename, file_ext = splitext(mht_file)
        new_dirname = re.sub(r"[\s\'\":]+", "_", filename.lower().strip())
        new_dirname = new_dirname.replace("&", "_and_")
        new_dirname = new_dirname.replace("_s_", "s_")
        new_dirname = re.sub(r"[_]+", "_", new_dirname)
        new_dirname = f"""{new_dirname}_{datetime.now().strftime("%Y%m%d_%H%M%S")}"""
        # TODO: Decide where to create dirs
        # os.mkdir(new_dirname)

        if export_utf8_mht:
            new_filename = f"{filename}.utf-8{file_ext}"
            with open(new_filename, "wb") as new_fh:
                new_fh.write(text_contents.encode(_STR_UTF8, errors="strict"))

        parser = Parser()
        parse_result = parser.parsestr(text_contents)

        logger.info(f"Headers of `{mht_file}`: \n{parse_result.items()}")

        if not parse_result.is_multipart():
            yield handle_non_multipart(filename, new_dirname, parse_result)
        else:
            for payload in parse_result.get_payload():
                if not payload:
                    logger.warn(f"Empty payload: {type(payload)} - {payload}")
                    continue

                if not hasattr(payload, "items"):
                    logger.warn(f"The payload does not have `items`: {type(payload)} - {payload}")
                    continue

                logger.info(f"Payload headers:\n{payload.items()}")
                if payload.is_multipart():
                    logger.warn("Recursive multi-part is ignored")
                    continue
                else:
                    yield handle_non_multipart(filename, new_dirname, payload)
    except Exception as e:
        logger.exception(
            f"An error occurred during detection, decoding, "
            f"or encoding of the file {mht_file}: {str(e)}!"
        )


def handle_non_multipart(orig_key, new_dirname, payload):
    content_transfer_enc = payload.get(_STR_CTE)
    content_location = payload.get(_STR_CLOC)

    uri_parse_obj = urlparse(content_location)
    logging.debug(f"uri_parse_obj = {uri_parse_obj}")

    path_parts = uri_parse_obj.path.split("/")[3:]
    target_dir = os.path.join(new_dirname, *path_parts[:-1])
    # TODO: Decide where to create dirs
    # os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(new_dirname, *path_parts)
    logging.debug(f"target_file = {target_file}")

    if content_transfer_enc == _STR_QPRI:
        # If you see "=3D" being everywhere
        # https://en.wikipedia.org/wiki/Quoted-printable
        # https://stackoverflow.com/questions/12147992/issue-parsing-mhtml
        payload_txt = body_decode(payload.get_payload())
        yield ParseResult(orig_key, target_dir, target_file, payload_txt.encode(_STR_UTF8))
    elif content_transfer_enc == _STR_BASE64:
        payload_raw = base64.decodebytes(payload.get_payload().encode(_STR_ASCII))
        yield ParseResult(orig_key, target_dir, target_file, payload_raw)
    else:
        logger.warn(f"{_STR_CTE} = {content_transfer_enc} is ignored")


def get_utf8_content_of_mht() -> Generator[ParseResult, None, None]:
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    mht_files = [
        f for f in listdir() if f.endswith(".mht") and not f.endswith(".utf-8.mht") and isfile(f)
    ]
    logger.info(f"List of MHT/MHTML files in this folder: {mht_files}")

    results = (handle_multipart(mht_file) for mht_file in mht_files)
    for sub_results in results:
        for sub_sub_sub_results in sub_results:
            for result in sub_sub_sub_results:
                yield result


if __name__ == "__main__":
    for result in get_utf8_content_of_mht():
        print(result.orig_key, result.target_dir, result.target_file)
