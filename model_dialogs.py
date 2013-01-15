from PySide.QtGui import QGroupBox, QGridLayout, QGraphicsScene, QGraphicsView, QDialog, \
                        QLineEdit, QLabel, QComboBox, QCheckBox, QHBoxLayout, QVBoxLayout, \
                        QPushButton, QSpinBox, QFileDialog, QBrush, QPen, QColor, QPainter, \
                        QPixmap, QListWidget, QDoubleSpinBox, QListView
from PySide.QtCore import QSize, Qt, QRectF, QAbstractListModel
import msh2
import os
import shutil
import misc_dialogs

STR_CODEC = 'ascii'


class ModelDialog(QDialog):
    types = ['null',
            'geodynamic',
            'cloth',
            'bone',
            'geobone',
            'geostatic',
            'geoshadow']
    types2 = {'null': 0,
            'geodynamic': 1,
            'cloth': 2,
            'bone': 3,
            'geobone': 4,
            'geostatic': 5,
            'geoshadow': 6}

    def __init__(self, mdl, parent=None):
        super(ModelDialog, self).__init__(parent)
        self.mdl = mdl
        self.controls = {}
        self.parent = parent
        self.initUI()

    def initUI(self):
        grp = QGroupBox('Model')
        grplay = QGridLayout()

        name = QLineEdit()
        name.setText(self.mdl.name)
        name.textChanged.connect(self.name_changed)
        self.controls['name'] = name

        grplay.addWidget(QLabel('Name'), 0, 0)
        grplay.addWidget(name, 0, 1)

        parent = QLineEdit()
        parent.setText(self.mdl.parent_name)
        self.controls['parent'] = parent

        grplay.addWidget(QLabel('Parent'), 0, 2)
        grplay.addWidget(parent, 0, 3)

        type_ = QComboBox()
        type_.addItems(self.types)
        type_.setCurrentIndex(self.types2[self.mdl.model_type])
        self.controls['type'] = type_

        grplay.addWidget(QLabel('Type'), 1, 0)
        grplay.addWidget(type_, 1, 1)

        vis = QCheckBox()
        if self.mdl.vis:
            vis.toggle()
        self.controls['vis'] = vis

        grplay.addWidget(QLabel('Hidden'), 1, 2)
        grplay.addWidget(vis, 1, 3)

        buttonlay = QHBoxLayout()

        collprim = QPushButton('Collision Primitive')
        buttonlay.addWidget(collprim)
        collprim.clicked.connect(self.edit_collprim)

        deformers = QPushButton('Deformers')
        deformers.clicked.connect(self.edit_deformers)
        buttonlay.addWidget(deformers)

        bbox_btn = QPushButton('Bounding Box')
        bbox_btn.clicked.connect(self.edit_bbox)

        trans = QPushButton('Transform')
        trans.clicked.connect(self.edit_tran)

        buttonlay.addWidget(bbox_btn)
        buttonlay.addWidget(trans)

        buttonlay2 = QHBoxLayout()

        validate = QPushButton('Validate')
        validate.clicked.connect(self.validate)

        uvs = QPushButton('UVs')
        uvs.clicked.connect(self.show_uvs)

        buttonlay2.addWidget(validate)
        buttonlay2.addWidget(uvs)
        buttonlay2.addStretch()

        grplay.addLayout(buttonlay, 2, 0, 1, 4)
        grplay.addLayout(buttonlay2, 3, 0, 1, 4)
        grp.setLayout(grplay)

        geogrp = QGroupBox('Geometry')
        geolay = QHBoxLayout()

        self.geometries = QListWidget()
        self.geometries.addItems(['{0} - {1}'.format(ind, geo.classname) for ind, geo in enumerate(self.mdl.segments)])

        geolay.addStretch()
        geolay.addWidget(self.geometries)

        edit_geo = QPushButton('Edit')
        edit_geo.clicked.connect(self.edit_geo)

        geolay.addWidget(edit_geo)

        geogrp.setLayout(geolay)

        btns = QHBoxLayout()

        save = QPushButton('Save')
        save.clicked.connect(self.save)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close)
        self.status = QLabel('Model Edit Mode')

        btns.addWidget(self.status)
        btns.addStretch()
        btns.addWidget(save)
        btns.addWidget(cancel)

        mainlay = QVBoxLayout()
        mainlay.addWidget(grp)
        mainlay.addWidget(geogrp)
        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 400, 200)
        self.setWindowTitle('MSH Suite - {0}'.format(self.mdl.name))
        self.show()

    def edit_geo(self):
        ind = self.geometries.currentIndex()
        item = self.geometries.itemFromIndex(ind)
        if not item:
            return
        geo = item.text().split('-')
        index = int(geo[0].strip())
        geo = self.mdl.segments[index]
        if geo.classname in ('SegmentGeometry', 'ClothGeometry'):
            gd = GeometryDialog(self, geo)


    def show_uvs(self):
        di = misc_dialogs.DoubleInt(self.render_uvs, self, 'Width', 'Height', 512, 512)

    def render_uvs(self, width, height):
        if ('geo' in self.mdl.model_type) or self.mdl.model_type == 'cloth':
            uvv = UVViewer(self.mdl, width, height, self)

    def print_faces(self):
        segm = self.mdl.segments[0]
        print len(segm.faces)
        for face in segm.faces:
            print 'Face'
            print '\t{0}'.format(face.sides)
            print '\t{0}'.format(face.SIindices())

    def edit_bbox(self):
        self.bd = misc_dialogs.BBoxDialog(self.mdl.bbox, self.parent)

    def edit_collprim(self):
        self.dd = CollisionPrimDialog(self.mdl, self.parent)

    def edit_deformers(self):
        self.dd = DeformerDialog(self.mdl, self.parent)

    def edit_tran(self):
        et = misc_dialogs.TransformDialog(self.mdl.transform, self.parent)

    def name_changed(self):
        self.status.setText(' Remember: change parent of child models.')

    def validate(self):
        # Check parent.
        parent = self.controls['parent'].text()
        if parent:
            if not self.parent.mdlmanager.mdlcoll.by_name(parent):
                self.controls['parent'].setStyleSheet('QWidget { color: red}')
            else:
                self.controls['parent'].setStyleSheet('QWidget { color: black}')
            if parent == self.controls['name'].text():
                self.controls['parent'].setStyleSheet('QWidget { color: red}')
        else:
            self.controls['parent'].setStyleSheet('QWidget { color: black}')
        self.status.setText('Validate done.')

    def save(self):
        self.mdl.name = self.controls['name'].text().encode(STR_CODEC)
        self.mdl.parent = self.controls['parent'].text().encode(STR_CODEC)
        self.mdl.vis = self.controls['vis'].isChecked()
        self.close()


