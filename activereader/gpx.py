# -*- coding: utf-8 -*-
""".gpx file reader architecture.

See also:
  
  `GPX schema <https://www.topografix.com/GPX/1/1/>`_
    Official documentation for GPX elements and file structure.

  `Garmin's GPX trackpoint extension schema <https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd>`_
    XML file describing the schema for Garmin's additional GPX trackpoint elements.
"""
import datetime
import io

from lxml import etree

from . import util
from .base import (
  ActivityElement,
  add_xml_data, add_xml_attr, add_xml_descendents, 
  create_data_prop, create_attr_prop, create_descendent_prop
)


class Trackpoint(ActivityElement):
  """Represents a single data sample corresponding to a point in time.
  
  The most granular of data contained in the file.
  """
  TAG = 'trkpt'

  time = create_data_prop('time', datetime.datetime)
  """datetime.datetime: Timestamp when trackpoint was recorded.
  
  See also:
    :ref:`data.timestamp`
  """

  altitude_m = create_data_prop('ele', float)
  """float: Elevation of ground surface in meters above sea level."""

  hr = create_data_prop('extensions/TrackPointExtension/hr', int)
  """int: Heart rate."""

  cadence_rpm = create_data_prop('extensions/TrackPointExtension/cad', int)
  """int: Cadence in RPM.
  
  See also:
    :ref:`data.cadence`
  """

  lat = create_attr_prop('lat', float)
  """float: Latitude in degrees N (-90 to 90)."""

  lon = create_attr_prop('lon', float)
  """float: Longitude in degrees E (-180 to 180)."""


class Segment(ActivityElement):
  """Holds a list of trackpoints which are logically connected in order.
  
  To represent a single GPS track where GPS reception was lost, or the 
  GPS receiver was turned off, start a new Track Segment for each continuous
  span of track data.
  """
  TAG = 'trkseg'

  trackpoints = create_descendent_prop(Trackpoint)


@add_xml_data(
  name=('name', str),
  activity_type=('type', str),
)
class Track(ActivityElement):
  """An ordered list of trackpoints describing a path."""
  TAG = 'trk'

  segments = create_descendent_prop(Segment)
  trackpoints = create_descendent_prop(Trackpoint)


@add_xml_data(name=('metadata/name', str))
@add_xml_attr(
  creator=('creator', str),
  version=('version', str),
)
class Gpx(ActivityElement):
  """Represents an entire .gpx file object."""

  TAG = 'gpx'

  @classmethod
  def from_file(cls, file_obj):
    """Initialize a Gpx element from a file-like object.

    Args:
      file_obj (str, bytes, io.StringIO, io.BytesIO): File-like object. 
        If str, either filename or a string representation of XML 
        object. If str or StringIO, the encoding should not be declared
        within the string.

    Returns:
      Gpx: An instance initialized with the :class:`~lxml.etree._Element`
      that was read in.

    See also:
      https://lxml.de/tutorial.html#the-parse-function

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

    return cls(root)

  start_time = create_data_prop('metadata/time', datetime.datetime)
  """datetime.datetime: Timestamp at start of recording.
  
  See also:
    :ref:`data.timestamp`
  """

  # @property
  # def name(self):
  #   # GPX elements sometimes don't have their own name, so default to
  #   # the first track's name.
  #   return self.tracks[0].name

  tracks = create_descendent_prop(Track)
  segments = create_descendent_prop(Segment)
  trackpoints = create_descendent_prop(Trackpoint)
