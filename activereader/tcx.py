# -*- coding: utf-8 -*-
""".tcx file reader architecture.

Originated in hns/filereaders.py.
"""
import datetime
import io

from dateutil import tz
from lxml import etree

from . import util
from .base import ActivityElement


class TrackPoint(ActivityElement):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """
  TAG = 'Trackpoint'
  DATA_TAGS = {
    'time': ('Time', 'time'),
    'lat': ('Position/LatitudeDegrees', float),
    'lon': ('Position/LongitudeDegrees', float),
    'altitude_m': ('AltitudeMeters', float),
    'distance_m': ('DistanceMeters', float),
    'hr': ('HeartRateBpm/Value', int),
    'speed_ms': ('Extensions/TPX/Speed', float),
    'cadence_rpm': ('Extensions/TPX/RunCadence', int),
  }

  @property
  def running_smoothness(self):
    raise NotImplementedError

  @property
  def stance_time(self):
    raise NotImplementedError

  @property
  def vertical_oscillation(self):
    raise NotImplementedError


class Track(ActivityElement):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Trackpoint` in xml file.
  """
  TAG = 'Track'
  DESCENDENT_CLASSES = {
    'trackpoints': TrackPoint,
  }


class Lap(ActivityElement):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Track` in xml file.
  """
  TAG = 'Lap'
  DATA_TAGS = {
    'total_time_s': ('TotalTimeSeconds', float),
    'distance_m': ('DistanceMeters', float),
    'max_speed_ms': ('MaximumSpeed', float),
    'avg_speed_ms': ('Extensions/LX/AvgSpeed', float),
    'calories': ('Calories', int),
    'hr_avg': ('AverageHeartRateBpm/Value', int),
    'hr_max': ('MaximumHeartRateBpm/Value', int),
    'cadence_avg': ('Extensions/LX/AvgRunCadence', int),
    'cadence_max': ('Extensions/LX/MaxRunCadence', int),
    'intensity': ('Intensity', str),
    'trigger_method': ('TriggerMethod', str),
  }
  ATTR_NAMES = {
    'start_time': ('StartTime', 'time'),
  }
  DESCENDENT_CLASSES = {
    'tracks': Track,
    'trackpoints': TrackPoint,
  }


class Activity(ActivityElement):
  TAG = 'Activity'
  DATA_TAGS = {
    'start_time': ('Id', 'time'),
    'device': ('Creator/Name', str),
    'device_id': ('Creator/UnitId', int),
    'product_id': ('Creator/ProductID', int),
    # 'version_major': ('Creator/Version/VersionMajor', int),
    # 'version_minor': ('Creator/Version/VersionMinor', int),
    # 'build_minor': ('Creator/Version/BuildMajor', int),
    # 'build_minor': ('Creator/Version/BuildMinor', int),
  }
  ATTR_NAMES = {
    'sport': ('Sport', str)
  }
  DESCENDENT_CLASSES = {
    'laps': Lap,
    'tracks': Track,
    'trackpoints': TrackPoint,
  }


class Tcx(ActivityElement):
  """.tcx file reader Class."""

  TAG = 'TrainingCenterDatabase'
  DATA_TAGS = {
    'creator': ('Author/Name', str),
    'part_number': ('Author/PartNumber', str)
  }
  DESCENDENT_CLASSES = {
    'activities': Activity,
    'laps': Lap,
    'tracks': Track,
    'trackpoints': TrackPoint,
  }

  def __init__(self, file_obj):
    """Initialize the reader from a file-like object.

    Args:
      file_obj(file or file-like object): Any accepted object accepted
        by `lxml.ElementTree.parse`.
        https://lxml.de/tutorial.html#the-parse-function
        
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

    super().__init__(root)

  # Below here are convenience properties that access data from
  # descendent elements.

  @property
  def start_time(self):
    return self.activity_start_time

  @property
  def activity_start_time(self):
    """tz-aware datetime"""
    return self.activities[0].start_time
    
  @property
  def date(self):
    """Colorado time, baby."""
    return self.activity_start_time_local('US/Denver').date()

  def activity_start_time_local(self, tz_name):
    tz_local = tz.gettz(tz_name)
    return self.activity_start_time.astimezone(tz_local)

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
