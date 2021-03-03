# -*- coding: utf-8 -*-
import unittest

import datetime

# from activereader.tcx import TcxFileReader
from activereader import tcx
# from activereader.gpx import GpxFileReader
from activereader import gpx


class TestTcxFileReader(unittest.TestCase):

  #@unittest.skip('Test with ya own damn files.')
  def test_create(self):
    """Integration test: create a TcxFileReader from .tcx file.
    
    TODO:
      * Test files with pauses and laps.
    """
    fname = 'activity_files/activity_3993313372.tcx'
    # fname = 'activity_files/activity_4257833732.tcx'
    # This file contains no elevation, speed, or cadence data.
    #fname = 'activity_files/20190425_110505_Running.tcx'

    reader = tcx.TcxFileReader(fname)

    self.assertIsInstance(reader, tcx.TcxFileReader)
    self.assertIsInstance(reader.get_trackpoints(), list)
    self.assertIsInstance(reader.activity_start_time, datetime.datetime)

  def test_lap(self):
    fname = 'activity_files/activity_4257833732.tcx'
    lap = tcx.TcxFileReader(fname).get_laps()[0]

    expected_attr_types = dict(
      start_time=datetime.datetime,
      total_time_s=float,
      distance_m=float,
      max_speed_ms=float,
      calories=int,
      hr_avg=int,
      hr_max=int,
      intensity=str,
      trigger_method=str,
    )

    for attr_name, expected_type in expected_attr_types.items():
      attr = getattr(lap, attr_name)
      self.assertIsNotNone(attr, attr_name)
      self.assertIsInstance(attr, expected_type)

  #@unittest.skip('Test with ya own damn files.')
  def test_trackpoint(self):
    """More like a running list of properties."""
    fname = 'activity_files/activity_4257833732.tcx'

    tp = tcx.TcxFileReader(fname).get_trackpoints()[0]

    expected_attr_types = dict(
      time=datetime.datetime,
      lat=float,
      lon=float,
      distance_m=float,
      altitude_m=float,
      hr=int,
      speed_ms=float,
      cadence_rpm=int,
    )

    for attr_name, expected_type in expected_attr_types.items():
      attr = getattr(tp, attr_name)
      self.assertIsNotNone(attr, attr_name)
      self.assertIsInstance(attr, expected_type)


  def test_summary(self):
    fname = 'activity_files/activity_4257833732.tcx'
    reader = tcx.TcxFileReader(fname)

    expected_attr_types = dict(
      date=datetime.date,
      start_time=datetime.datetime,
      device=str,
      distance_m=float,
      calories=int,
      lap_time_s=float,
    )

    for attr_name, expected_type in expected_attr_types.items():
      attr = getattr(reader, attr_name)
      self.assertIsNotNone(attr, attr_name)
      self.assertIsInstance(attr, expected_type)


class TestActivityElement(unittest.TestCase):

  def test_create(self):
    pass

class TestGpxFileReader(unittest.TestCase):

  #@unittest.skip('Test with ya own damn files.')
  def test_create(self):
    """Integration test: create a GpxFileReader from .gpx file.
    
    TODO:
      * Test files with pauses and laps.
    """
    # Same activity from Garmin Connect and Strava, respectively.
    fname = 'activity_files/activity_6339652005.gpx'
    # fname = 'activity_files/Lunch_Run.gpx'

    reader = gpx.GpxFileReader(fname)

    self.assertIsInstance(reader, gpx.GpxFileReader)
    # self.assertIsInstance(gpx.get_trackpoints(), list)
    # self.assertIsInstance(gpx.activity_start_time, datetime.datetime)

  def test_gpx(self):
    fname = 'activity_files/activity_6339652005.gpx'
    reader = gpx.GpxFileReader(fname)
    g = reader.gpx
    self.assertIsInstance(g, gpx.Gpx)
    self.assertIsInstance(reader.gpx.start_time, datetime.datetime)
    
    tracks = g.get_tracks()
    self.assertIsInstance(tracks, list)
    self.assertIsInstance(tracks[0], gpx.Track)

    segments = g.get_segments()
    self.assertIsInstance(segments, list)
    self.assertIsInstance(segments[0], gpx.Segment)

    trackpoints = g.get_trackpoints()
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.TrackPoint)

  def test_track(self):
    fname = 'activity_files/activity_6339652005.gpx'
    reader = gpx.GpxFileReader(fname)
    track = reader.gpx.get_tracks()[0]
    
    segments = track.get_segments()
    self.assertIsInstance(segments, list)
    self.assertIsInstance(segments[0], gpx.Segment)

    trackpoints = track.get_trackpoints()
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.TrackPoint)

  def test_segment(self):
    fname = 'activity_files/activity_6339652005.gpx'
    segment = gpx.GpxFileReader(fname).gpx.get_segments()[0]

    trackpoints = segment.get_trackpoints()
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.TrackPoint)

  def test_trackpoint(self):
    """More like a running list of properties."""
    fname = 'activity_files/activity_6339652005.gpx'

    tp = gpx.GpxFileReader(fname).get_trackpoints()[0]

    expected_attr_types = dict(
      time=datetime.datetime,
      lat=float,
      lon=float,
      # distance_m=float,
      altitude_m=float,
      hr=int,
      # speed_ms=float,
      cadence_rpm=int,
    )

    for attr_name, expected_type in expected_attr_types.items():
      attr = getattr(tp, attr_name)
      self.assertIsNotNone(attr, attr_name)
      self.assertIsInstance(attr, expected_type)

if __name__ == '__main__':
  unittest.main()