# -*- coding: utf-8 -*-
""".gpx file reader architecture."""
from lxml import etree

from . import util
from .base import ActivityElement


class GpxFileReader(object):

  def __init__(self, file_obj):
    self.tree = etree.parse(file_obj)
    root = self.tree.getroot()
    util.strip_namespaces(root)
    
    self.gpx = Gpx(root)

  def get_trackpoints(self):
    return [TrackPoint(tp) for tp in self.tree.xpath('//trkseg/trkpt')]

  @property
  def start_time(self):
    return self.gpx.start_time


class Gpx(ActivityElement):
  TAG = 'gpx'
  DATA_TAGS = {
    'start_time': ('metadata/time', 'time')
  }
  ATTR_TAGS = {
    'creator': ('creator', str),
    'version': ('version', str),
  }
  # CHILD_TAG = 'trk'

  def get_tracks(self):
    return [Track(child) for child in list(self.elem.iter('trk'))]

  def get_segments(self):
    return [Segment(e) for e in list(self.elem.iterfind('trk/trkseg'))]

  def get_trackpoints(self):
    return [TrackPoint(e) for e in list(self.elem.iterfind('trk/trkseg/trkpt'))]


class Track(ActivityElement):
  TAG = 'trk'
  DATA_TAGS = {
    'name': ('name', str),
    'activity_type': ('type', str)
  }
  # CHILD_TAG = 'trkseg'

  def get_segments(self):
    return [Segment(child) for child in list(self.elem.iter('trkseg'))]

  def get_trackpoints(self):
    return [TrackPoint(e) for e in list(self.elem.iterfind('trkseg/trkpt'))]


class Segment(ActivityElement):
  TAG = 'trkseg'
  
  def get_trackpoints(self):
    return [TrackPoint(child) for child in self.elem]


class TrackPoint(ActivityElement):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """
  TAG = 'trkpt'
  DATA_TAGS = {
    'time': ('time', 'time'),
    'altitude_m': ('ele', float),
    'hr': ('extensions/TrackPointExtension/hr', int),
    'cadence_rpm': ('extensions/TrackPointExtension/cad', int),
  }
  ATTR_NAMES = {
    'lat': ('lat', float),
    'lon': ('lon', float)
  }

  @property
  def distance_m(self):
    raise NotImplementedError

  @property
  def speed_ms(self):
    raise NotImplementedError
