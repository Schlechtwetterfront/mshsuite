from PySide.QtGui import *
import msh2
import os
import shutil

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
        # TODO: dialog

        deformers = QPushButton('Deformers')
        buttonlay.addWidget(deformers)
        # TODO: dialog

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
        buttonlay2.addStretch()

        grplay.addLayout(buttonlay, 2, 0, 1, 4)
        grplay.addLayout(buttonlay2, 3, 0, 1, 4)
        grp.setLayout(grplay)

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
        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 400, 200)
        self.setWindowTitle('MSH Suite - {0}'.format(self.mdl.name))
        self.show()

    def show_uvs(self):


    def print_faces(self):
        segm = self.mdl.segments[0]
        print len(segm.faces)
        for face in segm.faces:
            print 'Face'
            print '\t{0}'.format(face.sides)
            print '\t{0}'.format(face.SIindices())

    def edit_bbox(self):
        self.bd = BBoxDialog(self.mdl.bbox, self.parent)

    def edit_tran(self):
        et = TransformDialog(self.mdl.transform, self.parent)

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
        self.close()


class MaterialDialog(QDialog):
    pretty_flags = {'specular': '<b>Specular</b>',
                    'additive': '<b>Additive Transp.</b>',
                    'perpixel': '<b>Per-Pixel Lighting</b>',
                    'hard': '<b>Hardedged Transp.</b>',
                    'double': '<b>Doublesided Transp.</b>',
                    'single': '<b>Singlesided Transp.</b>',
                    'glow': '<b>Glow</b>',
                    'emissive': '<b>Emissive</b>'}
    render_types = ['Standard',
                    'Glow',
                    'Detail',
                    'Scrolling',
                    'Specular',
                    'Glossmap',
                    'Chrome',
                    'Animated',
                    'Ice',
                    'Sky',
                    'Water',
                    'Lightmap',
                    '2 Scroll',
                    'Rotate',
                    'Glow Rotate',
                    'Planar Reflection',
                    'Glow Scroll',
                    'Glow 2 Scroll',
                    'Curved Reflection',
                    'Normalmap Fade',
                    'Normalmap Inv Fade',
                    'Ice Reflection',
                    'Ice Refraction',
                    'Emboss',
                    'Wireframe',
                    'Engergy',
                    'Afterburner',
                    'Bumpmap',
                    'Bumpmap + Glossmap',
                    'Teleportal',
                    'MultiState',
                    'Shield']
    render_types2 = {'Standard': 0,
                    'Glow': 1,
                    'Detail': 2,
                    'Scrolling': 3,
                    'Specular': 4,
                    'Glossmap': 5,
                    'Chrome': 6,
                    'Animated': 7,
                    'Ice': 8,
                    'Sky': 9,
                    'Water': 10,
                    'Lightmap': 11,
                    '2 Scroll': 12,
                    'Rotate': 13,
                    'Glow Rotate': 14,
                    'Planar Reflection': 15,
                    'Glow Scroll': 16,
                    'Glow 2 Scroll': 17,
                    'Curved Reflection': 18,
                    'Normalmap Fade': 19,
                    'Normalmap Inv Fade': 20,
                    'Ice Reflection': 21,
                    'Ice Refraction': 22,
                    'Emboss': 23,
                    'Wireframe': 24,
                    'Energy': 25,
                    'Afterburner': 26,
                    'Bumpmap': 27,
                    'Bumpmap + Glossmap': 28,
                    'Teleportal': 29,
                    'MultiState': 30,
                    'Shield': 31}

    def __init__(self, mat, parent=None):
        super(MaterialDialog, self).__init__(parent)
        self.mat = mat
        self.controls = {}
        self.initUI()

    def initUI(self):
        grp = QGroupBox('Material')
        grplay = QGridLayout()

        name = QLineEdit()
        name.setText(self.mat.name)
        self.controls['name'] = name

        tex0 = QLineEdit()
        tex0.setText(self.mat.tex0)
        self.controls['tex0'] = tex0

        tex1 = QLineEdit()
        tex1.setText(self.mat.tex1)
        self.controls['tex1'] = tex1

        tex2 = QLineEdit()
        tex2.setText(self.mat.tex2)
        self.controls['tex2'] = tex2

        tex3 = QLineEdit()
        tex3.setText(self.mat.tex3)
        self.controls['tex3'] = tex3

        flags = QGroupBox('Flags')
        fllay = QGridLayout()

        for ind, flag in enumerate(self.mat.flags):
            fllay.addWidget(QLabel(self.pretty_flags[flag[0]]), ind, 0)
            box = QCheckBox()
            fllay.addWidget(box, ind, 1)
            if flag[1]:
                box.toggle()
            self.controls[flag[0]] = box

        fllay.addWidget(QLabel('<b>RenderType</b>'), 8, 0)
        numbox = QComboBox()
        numbox.addItems(self.render_types)
        numbox.setCurrentIndex(self.mat.render_type)
        fllay.addWidget(numbox)
        self.controls['render_type'] = numbox

        fllay.addWidget(QLabel('<b>Data0</b>'), 9, 0)
        d0 = QSpinBox()
        d0.setValue(self.mat.data0)
        d0.setMinimum(0)
        d0.setMaximum(255)
        fllay.addWidget(d0)
        self.controls['data0'] = d0

        fllay.addWidget(QLabel('<b>Data1</b>'), 10, 0)
        d1 = QSpinBox()
        d1.setValue(self.mat.data1)
        d1.setMinimum(0)
        d1.setMaximum(255)
        fllay.addWidget(d1)
        self.controls['data1'] = d1

        flags.setLayout(fllay)

        colors = QGroupBox('Colors')
        collay = QGridLayout()

        self.add_color('<b>Diffuse</b>', self.mat.diff_color, collay, 3)
        self.add_color('<b>Specular</b>', self.mat.spec_color, collay, 4)
        self.add_color('<b>Ambient</b>', self.mat.ambt_color, collay, 5)

        colors.setLayout(collay)

        grplay.addWidget(QLabel('<b>Name</b>'), 0, 0)
        grplay.addWidget(name, 0, 1)

        grplay.addWidget(QLabel('<b>Texture0</b>'), 1, 0)
        grplay.addWidget(tex0, 1, 1)
        grplay.addWidget(QLabel('<b>Texture1</b>'), 1, 2)
        grplay.addWidget(tex1, 1, 3)

        grplay.addWidget(QLabel('<b>Texture2</b>'), 2, 0)
        grplay.addWidget(tex2, 2, 1)
        grplay.addWidget(QLabel('<b>Texture3</b>'), 2, 2)
        grplay.addWidget(tex3, 2, 3)

        grplay.addWidget(QLabel('<b>Gloss</b>'), 3, 0)
        gloss = QDoubleSpinBox()
        gloss.setValue(self.mat.gloss)
        grplay.addWidget(gloss, 3, 1)
        self.controls['gloss'] = gloss

        grplay.addWidget(colors, 4, 0, 1, 5)
        grplay.addWidget(flags, 5, 0, 1, 3)

        grp.setLayout(grplay)

        btns = QHBoxLayout()

        save = QPushButton('Save')
        save.clicked.connect(self.save)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close)

        btns.addStretch()
        btns.addWidget(save)
        btns.addWidget(cancel)

        mainlay = QVBoxLayout()
        mainlay.addWidget(grp)
        mainlay.addLayout(btns)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 440, 200)
        self.setWindowTitle('MSH Suite - {0}'.format(self.mat.name))
        self.show()

    def save(self):
        self.mat.name = self.controls['name'].text().encode(STR_CODEC)
        self.mat.tex0 = self.controls['tex0'].text().encode(STR_CODEC)
        self.mat.tex1 = self.controls['tex1'].text().encode(STR_CODEC)
        self.mat.tex2 = self.controls['tex2'].text().encode(STR_CODEC)
        self.mat.tex3 = self.controls['tex3'].text().encode(STR_CODEC)
        new_flags = []
        for flag in self.mat.flags:
            new_flags.append((flag[0], self.controls[flag[0]].isChecked(), flag[2]))
        self.mat.flags = new_flags
        self.mat.render_type = self.render_types2[self.controls['render_type'].currentText()]
        self.mat.data0 = int(self.controls['data0'].text())
        self.mat.data1 = int(self.controls['data1'].text())
        self.mat.diff_color = msh2.Color((float(self.controls['<b>Diffuse</b>r'].text().replace(',', '.')),
                                            float(self.controls['<b>Diffuse</b>g'].text().replace(',', '.')),
                                            float(self.controls['<b>Diffuse</b>b'].text().replace(',', '.')),
                                            float(self.controls['<b>Diffuse</b>a'].text().replace(',', '.'))))
        self.mat.spec_color = msh2.Color((float(self.controls['<b>Specular</b>r'].text().replace(',', '.')),
                                            float(self.controls['<b>Specular</b>g'].text().replace(',', '.')),
                                            float(self.controls['<b>Specular</b>b'].text().replace(',', '.')),
                                            float(self.controls['<b>Specular</b>a'].text().replace(',', '.'))))
        self.mat.ambt_color = msh2.Color((float(self.controls['<b>Ambient</b>r'].text().replace(',', '.')),
                                            float(self.controls['<b>Ambient</b>g'].text().replace(',', '.')),
                                            float(self.controls['<b>Ambient</b>b'].text().replace(',', '.')),
                                            float(self.controls['<b>Ambient</b>a'].text().replace(',', '.'))))
        self.gloss = float(self.controls['gloss'].text().replace(',', '.'))
        self.close()

    def add_color(self, name, color, layout, row):
        layout.addWidget(QLabel('<b>{0}</b>'.format(name)), row, 0)
        layout.addWidget(QLabel('R'), row, 1)
        r = QDoubleSpinBox()
        r.setValue(color.red)
        r.setMinimum(0.0)
        r.setMaximum(1.0)
        layout.addWidget(r, row, 2)
        self.controls['{0}r'.format(name)] = r

        layout.addWidget(QLabel('G'), row, 3)
        g = QDoubleSpinBox()
        g.setValue(color.green)
        g.setMinimum(0.0)
        g.setMaximum(1.0)
        layout.addWidget(g, row, 4)
        self.controls['{0}g'.format(name)] = g

        layout.addWidget(QLabel('B'), row, 5)
        b = QDoubleSpinBox()
        b.setValue(color.blue)
        b.setMinimum(0.0)
        b.setMaximum(1.0)
        layout.addWidget(b, row, 6)
        self.controls['{0}b'.format(name)] = b

        layout.addWidget(QLabel('A'), row, 7)
        a = QDoubleSpinBox()
        a.setValue(color.alpha)
        a.setMinimum(0.0)
        a.setMaximum(1.0)
        layout.addWidget(a, row, 8)
        self.controls['{0}a'.format(name)] = a


