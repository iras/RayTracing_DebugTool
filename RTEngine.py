'''
Created on May 15, 2013
@author: ivano.ras@gmail.com
MIT License
'''
import sys

from PyQt4.QtGui  import qRgb, QVector3D
from PyQt4.QtCore import QThread, SIGNAL, QString
import MathTools


class REngineThread (QThread):
    '''
    (threaded) engine model class
    '''
    
    def __init__(self, image, camera_normal_transform_mtx, fovy):
        '''
        REngineThread constructor.
        '''
        QThread.__init__ (self)
        
        self.__image  = image
        self.__width  = self.__image.width  ()
        self.__height = self.__image.height ()
        
        self.__fovy   = fovy
        self.__normal_mtx = camera_normal_transform_mtx
        
        self.__Origin = [0, 0, 0]
        self.__OriginWorld = []
        
        if   self.__width  > self.__height and self.__height > 0:  self.__aspect_ratio = float(self.__width)/float(self.__height)
        elif self.__height >  self.__width and self.__width  > 0:  self.__aspect_ratio = float(self.__height)/float(self.__width)
        elif self.__height == self.__width and self.__width  > 0:  self.__aspect_ratio = 1.0
        else: raise sys.exit ("*** Something wrong with the chosen resolution. Width = " + str(self.__width) + "  Height = " + str(self.__height))
        
        self.__engine_mtools = MathTools.Tools (self.__normal_mtx)
        self.__angle  = self.__engine_mtools.getAngle (self.__fovy)
        self.__world_origin = self.__engine_mtools.cameraToWorldTransform (0, 0, 0)
        
        # main loop state
        self.carry_on = True
        
        # custom signals
        self.__SIGNAL_Update           = SIGNAL ('update(float)')
        self.__SIGNAL_IntersectCreated = SIGNAL ('inters_created (PyQt_PyObject, PyQt_PyObject)')
        self.__SIGNAL_VectorCreated    = SIGNAL ('vector_created (PyQt_PyObject, PyQt_PyObject, QString)')
        self.__SIGNAL_LineCreated      = SIGNAL ('line_created   (PyQt_PyObject, PyQt_PyObject, QString)')
        self.__SIGNAL_ThreadCompleted  = SIGNAL ('thread_completed()')
        
        self.__poly_model_e = None
        self.__poly_list_e  = []
    
    
    def __del__(self):
        '''
        REngineThread destructor. It makes sure the thread stops processing before it gets destroyed.
        '''
        self.wait()
    
    
    def run (self):
        '''
        usual thread method 'run'
        '''
        self.renderTest2 ()
        #self.terminate ()
    
    
    def renderTest2 (self):
        '''
        test (2) render method.
        
        It plainly renders the camera rays intersections with any polygon in the scene.
        '''
        self.carry_on = True
        
        inv_w = 2.0/self.__width
        inv_h = 2.0/self.__height
        h = 0.5
        a = 1
        m = -1.0
        ff = 255
        
        angle_times_aspect_ratio = self.__angle * self.__aspect_ratio
        
        for j in range (0, self.__height):
            for i in range (0, self.__width):
                
                w_param = ((h + i)*inv_w-1) * angle_times_aspect_ratio
                h_param = (1-(h + j)*inv_h) * self.__angle
                
                world_ray = self.__engine_mtools.cameraToWorldTransform (w_param, h_param, m)
                
                ray_dir = [world_ray[0] - self.__world_origin[0],
                           world_ray[1] - self.__world_origin[1],
                           world_ray[2] - self.__world_origin[2]]
                ray_dir_norm = self.__engine_mtools.normalise (ray_dir)
                
                
                
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
                        
                        self.emit (self.__SIGNAL_IntersectCreated, intersections_pos, [0,0,255])
                        
                        # fire vector_created signal : payload -> vector's origin in space, vector direction, vector's type (o:outwards, i:inwards)
                        self.emit (self.__SIGNAL_VectorCreated, intersections_pos, ray_dir_norm, QString('i'))                        
            
            if j%10 == 0: # update screen every 10 lines
                self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
            
            if not self.carry_on:
                break
        
        self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
        
        if self.carry_on: # if and only if the rendering was completed then fire this signal away.
            self.emit (self.__SIGNAL_ThreadCompleted)
    
    
    
    
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
    
    def setCarryOnFlag (self, boo):
        '''
        setter. This method allows putting the break onto the rendering process if boo is set to False.
        '''
        self.carry_on = boo
    
    
    def setModel (self, model):
        '''
        setter. This method transfers a copy of the model (polygons list) to the REngineThread class instance.
        '''
        self.__poly_model_e = model
        self.__poly_list_e  = model.getPolyListCopy ()
    
    
    
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    
    
    
    def renderTest1 (self):
        '''
        test (1) render method.
        
        It just "renders" plain vector directions from the center of the camera.
        '''
        self.carry_on = True
        
        inv_w = 2.0/self.__width
        inv_h = 2.0/self.__height
        h = 0.5
        a = 1
        m = -1.0
        ff = 255
        
        angle_times_aspect_ratio = self.__angle * self.__aspect_ratio
        
        for j in range (0, self.__height):
            for i in range (0, self.__width):
                
                w_param = ((h + i)*inv_w-1) * angle_times_aspect_ratio
                h_param = (1-(h + j)*inv_h) * self.__angle
                
                world_ray = self.__engine_mtools.cameraToWorldTransform (w_param, h_param, m)
                
                ray_dir = [world_ray[0] - self.__world_origin[0],
                           world_ray[1] - self.__world_origin[1],
                           world_ray[2] - self.__world_origin[2]]
                #ray_dir = self.__engine_mtools.normalise (ray_dir)
                
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
                    self.emit (self.__SIGNAL_IntersectCreated, intersections_pos, [0,0,255])
            
            if j%10 == 0: # display to screen every 10 lines
                self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
            
            if not self.carry_on:
                break
        
        self.emit (self.__SIGNAL_Update, float(j)/float(self.__height))
        
        if self.carry_on: # if and only if the rendering was completed then fire this signal away.
            self.emit (self.__SIGNAL_ThreadCompleted)
