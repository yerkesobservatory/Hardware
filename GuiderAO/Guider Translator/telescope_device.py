# telescope_device.py - A virtual device to serve as an intermediate layer between SEO and
# MaxIm DL.  We only need to implement methods relevant to pulse guide, with everything else
# already managed.

from threading import Timer
from threading import Lock
from logging import Logger
import time


class TelescopeDevice:
    def __init__(self, logger: Logger):
        self._lock = Lock()
        self.name: str = 'SEO Telescope v2'
        self.logger = logger
        #
        # Telescope Constants
        #
        self._alignment_mode = 0  # Alt/Az alignment
        self._aperture_area = 0.196  # Area of the SEO Telescope mirror
        self._aperture_diameter = 0.5  # Aperture diameter of SEO telescope
        self._can_find_home = False  # Not implemented in this driver
        self._can_park = False  # Not implemented in this driver
        self._can_pulse_guide = True  # To be implemented by us
        self._can_set_declination_rate = False  # Not implemented in this driver
        self._can_set_guide_rates = True  # To be implemented by us
        self._can_set_park = False  # TODO: Check with Marc and Dick
        self._can_set_pier_side = False  # Not implemented in this driver
        # TODO: Check if we can actually set the RA rate
        self._can_set_right_ascension_rate = False
        self._can_set_tracking = False  # Not implemented by us
        self._can_slew = True
        self._can_slew_alt_az = False
        self._can_slew_alt_az_async = False
        self._can_slew_async = True
        self._can_sync = True
        self._can_unpark = False  # Not implemented in this driver
        self._declination_rate = 0  # Always 0 due to cansetdeclinationrate being False
        # SEO does not do atmospheric refraction to coordinates
        self._does_refraction = False
        self._equatorial_system = 2  # J2000
        self._focal_length = 2  # TODO: Check for SEO
        self._right_ascension_rate = 0  # 0 because canSetRightAscensionRate is False
        self._side_of_pier = 0  # Cannot be changed
        self._site_elevation = 144  # TODO: Get this from Marc
        self._site_latitude = 50  # TODO: Get real value
        self._site_longitude = 70  # TODO: Get real value
        self._slew_settling_time = 0.5  # TODO: Chose what value to set this to
        self._tracking_rate = 0  # Sidereal Tracking (15.041 arcs/s)
        self._tracking_rates = [0]  # We only have 1 rate
        #
        # Telescope state variables
        #
        self._altitude = 0
        self._at_home = True
        self._at_park = True
        self._azimuth = 0
        self._connected = False
        self._declination = 0
        self._guide_rate_declination = 0.1
        self._guide_rate_right_ascension = 0.1
        self._is_pulse_guiding = False
        self._right_ascension = 0
        self._sidereal_time = 0.1
        self._slewing = False
        self._tracking = True
        self._target_declination = 0
        self._target_right_ascension = 0
        self._utc_date = None

    # Connector methods
    @property
    def connected(self) -> bool:
        self._lock.acquire()
        res = self._connected
        self._lock.release()
        return res

    @connected.setter
    def connected(self, connected: bool):
        self._lock.acquire()
        if (not connected) and self._connected and self._slewing:
            self._lock.release()
            # Yes you could call Halt() but this is for illustration
            raise RuntimeError('Cannot disconnect while telescope is moving')
        elif (not connected) and self._connected and self._is_pulse_guiding:
            raise RuntimeError('Cannot disconnect while guider is tracking')
        self._connected = connected
        self._lock.release()
        if connected:
            self.logger.info('[connected]')
        else:
            self.logger.info('[disconnected]')

    #
    # Guarded properties
    #

    @property
    def alignment_mode(self) -> int:
        self._lock.acquire()
        res = self._alignment_mode
        self._lock.release()
        return res

    @property
    def aperture_area(self) -> float:
        self._lock.acquire()
        res = self._aperture_area
        self._lock.release()
        return res

    @property
    def aperture_diameter(self) -> float:
        self._lock.acquire()
        res = self._aperture_diameter
        self._lock.release()
        return res

    @property
    def can_find_home(self) -> bool:
        self._lock.acquire()
        res = self._can_find_home
        self._lock.release()
        return res

    @property
    def can_park(self) -> bool:
        self._lock.acquire()
        res = self._can_park
        self._lock.release()
        return res

    @property
    def can_pulse_guide(self) -> bool:
        self._lock.acquire()
        res = self._can_pulse_guide
        self._lock.release()
        return res

    @property
    def can_set_declination_rate(self) -> bool:
        self._lock.acquire()
        res = self._can_set_declination_rate
        self._lock.release()
        return res

    @property
    def can_set_guide_rates(self) -> bool:
        self._lock.acquire()
        res = self._can_set_guide_rates
        self._lock.release()
        return res

    @property
    def can_set_park(self) -> bool:
        self._lock.acquire()
        res = self._can_set_park
        self._lock.release()
        return res

    @property
    def can_set_pier_side(self) -> bool:
        self._lock.acquire()
        res = self._can_set_pier_side
        self._lock.release()
        return res

    @property
    def can_set_right_ascension_rate(self) -> bool:
        self._lock.acquire()
        res = self._can_set_right_ascension_rate
        self._lock.release()
        return res

    @property
    def can_set_tracking(self) -> bool:
        self._lock.acquire()
        res = self._can_set_tracking
        self._lock.release()
        return res

    @property
    def can_slew(self) -> bool:
        self._lock.acquire()
        res = self._can_slew
        self._lock.release()
        return res

    @property
    def can_slew_alt_az(self) -> bool:
        self._lock.acquire()
        res = self._can_slew_alt_az
        self._lock.release()
        return res

    @property
    def can_slew_alt_az_async(self) -> bool:
        self._lock.acquire()
        res = self._can_slew_alt_az_async
        self._lock.release()
        return res

    @property
    def can_slew_async(self) -> bool:
        self._lock.acquire()
        res = self._can_slew_async
        self._lock.release()
        return res

    @property
    def can_sync(self) -> bool:
        self._lock.acquire()
        res = self._can_sync
        self._lock.release()
        return res

    @property
    def can_unpark(self) -> bool:
        self._lock.acquire()
        res = self._can_unpark
        self._lock.release()
        return res

    @property
    def declination_rate(self) -> float:
        self._lock.acquire()
        res = self._declination_rate
        self._lock.release()
        return res

    @property
    def does_refraction(self) -> bool:
        self._lock.acquire()
        res = self._does_refraction
        self._lock.release()
        return res

    @property
    def equatorial_system(self) -> int:
        self._lock.acquire()
        res = self._equatorial_system
        self._lock.release()
        return res

    @property
    def focal_length(self) -> float:
        self._lock.acquire()
        res = self._focal_length
        self._lock.release()
        return res

    @property
    def right_ascension_rate(self) -> float:
        self._lock.acquire()
        res = self._right_ascension_rate
        self._lock.release()
        return res

    @property
    def side_of_pier(self) -> int:
        self._lock.acquire()
        res = self._side_of_pier
        self._lock.release()
        return res

    @property
    def site_elevation(self) -> float:
        self._lock.acquire()
        res = self._site_elevation
        self._lock.release()
        return res

    @property
    def site_latitude(self) -> float:
        self._lock.acquire()
        res = self._site_latitude
        self._lock.release()
        return res

    @property
    def site_longitude(self) -> float:
        self._lock.acquire()
        res = self._site_longitude
        self._lock.release()
        return res

    @property
    def slew_settling_time(self) -> float:
        self._lock.acquire()
        res = self._slew_settling_time
        self._lock.release()
        return res

    @property
    def tracking_rate(self) -> int:
        self._lock.acquire()
        res = self._tracking_rate
        self._lock.release()
        return res

    @property
    def tracking_rates(self) -> list:
        self._lock.acquire()
        res = self._tracking_rates
        self._lock.release()
        return res

    #
    # State properties
    #

    @property
    def altitude(self) -> float:
        self._lock.acquire()
        res = self._altitude
        self._lock.release()
        return res

    @altitude.setter
    def altitude(self, altitude: float):
        self._lock.acquire()
        self._altitude = altitude
        self._lock.release()

    @property
    def at_home(self) -> bool:
        self._lock.acquire()
        res = self._at_home
        self._lock.release()
        return res

    @at_home.setter
    def at_home(self, at_home: bool):
        self._lock.acquire()
        self._at_home = at_home
        self._lock.release()

    @property
    def azimuth(self) -> float:
        self._lock.acquire()
        res = self._azimuth
        self._lock.release()
        return res

    @azimuth.setter
    def azimuth(self, azimuth: float):
        self._lock.acquire()
        self._azimuth = azimuth
        self._lock.release()

    @property
    def at_park(self) -> bool:
        self._lock.acquire()
        res = self._at_park
        self._lock.release()
        return res

    @at_park.setter
    def at_park(self, at_park: bool):
        self._lock.acquire()
        self._at_park = at_park
        self._lock.release()

    @property
    def declination(self) -> float:
        self._lock.acquire()
        res = self._declination
        self._lock.release()
        return res

    @declination.setter
    def declination(self, declination: float):
        self._lock.acquire()
        self._declination = declination
        self._lock.release()

    @property
    def guide_rate_declination(self) -> float:
        self._lock.acquire()
        res = self._guide_rate_declination
        self._lock.release()
        return res

    @guide_rate_declination.setter
    def guide_rate_declination(self, guide_rate_declination: float):
        self._lock.acquire()
        self._guide_rate_declination = guide_rate_declination
        self._lock.release()

    @property
    def guide_rate_right_ascension(self) -> float:
        self._lock.acquire()
        res = self._guide_rate_right_ascension
        self._lock.release()
        return res

    @guide_rate_right_ascension.setter
    def guide_rate_right_ascension(self, guide_rate_right_ascension: float):
        self._lock.acquire()
        self._guide_rate_right_ascension = guide_rate_right_ascension
        self._lock.release()

    @property
    def is_pulse_guiding(self) -> bool:
        self._lock.acquire()
        res = self._is_pulse_guiding
        self._lock.release()
        return res

    @is_pulse_guiding.setter
    def is_pulse_guiding(self, ispulseguiding: bool):
        self._lock.acquire()
        self._is_pulse_guiding = ispulseguiding
        self._lock.release()

    @property
    def right_ascension(self) -> float:
        self._lock.acquire()
        res = self._right_ascension
        self._lock.release()
        return res

    @right_ascension.setter
    def right_ascension(self, right_ascension: float):
        self._lock.acquire()
        self._right_ascension = right_ascension
        self._lock.release()

    @property
    def sidereal_time(self) -> float:
        self._lock.acquire()
        res = self._sidereal_time
        self._lock.release()
        return res

    @sidereal_time.setter
    def sidereal_time(self, sidereal_time: float):
        self._lock.acquire()
        self._sidereal_time = sidereal_time
        self._lock.release()

    @property
    def slewing(self) -> bool:
        self._lock.acquire()
        res = self._slewing
        self._lock.release()
        return res

    @slewing.setter
    def slewing(self, slewing: bool):
        self._lock.acquire()
        self._slewing = slewing
        self._lock.release()

    @property
    def tracking(self) -> bool:
        self._lock.acquire()
        res = self._tracking
        self._lock.release()
        return res

    @tracking.setter
    def tracking(self, tracking: bool):
        self._lock.acquire()
        self._tracking = tracking
        self._lock.release()

    @property
    def target_declination(self) -> float:
        self._lock.acquire()
        res = self._target_declination
        self._lock.release()
        return res

    @target_declination.setter
    def target_declination(self, target_declination: float):
        self._lock.acquire()
        self._target_declination = target_declination
        self._lock.release()

    @property
    def target_right_ascension(self) -> float:
        self._lock.acquire()
        res = self._target_right_ascension
        self._lock.release()
        return res

    @target_right_ascension.setter
    def target_right_ascension(self, target_right_ascension: float):
        self._lock.acquire()
        self._target_right_ascension = target_right_ascension
        self._lock.release()

    @property
    def utc_date(self) -> str:
        self._lock.acquire()
        res = self._utc_date
        self._lock.release()
        return res
    
    #
    # Methods
    #

    def abort_slew(self):
        pass

    def action(self, action: str, parameters: list):
        pass

    def axis_rates(self, axis: int) -> list:
        pass

    def can_move_axis(self, axis: int) -> bool:
        pass

    def pulse_guide(self, direction: int, duration: int):
        self._is_pulse_guiding = True
        if direction == 0:
            self.logger.info("Pulse guide: N")
        elif direction == 1:
            self.logger.info("Pulse guide: S")
        elif direction == 2:
            self.logger.info("Pulse guide: E")
        elif direction == 3:
            self,logger.info("Pulse guide: W")
        self.logger.info("Pulse guide: {} ms".format(duration))
        time.sleep(duration / 1000)
        self._is_pulse_guiding = False
