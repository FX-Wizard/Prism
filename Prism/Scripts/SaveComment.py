# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2020 Richard Frangenberg
#
# Licensed under GNU GPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.


import os
import platform

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

    psVersion = 2
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

    psVersion = 1

if psVersion == 1:
    from UserInterfacesPrism import SaveComment_ui
else:
    from UserInterfacesPrism import SaveComment_ui_ps2 as SaveComment_ui

from PrismUtils.Decorators import err_catcher


class SaveComment(QDialog, SaveComment_ui.Ui_dlg_SaveComment):
    def __init__(self, core):
        QDialog.__init__(self)
        self.setupUi(self)

        self.core = core
        self.core.parentWindow(self)
        self.previewDefined = False
        self.e_comment.textEdited.connect(lambda x: self.validate(self.e_comment))
        self.b_changePreview.clicked.connect(self.grabArea)
        self.setEmptyPreview()
        self.core.callback(
            name="onSaveExtendedOpen", types=["curApp", "custom"], args=[self]
        )
        self.resize(0, self.geometry().size().height())

    def enterEvent(self, event):
        QApplication.restoreOverrideCursor()

    @err_catcher(name=__name__)
    def validate(self, widget):
        self.core.validateLineEdit(widget)

    @err_catcher(name=__name__)
    def setEmptyPreview(self):
        imgFile = os.path.join(
            self.core.projectPath, "00_Pipeline", "Fallbacks", "noFileBig.jpg"
        )
        pmap = self.getImgPMap(imgFile)
        pmap = pmap.scaled(QSize(500, 281))
        self.l_preview.setPixmap(pmap)

    @err_catcher(name=__name__)
    def getImgPMap(self, path):
        if platform.system() == "Windows":
            return QPixmap(path)
        else:
            try:
                im = Image.open(path)
                im = im.convert("RGBA")
                r, g, b, a = im.split()
                im = Image.merge("RGBA", (b, g, r, a))
                data = im.tobytes("raw", "RGBA")

                qimg = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)

                return QPixmap(qimg)
            except:
                return QPixmap(path)

    @err_catcher(name=__name__)
    def grabArea(self):
        self.setWindowOpacity(0)
        from PrismUtils import ScreenShot

        previewImg = ScreenShot.grabScreenArea(self.core)
        self.setWindowOpacity(1)

        if previewImg is not None:
            self.l_preview.setPixmap(
                previewImg.scaled(
                    self.l_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            self.previewDefined = True

    @err_catcher(name=__name__)
    def getDetails(self):
        details = {
            "description": self.e_description.toPlainText(),
            "username": self.core.getConfig("globals", "UserName"),
        }
        self.core.callback(
            name="onGetSaveExtendedDetails",
            types=["curApp", "custom"],
            args=[self, details],
        )
        return details