class TransformDialog(QDialog):
    def __init__(self, tran, parent=None):
        super(TransformDialog, self).__init__(parent)
        self.tran = tran
        # Dict containing controls for saving.
        self.controls = {}
        self.initUI()

    def initUI(self):
        grp = QGroupBox('Transform')
        grplay = QGridLayout()
        # Translation
        grplay.addWidget(QLabel('<b>Translation</b>'), 0, 0)

        trax = QDoubleSpinBox()
        trax.setValue(self.tran.translation[0])
        self.controls['trax'] = trax
        grplay.addWidget(trax, 0, 1)

        tray = QDoubleSpinBox()
        tray.setValue(self.tran.translation[1])
        self.controls['tray'] = tray
        grplay.addWidget(tray, 0, 2)

        traz = QDoubleSpinBox()
        traz.setValue(self.tran.translation[2])
        self.controls['traz'] = traz
        grplay.addWidget(traz, 0, 3)

        # Rotation.
        grplay.addWidget(QLabel('<b>Rotation</b>'), 1, 0)

        rotx = QLineEdit()
        rotx.setText(str(self.tran.euler_angles()[0]))
        self.controls['rotx'] = rotx
        grplay.addWidget(rotx, 1, 1)

        roty = QLineEdit()
        roty.setText(str(self.tran.euler_angles()[1]))
        self.controls['roty'] = roty
        grplay.addWidget(roty, 1, 2)

        rotz = QLineEdit()
        rotz.setText(str(self.tran.euler_angles()[2]))
        self.controls['rotz'] = rotz
        grplay.addWidget(rotz, 1, 3)

        # Scale.
        grplay.addWidget(QLabel('<b>Scale</b>'), 2, 0)

        sclx = QDoubleSpinBox()
        sclx.setValue(self.tran.scale[0])
        self.controls['sclx'] = sclx
        grplay.addWidget(sclx, 2, 1)

        scly = QDoubleSpinBox()
        scly.setValue(self.tran.scale[1])
        self.controls['scly'] = scly
        grplay.addWidget(scly, 2, 2)

        sclz = QDoubleSpinBox()
        sclz.setValue(self.tran.scale[2])
        self.controls['sclz'] = sclz
        grplay.addWidget(sclz, 2, 3)

        grp.setLayout(grplay)
        # Buttons.
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.close)
        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)

        # Main Layout.
        mainlay = QVBoxLayout()
        mainlay.addWidget(grp)
        mainlay.addLayout(btns)
        mainlay.addStretch()

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 400, 100)
        self.setWindowTitle('MSH Suite - Edit BBox')
        self.show()

    def save(self):
        self.tran.translation = (float(self.controls['trax'].text().replace(',', '.')),
                            float(self.controls['tray'].text().replace(',', '.')),
                            float(self.controls['traz'].text().replace(',', '.')))
        self.tran.scale = (float(self.controls['sclx'].text().replace(',', '.')),
                            float(self.controls['scly'].text().replace(',', '.')),
                            float(self.controls['sclz'].text().replace(',', '.')))
        self.tran.euler_to_quaternion((float(self.controls['rotx'].text().replace(',', '.')),
                            float(self.controls['roty'].text().replace(',', '.')),
                            float(self.controls['rotz'].text().replace(',', '.'))))
        self.close()


