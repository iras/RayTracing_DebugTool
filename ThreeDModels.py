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
        
        self.addIcosahedron (QVector3D( 5,  3, 1), QVector3D(2,2,2))
        self.addIcosahedron (QVector3D(-2, -2, 0), QVector3D(4,4,4))
        
    def getNewId (self):
        self.__pid += 1
        return self.__pid
        
    
    def getPolyListCopy (self):
        
        return list (self.__poly_list) # return copy of list
    
    def addIcosahedron (self, pos, scale):
        '''
        this method generates a icosahedron.
        Kudos to The little Grasshopper. http://prideout.net/blog/?p=48
        
        @param pos   QVector3D
        @param scale QVector3D
        '''
        
        p0=pos.x();    p1=pos.y();    p2=pos.z()  
        s0=scale.x();  s1=scale.y();  s2=scale.z()
        
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
            
            a = QVector3D (verts[fi] *s0+p0, verts[fi+1] *s1+p1, verts[fi+2] *s2+p2)
            b = QVector3D (verts[fi1]*s0+p0, verts[fi1+1]*s1+p1, verts[fi1+2]*s2+p2)
            c = QVector3D (verts[fi2]*s0+p0, verts[fi2+1]*s1+p1, verts[fi2+2]*s2+p2)
            
            self.__poly_list.append ([a, b, c,               # 3 vertices
                                      QVector3D.normal(a,b), # normal to vector
                                      self.getNewId()])      # polygon's id.
