'''
Created on May 16, 2013
@author: ivano.ras@gmail.com
MIT license
'''

import math
from PyQt4.QtGui import QMatrix4x4 


class Tools:
    '''
    MathTools class
    '''
    
    def __init__(self, mtx = QMatrix4x4 (1.0,0.0,0.0,0.0,  0.0,1.0,0.0,0.0,  0.0,0.0,1.0,0.0,  0.0,0.0,0.0,1.0)):
        '''
        Constructor
        '''
        self.__normal_mtx  = mtx
        self.__pi_over_180 = math.pi / 180
        self.__he_over_pi  = 1 / self.__pi_over_180
        self.__h = 0.5
    
    
    def cameraToWorldTransform (self, vx, vy, vz):
        '''
        this method right multiplies the camera normal transform matrix by a given vector (vx, vy, vz,1)
        and returns a 3-list, the last bottom value=1 is not returned.
        '''
        m_ref = self.__normal_mtx.data () # retrieves the 16 items in this matrix and copies them to values in row-major order.
        
        return [m_ref[0]*vx + m_ref[4]*vy + m_ref[8]*vz  + m_ref[12],
                m_ref[1]*vx + m_ref[5]*vy + m_ref[9]*vz  + m_ref[13],
                m_ref[2]*vx + m_ref[6]*vy + m_ref[10]*vz + m_ref[14]]
    
    
    def normalise (self, vect):
        '''
        this method returns a normalised vector as a 3-list.
        '''
        vx = vect[0]; vy = vect[1]; vz = vect[2]
        euclidean_norm = math.sqrt (vx*vx + vy*vy +vz*vz)
        inv_norm = 1 / euclidean_norm
        
        return [vx*inv_norm, vy*inv_norm, vz*inv_norm]
    
    
    def setNormalMatrix (self, normal_mtx):
        '''
        setter
        '''
        self.__normal_mtx = normal_mtx
    
    
    def getAngle (self, fovy):
        '''
        this method calculates the angle the camera opens to based on the value of the "field of view, y".
        '''
        return math.tan (fovy / 2 * self.__pi_over_180)
    
    
    def alignZAxisToVector (self, v_x, v_y, v_z):
        '''
        this method calculates the angles the y-axis needs to rotate around to overlap to the given vector.
        '''
        v_x2=v_x*v_x;
        v_y2=v_y*v_y;
        v_z2=v_z*v_z
        
        xz_dist = math.sqrt (v_x2 + v_z2)
        v_dist  = math.sqrt (v_x2 + v_y2 + v_z2)
                
        if xz_dist == 0:
            if v_x > 0:
                y_angle =  math.pi * self.__h   #  90 degrees in radians
            else:
                y_angle = -math.pi * self.__h   # -90 degrees in radians
        else:
            y_angle = math.acos (v_z / xz_dist) # y_angle in radians
        
        x_angle = math.acos (xz_dist / v_dist)  # x_angle in radians
        
        if v_y > 0:
            pass
        else:
            x_angle = - x_angle
            
        if v_x > 0:
            y_angle = - y_angle
        
        return [x_angle * self.__he_over_pi,  y_angle * self.__he_over_pi, 0] # return angles (degrees) around main axes.
