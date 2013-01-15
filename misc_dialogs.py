from PySide.QtGui import QSpinBox, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, \
                            QLabel, QGroupBox, QDoubleSpinBox, QLineEdit, QCheckBox, QListWidget, \
                            QComboBox, QFileDialog
import msh2
import os
import shutil


class DoubleInt(QDialog):
    def __init__(self, cmd, parent=None, text_left='left', text_right='right',
                default1=0, default2=0):
        # cmd is a command which this dialog will call upon OKing.
        # The arguments are cmd(i1, i2), the two chosen ints.
        super(DoubleInt, self).__init__(parent)
        self.tr = text_right
        self.tl = text_left
        self.i1 = 0
        self.i2 = 0
        self.default1 = default1
        self.default2 = default2
        self.cmd = cmd
        self.initUI()

    def initUI(self):
        mainlay = QVBoxLayout()
        btns = QHBoxLayout()
        mainui = QGridLayout()

        mainlay.addLayout(mainui)
        mainlay.addLayout(btns)

        ok = QPushButton('OK')
        ok.clicked.connect(self.ok)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.close)

        btns.addStretch()
        btns.addWidget(ok)
        btns.addWidget(cancel)

        text1 = QLabel(self.tl)
        text2 = QLabel(self.tr)
        self.int1 = QSpinBox()
        self.int1.setMaximum(2048)
        self.int1.setMinimum(128)
        self.int1.setValue(self.default1)
        self.int2 = QSpinBox()
        self.int2.setMaximum(2048)
        self.int2.setMinimum(128)
        self.int2.setValue(self.default2)
        mainui.addWidget(text1, 0, 0)
        mainui.addWidget(text2, 0, 1)
        mainui.addWidget(self.int1, 1, 0)
        mainui.addWidget(self.int2, 1, 1)

        self.setLayout(mainlay)
        self.setGeometry(340, 340, 200, 100)
        self.setWindowTitle('MSH Suite - Double Integer')
        self.show()

    def ok(self):
        self.i1 = int(self.int1.text())
        self.i2 = int(self.int2.text())
        self.cmd(self.i1, self.i2)
        self.close()