class AnimMungeDialog(QDialog):
    types = ['FirstPerson/Soldier',
            'Prop/Vehicle']
    types2 = {'FirstPerson/Soldier': '/comp_debug 0 /debug',
                'Prop/Vehicle': '/specialquathack'}

    def __init__(self, files, main, parent=None):
        super(AnimMungeDialog, self).__init__(parent)
        self.outd = os.getcwd() + '\\munge\\output'
        self.ind = os.getcwd() + '\\munge\\input'
        self.files = files
        self.clear_input_files()
        self.clear_output_files()
        for filename in self.files:
            shutil.copy(filename, self.ind)
        self.initUI()

    def munge(self):
        self.statlabel.setText('<b>AnimMunging</b>')
        params = self.types2[self.type_box.currentText()]
        if self.bf1mode.isChecked():
            os.system(os.getcwd() + '\\zenasset1.exe /multimsh /src {0} /keepframe0 {1} /dest {2}\\{3}.zaf'.format(self.ind, params, self.outd, self.animname.text()))
            os.system(os.getcwd() + '\\binmunge1.exe -inputfile munge\\output\\*.zaa -chunkid zaa_ -ext zaabin -outputdir {1}\\'.format(self.outd, self.outd))
            os.system(os.getcwd() + '\\binmunge1.exe -inputfile munge\\output\\*.zaf -chunkid zaf_ -ext zafbin -outputdir {1}\\'.format(self.outd, self.outd))
        else:
            os.system(os.getcwd() + '\\zenasset.exe /multimsh /writefiles /src {0} /keepframe0 {1} /dest {2}\\{3}.zaf'.format(self.ind, params, self.outd, self.animname.text()))
            os.system(os.getcwd() + '\\binmunge.exe -inputfile munge\\output\\*.zaa -chunkid zaa_ -ext zaabin -outputdir {1}'.format(self.outd, self.outd))
            os.system(os.getcwd() + '\\binmunge.exe -inputfile munge\\output\\*.zaf -chunkid zaf_ -ext zafbin -outputdir {1}'.format(self.outd, self.outd))
        self.clear_byproduct()
        files = []
        for filename in os.listdir(self.outd):
            files.append(filename)
        self.outfiles.addItems(files)
        self.statlabel.setText('<b>AnimMunged</b>')

    def initUI(self):
        grp = QGroupBox('Anim Munge')
        grplay = QGridLayout()
        self.bf1mode = QCheckBox()
        grplay.addWidget(QLabel('<b>SWBF1</b>'), 0, 1)
        grplay.addWidget(self.bf1mode, 0, 2)
        grplay.addWidget(QLabel('<b>Input</b>'), 1, 1)
        grplay.addWidget(QLabel('<b>Output</b>'), 1, 3)
        self.infiles = QListWidget()
        self.infiles.setMinimumWidth(150)
        self.infiles.addItems([os.path.basename(item) for item in self.files])
        grplay.addWidget(self.infiles, 2, 1, 1, 2)
        self.outfiles = QListWidget()
        self.outfiles.setMinimumWidth(150)
        grplay.addWidget(self.outfiles, 2, 3, 1, 2)

        self.statlabel = QLabel('<b>AnimMunger</b>')
        grplay.addWidget(self.statlabel, 4, 1, 1, 1)
        self.animname = QLineEdit()
        self.animname.setText('AnimName')
        self.animname.setToolTip('<b>Animation Name.</b> Name of the final animation files. IE: name.zafbin, name.zaabin, name.anims.')
        grplay.addWidget(self.animname, 3, 1)
        self.type_box = QComboBox()
        self.type_box.addItems(self.types)
        self.type_box.setToolTip('<b>Munge Mode.</b> This switches munge parameters.')
        grplay.addWidget(QLabel('<b>Munge Mode:</b>'), 3, 2)
        grplay.addWidget(self.type_box, 3, 3, 1, 2)
        munge_btn = QPushButton('Munge')
        munge_btn.clicked.connect(self.munge)
        munge_btn.setToolTip('<b>Munge.</b> Munges the input files with the selected mode.')
        grplay.addWidget(munge_btn, 4, 2)
        save_out = QPushButton('Save')
        save_out.clicked.connect(self.save)
        save_out.setToolTip('<b>Save.</b> Saves the output files.')
        grplay.addWidget(save_out, 4, 3)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.cancel)
        cancel_btn.setToolTip('<b>Cancel.</b> Closes the dialog and removes all temporary files.')
        grplay.addWidget(cancel_btn, 4, 4)

        grp.setLayout(grplay)

        mainlay = QVBoxLayout()
        mainlay.addWidget(grp)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 320, 300)
        self.setWindowTitle('MSH Suite - Animation Munge')
        self.show()

    def save(self):
        filepath = QFileDialog.getExistingDirectory(self, 'Select .MSH', os.getcwd())
        for filename in os.listdir(self.outd):
            shutil.copy(os.path.join(self.outd, filename), filepath)
        self.cancel()

    def cancel(self):
        self.statlabel.setText('<b>AnimSeeYa</b>')
        self.clear_input_files()
        self.clear_output_files()
        self.close()

    def clear_byproduct(self):
        for filename in os.listdir(self.outd):
            if filename.split('.')[-1] in ('zaa', 'zaf'):
                os.unlink(os.path.join(self.outd, filename))

    def clear_output_files(self):
        for filename in os.listdir(self.outd):
            filepath = os.path.join(self.outd, filename)
            try:
                if os.path.isfile(filepath):
                    os.unlink(filepath)
            except Exception, e:
                print e

    def clear_input_files(self):
        for filename in os.listdir(self.ind):
            filepath = os.path.join(self.ind, filename)
            try:
                if os.path.isfile(filepath):
                    os.unlink(filepath)
            except Exception, e:
                print e
