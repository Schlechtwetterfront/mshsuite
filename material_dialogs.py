from PySide.QtGui import QDialog, QGridLayout, QGroupBox, QLineEdit, QHBoxLayout, QVBoxLayout, \
                        QLabel, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton
import msh2

STR_CODEC = 'ascii'


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