class BBoxDialog(QDialog):
    def __init__(self, bbox, parent=None):
        super(BBoxDialog, self).__init__(parent)
        self.bbox = bbox
        # Dict containing controls for saving.
        self.controls = {}
        self.initUI()

    def initUI(self):
        grp = QGroupBox('Bounding Box')
        grplay = QGridLayout()

        # Extents.
        extx = QDoubleSpinBox()
        extx.setMinimum(0)
        extx.setMaximum(100)
        extx.setValue(self.bbox.extents[0])
        self.controls['extx'] = extx
        exty = QDoubleSpinBox()
        exty.setMinimum(0)
        exty.setMaximum(100)
        exty.setValue(self.bbox.extents[1])
        self.controls['exty'] = exty
        extz = QDoubleSpinBox()
        extz.setMinimum(0)
        extz.setMaximum(100)
        extz.setValue(self.bbox.extents[2])
        self.controls['extz'] = extz
        grplay.addWidget(QLabel('<b>Extents</b>'), 0, 0)
        grplay.addWidget(QLabel('X'), 0, 1)
        grplay.addWidget(extx, 0, 2)
        grplay.addWidget(QLabel('Y'), 0, 3)
        grplay.addWidget(exty, 0, 4)
        grplay.addWidget(QLabel('Z'), 0, 5)
        grplay.addWidget(extz, 0, 6)
        # Center.
        cntx = QDoubleSpinBox()
        cntx.setMinimum(-10000)
        cntx.setMaximum(10000)
        cntx.setValue(self.bbox.center[0])
        self.controls['cntx'] = cntx
        cnty = QDoubleSpinBox()
        cnty.setMinimum(-10000)
        cnty.setMaximum(10000)
        cnty.setValue(self.bbox.center[1])
        self.controls['cnty'] = cnty
        cntz = QDoubleSpinBox()
        cntz.setMinimum(-10000)
        cntz.setMaximum(10000)
        cntz.setValue(self.bbox.center[2])
        self.controls['cntz'] = cntz
        grplay.addWidget(QLabel('<b>Center</b>'), 1, 0)
        grplay.addWidget(QLabel('X'), 1, 1)
        grplay.addWidget(cntx, 1, 2)
        grplay.addWidget(QLabel('Y'), 1, 3)
        grplay.addWidget(cnty, 1, 4)
        grplay.addWidget(QLabel('Z'), 1, 5)
        grplay.addWidget(cntz, 1, 6)
        # Radius.
        radius = QDoubleSpinBox()
        cntz.setMinimum(0)
        cntz.setMaximum(10000)
        radius.setValue(self.bbox.radius)
        self.controls['radius'] = radius
        grplay.addWidget(QLabel('<b>BSphereRadius'), 2, 0)
        grplay.addWidget(radius, 2, 1, 1, 2)

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
        self.bbox.center = (float(self.controls['cntx'].text().replace(',', '.')),
                            float(self.controls['cnty'].text().replace(',', '.')),
                            float(self.controls['cntz'].text().replace(',', '.')))
        self.bbox.extents = (float(self.controls['extx'].text().replace(',', '.')),
                            float(self.controls['exty'].text().replace(',', '.')),
                            float(self.controls['extz'].text().replace(',', '.')))
        self.bbox.radius = float(self.controls['radius'].text().replace(',', '.'))
        self.close()


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
        trax.setMinimum(-10000)
        trax.setMaximum(10000)
        trax.setValue(self.tran.translation[0])
        self.controls['trax'] = trax
        grplay.addWidget(trax, 0, 1)

        tray = QDoubleSpinBox()
        tray.setMinimum(-10000)
        tray.setMaximum(10000)
        tray.setValue(self.tran.translation[1])
        self.controls['tray'] = tray
        grplay.addWidget(tray, 0, 2)

        traz = QDoubleSpinBox()
        traz.setMinimum(-10000)
        traz.setMaximum(10000)
        traz.setValue(self.tran.translation[2])
        self.controls['traz'] = traz
        grplay.addWidget(traz, 0, 3)

        # Rotation.
        grplay.addWidget(QLabel('<b>Rotation</b>'), 1, 0)

        rotx = QSpinBox()
        rotx.setMinimum(-10000)
        rotx.setMaximum(10000)
        #rotx.setText(str(self.tran.euler_angles()[0]))
        traz.setValue(self.tran.euler_angles()[0])
        self.controls['rotx'] = rotx
        grplay.addWidget(rotx, 1, 1)

        roty = QSpinBox()
        roty.setMinimum(-10000)
        roty.setMaximum(10000)
        #roty.setText(str(self.tran.euler_angles()[1]))
        traz.setValue(self.tran.euler_angles()[1])
        self.controls['roty'] = roty
        grplay.addWidget(roty, 1, 2)

        rotz = QSpinBox()
        rotz.setMinimum(-10000)
        rotz.setMaximum(10000)
        #rotz.setText(str(self.tran.euler_angles()[2]))
        traz.setValue(self.tran.euler_angles()[2])
        self.controls['rotz'] = rotz
        grplay.addWidget(rotz, 1, 3)

        # Scale.
        grplay.addWidget(QLabel('<b>Scale</b>'), 2, 0)

        sclx = QDoubleSpinBox()
        sclx.setMinimum(-10000)
        sclx.setMaximum(10000)
        sclx.setValue(self.tran.scale[0])
        self.controls['sclx'] = sclx
        grplay.addWidget(sclx, 2, 1)

        scly = QDoubleSpinBox()
        scly.setMinimum(-10000)
        scly.setMaximum(10000)
        scly.setValue(self.tran.scale[1])
        self.controls['scly'] = scly
        grplay.addWidget(scly, 2, 2)

        sclz = QDoubleSpinBox()
        sclz.setMinimum(-10000)
        sclz.setMaximum(10000)
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
        add_params = ''
        if self.add_params.text() != 'Additional Params':
            add_params = ' {0}'.format(self.add_params.text())
        if self.bf1mode.isChecked():
            os.system(os.getcwd() + '\\zenasset1.exe /multimsh /src {0}{1} /keepframe0 {2} /dest {3}\\{4}.zaf'.format(self.ind, add_params, params, self.outd, self.animname.text()))
            os.system(os.getcwd() + '\\binmunge1.exe -inputfile munge\\output\\*.zaa -chunkid zaa_ -ext zaabin -outputdir {1}\\'.format(self.outd, self.outd))
            os.system(os.getcwd() + '\\binmunge1.exe -inputfile munge\\output\\*.zaf -chunkid zaf_ -ext zafbin -outputdir {1}\\'.format(self.outd, self.outd))
        else:
            os.system(os.getcwd() + '\\zenasset.exe /multimsh /writefiles /src {0}{1} /keepframe0 {2} /dest {3}\\{4}.zaf'.format(self.ind, add_params, params, self.outd, self.animname.text()))
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
        self.add_params = QLineEdit()
        self.add_params.setText('Additional Params')
        self.add_params.setToolTip('<b>Additional Munge Parameters.</b> Like scale 1.5')
        grplay.addWidget(self.add_params, 0, 3, 1, 2)

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
