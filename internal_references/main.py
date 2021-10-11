# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Main Module, hooks add-on methods into Anki

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""



from aqt.qt import *
from aqt.editor import Editor
from aqt.utils import tooltip
from anki.hooks import addHook

from .consts import *
from .insertlink import InsertLink
from . import browser
from . import linkhandlers


def onInsertInternalReference(self):
    """Get selection, call link inserter"""
    # will have to use asynchronous callback on 2.1:
    data_tuple = self.web.page().mainFrame().evaluateJavaScript("""
        function getSelectionData() {
           var node = document.getSelection().anchorNode;
           var text = node.textContent
           var data = node.parentNode.getAttribute('data-a');
           return [text, data]
        }
        getSelectionData()
        """)
    if not data_tuple[1] or isinstance(data_tuple[1], QPyNullVariant):
        data_string = None
        selected = self.web.selectedText()
    else:
        selected, data_string = data_tuple

    parent = self.parentWindow
    dialog = InsertLink(
        self, parent, selected=selected, data_string=data_string)
    dialog.show()


def onSetupButtons(buttons, editor):
    """Add buttons to editor"""
    b = editor.addButton("contents", "IR", lambda o=editor: onInsertInternalReference(o),
        tip="Insert link to internal reference ({})".format(HOTKEY_EDITOR),
        keys=HOTKEY_EDITOR)
    buttons.append(b)
    return buttons


Editor.onInsertInternalReference = onInsertInternalReference
addHook("setupEditorButtons", onSetupButtons)