# -*- coding: utf-8 -*-
""".gpx file reader architecture.

Check out the schema here:
https://www.topografix.com/GPX/1/1/

Also check out Garmins GPX trackpoint extension in
activity_files/TrackPointExtensionv2.xsd

"""
import io

from lxml import etree

from . import util
from .base import ActivityElement


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


class Segment(ActivityElement):
  TAG = 'trkseg'
  DESCENDENT_CLASSES = {
    'trackpoints': TrackPoint,
  }


class Track(ActivityElement):
  TAG = 'trk'
  DATA_TAGS = {
    'name': ('name', str),
    'activity_type': ('type', str)
  }
  DESCENDENT_CLASSES = {
    'segments': Segment,
    'trackpoints': TrackPoint,
  }


# class GpxFileReader(object):
class Gpx(ActivityElement):
  TAG = 'gpx'
  DATA_TAGS = {
    'start_time': ('metadata/time', 'time'),
    'name': ('metadata/name', str),
  }
  ATTR_NAMES = {
    'creator': ('creator', str),
    'version': ('version', str),
  }
  DESCENDENT_CLASSES = {
    'tracks': Track,
    'segments': Segment,
    'trackpoints': TrackPoint,
  }

  def __init__(self, file_obj):
    """Creates a Gpx root object from an acceptable file object.

    Args:
      file_obj (str, bytes, io.StringIO, io.BytesIO): File-like object. 
        If str, either filename or a string representation of XML 
        object. If str or StringIO, the encoding should not be declared
        within the string.

    """
    if not isinstance(file_obj, (str, bytes, io.StringIO, io.BytesIO)):
      raise TypeError(f'file object type not accepted: {type(file_obj)}')

    if isinstance(file_obj, str) and not file_obj.lower().endswith('.gpx'):
      file_obj = io.StringIO(file_obj)
    elif isinstance(file_obj, bytes):
      file_obj = io.BytesIO(file_obj)

    tree = etree.parse(file_obj)
    root = tree.getroot()

    util.strip_namespaces(root)

    super().__init__(root)

  # @property
  # def name(self):
  #   # GPX elements sometimes don't have their own name, so default to
  #   # the first track's name.
  #   return self.tracks[0].name
