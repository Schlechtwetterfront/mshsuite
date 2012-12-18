import sys
import msh2_unpack
import os
from PySide.QtGui import QMainWindow, QApplication, QFrame, QGridLayout, QLabel, \
                        QLineEdit, QGroupBox, QSpinBox, QDoubleSpinBox, QPushButton, \
                        QHBoxLayout, QVBoxLayout, QListView, QFileDialog, \
                        QMessageBox
from PySide import QtCore
import model_dialogs
import material_dialogs
import misc_dialogs

SUITE_VER = 0.4
WIDTH_LAUNCH = 200
HEIGHT_LAUNCH = 50
WIDTH_MSH = 400
HEIGHT_MSH = 600


class ModelsModel(QtCore.QAbstractListModel):
    def __init__(self, mcoll, parent=None):
        super(ModelsModel, self).__init__(parent)
        self.coll = mcoll

    def rowCount(self, parent):
        return len(self.coll)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.coll[index.row()].name
        elif role == QtCore.Qt.UserRole + 1:
            return self.coll[index.row()]


class MaterialsModel(QtCore.QAbstractListModel):
    def __init__(self, mcoll, parent=None):
        super(MaterialsModel, self).__init__(parent)
        self.coll = mcoll

    def rowCount(self, parent):
        return len(self.coll)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return '{0}'.format(self.coll[index.row()].name)
        elif role == QtCore.Qt.UserRole + 1:
            return self.coll[index.row()]


class InfoManager:
    def __init__(self, info, main):
        self.info = info
        self.main = main
        self.bbox_dialog = False

    def get_frame(self):
        # Info stuff.
        self.infos = {}
        infogrp = QGroupBox('Scene Info')
        grdlay = QGridLayout()
        grdlay.addWidget(QLabel('<b>Name</b>'), 0, 0)
        namebox = QLineEdit()
        self.infos['name'] = namebox
        namebox.setText(self.info.name)

        rangebox1 = QSpinBox()
        rangebox1.setMinimum(0)
        rangebox1.setMaximum(1000)
        self.infos['rangestart'] = rangebox1
        rangebox1.setValue(self.info.frame_range[0])

        rangebox2 = QSpinBox()
        rangebox2.setMinimum(0)
        rangebox2.setMaximum(1000)
        self.infos['rangeend'] = rangebox2
        rangebox2.setValue(self.info.frame_range[1])

        fpsbox = QDoubleSpinBox()
        self.infos['fps'] = fpsbox
        fpsbox.setValue(self.info.fps)

        bbox_btn = QPushButton('Bounding Box')
        bbox_btn.clicked.connect(self.edit_bbox)
        grdlay.addWidget(namebox, 0, 1)
        grdlay.addWidget(QLabel('<b>StartFrame</b>'), 1, 0)
        grdlay.addWidget(rangebox1, 1, 1)
        grdlay.addWidget(QLabel('<b>EndFrame</b>'), 1, 2)
        grdlay.addWidget(fpsbox, 0, 3)
        grdlay.addWidget(rangebox2, 1, 3)
        grdlay.addWidget(QLabel('<b>FPS</b>'), 0, 2)

        grdlay.addWidget(bbox_btn, 2, 0)

        grplay = QVBoxLayout()
        grplay.addLayout(grdlay)
        #grplay.addStretch()
        infogrp.setLayout(grplay)

        return infogrp

    def edit_bbox(self):
        self.bd = misc_dialogs.BBoxDialog(self.info.bbox, self.main)

    def save(self):
        self.info.name = self.infos['name'].text()
        self.info.frame_range = int(self.infos['rangestart'].text()), int(self.infos['rangeend'].text())
        self.info.fps = float(self.infos['fps'].text().replace(',', '.'))


class MaterialManager:
    def __init__(self, matcoll, main):
        self.matcoll = matcoll
        self.main = main
        self.materials_model = MaterialsModel(matcoll)
        self.material_dialogs = {}
        for mat in self.materials_model.coll:
            self.material_dialogs[mat.name] = None

    def get_frame(self):
        # Material stuff.
        listvmd = QListView()
        listvmd.setMaximumWidth(150)
        listvmd.setModel(self.materials_model)
        listvmd.doubleClicked.connect(self.edit_mat)
        listvmd.setResizeMode(listvmd.ResizeMode.Adjust)
        self.listview = listvmd

        return listvmd

    def edit_mat(self):
        ind = self.listview.currentIndex()
        mat = self.materials_model.data(ind, QtCore.Qt.UserRole + 1)
        if self.material_dialogs[mat.name]:
            return
        self.material_dialogs[mat.name] = material_dialogs.MaterialDialog(mat, self.main)

    def count(self):
        return len(self.materials_model.coll)


class ModelManager:
    def __init__(self, mdlcoll, main):
        self.mdlcoll = mdlcoll
        self.main = main
        self.models_model = ModelsModel(mdlcoll)
        self.model_dialogs = {}
        for mdl in self.models_model.coll:
            self.model_dialogs[mdl.name] = None

    def get_frame(self):
        listvmd = QListView()
        listvmd.setMaximumWidth(150)
        listvmd.setModel(self.models_model)
        listvmd.doubleClicked.connect(self.edit_mdl)
        listvmd.setResizeMode(listvmd.ResizeMode.Adjust)
        self.listview = listvmd

        return listvmd

    def edit_mdl(self):
        ind = self.listview.currentIndex()
        mdl = self.models_model.data(ind, QtCore.Qt.UserRole + 1)
        if self.model_dialogs[mdl.name]:
            return
        self.model_dialogs[mdl.name] = model_dialogs.ModelDialog(mdl, self.main)

    def count(self):
        return len(self.models_model.coll)


