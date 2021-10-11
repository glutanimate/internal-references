# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Common reusable utilities

dataEncode and dataDecode are based on code found in the Power Format Pack
add-on by Stefan van den Akker
(https://github.com/Neftas/supplementary-buttons-anki)

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
           (c) 2014-2017 Stefan van den Akker <neftas@protonmail.com>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""

import base64
import json


def dataEncode(data):
    """
    Take a dictionary and JSONify it. Return the resultant string,
    encoded in base64.
    """
    if not data:
        return ""

    encoded = str(base64.b64encode(bytes(json.dumps(data), encoding='utf8')))
    return encoded


def dataDecode(data):
    """
    Decode a base64-encoded JSON string and return a dictionary.
    """
    if not data:
        return ""
    
    try:
        decoded = base64.b64decode(data)
    except (TypeError, UnicodeEncodeError) as e:
        # `data` is not a valid base64-encoded string
        print(e)
        return "corrupted"

    try:
        ret = json.loads(decoded)
        return ret
    except ValueError as e:
        print(e)
        return "corrupted"
