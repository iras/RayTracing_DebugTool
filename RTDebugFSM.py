'''
Created on June 6, 2013
@author: ivano.ras@gmail.com
MIT license
'''

import errno
from main import Ui_Form
from RTEngine import REngineThread
from OpenGLCompo import OGLViewer


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class State:
    '''
    Abstract State class
    '''
    def __init__(self, fsm):
        
        # protected var. It'll be inherited by the subclass DebugStateMachine's instances.
        self._fsm    = fsm
    
    def startRendering (self):  assert 0, "start-rendering not implemented"
    def pauseRendering (self):  assert 0, "pause-rendering not implemented"
    def resetRendering (self):  assert 0, "reset-rendering not implemented"
    def finaliseRender (self):  assert 0, "finalise-render not implemented"


class Reset (State):
    '''
    Reset State class
    '''
    def __init__(self, fsm):
        State.__init__ (self, fsm)
    
    def startRendering (self):
        
        self._fsm.delegateUIButtonsEnabling ({'renderBtn'   :False,  'pauseBtn'   :True,   'stopBtn'    :True,   'upBtn'      :False,
                                              'downBtn'     :False,  'moreDownBtn':False,  'moreUpBtn'  :False,  'rightBtn'   :False,
                                              'moreRightBtn':False,  'leftBtn'    :False,  'furtherLeft':False,  'progressBar':'reset'})
        self._fsm.delegateCameraAddition ()
        self._fsm.delegateScreenshotAddition ()
        self._fsm.delegateEnginePrepAndStart ()
        
        return self._fsm.getPlayingState()
    
    def resetRendering (self):
        raise Error ("Already reset. This message shouldn't appear as the reset button should be greyed out.")
    
    def pauseRendering (self):
        raise Error ("Can't pause when state is reset. This message shouldn't appear as the reset button should be greyed out.")
    
    def finaliseRender (self):
        raise Error ("Can't finalise rendering when state is reset.")


class Started (State):
    '''
    Started State class
    '''
    def __init__(self, fsm):
        State.__init__ (self, fsm)
    
    def startRendering (self):
        raise Error ("Already rendering. This message shouldn't appear as the reset button should be greyed out.")
    
    def resetRendering (self):
        
        self._fsm.delegateUIButtonsEnabling ({'renderBtn'   :True,   'pauseBtn'   :False,  'stopBtn'    :False,  'upBtn'      :False,
                                              'downBtn'     :False,  'moreDownBtn':False,  'moreUpBtn'  :False,  'rightBtn'   :False,
                                              'moreRightBtn':False,  'leftBtn'    :False,  'furtherLeft':False,  'progressBar':''})
        self._fsm.delegateCarryOnFlagSetting (False)
        
        return self._fsm.getStoppedState ()
    
    def pauseRendering (self):
        raise Error ("TODO Started:pauseRendering")
    
    def finaliseRender (self):
        
        self._fsm.delegateUIButtonsEnabling ({'renderBtn'   :True,   'pauseBtn'   :False,  'stopBtn'    :False,  'upBtn'      :False,
                                              'downBtn'     :False,  'moreDownBtn':False,  'moreUpBtn'  :False,  'rightBtn'   :False,
                                              'moreRightBtn':False,  'leftBtn'    :False,  'furtherLeft':False,  'progressBar':'completed'})
        return self._fsm.getStoppedState ()


class Paused (State):
    '''
    Paused State class
    '''
    def __init__(self, fsm):
        State.__init__ (self, fsm)
    
    def startRendering (self):
        raise Error ("TODO Paused:startRendering")
    
    def resetRendering (self):
        raise Error ("TODO Paused:resetRendering")
    
    def pauseRendering (self):
        raise Error ("TODO Paused:pauseRendering")
    
    def finaliseRender (self):
        raise Error ("TODO Paused:finaliseRender")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class DebugStateMachine ():
    '''
    Debug State Machine class
    '''
    
    def __init__ (self, ui):
        
        self.__ui = ui
        
        self.__state_stopped = Reset   (self)
        self.__state_paused  = Paused  (self)
        self.__state_playing = Started (self)
        
        self.__currentState  = self.__state_stopped
    
    def startRendering (self): self.__currentState = self.__currentState.startRendering ()
    def stopRendering  (self): self.__currentState = self.__currentState.resetRendering ()
    def finaliseRender (self): self.__currentState = self.__currentState.finaliseRender ()
    
    # delegates
    def delegateUIButtonsEnabling  (self, dict_ui): self.__ui.enableUIButtons (dict_ui)
    def delegateCarryOnFlagSetting (self, boo):     self.__ui.setCarryOnFlag (boo)
    def delegateEnginePrepAndStart (self):          self.__ui.prepAndStartEngineUp ()
    def delegateScreenshotAddition (self):          self.__ui.addScreenshot ()
    def delegateCameraAddition     (self):          self.__ui.addCamera ()
    
    # state getters
    def getStoppedState (self): return self.__state_stopped
    def getPausedState  (self): return self.__state_paused
    def getPlayingState (self): return self.__state_playing