class AnimManager:
    def __init__(self, anim):
        self.anim = anim

    def get_frame(self):
        frame = QFrame()

        return frame


class LaunchScreen(QMainWindow):
    def __init__(self, parent=None):
        super(LaunchScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        open_msh_btn = QPushButton('Open .MSH...')
        open_msh_btn.clicked.connect(self.load_msh)
        open_msh_btn.setToolTip('<b>Loads a .MSH file</b> for editing.')
        dump_msh_btn = QPushButton('Dump .MSH...')
        dump_msh_btn.clicked.connect(self.dump_msh)
        dump_msh_btn.setToolTip('<b>Dumps .MSH file information</b> into a text file.')
        munge_anim_btn = QPushButton('Munge Animation')
        munge_anim_btn.clicked.connect(self.munge_anim)
        munge_anim_btn.setToolTip('<b>Launches the AnimMunger.</b>')
        buttonslay = QGridLayout()
        buttonslay.addWidget(open_msh_btn, 1, 1)
        buttonslay.addWidget(dump_msh_btn, 1, 3)
        buttonslay.addWidget(munge_anim_btn, 3, 1)

        frame = QFrame()
        frame.setLayout(buttonslay)
        self.setCentralWidget(frame)

        self.setGeometry(200, 100, WIDTH_LAUNCH, HEIGHT_LAUNCH)
        self.setWindowTitle('MSH Suite')
        self.show()

    def about(self):
        pass

    def munge_anim(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, 'Select .MSH', os.getcwd(), 'MSH  Files (*.msh)')
        self.am = misc_dialogs.AnimMungeDialog(filenames, self, self)

    def init_msh_classes(self):
        self.infomanager = InfoManager(self.msh.info, self)
        self.matmanager = MaterialManager(self.msh.materials, self)
        self.mdlmanager = ModelManager(self.msh.models, self)

    def init_msh_ui(self):
        comps = QGroupBox('Components')

        mdlgr = QGroupBox('Models - {0}'.format(self.mdlmanager.count()))
        mdllay = QVBoxLayout()
        mdllay.addWidget(self.mdlmanager.get_frame())
        #mdllay.addStretch()
        mdlgr.setLayout(mdllay)
        matgr = QGroupBox('Materials - {0}'.format(self.matmanager.count()))
        matlay = QVBoxLayout()
        matlay.addWidget(self.matmanager.get_frame())
        #matlay.addStretch()
        matgr.setLayout(matlay)
        frame2lay = QHBoxLayout()
        frame2lay.addWidget(matgr)
        frame2lay.addWidget(mdlgr)
        comps.setLayout(frame2lay)

        # Misc stuff.
        self.setGeometry(200, 100, WIDTH_MSH, HEIGHT_MSH)
        frame = QFrame()
        framelay = QVBoxLayout()
        framelay.addWidget(self.infomanager.get_frame())
        framelay.addWidget(comps)
        #framelay.addStretch()

        load = QPushButton('Open')
        load.clicked.connect(self.load_msh)
        save = QPushButton('Save')
        save.clicked.connect(self.save)
        close = QPushButton('Close')
        close.clicked.connect(self.close)
        btnlay = QHBoxLayout()
        btnlay.addWidget(QLabel('<b>MSH Suite</b> Version {0}'.format(SUITE_VER)))
        btnlay.addStretch()
        btnlay.addWidget(load)
        btnlay.addWidget(save)
        btnlay.addWidget(close)

        framelay.addLayout(btnlay)
        frame.setLayout(framelay)

        self.setCentralWidget(frame)
        self.setWindowTitle('MSH Suite - {0}'.format(self.msh.info.name))

    def dump_msh(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select .MSH', os.getcwd(), 'MSH  Files (*.msh)')
        mup = msh2_unpack.MSHUnpack(filename)
        msh = mup.unpack()
        msh.dump(filename + '.dump')
        msg_box = QMessageBox()
        msg_box.setWindowTitle('MSH Suite')
        msg_box.setText('Dumped to {0}.'.format(filename + '.dump'))
        msg_box.exec_()

    def load_msh(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select .MSH', os.getcwd(), 'MSH  Files (*.msh)')
        if not filename:
            return
        mup = msh2_unpack.MSHUnpack(filename, {'do_logging': True,
                                                'ignore_geo': False,
                                                'debug': False,
                                                'safe': False,
                                                'triangulate': False})
        self.msh = mup.unpack()
        self.init_msh_classes()
        self.init_msh_ui()

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save .MSH', os.getcwd(), 'MSH Files (*.msh)')
        if not filename:
            return
        data = self.msh.repack()
        self.infomanager.save()
        with open(filename, 'wb') as fh:
            fh.write(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = LaunchScreen()
    sys.exit(app.exec_())
