# -*- coding: utf-8 -*-
""".tcx file reader architecture.

Originated in hns/filereaders.py.
"""
import datetime

from lxml import etree
from dateutil import tz

from . import util
from .base import ActivityElement


class TcxFileReader(object):
  """.tcx file reader Class."""

  def __init__(self, file_obj):
    """Initialize the reader from a file-like object.

    Args:
      file_obj(file or file-like object): Any accepted object accepted
        by `lxml.ElementTree.parse`.
        https://lxml.de/tutorial.html#the-parse-function
        
    """
    # Attach these fields to the instance in case the user wants 
    # to interact with the file data in some way.
    # Note: tree is an ElementTree, which is just a thin wrapper
    # around root, which is an element
    self.tree = etree.parse(file_obj)
    root = self.tree.getroot()
    util.strip_namespaces(root)

    self.tcx = Tcx(root)

    # activities = self.tree.xpath('//Activities/Activity')
    activities = self.tcx.get_activities()
    assert len(activities) == 1

    self.activity = activities[0]
    # activity = activities[0]

  @property
  def start_time(self):
    return self.activity_start_time

  @property
  def activity_start_time(self):
    """tz-aware datetime"""
    return self.activity.start_time
    
  @property
  def date(self):
    """Colorado time, baby."""
    return self.activity_start_time_local('US/Denver').date()

  def activity_start_time_local(self, tz_name):
    tz_local = tz.gettz(tz_name)
    return self.activity_start_time.astimezone(tz_local)

  @property
  def device(self):
    return self.activity.device

  @property
  def distance_m(self):
    return sum([lap.distance_m for lap in self.get_laps()])

  @property
  def calories(self):
    return sum([lap.calories for lap in self.get_laps()])

  @property
  def lap_time_s(self):
    return sum([lap.total_time_s for lap in self.get_laps()])

  @property
  def num_laps(self):
    return len(self.get_laps())

  @property
  def num_bouts(self):
    return len(self.get_tracks(self))

  @property
  def num_records(self):
    return len(self.get_trackpoints())

  def get_laps(self):
    #return [Lap(l) for l in self.tree.xpath('//Lap')]
    return [Lap(child) for child in self.activity.elem.iter('Lap')]

  def get_tracks(self):
    return [Track(e) for e in self.activity.elem.findall('Lap/Track')]

  def get_trackpoints(self):
    return [TrackPoint(e) for e in self.activity.elem.findall('Lap/Track/Trackpoint')]


class Tcx(ActivityElement):
  TAG = 'TrainingCenterDatabase'
  DATA_TAGS = {
    'creator': ('Author/Name', str),
    'part_number': ('Author/PartNumber', str)
  }

  def get_activities(self):
    return [Activity(e) for e in self.elem.findall('Activities/Activity')]


class Activity(ActivityElement):
  TAG = 'Activity'
  DATA_TAGS = {
    'start_time': ('Id', 'time'),
    'device': ('Creator/Name', str),
    'device_id': ('Creator/UnitId', int),
    # 'product_id': ('Creator/ProductID', int),
    # 'version_major': ('Creator/Version/VersionMajor', int),
    # 'version_minor': ('Creator/Version/VersionMinor', int),
    # 'build_minor': ('Creator/Version/BuildMajor', int),
    # 'build_minor': ('Creator/Version/BuildMinor', int),
  }
  ATTR_NAMES = {
    'sport': ('Sport', str)
  }

  def get_laps(self):
    return [Lap(e) for e in self.elem.iter('Lap')]

  def get_tracks(self):
    return [Track(e) for e in self.elem.iterfind('Lap/Track')]

  def get_trackpoints(self):
    return [TrackPoint(e) for e in self.elem.iterfind('Lap/Track/Trackpoint')]


class Lap(ActivityElement):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Track` in xml file.
  """
  TAG = 'Lap'
  DATA_TAGS = {
    'total_time_s': ('TotalTimeSeconds', float),
    'distance_m': ('DistanceMeters', float),
    'max_speed_ms': ('MaximumSpeed', float),
    'calories': ('Calories', int),
    'hr_avg': ('AverageHeartRateBpm/Value', int),
    'hr_max': ('MaximumHeartRateBpm/Value', int),
    'intensity': ('Intensity', str),
    'trigger_method': ('TriggerMethod', str),
  }
  ATTR_NAMES = {
    'start_time': ('StartTime', 'time'),
  }

  def get_tracks(self):
    return [Track(child) for child in self.elem.iter('Track')]

  def get_trackpoints(self):
    return [TrackPoint(e) for e in self.elem.iterfind('Track/Trackpoint')]


class Track(ActivityElement):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Trackpoint` in xml file.
  """
  TAG = 'Track'

  def get_trackpoints(self):
    return [TrackPoint(e) for e in self.elem.iter('Trackpoint')]


class TrackPoint(ActivityElement):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """
  TAG = 'Trackpoint'
  DATA_TAGS = {
    'time': ('Time', 'time'),
    # 'time': ('Time', datetime.datetime),
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