# -*- coding: utf-8 -*-
""".tcx file reader architecture.

Originated in `heartandsole <https://github.com/aaron-schroeder/heartandsole/blob/affc028c266e108e669d93a99b19dbb8e176db49/heartandsole/filereaders.py#L295>`_
back in the day.

See also:

  `Garmin's TCX schema <https://www8.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd>`_
    XML file describing the schema for TCX files.

  `Garmin's ActivityExtension schema <https://www8.garmin.com/xmlschemas/ActivityExtensionv2.xsd>`_
    XML file describing Garmin's extensions to the TCX schema.
"""
import datetime
import io

from dateutil import tz
from lxml import etree

from . import util
from .base import (
  ActivityElement, 
  add_xml_data, add_xml_attr, add_xml_descendents,
  # add_data_props, add_attr_props, add_descendent_props,
  create_data_prop, create_attr_prop, create_descendent_prop
)


class Trackpoint(ActivityElement):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """
  TAG = 'Trackpoint'

  time = create_data_prop('Time', datetime.datetime)
  """datetime.datetime: Timestamp when trackpoint was recorded.
  
  See also:
    :ref:`data.timestamp`
  """
  
  # OR
  # @data_prop('dummy_tag', float)
  # 

  lat = create_data_prop('Position/LatitudeDegrees', float)
  """float: Latitude in degrees N (-90 to 90)."""

  lon = create_data_prop('Position/LongitudeDegrees', float)
  """float: Longitude in degrees E (-180 to 180)."""

  altitude_m = create_data_prop('AltitudeMeters', float)
  """float: Elevation of ground surface in meters above sea level."""

  distance_m = create_data_prop('DistanceMeters', float)
  """float: Cumulative distance from the start of the activity, in meters.
  
  See also:
    :ref:`data.distance`
  """

  hr = create_data_prop('HeartRateBpm/Value', int)
  """int: Heart rate."""

  speed_ms = create_data_prop('Extensions/TPX/Speed', float)
  """float: Speed in meters per second.
  
  TODO:
    * Consider looping this in to the explanation for distance data,
      maybe it can be a whole thing on sensor fusion with links.
  """

  cadence_rpm = create_data_prop('Extensions/TPX/RunCadence', int)
  """int: Cadence in RPM.
  
  See also:
    :ref:`data.cadence`
  """


class Track(ActivityElement):
  """In a running TCX file, there is typically one Track per Lap.

  As far as I can tell, in a running file, Tracks and Laps are one
  and the same; when a Lap starts or ends, so does its contained Track.
  
  Made up of 1 or more :class:`Trackpoint` in xml file.
  """
  TAG = 'Track'

  trackpoints = create_descendent_prop(Trackpoint)


@add_xml_data(
  intensity=('Intensity', str),
  trigger_method=('TriggerMethod', str),
)
class Lap(ActivityElement):
  """Represents one bout from {start/lap} -> {lap/stop}.

  There is at least one lap per activity file, created by the `start` button
  press and ended by the `stop` button press. Hitting the `lap` button begins
  a new lap. Hitting the pause button stops data recording, but the same lap
  resumes after the pause.
  
  Made up of 1 or more :class:`Track` in the XML structure.
  """
  TAG = 'Lap'

  start_time = create_attr_prop('StartTime', datetime.datetime)
  """datetime.datetime: Timestamp of lap start.
  
  See also:
    :ref:`data.timestamp`
  """

  total_time_s = create_data_prop('TotalTimeSeconds', float)
  """float: Total lap time, in seconds, as reported by the device.
  
  This is timer time, not elapsed time; it does not include any time when
  the device is paused.

  See also:
    :ref:`data.tcx.start_stop_pause`
  """

  distance_m = create_data_prop('DistanceMeters', float)
  """float: Total lap distance, in meters, as reported by the device.
  
  See also:
    :ref:`data.distance`
  """

  max_speed_ms = create_data_prop('MaximumSpeed', float)
  """float: The maximum speed achieved during the lap as reported by the 
  device, in meters per second.
  """

  avg_speed_ms = create_data_prop('Extensions/LX/AvgSpeed', float)
  """float: The average speed during the lap as reported by the device,
  in meters per second.
  """

  hr_avg = create_data_prop('AverageHeartRateBpm/Value', int)
  """float: average heart rate during the lap as reported by the device."""

  hr_max = create_data_prop('MaximumHeartRateBpm/Value', int)
  """float: maximum heart rate during the lap as reported by the device."""

  cadence_avg = create_data_prop('Extensions/LX/AvgRunCadence', int)
  """float: average cadence during the lap as reported by the device, in RPM.
  
  See also:
    :ref:`data.cadence`
  """

  cadence_max = create_data_prop('Extensions/LX/MaxRunCadence', int)
  """float: maximum cadence during the lap as reported by the device, in RPM.
  
  See also:
    :ref:`data.cadence`
  """

  calories = create_data_prop('Calories', int)
  """float: Calories burned during the lap as approximated by the device."""

  tracks = create_descendent_prop(Track)
  trackpoints = create_descendent_prop(Trackpoint)


@add_xml_data(product_id=('Creator/ProductID', int))
class Activity(ActivityElement):
  """TCX files representing a run should only contain one Activity.

  Contains one or more :class:`Lap` elements.
  """
  TAG = 'Activity'

  start_time = create_data_prop('Id', datetime.datetime)
  """datetime.datetime: Timestamp for activity start time.
  
  See also:
    :ref:`data.timestamp`
  """

  sport = create_attr_prop('Sport', str)
  """str: Activity sport. 
  
  Restricted to "Running", "Biking", or "Other" according to Garmin's TCX 
  file schema.
  """

  device = create_data_prop('Creator/Name', str)
  """str: Device brand name."""

  device_id = create_data_prop('Creator/UnitId', int)
  """int: Device ID - specific to the individual device."""
  
  @property
  def version(self):
    major = self.get_data('Creator/Version/VersionMajor', int)
    minor = self.get_data('Creator/Version/VersionMinor', int)
    return f'{major}.{minor}'

  @property
  def build(self):
    major = self.get_data('Creator/Version/BuildMajor', int)
    minor = self.get_data('Creator/Version/BuildMinor', int)
    return f'{major}.{minor}'

  laps = create_descendent_prop(Lap)
  tracks = create_descendent_prop(Track)
  trackpoints = create_descendent_prop(Trackpoint)


@add_xml_data(
  creator=('Author/Name', str),
  part_number=('Author/PartNumber', str)
)
class Tcx(ActivityElement):
  """Represents an entire .tcx file object."""

  TAG = 'TrainingCenterDatabase'

  @classmethod
  def from_file(cls, file_obj):
    """Initialize a Tcx element from a file-like object.

    Args:
      file_obj (str, bytes, io.StringIO, io.BytesIO): File-like object. 
        If str, either filename or a string representation of XML 
        object. If str or StringIO, the encoding should not be declared
        within the string.

    Returns:
      Tcx: An instance initialized with the :class:`~lxml.etree._Element`
      that was read in.

    See also:
      https://lxml.de/tutorial.html#the-parse-function

    TODO:
      * Consider if the master file readers should use a separate for
        creation, akin to etree.parse or from_string. Gah. I could make
        it more flexible, sure. But it seems weird to just have one
        random subclass with a different init. Maybe Tcx is the only
        one who gets this special extra class. Also naturally am
        thinking about delegating it.
      * How many delegated methods are we looking at now? parse, from_string,
        find_text, get, xpath, ... others?
        
    """
    if not isinstance(file_obj, (str, bytes, io.StringIO, io.BytesIO)):
      raise TypeError(f'file object type not accepted: {type(file_obj)}')

    if isinstance(file_obj, str) and not file_obj.lower().endswith('.tcx'):
      file_obj = io.StringIO(file_obj)
    elif isinstance(file_obj, bytes):
      file_obj = io.BytesIO(file_obj)

    # Note: tree is an ElementTree, which is just a thin wrapper
    # around root, which is an element
    tree = etree.parse(file_obj)
    root = tree.getroot()
    util.strip_namespaces(root)

    return cls(root)

  # Below here are convenience properties that access data from
  # descendent elements. Not sure if they all stay.

  @property
  def device(self):
    return self.activities[0].device

  @property
  def distance_m(self):
    return sum([lap.distance_m for lap in self.laps])

  @property
  def calories(self):
    return sum([lap.calories for lap in self.laps])

  @property
  def lap_time_s(self):
    return sum([lap.total_time_s for lap in self.laps])

  @property
  def num_laps(self):
    return len(self.laps)

  @property
  def num_bouts(self):
    return len(self.tracks)

  @property
  def num_records(self):
    return len(self.trackpoints)

  activities = create_descendent_prop(Activity)
  laps = create_descendent_prop(Lap)
  tracks = create_descendent_prop(Track)
  trackpoints = create_descendent_prop(Trackpoint)
