'''
Created on May 15, 2013
@author: ivano.ras@gmail.com
MIT License
'''
import sys

from PyQt4.QtGui  import qRgb
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
        elif self.__height > self.__width  and self.__width  > 0:  self.__aspect_ratio = float(self.__height)/float(self.__width)
        else: raise sys.exit ("*** Something wrong with the chosen resolution. Width = " + str(self.__width) + "  Height = " + str(self.__height))
        
        self.__engine_mtools = MathTools.Tools (self.__normal_mtx)
        self.__angle  = self.__engine_mtools.getAngle (self.__fovy)
        self.__world_origin = self.__engine_mtools.cameraToWorldTransform (0, 0, 0)
        
        self.carry_on = True
        
        # signals
        self.__Update          = SIGNAL ('update(float)')
        self.__VectorCreated   = SIGNAL ('vector_created (PyQt_PyObject, PyQt_PyObject, QString)')
        self.__ThreadCompleted = SIGNAL ('thread_completed()')
        
    
    
    def __del__(self):
        '''
        REngineThread destructor. It makes sure the thread stops processing before it gets destroyed.
        '''
        self.wait()
    
    
    def run (self):
        '''
        usual thread method 'run'
        '''
        self.renderPlainDirections ()
        #self.terminate ()
    
    
    def renderPlainDirections (self):
        '''
        test render method
        '''
        self.carry_on = True
        
        inv_w = 2.0/self.__width
        inv_h = 2.0/self.__height
        h = 0.5
        a = 1
        m = -1.0
        ff = 255
        
        angle_by_aspect_ratio = self.__angle * self.__aspect_ratio
        
        for j in range (0, self.__height):
            for i in range (0, self.__width):
                
                w_param = ((h + i)*inv_w-1) * angle_by_aspect_ratio
                h_param = (1-(h + j)*inv_h) * self.__angle
                
                world_ray = self.__engine_mtools.cameraToWorldTransform (w_param, h_param, m)
                #world_ray = self.__engine_mtools.normalise (world_ray)
                
                ray_direction = [world_ray[0] - self.__world_origin[0],
                                 world_ray[1] - self.__world_origin[1],
                                 world_ray[2] - self.__world_origin[2]]
                
                self.__image.setPixel (i, j, qRgb ((ff * (a + ray_direction[0]) * h), (ff * (a + ray_direction[1]) * h), 0))
                
                if j%100 == 0 and i%100 == 0: # display to screen every 10 lines 10 pixels apart.
                    # fire vector_created signal : payload -> vector's origin in space, vector direction
                    self.emit (self.__VectorCreated, self.__world_origin, world_ray, QString('d')) # position = self.__world_origin, orientation = world_ray
            
            if j%10 == 0: # display to screen every 10 lines
                self.emit (self.__Update, float(j)/float(self.__height))
            
            if not self.carry_on:
                break
        
        self.emit (self.__Update, float(j)/float(self.__height))
        
        if self.carry_on: # if and only if the rendering was completed then fire this signal away.
            self.emit (self.__ThreadCompleted)
    
    
    def setCarryOnFlag (self, boo):
        '''
        setter. This methods puts the break on the rendering if boo is set to False.
        '''
        self.carry_on = boo
