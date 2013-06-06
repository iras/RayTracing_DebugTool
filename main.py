'''
Created on May 13, 2013
@author: ivano.ras@gmail.com
MIT license
'''

from PyQt4.QtCore import QTimer, QObject, QString, QRect, QMetaObject, SIGNAL, Qt
from PyQt4.QtGui  import QProgressBar, QPushButton, QWidget, QFont, QSizePolicy, QApplication, QImage, QColor, qRgb, QPixmap, QLabel, QPlainTextEdit, QSlider
from OpenGLCompo  import OGLViewer

from RTEngine     import REngineThread
from ThreeDModels import Model


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



class Ui_Form (QWidget):
    '''
    Ui class. Generated with pyuic4.
    '''
    def __init__ (self, parent=None):
        
        QWidget.__init__(self, parent)
        self.timer = QTimer (self)
        
        self.__engine = None
        self.__model  = Model ()
        
        self.image = QImage (720, 450, QImage.Format_RGB888)
        
        self.__engine = REngineThread ()
    
    def wireEngineUp (self):
        '''
        this method connects the REngine's signals.
        '''
        self.connect (self.__engine, SIGNAL ("update (float)"), self.updateImage)
        self.connect (self.__engine, SIGNAL ("thread_completed()"), self.endCrunching)
        self.connect (self.__engine, SIGNAL ("inters_created (PyQt_PyObject, PyQt_PyObject)"),          self.widget.addIntersection)
        self.connect (self.__engine, SIGNAL ("vector_created (PyQt_PyObject, PyQt_PyObject, QString)"), self.widget.addArrow)
        self.connect (self.__engine, SIGNAL ("line_created   (PyQt_PyObject, PyQt_PyObject, QString)"), self.widget.addLine)
    
    def wireOGLViewerUp (self):
        '''
        this method connects the REngine's signals.
        '''
        self.widget.setModel (self.__model)
        
        QObject.connect (self.widget, SIGNAL ("MatrixChanged (PyQt_PyObject)"), self.displayGLMatrix)

        # call the function run regularly when the focus is on it. (60 FPS if interval = 20)
        QObject.connect (self.timer, SIGNAL ('timeout()'), self.widget.run)
    
    def freezeGLFrameRate (self):
        
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
        self.plainTextEdit.setGeometry (QRect (740, 280, 221, 611))
        self.plainTextEdit.setObjectName (_fromUtf8 ("plainTextEdit"))
        self.plainTextEdit.setFont (font)
        
        self.widget = OGLViewer (Form)
        self.widget.setUi_Form (self)
        self.widget.setGeometry (QRect (10, 10, 720, 450))
        sizePolicy.setHeightForWidth (self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy (sizePolicy)
        self.widget.setObjectName (_fromUtf8 ("widget"))
        self.wireOGLViewerUp ()
        self.wireEngineUp ()
        
        self.label_view = QLabel (Form)
        self.label_view.setGeometry  (QRect (10, 470, 720, 450))
        sizePolicy.setHeightForWidth (self.label_view.sizePolicy().hasHeightForWidth())
        self.label_view.setSizePolicy (sizePolicy)
        self.label_view.setObjectName (_fromUtf8 ("label_view"))
        self.initLabel ()          
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
        
        # buttons definitions
        
        self.renderBtn    = QPushButton (Form)
        self.pauseBtn     = QPushButton (Form)
        self.stopBtn      = QPushButton (Form)
        self.upBtn        = QPushButton (Form)
        self.downBtn      = QPushButton (Form)
        self.moreDownBtn  = QPushButton (Form)
        self.moreUpBtn    = QPushButton (Form)
        self.rightBtn     = QPushButton (Form)
        self.moreRightBtn = QPushButton (Form)
        self.leftBtn      = QPushButton (Form)
        self.furtherLeft  = QPushButton (Form)
        self.grid_switch  = QPushButton (Form)
        
        buttons_properties_list = [[self.renderBtn,    QRect (740, 140, 61, 21), "render",            True],
                                   [self.pauseBtn,     QRect (740, 120, 61, 21), "pause",             False],
                                   [self.stopBtn,      QRect (740, 100, 61, 21), "stop",              False],
                                   [self.upBtn,        QRect (820, 120, 21, 21), "one_row_up",        False],
                                   [self.downBtn,      QRect (820, 140, 21, 21), "one_row_down",      False],
                                   [self.moreDownBtn,  QRect (820, 160, 21, 21), "ten_rows_down",     False],
                                   [self.moreUpBtn,    QRect (820, 100, 21, 21), "ten_rows_up",       False],
                                   [self.rightBtn,     QRect (780, 180, 21, 21), "one_column_right",  False],
                                   [self.moreRightBtn, QRect (800, 180, 21, 21), "ten_columns_right", False],
                                   [self.leftBtn,      QRect (760, 180, 21, 21), "one_column_left",   False],
                                   [self.furtherLeft,  QRect (740, 180, 21, 21), "ten_columns_left",  False],
                                   [self.grid_switch,  QRect (870, 230, 91, 31), "grid_switch",       False]]
        
        for button in buttons_properties_list:
            button[0].setGeometry (button[1])
            button[0].setFont (font)
            button[0].setObjectName (_fromUtf8 (button[2]))
            button[0].setEnabled (button[3])
        
        # other UI elements
        
        self.progressBar = QProgressBar (Form)
        self.progressBar.setGeometry (QRect (740, 901, 221, 20))
        self.progressBar.setProperty ("value", 0)
        self.progressBar.setObjectName (_fromUtf8("progressBar"))
        self.progressBar.setMinimum (0)
        self.progressBar.setMaximum (100)
        
        self.slider_label = QLabel (Form)
        self.slider_label.setGeometry (QRect(900, 260, 61, 16))
        self.slider_label.setFont(font)
        self.slider_label.setObjectName (_fromUtf8("slider_label"))
        self.slider_label.setEnabled (True)
        
        self.arrowSizeSlider = QSlider (Form)
        self.arrowSizeSlider.setGeometry (QRect (740, 258, 151, 22))
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
        
        self.renderBtn.setText    (_translate ("Form", "Render", None))
        self.pauseBtn.setText     (_translate ("Form", "Pause", None))
        self.stopBtn.setText      (_translate ("Form", "Stop", None))
        self.upBtn.setText        (_translate ("Form", "^", None))
        self.downBtn.setText      (_translate ("Form", "v", None))
        self.moreDownBtn.setText  (_translate ("Form", "+", None))
        self.moreUpBtn.setText    (_translate ("Form", "-", None))
        self.rightBtn.setText     (_translate ("Form", ">", None))
        self.moreRightBtn.setText (_translate ("Form", "+", None))
        self.leftBtn.setText      (_translate ("Form", "<", None))
        self.furtherLeft.setText  (_translate ("Form", "-", None))
        
        self.grid_switch.setText  (_translate ("Form", "Grid on/off", None))
        self.slider_label.setText (_translate ("Form", "Arrows size", None))
        
        self.connect (self.renderBtn,       SIGNAL ("clicked()"),        self.startRender)
        self.connect (self.stopBtn,         SIGNAL ("clicked()"),        self.stopRender)
        self.connect (self.arrowSizeSlider, SIGNAL ("sliderMoved(int)"), self.resizeArrows)
    
    def initLabel (self):
        
        color = QColor (250, 250, 250)
        self.image.fill (color)
        
        '''
        # test init
        for i in range (0, 200, 20):
            for x in range (i, i+20):
                for y in range (i, i+20):
                    self.image.setPixel (x,y, qRgb (0, 0, 0))
        '''
    
    # listeners  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def resizeArrows (self, e):
        
        self.widget.changeArrowsSize (e*0.5)
    
    def stopRender (self):
        
        if self.__engine:
            
            self.__engine.setCarryOnFlag (False)
            self.renderBtn.setDisabled   (False)
            self.stopBtn.setDisabled     (True)
    
    def startRender (self):
        
        self.renderBtn.setDisabled (True) # grey out the render button.
        self.stopBtn.setDisabled  (False) # enable the stop button.
        self.progressBar.reset ()
        
        # add 3D representation of a 3D camera.
        self.plainTextEdit.insertPlainText ('\n\n\n'+str(self.widget.getMatrix()))
        self.widget.addCamera ()
        
        # grab screenshot of OpenGL viewer and add it into the QImage instance.
        self.image = self.widget.grabFrameBuffer ()
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
        
        # prep engine and start it up.
        self.__engine.setImage (self.image)
        self.__engine.setCameraNormalMatrix (self.widget.getNormalMatrix(), self.widget.getFovy ())
        self.__engine.setModel (self.__model)
        self.__engine.start ()
    
    def endCrunching (self):
        self.renderBtn.setDisabled (False)
        self.stopBtn.setDisabled   (True)
        self.progressBar.setValue  (100)
    def updateImage (self, e):
        self.pixmap_item = self.label_view.setPixmap (QPixmap.fromImage (self.image))
        self.progressBar.setValue (int(100*e))
    def displayGLMatrix (self, e):
        '''
        this method is registered to the MatrixChanged event fired from the OGLViewer
        component. It prints the model matrix. Only for debugging purposes.
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