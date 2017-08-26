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
from anki import json


def dataEncode(data):
    """
    Take a dictionary and JSONify it. Return the resultant string,
    encoded in base64.
    """
    if not data:
        return u""

    encoded = unicode(base64.b64encode(json.dumps(data)))
    return encoded


def dataDecode(data):
    """
    Decode a base64-encoded JSON string and return a dictionary.
    """
    if not data:
        return u""
    
    try:
        decoded = base64.b64decode(data)
    except (TypeError, UnicodeEncodeError) as e:
        # `data` is not a valid base64-encoded string
        print e
        return "corrupted"

    try:
        ret = json.loads(decoded)
        return ret
    except ValueError as e:
        print e
        return "corrupted"
