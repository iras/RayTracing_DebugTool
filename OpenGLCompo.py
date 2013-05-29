'''
Created on May 13, 2013
@author: ivano.ras@gmail.com
MIT license
'''

import sys

import OpenGL
OpenGL.ERROR_CHECKING = True
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

#from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtOpenGL import QGLFormat, QGLWidget
from PyQt4.QtCore   import QPoint, Qt, SIGNAL
from PyQt4.QtGui    import QMatrix4x4, QCursor, QVector3D

import MathTools


class OGLViewer (QGLWidget):
    '''
    OpenGL viewer class
    '''
    
    def __init__ (self, parent = None):
        '''
        Viewer's Constructor
        '''
        frmt = QGLFormat ()
        frmt.setSampleBuffers (True)
        
        super (OGLViewer, self).__init__ (frmt, parent)
        
        #self.setMouseTracking (True)
        self.__mouse = QCursor ()
        self.setCursor (Qt.OpenHandCursor)
        self.setFocusPolicy (Qt.ClickFocus)
        
        self.__Ctrl_or_Meta_key_pressed = False
        self.__Alt_key_pressed = False
        
        self.__w = 720
        self.__h = 450
        
        self._init_camera_vars ()
        self._init_objec_vars  ()
        
        # matrix changed signal. The signal's payload is the matrix itself.
        self.__GLMatrixChanged = SIGNAL ("MatrixChanged (PyQt_PyObject)")
        
        self.__compo_light_pos = QVector3D (.3,.2,.1)
        self.__AmbientMaterial = QVector3D ( .2, .2, .2)
    
    
    def _init_camera_vars (self):
        '''
        static method. It initializes the math variables.
        '''
        self.__compo_mtools = MathTools.Tools ()
        
        self.__curr_angles  = QPoint (0,0)
        self.__last_pos     = QPoint (0,0)
        self.__delta        = QPoint (0,0)
        self.__orig         = QVector3D (0.0, 0.0, 0.0)
        self.__cam_dist     = 0.0
        self.__z_near       = 0.1
        self.__z_far        = 2000.0
        self.__fovy         = 45.0
        self.__angle        = self.__compo_mtools.getAngle (self.__fovy)
        
        self.__norm_mtx     = QMatrix4x4 () #(GLdouble * 16)()
        self.__norm_mtx.setToIdentity ()
        
        self.__mtx          = QMatrix4x4 () #(GLdouble * 16)()
        self.__mtx.setToIdentity ()
        
        self.__aspect_ratio = float(self.__w)/float(self.__h)
        
        self.__camera_list  = []
    
    def _init_objec_vars (self):
        
        self.__arrows_list  = []
        self.__arrow_len    = 2.0
        
        self.__lines_list   = []
        self.__l_param      = 200.0
        
        self.__intersections_list = []
        
        self.__poly_model   = None
        self.__poly_list    = [] # by polygon I mean triangle.
    
    def initializeGL (self):
        '''
        usual OpenGL method
        '''
        glClearColor (0.93, 0.93, 0.93, 1.0)   
        glClearDepth (1.0)
        
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity()
        gluPerspective (self.__fovy, float(self.__w)/float(self.__h), self.__z_near, self.__z_far)
        
        self.refreshMatrices ()
    
    def resizeGL (self, w, h):
        '''
        usual OpenGL method
        '''
        self.__w = w
        self.__h = h
        
        self.__aspect_ratio = float (self.__w)/float(self.__h)
        
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()
        gluPerspective (self.__fovy, self.__aspect_ratio, self.__z_near, self.__z_far)
        glViewport (0, 0, self.__w, self.__h)
        
        gluLookAt  (0, 0,-1,  # CameraPos
                    0, 0 ,0,  # CameraLookAt
                    0, 1 ,0)  # CameraUp
    
    def paintGL (self):
        '''
        usual OpenGL method
        '''
        self.__delta = QPoint (0,0)
        
        q = self.__mouse.pos()
        if self.__Ctrl_or_Meta_key_pressed ^ self.__Alt_key_pressed: #  xor (strictly one or the other)
            
            if self.__Ctrl_or_Meta_key_pressed:
                
                # rotation
                
                self.__delta = q - self.__last_pos
                
            else:
                
                # translation
                
                # transform mouse deltas and camera's local axes so that it'll look like as if the camera gets
                # translated based on the local axes x and y. What really happens is that the origin shifts along.
                # The resulting behaviour reminds of the Maya Camera Track Tool.
                d_x = q.x() - self.__last_pos.x()
                d_y = q.y() - self.__last_pos.y()
                
                zero = 0.0 #GLdouble (0.0)
                m_ref = self.__mtx.data () # retrieves the 16 items in this matrix and copies them to values in row-major order.
                vec_x = - m_ref[0]*d_x + m_ref[4]*d_y + zero*m_ref[8]
                vec_y = - m_ref[1]*d_x + m_ref[5]*d_y + zero*m_ref[9]
                vec_z = - m_ref[2]*d_x + m_ref[6]*d_y + zero*m_ref[10]
                
                mult = 0.03
                self.__orig.setX (self.__orig.x() + mult*vec_x)
                self.__orig.setY (self.__orig.y() + mult*vec_y)
                self.__orig.setZ (self.__orig.z() + mult*vec_z)
            
            # fire signal after done changing the model matrix.
            self.emit (self.__GLMatrixChanged, self.__mtx)
        
        self.__last_pos = q
        
        self.__curr_angles += self.__delta
        
        if glCheckFramebufferStatus (GL_FRAMEBUFFER) == 36053:  # 36053 = GL_FRAMEBUFFER_COMPLETE
            
            glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity ()
            
            # Set the camera orientation :
            glMatrixMode (GL_MODELVIEW)
            glLoadIdentity ()
            
            gluLookAt (self.__orig.x(), self.__orig.y(), self.__orig.z() - 40,  # CameraPos
                       self.__orig.x(), self.__orig.y(), self.__orig.z(),       # CameraLookAt
                                   0.0,             1.0,             1.0)       # CameraUp
            
            # Rotate and move camera forward or backward.
            glTranslatef (0, 0, -self.__cam_dist)
            glTranslatef (self.__orig.x(), self.__orig.y(), self.__orig.z())    # rotation around current origin.
            glRotatef    (-30 - self.__curr_angles.y() * 0.15,  1, 0, 0)        # rotate around axis x.
            glRotatef    (-30 + self.__curr_angles.x() * 0.1,   0, 1, 0)        # rotate around axis y.
            glTranslatef (-self.__orig.x(), -self.__orig.y(), -self.__orig.z()) # rotation around current origin.
            
            self.refreshMatrices ()
            
            self.displayObjects ()
            self.displayArrows ()
            self.displayLines ()
            self.displayIntersections ()
            
            self.drawGrid ()
            self.drawFixedOriginAxes ()
            self.drawCurrentOriginAxes ()
            
            self.displayCamera ()
    
    def refreshMatrices (self):
        
        tmp        = glGetDoublev (GL_MODELVIEW_MATRIX) # this returns a list of lists BUT QMatrix4x4 accepts a list of floats.
        tmp_qmtx   = QMatrix4x4 ([item for sublist in tmp for item in sublist]) # flattens the list of lists out in a single list.
        
        self.__mtx = tmp_qmtx
        
        tmp_tuple  = tmp_qmtx.inverted ()
        self.__norm_mtx = (tmp_tuple[0]).transposed () # assumption : matrix always invertible so I'm not going to check the boolean tmp_tuple[1].
    
    def run (self):
        '''
        method refreshed cyclically by a timer when it is in focus.
        When out of focus, the timer stops calling it and so freezing
        the image to what it looked like when last used.
        '''
        self.paintGL () # render actual frame
        self.swapBuffers ()
    
    def addCamera (self):
        
        self.__compo_mtools.setNormalMatrix (self.__norm_mtx)
        
        angle_by_aspect_ratio = self.__angle * self.__aspect_ratio
        inv_w = 1.0/self.__w
        inv_h = 1.0/self.__h
        m = -1.0
        
        w_param = (inv_w-1) * angle_by_aspect_ratio
        h_param = (1-inv_h) * self.__angle
        
        # compute center + corners
        cam_centre   = self.__compo_mtools.cameraToWorldTransform (0, 0, 0)
        top_left     = self.__compo_mtools.cameraToWorldTransform ( w_param,  h_param, m)
        top_right    = self.__compo_mtools.cameraToWorldTransform ( w_param, -h_param, m)
        bottom_left  = self.__compo_mtools.cameraToWorldTransform (-w_param,  h_param, m)
        bottom_right = self.__compo_mtools.cameraToWorldTransform (-w_param, -h_param, m)
        
        self.__camera_list.append ([cam_centre, top_left, top_right, bottom_left, bottom_right])
    
    # - - -  viewer graphics  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def displayCamera (self):
        
        glLineWidth (1.0)
        for cam in self.__camera_list:
            
            cc=cam[0];  tl=cam[1];  tr=cam[2];  bl=cam[3];  br=cam[4]
            
            glBegin (GL_LINES)
            glColor3f  (0.6, 0.6, 0.6)
            glVertex3f (cc[0],cc[1],cc[2]);   glVertex3f (tl[0],tl[1],tl[2])
            glVertex3f (cc[0],cc[1],cc[2]);   glVertex3f (tr[0],tr[1],tr[2])
            glVertex3f (cc[0],cc[1],cc[2]);   glVertex3f (br[0],br[1],br[2])
            glVertex3f (cc[0],cc[1],cc[2]);   glVertex3f (bl[0],bl[1],bl[2])
            glVertex3f (tl[0],tl[1],tl[2]);   glVertex3f (tr[0],tr[1],tr[2])
            glVertex3f (tr[0],tr[1],tr[2]);   glVertex3f (br[0],br[1],br[2])
            glVertex3f (br[0],br[1],br[2]);   glVertex3f (bl[0],bl[1],bl[2])
            glVertex3f (bl[0],bl[1],bl[2]);   glVertex3f (tl[0],tl[1],tl[2])
            glEnd ()
    
    def displayObjects (self):
        
        glClear (GL_COLOR_BUFFER_BIT)
        
        glEnable (GL_DEPTH_TEST)
        glDepthMask (GL_TRUE)
        #glEnable (GL_CULL_FACE)
        
        for poly in self.__poly_list:
            
            p0 = poly[0];  p1 = poly[1];  p2 = poly[2]
            
            glBegin (GL_TRIANGLES)
            col = .4 + 0.5*QVector3D.dotProduct (poly[3], self.__compo_light_pos)
            glColor3f   (col, col, col)
            glVertex3f (p0.x(), p0.y(), p0.z())
            glVertex3f (p1.x(), p1.y(), p1.z())
            glVertex3f (p2.x(), p2.y(), p2.z())
            glEnd ()
    
    def displayIntersections (self):
        
        for intsect in self.__intersections_list:
            
            p = intsect[0]
            c = intsect[1]
            # Draw a translated solid sphere
            glPushMatrix ()
            glTranslatef (p[0], p[1], p[2])
            glColor3f    (c[0], c[1], c[2])
            glutSolidSphere (GLdouble (0.03), 9, 9)
            glPopMatrix ()
    
    def displayLines (self):
        
        glLineWidth (1.0)
        for line in self.__lines_list:
            
            p = line[0]       # line initial position  (3-list)
            d = line[1]       # line direction (3-list)
            t = str(line[2])  # line type (o:open line, p:point-to-point line)
            
            glBegin (GL_LINES)
            glColor3ub (255, 255, 255)
            glVertex3f (p[0], p[1], p[2])
            
            # open line
            if   t=='o':
                glVertex3f (self.__l_param*d[0] + p[0],
                            self.__l_param*d[1] + p[1],
                            self.__l_param*d[2] + p[2])
            # point-to-point line
            elif t=='p':
                glVertex3f (d[0], d[1], d[2])
            
            else: raise sys.exit ('*** Unrecognised line type : "' + t + '"')
            
            glEnd ()
    
    def displayArrows (self):
        
        for arrow in self.__arrows_list:
            
            p = arrow[0]      # arrow position  (3-list)
            d = arrow[1]      # arrow direction (3-list)
            t = str(arrow[2]) # arrow type (i:inwards, o:outwards)
            
            # scale parameters
            scale_x = 0.01
            scale_y = scale_x
            scale_z = 0.5
            t_z     = scale_z * self.__arrow_len
            
            # arrow type
            if   t=='o': add_t = 0
            elif t=='i': add_t = -t_z*2.5
            else: raise sys.exit ('*** Unrecognised arrow type : "' + t + '"')
            
            glPushMatrix ()
            
            # arrow shaft
            glColor3f (0.5, 0.5, 0)
            glTranslatef (p[0], p[1], p[2])
            angles_from_orient = self.__compo_mtools.alignZAxisToVector (d[0], d[1], d[2])
            glRotatef (                  180,  0, 0, 1)
            glRotatef (angles_from_orient[1],  0, 1, 0)
            glRotatef (angles_from_orient[0],  1, 0, 0)
            glScale (scale_x, scale_y, scale_z)
            glTranslatef (0, 0, t_z+add_t)
            glutSolidCube (GLdouble(self.__arrow_len))
            
            # arrow head (remember : the head's transformations are built on top of the arrow shaft's and are not independent) 
            glColor3f (0.4, 0.4, 0)
            glTranslatef (0, 0, t_z)
            glutSolidCone (GLdouble(t_z*5), GLdouble(t_z*0.5), GLint(6), GLint(1))
            
            glPopMatrix ()
    
    def drawGrid (self):
        
        glLineWidth (1.0)
        for i in range (-10, 11):
            glBegin (GL_LINES)
            glColor3ub (185, 185, 185)
            glVertex3f (-10, 0, i)
            glVertex3f (10, 0, i)
            glVertex3f (i, 0,-10)
            glVertex3f (i, 0, 10)
            glEnd ()
    
    def drawFixedOriginAxes (self):
        
        glLineWidth (3.0)
        glBegin (GL_LINES)
        glColor3ub (250, 0, 0); glVertex3f (0, 0, 0); glVertex3f (0, 0, 5)
        glColor3ub (255, 150, 150); glVertex3f (0, 0, 5); glVertex3f (0, 0, 10); glEnd ()
        glBegin (GL_LINES)
        glColor3ub (0, 250, 0); glVertex3f (0, 0, 0); glVertex3f (0, 5, 0)
        glColor3ub (150, 255, 150); glVertex3f (0, 5, 0); glVertex3f (0, 10, 0); glEnd ()
        glBegin (GL_LINES)
        glColor3ub (0, 0, 250); glVertex3f (0, 0, 0); glVertex3f (5, 0, 0)
        glColor3ub (150, 150, 255); glVertex3f (5, 0, 0); glVertex3f (10, 0, 0); glEnd ()
    
    def drawCurrentOriginAxes (self):
        
        glPointSize (6.0)
        glBegin (GL_POINTS)
        glColor3f (0.0,1.0,1.0)
        glVertex3f (self.__orig.x(), self.__orig.y(), self.__orig.z());   glEnd ()
        
        glBegin (GL_LINES); glColor3ub (250, 0, 0)
        glVertex3f (self.__orig.x(), self.__orig.y(), self.__orig.z())
        glVertex3f (self.__orig.x(), self.__orig.y(), self.__orig.z()+5); glEnd ()
        glBegin (GL_LINES); glColor3ub (0, 250, 0);
        glVertex3f (self.__orig.x(), self.__orig.y(), self.__orig.z())
        glVertex3f (self.__orig.x(), self.__orig.y()+5, self.__orig.z()); glEnd ()
        glBegin (GL_LINES); glColor3ub (0, 0, 250);
        glVertex3f (self.__orig.x(), self.__orig.y(), self.__orig.z())
        glVertex3f (self.__orig.x()+5, self.__orig.y(), self.__orig.z()); glEnd ()
    
    # - - -  listeners  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def changeArrowsSize (self, new_size):
        if len(self.__arrows_list) > 0:
            self.__arrow_len = new_size
        
    def addArrow (self, pos, orient, arrow_type):
        self.__arrows_list.append ([pos, orient, arrow_type])
        
    def addLine (self, pos, orient_or_second_point, line_type):
        self.__lines_list.append ([pos, orient_or_second_point, line_type])
    
    def addIntersection (self, pos, icolor):
        self.__intersections_list.append ([pos, icolor])
    
    def keyPressEvent (self, e):
        if e.key() == Qt.Key_Control or e.key() == Qt.Key_Meta:  self.__Ctrl_or_Meta_key_pressed = True
        if e.key() == Qt.Key_Alt:  self.__Alt_key_pressed = True
    
    def keyReleaseEvent (self, e):
        if e.key() == Qt.Key_Control or e.key() == Qt.Key_Meta:  self.__Ctrl_or_Meta_key_pressed = False
        if e.key() == Qt.Key_Alt:  self.__Alt_key_pressed = False
    
    def wheelEvent (self, e):
        if self.__Ctrl_or_Meta_key_pressed:
            self.__cam_dist += e.delta() * 0.01
    
    # the three methods below are for regulate the OpenGL widget's FPS based on the focus received by the user.
    def setUi_Form      (self, uif): self.uiform = uif
    def focusInEvent    (self, e):   self.uiform.speedUpGLFrameRate ()
    def focusOutEvent   (self, e):   self.uiform.stopGLFrameRate ()
    
    def getFovy         (self): return self.__fovy
    def getMatrix       (self): return self.__mtx
    def getNormalMatrix (self): return self.__norm_mtx
    
    def setModel        (self, model):
        self.__poly_model = model
        self.__poly_list  = model.getPolyListCopy ()