class UVViewer(QDialog):
    def __init__(self, model, w, h, parent=None):
        super(UVViewer, self).__init__(parent)
        self.w = w
        self.h = h
        self.mdl = model
        self.white_b = QBrush(Qt.white)
        self.black_b = QBrush(Qt.black)
        self.pen_width = 2
        self.initUI()

    def initUI(self):
        mainlay = QVBoxLayout()
        scn = QGraphicsScene(0, 0, self.w, self.h)

        self.view = QGraphicsView()
        self.view.setScene(scn)
        self.view.setSceneRect(QRectF(0, 0, self.w, self.h))
        self.view.setMaximumWidth(self.w)
        self.view.setMaximumHeight(self.h)

        mainlay.addWidget(self.view)

        btns = QHBoxLayout()
        btns.addStretch()

        self.pen_w = QSpinBox()
        self.pen_w.setValue(self.pen_width)
        redraw = QPushButton('Redraw')
        redraw.clicked.connect(self.draw_uvs)
        save = QPushButton('Save')
        save.clicked.connect(self.save)
        close = QPushButton('Close')
        close.clicked.connect(self.close)

        btns.addWidget(QLabel('Stroke Width'))
        btns.addWidget(self.pen_w)
        btns.addWidget(redraw)
        btns.addWidget(save)
        btns.addWidget(close)

        mainlay.addLayout(btns)

        self.draw_uvs()

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 512, 560)
        self.setWindowTitle('MSH Suite UV Viewer')
        self.show()

    def draw_uvs(self):
        self.img = QPixmap(QSize(self.w, self.h))
        pen = QPen()
        pen.setWidth(int(self.pen_w.text()))
        pen.setBrush(QBrush(Qt.white))
        pen.setColor(QColor('white'))
        painter = QPainter()
        painter.begin(self.img)
        painter.setPen(pen)
        coords = self.get_coords()
        for face in coords:
            for n in xrange(len(face) - 1):
                print face[n][0], face[n][1], face[n + 1][0], face[n + 1][1]
                painter.drawLine(face[n][0], face[n][1], face[n + 1][0], face[n + 1][1])
        painter.end()
        self.view.scene().addPixmap(self.img)

    def get_coords(self):
        coords = []
        for seg in self.mdl.segments:
            if seg.classname == 'SegmentGeometry':
                print 'doing stuff'
                vcoll = seg.vertices
                for face in seg.faces:
                    face_coords = []
                    for v in face.SIindices():
                        face_coords.append((vcoll[v].u * self.w, (1 - vcoll[v].v) * self.h))
                    face_coords.append((vcoll[face.vertices[0]].u * self.w,
                                        (1 - vcoll[face.vertices[0]].v) * self.h))
                    coords.append(face_coords)
                    #print face_coords
        return coords

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save UV Mesh', os.getcwd(), 'PNG Files (*.png)')
        if not filename:
            return
        self.img.save(filename, 'PNG')
        self.close()


