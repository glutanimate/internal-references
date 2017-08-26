# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Handlers for internal reference links

Copyright: (c) Glutanimate 2017 <https://glutanimate.com/>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import aqt
from aqt.qt import *
from aqt.utils import openLink
from aqt.reviewer import Reviewer
from aqt.editor import EditorWebView

from anki.hooks import wrap, addHook

from .utils import dataDecode


def linkHandler(self, url, _old=None):
    if not url.startswith("ilink"):
        if _old:
            return _old(self, url)
        else:
            return openLink(url)
    
    cmd, data = url.split(":")
    data_dict = dataDecode(data)
    if not data_dict or data_dict == "corrupted":
        return False

    search = data_dict.get("src")
    dialog = data_dict.get("dlg")
    highlight = data_dict.get("hlt")

    if dialog == "preview":
        openPreviewLink(search, highlight)
    else:
        openBrowseLink(search, highlight)


def openBrowseLink(search, highlight):
    browser = aqt.dialogs.open("Browser", aqt.mw)
    query = '''{}'''.format(search)
    browser.form.searchEdit.lineEdit().setText(query)
    browser.onSearch()
    if not highlight or not browser.editor:
        return
    browser.editor.web.findText(highlight,
        QWebPage.HighlightAllOccurrences)
    browser.editor.web.findText(highlight)


def openPreviewLink(search, highlight):
    pass


# Add link handlers to webviews

## Advanced Previewer
def profileLoaded():
    try:
        from advanced_previewer.previewer import Previewer
    except ImportError:
        return
    Previewer.linkHandler = wrap(
        Previewer.linkHandler, linkHandler, "around")

addHook("profileLoaded", profileLoaded)

## Editor
def onEditorWebInit(self, parent, editor):
    self.setLinkHandler(self._linkHandler)

EditorWebView._linkHandler = linkHandler
EditorWebView.__init__ = wrap(EditorWebView.__init__, onEditorWebInit, "after")

## Reviewer
Reviewer._linkHandler = wrap(Reviewer._linkHandler, linkHandler, "around")