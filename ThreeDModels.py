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
        self.__pid = -1 # polygon id counter
        self.__poly_list = [] # by poly I really mean triangle.
        
        self.addIcosahedron()
        
    def getNewId (self):
        self.__pid += 1
        return self.__pid
        
    
    def getPolyListCopy (self):
        
        return list (self.__poly_list) # return copy of list
    
    def addIcosahedron (self):
        '''
        this method generates a icosahedron.
        Kudos to The little Grasshopper. http://prideout.net/blog/?p=48
        '''
        faces = [2,1,0,  3,2,0,  4,3,0,  5,4,0,  1,5,0,  11,6,7,  11,7,8,  11,8,9,  11,9,10,  11,10,6,
                 1,2,6,  2,3,7,  3,4,8,  4,5,9,  5,1,10,  2,7,6,   3,8,7,   4,9,8,   5,10,9,   1,6,10]
        
        verts = [0.0,0.0,1.0,            0.894,0.0,0.447,       0.276,0.851,0.447,
                 -0.724,0.526,0.447,    -0.724,-0.526,0.447,    0.276,-0.851,0.447,
                 0.724,0.526,-0.447,    -0.276,0.851,-0.447,   -0.894,0.000,-0.447,
                 -0.276,-0.851,-0.447,   0.724,-0.526,-0.447,   0.0,0.0,-1.0]
        
        for i in range (0, len(faces), 3):
            
            fi  = faces[i]*3
            fi1 = faces[i+1]*3
            fi2 = faces[i+2]*3
            
            a = QVector3D (verts[fi],  verts[fi+1],  verts[fi+2])
            b = QVector3D (verts[fi1], verts[fi1+1], verts[fi1+2])
            c = QVector3D (verts[fi2], verts[fi2+1], verts[fi2+2])
            
            self.__poly_list.append ([a, b, c,               # 3 vertices
                                      QVector3D.normal(a,b), # normal to vector
                                      self.getNewId()])      # polygon's id.