class DeformerDialog(QDialog):
    def __init__(self, model, parent=None):
        super(DeformerDialog, self).__init__(parent)
        self.mdl = model
        self.initUI()

    def initUI(self):
        mainlay = QVBoxLayout()
        mainlay.addWidget(QLabel('<b>Deformers ({0})</b>'.format(len(self.mdl.deformers))))

        def_list = QListWidget()
        for index, el in enumerate(self.mdl.deformers):
            def_list.addItem('{0} - {1}'.format(index, el))
        #def_list.addItems(self.mdl.deformers)
        mainlay.addWidget(def_list)

        self.def_list = def_list

        btns = QHBoxLayout()
        btns.addStretch()

        save = QPushButton('Save')
        save.clicked.connect(self.save)
        close = QPushButton('Close')
        close.clicked.connect(self.close)

        btns.addWidget(save)
        btns.addWidget(close)

        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 200, 400)
        self.setWindowTitle('MSH Suite - {0} Deformers'.format(self.mdl.name))
        self.show()

    def save(self):
        self.close()


class CollisionPrimDialog(QDialog):
    def __init__(self, model, parent=None):
        super(CollisionPrimDialog, self).__init__(parent)
        self.mdl = model
        self.controls = {}
        self.initUI()

    def initUI(self):
        grp = QGroupBox('Collision Primitive')
        grplay = QGridLayout()
        grp.setLayout(grplay)

        enabled = QCheckBox()
        benable = False
        if self.mdl.collprim:
            enabled.toggle()
            benable = True
        enabled.stateChanged.connect(self.enabled_changed)
        self.controls['collprim'] = enabled
        grplay.addWidget(QLabel('Enabled'), 0, 0)
        grplay.addWidget(enabled, 0, 1)

        widthl = QLabel('Dflt')
        grplay.addWidget(widthl, 1, 0)
        width = QDoubleSpinBox()
        width.setEnabled(benable)
        width.setValue(self.mdl.primitive[1])
        grplay.addWidget(width, 1, 1)
        self.controls['width'] = width
        self.controls['widthl'] = widthl

        heightl = QLabel('Dflt')
        grplay.addWidget(heightl, 1, 2)
        height = QDoubleSpinBox()
        height.setEnabled(benable)
        height.setValue(self.mdl.primitive[2])
        grplay.addWidget(height, 1, 3)
        self.controls['height'] = height
        self.controls['heightl'] = heightl

        depthl = QLabel('Dflt')
        grplay.addWidget(depthl, 1, 4)
        depth = QDoubleSpinBox()
        depth.setEnabled(benable)
        depth.setValue(self.mdl.primitive[3])
        grplay.addWidget(depth, 1, 5)
        self.controls['depth'] = depth
        self.controls['depthl'] = depthl

        numbox = QComboBox()
        numbox.addItems(self.mdl.collprim_by_name.keys())
        numbox.currentIndexChanged.connect(self.type_changed)
        numbox.setEnabled(benable)
        grplay.addWidget(QLabel('Type'), 0, 2)
        grplay.addWidget(numbox, 0, 3)
        self.controls['collprimtype'] = numbox
        if self.mdl.primitive[0] == 0:
            numbox.setCurrentIndex(0)
        elif self.mdl.primitive[0] == 1:
            numbox.setCurrentIndex(0)
        elif self.mdl.primitive[0] == 2:
            numbox.setCurrentIndex(1)
        elif self.mdl.primitive[0] == 4:
            numbox.setCurrentIndex(2)

        mainlay = QVBoxLayout()
        mainlay.addWidget(grp)

        btns = QHBoxLayout()
        btns.addStretch()

        save = QPushButton('Save')
        save.clicked.connect(self.save)
        close = QPushButton('Close')
        close.clicked.connect(self.close)

        btns.addWidget(save)
        btns.addWidget(close)

        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 200, 120)
        self.setWindowTitle('MSH Suite - {0} Collision Primitive'.format(self.mdl.name))
        self.update_labels()
        self.show()

    def enabled_changed(self):
        enable = self.controls['collprim'].isChecked()
        self.controls['collprimtype'].setEnabled(enable)
        self.controls['width'].setEnabled(enable)
        self.controls['depth'].setEnabled(enable)
        self.controls['height'].setEnabled(enable)
        self.update_labels()

    def type_changed(self, new_text):
        self.update_labels()

    def update_labels(self):
        if self.controls['collprimtype'].currentText() == 'Cube':
            self.controls['widthl'].setText('Width')
            self.controls['depthl'].setText('Depth')
            self.controls['heightl'].setText('Height')
            self.controls['width'].setEnabled(True)
            self.controls['depth'].setEnabled(True)
            self.controls['height'].setEnabled(True)
        elif self.controls['collprimtype'].currentText() == 'Cylinder':
            self.controls['widthl'].setText('Radius')
            self.controls['depthl'].setText('')
            self.controls['heightl'].setText('Height')
            self.controls['width'].setEnabled(True)
            self.controls['depth'].setEnabled(False)
            self.controls['height'].setEnabled(True)
        elif self.controls['collprimtype'].currentText() == 'Sphere':
            self.controls['widthl'].setText('Radius')
            self.controls['depthl'].setText('')
            self.controls['heightl'].setText('')
            self.controls['width'].setEnabled(True)
            self.controls['depth'].setEnabled(False)
            self.controls['height'].setEnabled(False)

    def save(self):
        self.mdl.primitive = (self.mdl.get_collprim_index(self.controls['collprimtype'].currentText()),
                                float(self.controls['width'].text().replace(',', '.')),
                                float(self.controls['height'].text().replace(',', '.')),
                                float(self.controls['depth'].text().replace(',', '.')))
        self.mdl.collprim = self.controls['collprim'].isChecked()
        self.close()


