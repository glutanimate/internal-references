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
from .forms4 import insertlink



class InsertLink(QDialog):
    """Link Insertion Dialog"""

    bridge = "py.link"
    link_format = ('''<a href='#' class="ilink" '''
                   '''onclick='{bridge}("{command}");'>{label}</a>''')

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
        self.form.btnSel.setFocus()

    #  UI

    def setupUi(self):
        self.form.teSearch.setText(self.selected)
        self.form.teHighlight.setText(self.selected)


    def setupEvents(self):
        self.form.btnSel.clicked.connect(self.selectInBrowser)
        self.okButton = self.form.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        self.form.teSearch.textChanged.connect(self.enableOk)


    def enableOk(self):
        if self.form.teSearch.text():
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    # Editor

    def escapeHtmlCharacters(self, text):
        """
        Escape HTML characters in a string. Return a safe string.
        """
        if not text:
            return u""
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        result = u"".join(html_escape_table.get(c, c) for c in text)
        return result


    def createAnchor(self, url, text, highlight, preview):
        """
        Create a hyperlink string, where `url` is the hyperlink reference
        and `text` the content of the tag.
        """
        text = self.escapeHtmlCharacters(text)

        return u"<a href=\"{0}\">{1}</a>".format(url, text or url)


    def insertAnchor(self):
        """
        Inserts a HTML anchor `<a>` into the text field.
        """
        url = self.form.teSearch.text()
        text = self.form.teName.text()
        highlight = self.form.teHighlight.text()
        preview = self.form.rbBrowse.isChecked()

        anchor = self.createAnchor(url, text, highlight, preview)

        self.editor.web.eval(
            "document.execCommand('insertHTML', false, %s);"
            % json.dumps(anchor))

    # Browser
    
    def selectInBrowser(self):
        browser = aqt.dialogs.open("Browser", aqt.mw)
        browser.createInsertlinkSelector(self)
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

