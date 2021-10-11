# -*- coding: utf-8 -*-

"""
This file is part of the Internal References add-on for Anki

Link handlers and dialogs launched by them

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""



import aqt
from aqt.qt import *
from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView
from aqt.reviewer import Reviewer
from aqt.editor import EditorWebView
from aqt.utils import saveGeom, restoreGeom, openLink, \
                      tooltip

from anki.sound import clearAudioQueue, playFromText, play
from anki.hooks import runFilter, wrap
from anki.utils import stripHTML

from .consts import *
from .utils import dataDecode
# from .forms4 import previewer


# support for JS Booster add-on
try:
    from jsbooster.location_hack import getBaseUrlText, stdHtmlWithBaseUrl
    preview_jsbooster = True
except ImportError:
    preview_jsbooster = False


class CardPreviewer(QDialog):
    """Custom card previewer dialog"""

    title = "Card {}: '{}...'"

    def __init__(self, cid, highlight):
        super(CardPreviewer, self).__init__(parent=mw.app.activeWindow())
        self.mw = mw
        self.cid = cid
        self.highlight = highlight
        self.form = aqt.forms.previewer.Ui_Dialog()
        self.form.setupUi(self)
        self.setupEvents()
        self.setupUi()
        ret = self.setCard(self.cid)
        self.setHighlight(self.highlight)
        restoreGeom(self, "irpreviewer")
        if ret is not False:
            self.show()
        else:
            self.close()

    #  UI

    def setupUi(self):
        self.web = AnkiWebView()
        self.web.setLinkHandler(linkHandler)
        self.form.verticalLayout.insertWidget(0, self.web)


    def setupEvents(self):
        self.form.btnBrowse.clicked.connect(self.onBrowse)
        self.form.btnBacklinks.clicked.connect(self.onBacklinks)


    def setCard(self, cid):
        """
        Set title and webview HTML
        """
        try:
            card = self.mw.col.getCard(cid)
        except TypeError:
            tooltip("Could not find linked card with cid:'{}'.".format(cid))
            return False

        # Set previewer title based on note contents
        note = card.note()
        fields = note.fields
        model = note.model()
        fnames = mw.col.models.fieldNames(model)
        idx = 0
        if "Note ID" in note:
            nid_idx = fnames.index("Note ID")
            if nid_idx == idx:
                idx = min(idx+1, len(fields))
        field1 = stripHTML(fields[idx])
        title = self.title.format(cid, field1[:50])
        self.setWindowTitle(title)

        # Set card HTML
        html = card.a()
        html = runFilter("previewerMungeQA", html)

        ti = lambda x: x
        base = self.mw.baseHTML()
        css = self.mw.reviewer._styles()
        if preview_jsbooster:
            # JS Booster available
            baseUrlText = getBaseUrlText(self.mw.col) + "__previewer__.html"
            stdHtmlWithBaseUrl(self.web,
                ti(mw.prepare_card_text_for_display(html)), baseUrlText, css,
                bodyClass="card card%d" % (card.ord+1), 
                head=base, js=None)
        else:
            # fall back to default
            self.web.stdHtml(
                mw.prepare_card_text_for_display(html), css, 
                bodyClass="card card%d" % (card.ord+1), 
                head=base, js=None)

        # Handle audio
        clearAudioQueue()
        if self.mw.reviewer.autoplay(card):
            playFromText(html)


    def setHighlight(self, highlight):
        self.web.findText(highlight, QWebPage.HighlightAllOccurrences)
        self.web.findText(highlight)


    def onBrowse(self):
        search = "cid:{}".format(self.cid)
        openBrowseLink(search, self.highlight)


    def onBacklinks(self):
        openBrowseLink(self.cid, self.highlight)


    def closeEvent(self, event):
        if self.mw.pm.profile is not None:
            saveGeom(self, "irpreviewer")
        event.accept()


def hookedLinkHandler(self, url, _old=None):
    if not url.startswith("ilink"):
        if _old:
            return _old(self, url)
        else:
            return openLink(url)
    linkHandler(url)


def linkHandler(url):
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
    cid = search.split(":")[1]
    CardPreviewer(cid, highlight)



# Add link handlers to webviews

## Advanced Previewer
def profileLoaded():
    try:
        from advanced_previewer.previewer import Previewer
    except ImportError:
        return
    Previewer.linkHandler = wrap(
        Previewer.linkHandler, hookedLinkHandler, "around")

gui_hooks.profile_did_open.append(profileLoaded)

# ## Editor
# def onEditorWebInit(self, parent, editor):
#     self.setLinkHandler(self._linkHandler)
#     mw.web

# EditorWebView._linkHandler = hookedLinkHandler
# EditorWebView.__init__ = wrap(EditorWebView.__init__, onEditorWebInit, "after")

## Reviewer
Reviewer._linkHandler = wrap(Reviewer._linkHandler, hookedLinkHandler, "around")