class VertexModel(QAbstractListModel):
    def __init__(self, vcoll, parent=None):
        super(VertexModel, self).__init__(parent)
        self.vcoll = vcoll

    def rowCount(self, parent):
        return len(self.vcoll)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return 'Vertex({0}, {1}, {2})'.format(round(self.vcoll[index.row()].pos[0], 2), round(self.vcoll[index.row()].pos[1], 2), round(self.vcoll[index.row()].pos[2], 2))
        elif role == Qt.UserRole + 1:
            return self.vcoll[index.row()]


class FaceModel(QAbstractListModel):
    def __init__(self, fcoll, parent=None):
        super(FaceModel, self).__init__(parent)
        self.fcoll = fcoll

    def rowCount(self, parent):
        return len(self.fcoll)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return 'Face'
        elif role == Qt.UserRole + 1:
            return self.vcoll[index.row()]


class GeometryDialog(QDialog):
    def __init__(self, parent, geo):
        super(GeometryDialog, self).__init__(parent)
        self.geo = geo
        self.vmodel = VertexModel(self.geo.vertices, self)
        self.fmodel = FaceModel(self.geo.faces, self)
        self.init_UI()

    def init_UI(self):
        maingrp = QGroupBox(self.geo.classname)
        grplay = QGridLayout()

        vertices = QListView()
        vertices.setModel(self.vmodel)
        vertices.doubleClicked.connect(self.edit_vertex)
        self.v = vertices

        faces = QListView()
        faces.setModel(self.fmodel)

        grplay.addWidget(vertices, 0, 0, 2, 2)
        grplay.addWidget(faces, 0, 2, 2, 2)

        maingrp.setLayout(grplay)

        mainlay = QHBoxLayout()
        mainlay.addWidget(maingrp)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 400, 500)
        self.setWindowTitle('MSH Suite - Geometry Editor')
        self.show()

    def edit_vertex(self):
        ind = self.v.currentIndex()
        v = self.vmodel.data(ind, Qt.UserRole + 1)
        vd = VertexDialog(v, self)


