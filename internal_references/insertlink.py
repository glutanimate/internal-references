# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Associated dialogs

Copyright: (c) Glutanimate 2017 <https://glutanimate.com/>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import aqt
from aqt.qt import *
from anki.utils import json

from .consts import *
from .utils import dataEncode
from .forms4 import insertlink


class InsertLink(QDialog):
    """Link Insertion Dialog"""

    bridge = "py.link"
    link = ('''<a href="" class="ilink" '''
            '''onclick='{bridge}("ilink:{data}"); return false;'>{text}</a>''')

    def __init__(self, editor, parent, selected):
        super(InsertLink, self).__init__(parent=parent)
        self.editor = editor
        self.browser = None
        self.parent = parent
        self.selected = selected
        self.form = insertlink.Ui_Dialog()
        self.form.setupUi(self)
        self.setupEvents()
        self.setupUi()
        self.form.teSearch.setFocus()

    #  UI

    def setupUi(self):
        self.form.teName.setText(self.selected)
        self.form.teHighlight.setText(self.selected)
        self.okButton = self.form.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)


    def setupEvents(self):
        self.form.btnSel.clicked.connect(self.selectInBrowser)
        self.form.teSearch.textChanged.connect(self.enableWidgets)


    def enableWidgets(self):
        search = self.form.teSearch.text()
        
        if search:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)
        
        if search.startswith(('"cid:', 'cid:')):
            self.form.rbPreview.setEnabled(True)
            self.form.teHighlight.setEnabled(True)
            self.form.labNotCard.setText("")
        else:
            self.form.rbPreview.setEnabled(False)
            self.form.teHighlight.setEnabled(False)
            self.form.labNotCard.setText(
                """Previewing items and highlighting """
                """terms only works for single cards.""")

    # Editor


    def createAnchor(self, search, text, highlight, preview):
        """
        Create a hyperlink string
        """
        if preview:
            dialog = "preview"
        else:
            dialog = "browse"
        
        data_dict = {
            "dlg": dialog,
            "src": search,
            "hlt": highlight
        }

        data = dataEncode(data_dict)

        anchor = self.link.format(
            bridge=self.bridge, data=data, text=text or search)

        return anchor


    def insertAnchor(self):
        """
        Inserts an HTML anchor `<a>` into the text field.
        """
        search = self.form.teSearch.text().strip()
        text = self.form.teName.text().strip()

        if search.startswith(('"cid:', 'cid:')):
            highlight = self.form.teHighlight.text().strip()
        else:
            highlight = ""

        preview = self.form.rbPreview.isChecked()

        anchor = self.createAnchor(search, text, highlight, preview)

        self.editor.web.setFocus()
        self.editor.web.eval("focusField(%d);" % self.editor.currentField)
        self.editor.web.eval(
            "document.execCommand('insertHTML', false, %s);"
            % json.dumps(anchor))

    # Browser
    
    def selectInBrowser(self):
        search = self.form.teSearcg.text().strip() 
        browser = aqt.dialogs.open("Browser", aqt.mw)
        browser.createInsertlinkSelector(self, search)
        self.browser = browser


    def closeBrowserInstance(self):
        if self.browser:
            self.browser.close()


    def onConfirmBrowserSelection(self, search):
        if search:
            self.form.teSearch.setText(search)
        self.browser = None

    # Close events

    def accept(self):
        self.closeBrowserInstance()
        self.insertAnchor()
        super(InsertLink, self).accept()

    def reject(self):
        self.closeBrowserInstance()
        super(InsertLink, self).reject()

