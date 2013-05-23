'''
Created on May 13, 2013
@author: ivano.ras@gmail.com
MIT license
'''

from PyQt4.QtCore import QTimer, QObject, QString, QRect, QMetaObject, SIGNAL, Qt
from PyQt4.QtGui  import QProgressBar, QPushButton, QWidget, QFont, QSizePolicy, QApplication, QImage, QColor, qRgb, QPixmap, QLabel, QPlainTextEdit, QSlider
from OpenGLCompo  import OGLViewer

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8 (s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate (context, text, disambig):
        return QApplication.translate (context, text, disambig, _encoding)
except AttributeError:
    def _translate (context, text, disambig):
        return QApplication.translate (context, text, disambig)

from RTModel import REngineThread



class Ui_Form (QWidget):
    '''
    Ui class. Generated with pyuic4.
    '''
    def __init__ (self, parent=None):
        
        QWidget.__init__(self, parent)
        self.timer = QTimer (self)
        
        self.engine = None
    
    def wireOGLViewer (self):
        
        QObject.connect (self.widget, SIGNAL ("MatrixChanged (PyQt_PyObject)"), self.displayGLMatrix)

        # call the function run regularly when the focus is on it. (60 FPS if interval = 20)
        QObject.connect (self.timer, SIGNAL ('timeout()'), self.widget.run)
    
    def stopGLFrameRate (self):
        
        self.timer.stop ()
    
    def speedUpGLFrameRate (self):
        
        self.timer.start ()
        self.timer.setInterval (20)
        
    def setupUi (self, Form):
        
        font = QFont ()
        font.setPointSize (9)
        font.setBold (False)
        font.setWeight (50)
        
        sizePolicy = QSizePolicy (QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch (0)
        sizePolicy.setVerticalStretch (0)
        
        Form.setObjectName (_fromUtf8("Form"))
        Form.resize (971, 930)
        self.plainTextEdit = QPlainTextEdit (Form)
        self.plainTextEdit.setGeometry (QRect (740, 100, 241, 791))
        self.plainTextEdit.setObjectName (_fromUtf8 ("plainTextEdit"))
        self.plainTextEdit.setFont (font)
        
        self.widget = OGLViewer (Form)
        self.widget.setUi_Form (self)
        self.widget.setGeometry (QRect (10, 10, 720, 450))
        sizePolicy.setHeightForWidth (self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy (sizePolicy)
        self.widget.setObjectName (_fromUtf8 ("widget"))
        self.wireOGLViewer ()
        
        self.label_view = QLabel (Form)
        self.label_view.setGeometry  (QRect (10, 470, 720, 450))
        sizePolicy.setHeightForWidth (self.label_view.sizePolicy().hasHeightForWidth())
        self.label_view.setSizePolicy (sizePolicy)
        self.label_view.setObjectName (_fromUtf8 ("label_view"))


        
        self.image = QImage (720, 450, QImage.Format_RGB888)
        color = QColor (250, 250, 250)
        self.image.fill (color)
        
        for i in range (0, 200, 20):
            for x in range (i, i+20):
                for y in range (i, i+20):
                    self.image.setPixel (x,y, qRgb (0, 0, 0))
                            
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
        
        
        
        self.stopBtn = QPushButton (Form)
        self.stopBtn.setGeometry (QRect (830, 50, 51, 31))
        self.stopBtn.setFont (font)
        self.stopBtn.setObjectName (_fromUtf8 ("stop"))
        self.stopBtn.setDisabled (True)
        
        self.renderBtn = QPushButton (Form)
        self.renderBtn.setGeometry (QRect (740, 50, 91, 31))
        self.renderBtn.setFont (font)
        self.renderBtn.setObjectName (_fromUtf8 ("render"))
        
        self.progressBar = QProgressBar (Form)
        self.progressBar.setGeometry (QRect (740, 901, 221, 20))
        self.progressBar.setProperty ("value", 0)
        self.progressBar.setObjectName (_fromUtf8("progressBar"))
        self.progressBar.setMinimum (0)
        self.progressBar.setMaximum (100)
        
        self.label_slider = QLabel (Form)
        self.label_slider.setEnabled (True)
        self.label_slider.setGeometry (QRect(880, 80, 81, 16))
        self.label_slider.setFont(font)
        self.label_slider.setObjectName (_fromUtf8("label_slider"))
        
        self.arrowSizeSlider = QSlider (Form)
        self.arrowSizeSlider.setGeometry (QRect(750, 80, 121, 22))
        self.arrowSizeSlider.setMinimum (2)
        self.arrowSizeSlider.setMaximum (40)
        self.arrowSizeSlider.setSingleStep (1)
        self.arrowSizeSlider.setProperty ("value", 4)
        self.arrowSizeSlider.setOrientation (Qt.Horizontal)
        self.arrowSizeSlider.setObjectName  (_fromUtf8("arrowSizeSlider"))

        self.retranslateUi (Form)
        QMetaObject.connectSlotsByName (Form)
    
    def retranslateUi (self, Form):
        
        Form.setWindowTitle       (_translate ("Form", "RayTracing Debugging Tool", None))
        self.renderBtn.setText    (_translate ("Form", "Render",                    None))
        self.stopBtn.setText      (_translate ("Form", "Stop",                      None))
        self.label_slider.setText (_translate ("Form", "Arrows size",               None))
        
        self.connect (self.renderBtn,       SIGNAL ("clicked()"),        self.clickRender)
        self.connect (self.stopBtn,         SIGNAL ("clicked()"),        self.stopRender)
        self.connect (self.arrowSizeSlider, SIGNAL ("sliderMoved(int)"), self.resizeArrows)
    
    # listeners
    
    def resizeArrows (self, e):
        
        self.widget.changeArrowsSize (e*0.5)
    
    def stopRender (self):
        
        if self.engine:
            
            self.engine.setCarryOnFlag (False)
            self.renderBtn.setDisabled (False)
            self.stopBtn.setDisabled   (True)
            
            self.disconnect (self.engine, SIGNAL ("update (float)"), self.updateImage)
            self.disconnect (self.engine, SIGNAL ("thread_completed()"), self.endCrunching)
            self.disconnect (self.engine, SIGNAL ("vector_created(PyQt_PyObject, PyQt_PyObject, QString)"), self.widget.addArrow)
    
    def clickRender (self):
        
        self.renderBtn.setDisabled (True) # grey out the render button.
        self.stopBtn.setDisabled  (False) # enable the stop button.
        self.progressBar.reset ()
        
        # add 3D representation of a 3D camera.
        self.plainTextEdit.insertPlainText ('\n\n\n'+str(self.widget.getMatrix()))
        self.widget.addCamera ()
        
        # grab screenshot of OpenGL viewer and add it into the QImage instance.
        self.image = self.widget.grabFrameBuffer ()
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
                
        self.engine = REngineThread (self.image, self.widget.getNormalMatrix (), self.widget.getFovy ())
        self.connect (self.engine, SIGNAL("update (float)"), self.updateImage)
        self.connect (self.engine, SIGNAL("thread_completed()"), self.endCrunching)
        self.connect (self.engine, SIGNAL("vector_created(PyQt_PyObject, PyQt_PyObject, QString)"), self.widget.addArrow)
        
        self.engine.start ()
    
    def endCrunching (self):
        self.renderBtn.setDisabled (False)
        self.stopBtn.setDisabled   (True)
        self.progressBar.setValue  (100)
    def updateImage    (self, e):
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
        self.progressBar.setValue (int(100*e))
    def displayGLMatrix (self, e):
        '''
        this method registered to the MatrixChanged event fired from the OGLViewer
        component. It prints the model matrix. Useful for debugging purposes.
        '''
        pass
        #print e


if __name__ == "__main__":
    
    import sys
    app = QApplication (sys.argv)
    Form = QWidget ()
    ui = Ui_Form ()
    ui.setupUi (Form)
    Form.show ()
    sys.exit (app.exec_())