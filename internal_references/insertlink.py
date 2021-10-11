# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

InsertLink dialog

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""




import aqt
from aqt.qt import *
import json

from .consts import *
from .utils import dataEncode, dataDecode
from .insertlink_ui import Ui_Dialog

class InsertLink(QDialog):
    """Link insertion dialog"""

    bridge = "pycmd"
    link = ('''<a href="" class="ilink" data-a="{{data}}" {{ciddata}} '''
            '''onclick="{bridge}('ilink:' + this.dataset.a); return false;">'''
            '''{{text}}</a>'''.format(bridge=bridge))

    def __init__(self, editor, parent, selected=None, data_string=None):
        super(InsertLink, self).__init__(parent=parent)
        self.editor = editor
        self.browser = None
        self.parent = parent
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.setupUi()
        self.setInitial(selected, data_string)
        self.setupEvents()
        self.form.teSearch.setFocus()

    #  UI

    def setupUi(self):
        self.okButton = self.form.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)


    def setupEvents(self):
        self.form.btnSel.clicked.connect(self.selectInBrowser)
        self.form.teSearch.textChanged.connect(self.enableWidgets)


    def enableWidgets(self, initial=False):
        search = self.form.teSearch.text()
        
        if search:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)
        
        if search.startswith(('"cid:', 'cid:')):
            self.form.rbPreview.setEnabled(True)
            if PREVIEW_BY_DEFAULT and not initial:
                self.form.rbPreview.setChecked(True)
            self.form.teHighlight.setEnabled(True)
            self.form.labNotCard.setText("")
        else:
            self.form.rbPreview.setEnabled(False)
            if PREVIEW_BY_DEFAULT and not initial:
                self.form.rbBrowse.setChecked(True)
            self.form.teHighlight.setEnabled(False)
            self.form.labNotCard.setText(
                """Previewing items and highlighting """
                """terms only works for single cards.""")

    # Editor

    def setInitial(self, selected, data_string):
        """
        Set initial values based on provided data string
        or selected text
        """
        if data_string:
            data_dict = dataDecode(data_string)
            search = data_dict.get("src")
            dialog = data_dict.get("dlg")
            highlight = data_dict.get("hlt")
            self.form.teSearch.setText(search)
            self.form.teHighlight.setText(highlight)
            if dialog == "preview":
                self.form.rbPreview.setChecked(True)
        else:
            self.form.teHighlight.setText(selected)
        self.form.teName.setText(selected)
        self.enableWidgets(initial=True)


    def createAnchor(self, search, text, highlight, preview, ciddata):
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
            data=data, ciddata=ciddata, text=text or search)

        return anchor


    def insertAnchor(self):
        """
        Inserts an HTML anchor `<a>` into the text field.
        """
        search = self.form.teSearch.text().strip()
        text = self.form.teName.text().strip()

        if search.startswith(('"cid:', 'cid:')):
            highlight = self.form.teHighlight.text().strip()
            cid = search.split(":")[1]
            ciddata = 'data-cid="{}"'.format(cid)
        else:
            highlight = ""
            ciddata = ""

        preview = self.form.rbPreview.isChecked()

        anchor = self.createAnchor(search, text, highlight, preview, ciddata)

        self.editor.web.setFocus()
        self.editor.web.eval("focusField(%d);" % self.editor.currentField)
        # replace or insert new anchor:
        self.editor.web.eval("""
            function replaceOrInsertHTML(html) {
               var parent = document.getSelection().anchorNode.parentNode;
               var parent_name = parent.nodeName.toLowerCase()
               var parent_class = parent.className
               if (parent_name === "a" && parent_class === "ilink") {
                    var newAnchor = document.createElement("a")
                    newAnchor.innerHTML = html
                    parent.parentNode.replaceChild(newAnchor, parent);
               } else {
                    document.execCommand('insertHTML', false, html);
               }
            }
            replaceOrInsertHTML(%s)
            """ % json.dumps(anchor))

    # Browser
    
    def selectInBrowser(self):
        search = self.form.teSearch.text().strip()
        highlight = self.form.teHighlight.text().strip()
        browser = aqt.dialogs.open("Browser", aqt.mw)
        browser.createInsertlinkSelector(self, search, highlight)
        self.browser = browser


    def closeBrowserInstance(self):
        if self.browser:
            self.browser.close()


    def onConfirmBrowser(self, search, highlight):
        if search:
            self.form.teSearch.setText(search)
        if highlight:
            self.form.teHighlight.setText(highlight)
            if not self.form.teName.text():
                self.form.teName.setText(highlight)
        self.browser = None

    # Close events

    def accept(self):
        self.closeBrowserInstance()
        self.insertAnchor()
        super(InsertLink, self).accept()

    def reject(self):
        self.closeBrowserInstance()
        super(InsertLink, self).reject()

