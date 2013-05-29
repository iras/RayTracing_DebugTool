'''
Created on May 27, 2013
@author: ivano.ras@gmail.com
MIT License
'''

from PyQt4.QtGui import QVector3D


class Model:
    '''
    model class
    '''
    
    def __init__ (self):
        '''
        Model constructor.
        '''
        self.__pid = 0 # polygon id counter
        
        
        self.__poly_list = [] # by poly I mean triangle.
        
        self.__poly_list.append ([QVector3D (2.0,  2.0, 2.0),
                                  QVector3D (2.0, -2.0, 2.0),
                                  QVector3D (-2.0,-2.0, 2.0),
                                  self.__pid])
        
        self.__pid += 1
        self.__poly_list.append ([QVector3D (4.0,  4.0, 4.0),
                                  QVector3D (4.0,  1.0, 4.0),
                                  QVector3D (10.0,  2.0, 4.0),
                                  self.__pid])
    
    def getPolyListCopy (self):
        
        return list (self.__poly_list) # return copy of list
