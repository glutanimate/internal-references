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
import os

from .consts import *
from .insertlink import InsertLink
from . import browser
from . import linkhandlers


def onInsertInternalReference(self: Editor):
    """Get selection, call link inserter"""
    # but first define an asynchronous callback
    def on_result(data_tuple):
        data_string = None
        selected = None
        if not data_tuple[1] or isinstance(data_tuple[1], QPyNullVariant):
            data_string = None
            selected = self.web.selectedText()
        else:
            selected, data_string = data_tuple
        
        parent = self.parentWindow
        dialog = InsertLink(
            self, parent, selected=selected, data_string=data_string)
        dialog.show()
    
    self.web.page().runJavaScript("""
        function getSelectionData() {
           var node = document.getSelection().anchorNode;
           var text = node.textContent
           var data = node.parentNode.getAttribute('data-a');
           return [text, data]
        }
        getSelectionData()
        """, on_result)


def onSetupButtons(buttons, editor):
    """Add buttons to editor"""
    icon_path = os.path.join(os.path.dirname(__file__), "link.png")
    b = editor.addButton(icon_path, "IR", lambda o=editor: onInsertInternalReference(o),
        tip="Insert link to internal reference ({})".format(HOTKEY_EDITOR),
        keys=HOTKEY_EDITOR)
    buttons.append(b)
    return buttons


Editor.onInsertInternalReference = onInsertInternalReference
addHook("setupEditorButtons", onSetupButtons)