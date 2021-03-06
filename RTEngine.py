'''
Created on May 15, 2013
@author: ivano.ras@gmail.com
MIT License
'''
import sys
from time import sleep

from PyQt4.QtGui  import qRgb, QVector3D
from PyQt4.QtCore import QThread, SIGNAL, QString
import MathTools


class REngineThread (QThread):
    '''
    (threaded) engine model class
    '''
    
    def __init__(self):
        '''
        REngineThread constructor.
        '''
        QThread.__init__ (self)
        
        self.__Origin = [0, 0, 0]
        self.__OriginWorld = []
        
        # custom signals
        self.__SIGNAL_Update          = SIGNAL ('update(float)')
        self.__SIGNAL_ThreadCompleted = SIGNAL ('thread_completed()')
        self.__SIGNAL_IntersCreated   = SIGNAL ('inters_created (PyQt_PyObject, PyQt_PyObject)')
        self.__SIGNAL_VectorCreated   = SIGNAL ('vector_created (PyQt_PyObject, PyQt_PyObject, QString)')
        self.__SIGNAL_LineCreated     = SIGNAL ('line_created   (PyQt_PyObject, PyQt_PyObject, QString)')
        
        self.__poly_model_e = None
        self.__poly_list_e  = []
        
        # main loop flags + loop state vars
        self.is_stopped = False
        self.is_paused  = False
        
        self.resetLoopReferences ()
    
    def setImage (self, image):
        
        self.__image  = image
        self.__width  = self.__image.width  ()
        self.__height = self.__image.height ()
        
        if   self.__width  > self.__height and self.__height > 0:  self.__aspect_ratio = float(self.__width)/float(self.__height)
        elif self.__height >  self.__width and self.__width  > 0:  self.__aspect_ratio = float(self.__height)/float(self.__width)
        elif self.__height == self.__width and self.__width  > 0:  self.__aspect_ratio = 1.0
        else: raise sys.exit ("*** Something wrong with the chosen resolution. Width = " + str(self.__width) + "  Height = " + str(self.__height))
    
    def setCameraNormalMatrix (self, camera_normal_transform_mtx, fovy):
        
        self.__fovy = fovy
        
        self.__normal_mtx = camera_normal_transform_mtx
        self.__engine_mtools = MathTools.Tools (self.__normal_mtx)
        self.__angle  = self.__engine_mtools.getAngle (self.__fovy)
        self.__world_origin = self.__engine_mtools.cameraToWorldTransform (0, 0, 0)
    
    
    def __del__(self):
        '''
        REngineThread destructor. It makes sure the thread stops processing before it gets destroyed.
        '''
        self.wait()
    
    
    def run (self):
        '''
        usual thread method 'run'
        '''
        self.render ()
        #self.terminate ()
    
    
    def render (self):
        '''
        this method provides the chosen view's camera rays to the core_render method.
        '''
        self.is_stopped = False
        
        inv_w = 2.0/self.__width
        inv_h = 2.0/self.__height
        h = 0.5
        a = 1
        m = -1.0
        ff = 255
        
        angle_times_aspect_ratio = self.__angle * self.__aspect_ratio
        
        while True:
            
            if self.is_paused:
                sleep (0.25)
            else:
                for j in range (self.j_copy, self.__height):
                    for i in range (self.i_copy, self.__width):
                        
                        # set up basic camera rays. 
                        w_param = ((h + i)*inv_w-1) * angle_times_aspect_ratio
                        h_param = (1-(h + j)*inv_h) * self.__angle
                        
                        world_ray = self.__engine_mtools.cameraToWorldTransform (w_param, h_param, m)
                        
                        ray_dir = [world_ray[0] - self.__world_origin[0],
                                   world_ray[1] - self.__world_origin[1],
                                   world_ray[2] - self.__world_origin[2]]
                        ray_dir_norm = self.__engine_mtools.normalise (ray_dir)
                        
                        
                        
                        # core rendering bit.
                        self.core_render_test2 (i, j, ray_dir_norm, ray_dir)
                        
                        
                        
                        # inner loop control
                        if self.is_stopped: break # out of the inner loop
                        if self.is_paused:
                            self.saveLoopReferences (i, j)
                            break # out of the inner loop
                    
                    # mid loop control
                    if self.is_stopped: break # out of the mid loop
                    if self.is_paused:
                        break # out of the mid loop
                    else:
                        self.i_copy = 0 # normal behaviour
                    
                    
                    # update screen every 10 lines
                    if j%10==0:  self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
                
                
                self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
                
                
                # outer loop control
                if not self.is_stopped and not self.is_paused: # if and only if the rendering was completed then fire this signal away.
                    self.emit (self.__SIGNAL_ThreadCompleted)
                    self.resetLoopReferences ()
                    break # out of the outer loop
                if self.is_stopped:
                    self.resetLoopReferences ()
                    break # out of the outer loop
    
    
    def core_render_test2 (self, i, j, ray_dir_norm, ray_dir):
        '''
        This method plainly displays some camera rays intersections with any polygon in the scene. No optimisation here, just brute force approach.
        '''
        if j%10 == 0 and i%10 == 0: # display to screen every 10 lines 10 pixels apart.
                    
            tmp_isect_param = self.intersectRayTriangles (self.__world_origin, ray_dir_norm)
            if tmp_isect_param == None:
                self.__image.setPixel (i, j, qRgb (0, 0, 0))
            else:
                self.__image.setPixel (i, j, qRgb (255, 255, 0))
                
                # position = self.__world_origin, orientation = ray_dir_norm
                
                # fire inters_created signal : payload -> position in space, color
                intersections_pos = [self.__world_origin[0] + ray_dir_norm[0]*tmp_isect_param,
                                     self.__world_origin[1] + ray_dir_norm[1]*tmp_isect_param,
                                     self.__world_origin[2] + ray_dir_norm[2]*tmp_isect_param]
                
                # fire line_created signal : payload -> line origin in space, line direction, line type
                self.emit (self.__SIGNAL_LineCreated,   self.__world_origin, intersections_pos, QString('p'))
                
                self.emit (self.__SIGNAL_IntersCreated, intersections_pos, [0,0,255])
                
                # fire vector_created signal : payload -> vector's origin in space, vector direction, vector's type (o:outwards, i:inwards)
                self.emit (self.__SIGNAL_VectorCreated, intersections_pos, ray_dir_norm, QString('i'))
    
    
    
    def intersectRayTriangles (self, orig, dir):
        '''
        method dealing with ray-triangles intersections.
        
        @param orig 3-list
        @param dir  3-list
        
        @return closest_intersection_param float
        '''
        
        closest_intersection_param = None   # closest intersection to camera origin.
        intersections = []
        
        orig_v = QVector3D (orig[0], orig[1], orig[2])
        dir_v  = QVector3D ( dir[0],  dir[1],  dir[2])
        
        
        intersections_list = []
        for pl in self.__poly_list_e:
            
            isect_t = self.intersect (orig_v, dir_v,  pl)
            if isect_t != None:
                intersections_list.append ([pl, isect_t])
        
        # order the intersections_list
        tmp = 100000
        if len(intersections_list) > 0:
            for isectn in intersections_list:
                if isectn[1] < tmp:
                    tmp = isectn[1]
                    closest_intersection_param = tmp
        
        return closest_intersection_param
    
    
    def intersect (self, orig_v, dir_v, pl):
        '''
        method performing ray-triangle intersection (Moller-Trumbore algorithm)
        
        @param orig QVector3D
        @param dir  QVector3D
        
        @return isect_t float or None
        '''
        e1 = pl[1]  - pl[0]
        e2 = pl[2]  - pl[0]
        
        p = QVector3D.crossProduct (dir_v, e2)
        
        p_dot_e1 = QVector3D.dotProduct (p, e1)
        if p_dot_e1 == 0:
            return None
        
        inv_p_dot_e1 = 1.0 / p_dot_e1
        t  = orig_v - pl[0]
        isect_u = inv_p_dot_e1 * QVector3D.dotProduct (p, t)
        if isect_u<0 or isect_u>1:
            return None
        
        q = QVector3D.crossProduct (t, e1)
        isect_v = inv_p_dot_e1 * QVector3D.dotProduct (q, dir_v)
        if isect_v<0 or isect_u + isect_v>1:
             return None
         
        isect_t = inv_p_dot_e1 * QVector3D.dotProduct (e2, q)
        
        return isect_t
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
     
    def setModel (self, model):
        '''
        This method transfers a copy of the model (polygons list) to the REngineThread class instance.
        '''
        self.__poly_model_e = model
        self.__poly_list_e  = model.getPolyListCopy ()
    
    def setIsStoppedFlag (self, boo): self.is_stopped = boo
    def setIsPausedFlag  (self, boo): self.is_paused  = boo
    
    def resetLoopReferences (self):
        self.i_copy = 0
        self.j_copy = 0
        
    def saveLoopReferences (self, i, j):
        self.i_copy = i
        self.j_copy = j
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def core_render_test1 (self, i, j, ray_dir_norm, ray_dir):
        '''
        This method just "renders" plain vector directions from the center of the camera.
        No fancy user controls. Just a sweep.
        '''
        ff = 255;   a = 1;  h = 0.5;
        
        intersections_pos = [self.__world_origin[0] + ray_dir[0],
                             self.__world_origin[1] + ray_dir[1],
                             self.__world_origin[2] + ray_dir[2]]
                
        self.__image.setPixel (i, j, qRgb ((ff * (a + ray_dir[0]) * h), (ff * (a + ray_dir[1]) * h), 0))
        
        if j%100 == 0 and i%100 == 0: # display to screen every 10 lines 10 pixels apart.
            # fire line_created signal : payload -> line origin in space, line direction, line type
            # position = self.__world_origin, orientation = world_ray
            self.emit (self.__SIGNAL_LineCreated,   self.__world_origin, ray_dir, QString('o'))
            # fire vector_created signal : payload -> vector's origin in space, vector direction, vector's type (o:outwards, i:inwards)
            self.emit (self.__SIGNAL_VectorCreated, self.__world_origin, ray_dir, QString('o'))
            # fire inters_created signal : payload -> position in space, color
            self.emit (self.__SIGNAL_IntersectCreated, intersections_pos, [0,0,ff])
