# -*- coding: utf-8 -*-
""".tcx file reader architecture.

Originated in hns/filereaders.py.
"""
import datetime

from dateutil import parser, tz
from lxml import etree, objectify


def get_time(time_text):
  """Returns a tz-aware datetime."""
  try:
    return parser.isoparse(time_text)
  except TypeError:
    return None


def conv_or_none(elem, text_to_find, conv_type):
  try:
    return conv_type(elem.findtext(text_to_find))
  except TypeError:
    return None


class TcxFileReader(object):
  """.tcx file reader Class.
  
  TODO:
    * Add properties for file header info (creator etc.)

  """

  def __init__(self, file_path):
    # Verify that this is .tcx (it should be if it is passed here)
    # if file_path.lower().endswith('.tcx'):

    # Attach these fields to the instance in case the user wants 
    # to interact with the file data in some way.
    # Note: tree is an ElementTree, which is just a thin wrapper
    # around root, which is an element
    self.tree = etree.parse(file_path)
    self.root = self.tree.getroot()

    self.strip_namespaces(self.root)

    assert self.root.tag == 'TrainingCenterDatabase'

    activities = self.tree.xpath('//Activities/Activity')
    assert len(activities) == 1

    self.activity_elem = activities[0]
    self.sport_name = self.activity_elem.get('Sport')

    # tz-aware datetime
    self.activity_start_time = get_time(self.activity_elem.findtext('Id'))
    
    # Not needed right now.
    # tz_local = tz.gettz('US/Denver')
    # activity_start_time_local = self.activity_start_time.astimezone(tz_local)

  @staticmethod
  def strip_namespaces(element):
    """Strip namespaces from all elements to permit easier operations.

    https://stackoverflow.com/questions/18159221/remove-namespace-and-prefix-from-xml-in-python-using-lxml
    
    From what I've heard, lxml isn't really smart enough to deal with
    them better than I can (by hand). I only have a few file types to
    deal with. 
    
    Kind of like how FitParse can deal with profile.xlsx, but I've opted
    to do that by hand. I think this is analogous?
    """
    for elem in element.getiterator():
      # Guard against comments.
      if not hasattr(elem.tag, 'find'): continue
      
      # Locate the extent of the namespace text and remove it.
      i = elem.tag.find('}')
      if i >= 0:
        elem.tag = elem.tag[i+1:]

    # Get rid of all the `'ns5': 'http://...'` and `xsi:type` business
    objectify.deannotate(element, cleanup_namespaces=True)

  def get_laps(self):
    #return [Lap(l) for l in self.tree.xpath('//Lap')]
    return [Lap(l) for l in self.activity_elem.iterfind('Lap')]

  def get_tracks(self):
    return [Track(t) for t in self.tree.xpath('//Track')]

  def get_trackpoints(self):
    return [TrackPoint(tp) for tp in self.tree.xpath('//Track/Trackpoint')]


class Lap(object):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Track` in xml file.
  """

  def __init__(self, lxml_elem):
    assert lxml_elem.tag == 'Lap'
    
    self.elem = lxml_elem
    self.start_time = get_time(self.elem.get('StartTime'))
    self.total_time_s = conv_or_none(self.elem, 'TotalTimeSeconds', float)
    self.distance_m = conv_or_none(self.elem, 'DistanceMeters', float)
    self.max_speed_ms = conv_or_none(self.elem, 'MaximumSpeed', float)
    self.calories = conv_or_none(self.elem, 'Calories', int)
    self.hr_avg = conv_or_none(self.elem, 'AverageHeartRateBpm/Value', int)
    self.hr_max = conv_or_none(self.elem, 'MaximumHeartRateBpm/Value', int)
    self.intensity = conv_or_none(self.elem, 'Intensity', str)
    self.trigger_method = conv_or_none(self.elem, 'TriggerMethod', str)

  def get_tracks(self):
    return [Track(t) for t in self.elem.iterfind('Track')]

  def get_trackpoints(self):
    return [TrackPoint(tp) for tp in self.elem.iterfind('Track/Trackpoint')]


class Track(object):
  """Represents one bout from {start/restart} -> {pause/stop}.
  
  Made up of 1 or more `Trackpoint` in xml file.
  """

  def __init__(self, lxml_elem):
    assert lxml_elem.tag == 'Track'
    
    self.elem = lxml_elem


class TrackPoint(object):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """

  def __init__(self, lxml_elem):
    assert lxml_elem.tag == 'Trackpoint'
    
    self.elem = lxml_elem

    # Might want to memoize these to make use of @property.
    self.time = get_time(self.elem.findtext('Time'))
    self.lat = conv_or_none(self.elem, 'Position/LatitudeDegrees', float)
    self.lon = conv_or_none(self.elem, 'Position/LongitudeDegrees', float)
    self.altitude_m = conv_or_none(self.elem, 'AltitudeMeters', float)
    self.distance_m = conv_or_none(self.elem, 'DistanceMeters', float)
    self.hr = conv_or_none(self.elem, 'HeartRateBpm/Value', int)
    self.speed_ms = conv_or_none(self.elem, 'Extensions/TPX/Speed', float)
    self.cadence_rpm = conv_or_none(self.elem, 'Extensions/TPX/RunCadence', int)
    # self.running_smoothness = 
    # self.stance_time = 
    # self.vertical_oscillation = 
      