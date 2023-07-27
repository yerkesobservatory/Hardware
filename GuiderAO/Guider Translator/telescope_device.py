# telescope_device.py - A virtual device to serve as an intermediate layer between SEO and 
# MaxIm DL.  We only need to implement methods relevant to pulse guide, with everything else
# already managed.

from threading import Timer
from threading import Lock
from logging import Logger

class TelescopeDevice:
    def __init(self, logger:Logger):
        self._lock = Lock()
        self.name: str = 'SEO Telescope'
        self.logger = logger
        #
        # Telescope Constants
        #
        self._alignmentmode = 0 # Alt/Az alignment
        self._aperturearea = 0.196 # Area of the SEO Telescope mirror
        self._aperturediameter = 0.5  # Aperture diameter of SEO telescope
        self._canfindhome = False # Not implemented in this driver
        self._canpark = False # Not implemented in this driver
        self._canpulseguide = True # To be implemented by us
        self._cansetdeclinationrate = False # Not implemented in this driver
        self.cansetguiderates = True # To be implemented by us
        self._cansetpark = False # TODO: Check with Marc and Dick
        self._cansetpierside = False # Not implemented in this driver
        self._cansetrightascensionrate = False # TODO: Check if we can actually set the RA rate
        self._cansettracking = False # Not implemented by us
        self._canslew = True 
        self._canslewaltaz = False
        self._canslewaltazasync = False
        self._canslewasync = True
        self._cansync = True
        self._canunpark = False # Not implemented in this driver
        self.declinationRate = 0 # Always 0 due to cansetdeclinationrate being False
        self._doesRefraction = False #SEO does not do atmospheric refration to coordinates
        self._equatorialsystem = 2 # J2000
        self._focallength = 2 # TODO: Check for SEO
        self._sideofpier = 0 # Cannot be changed
        self._siteelevation = 144 # TODO: Get this from Marc
        self._sitelatitude = 50 # TODO: Get real value
        self._sitelongitude = 70 # TODO: Get real value
        self._slewsettlingtime = 0.5 # TODO: Chose what value to set this to
        self._tracking = True # Cannot be changed
        self._trackingrate = 0 # Sidereal Tracking (15.041 arcs/s)
        self._trackingrates = [0] # We only have 1 rate
        #
        # Telescope state variables
        #
        self._altitude = 0
        self._athome = True
        self._atpark = True
        self._azimuth = 0
        self.declination = 0
        self._guideratedeclination = 0.1
        self._guideraterightascension = 0.1 
        self._ispulseguiding = False
        self._rightascension = 0
        self._rightascensionrate = 1
        self._siderealtime = 0.1
        self._slewing = False
        self._targetdeclination = 0
        self._targetrightascension = 0
        self._utcdate = None
