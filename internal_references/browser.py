# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Modifications to Anki's card browser

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from aqt.qt import *
from aqt.utils import tooltip

from anki.hooks import wrap
from aqt.browser import Browser

from .consts import *


def createInsertlinkSelector(self, insertLink, search, highlight):
    self.insertLink = insertLink

    target = self.form.verticalLayout_3
    selector = QWidget()
    layout = QHBoxLayout(selector)
    
    label = QLabel("<b>Insert internal reference using:</b>")
    
    btnCard = QPushButton("Current card")
    btnCard.setToolTip("Hotkey: {}".format(HOTKEY_BROWSER_CARD))
    btnCard.clicked.connect(lambda: self.onInsertLinkButton("card"))
    btnCard.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    btnSearch = QPushButton("Current search")
    btnSearch.setToolTip("Hotkey: {}".format(HOTKEY_BROWSER_SEARCH))
    btnSearch.clicked.connect(lambda: self.onInsertLinkButton("search"))
    btnSearch.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    layout.addStretch()
    layout.addWidget(label)
    spacer = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
    layout.addItem(spacer)
    layout.addWidget(btnCard)
    layout.addWidget(btnSearch)
    target.addWidget(selector)

    QShortcut(QKeySequence(HOTKEY_BROWSER_CARD), self,
        activated=btnCard.animateClick)
    QShortcut(QKeySequence(HOTKEY_BROWSER_SEARCH), self,
        activated=btnSearch.animateClick)

    self.form.searchEdit.lineEdit().setText(search or "deck:current")
    self.onSearch()

    if highlight and self.editor:
        self.editor.web.findText(highlight,
            QWebPage.HighlightAllOccurrences)
        self.editor.web.findText(highlight)


def onInsertLinkButton(self, btn):
    if btn == "card":
        cids = self.selectedCards()
        if not cids:
            tooltip("Please select a card first")
            return
        elif len(cids) > 1:
            tooltip("Please select just one card")
            return
        search = "cid:{}".format(cids[0])
    elif btn == "search":
        search = self.form.searchEdit.lineEdit().text()
    if self.editor:
        highlight = self.editor.web.selectedText()
    else:
        highlight = ""
    self.insertLink.onConfirmBrowser(search, highlight)
    self.close()


Browser.createInsertlinkSelector = createInsertlinkSelector
Browser.onInsertLinkButton = onInsertLinkButton