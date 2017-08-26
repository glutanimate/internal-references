# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Main Module, hooks add-on methods into Anki

Copyright: (c) Glutanimate 2017 <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from aqt.editor import Editor
from aqt.utils import tooltip
from anki.hooks import addHook

from .consts import *
from .insertlink import InsertLink
from . import browser
from . import linkhandler


def onInsertInternalReference(self):
    """Get selection, call link inserter"""
    selected = self.web.selectedText()
    parent = self.parentWindow
    dialog = InsertLink(self, parent, selected)
    dialog.show()


def onSetupButtons(self):
    """Add buttons to editor"""
    self._addButton("contents", self.onInsertInternalReference,
        tip="Insert link to internal reference ({})".format(HOTKEY_EDITOR),
        key=HOTKEY_EDITOR)


Editor.onInsertInternalReference = onInsertInternalReference
addHook("setupEditorButtons", onSetupButtons)