class VertexDialog(QDialog):
    def __init__(self, v, parent=None):
        super(VertexDialog, self).__init__(parent)
        self.v = v
        self.controls = {}
        self.init_UI()

    def init_UI(self):
        lay = QGridLayout()
        lay.addWidget(QLabel('<b>Position</b>'), 0, 0, 1, 4)

        posx = QDoubleSpinBox()
        posx.setValue(self.v.x)
        self.controls['posx'] = posx

        posy = QDoubleSpinBox()
        posy.setValue(self.v.y)
        self.controls['posy'] = posy

        posz = QDoubleSpinBox()
        posz.setValue(self.v.z)
        self.controls['posz'] = posz

        lay.addWidget(posx, 1, 0)
        lay.addWidget(posy, 1, 1)
        lay.addWidget(posz, 1, 2)

        lay.addWidget(QLabel('<b>Normal</b>'), 2, 0, 1, 4)

        norx = QDoubleSpinBox()
        norx.setValue(self.v.nx)
        self.controls['norx'] = norx

        nory = QDoubleSpinBox()
        nory.setValue(self.v.ny)
        self.controls['nory'] = nory

        norz = QDoubleSpinBox()
        norz.setValue(self.v.nz)
        self.controls['norz'] = norz

        lay.addWidget(norx, 3, 0)
        lay.addWidget(nory, 3, 1)
        lay.addWidget(norz, 3, 2)

        lay.addWidget(QLabel('<b>Texture Coordinates</b>'), 4, 0, 1, 4)

        u = QDoubleSpinBox()
        u.setValue(self.v.u)
        self.controls['u'] = u

        v = QDoubleSpinBox()
        v.setValue(self.v.v)
        self.controls['v'] = v

        lay.addWidget(u, 5, 0)
        lay.addWidget(v, 5, 1)

        lay.addWidget(QLabel('<b>Color</b>'), 6, 0, 1, 4)

        red = QSpinBox()
        red.setMinimum(0)
        red.setMaximum(255)
        red.setValue(self.v.color.red)
        self.controls['red'] = red

        green = QSpinBox()
        green.setMinimum(0)
        green.setMaximum(255)
        green.setValue(self.v.color.green)
        self.controls['green'] = green

        blue = QSpinBox()
        blue.setMinimum(0)
        blue.setMaximum(255)
        blue.setValue(self.v.color.blue)
        self.controls['blue'] = blue

        alpha = QSpinBox()
        alpha.setMinimum(0)
        alpha.setMaximum(255)
        alpha.setValue(self.v.color.alpha)
        self.controls['alpha'] = alpha

        lay.addWidget(red, 7, 0)
        lay.addWidget(green, 7, 1)
        lay.addWidget(blue, 7, 2)
        lay.addWidget(alpha, 7, 3)

        grp = QGroupBox('Vertex')
        grp.setLayout(lay)

        btns = QVBoxLayout()
        save = QPushButton('Save')
        save.clicked.connect(self.save)

        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close)

        btns.addStretch()
        btns.addWidget(save)
        btns.addWidget(cancel)

        mainlay = QHBoxLayout()
        mainlay.addWidget(grp)
        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 300, 250)
        self.setWindowTitle('MSH Suite - Vertex Editor')
        self.show()

    def save(self):
        self.v.x = self.controls['posx'].value()
        self.v.y = self.controls['posy'].value()
        self.v.z = self.controls['posz'].value()

        self.v.nx = self.controls['norx'].value()
        self.v.ny = self.controls['nory'].value()
        self.v.nz = self.controls['norz'].value()

        self.v.u = self.controls['u'].value()
        self.v.v = self.controls['v'].value()

        self.v.color.red = self.controls['red'].value()
        self.v.color.green = self.controls['green'].value()
        self.v.color.blue = self.controls['blue'].value()
        self.v.color.alpha = self.controls['alpha'].value()
        self.close()
