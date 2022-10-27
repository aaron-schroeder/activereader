# -*- coding: utf-8 -*-
import unittest

import datetime
import io
import os

from lxml import etree

from activereader import tcx, gpx


class ActivityElementTestMixin(object):

  def setUp(self):
    with open(self.TESTDATA_FILENAME, 'rb') as fb:
      self.testdata_bin = fb.read()

    with open(self.TESTDATA_FILENAME, 'r') as fs:
      self.testdata_str = fs.read().replace(' encoding="UTF-8"', '')

  def test_read(self):
    data = [
      self.TESTDATA_FILENAME,
      io.BytesIO(self.testdata_bin),
      self.testdata_bin,
      self.testdata_str,
      io.StringIO(self.testdata_str),
    ]

    for i in range(len(data) - 1):
      r1 = self.reader.from_file(data[i]).elem
      r2 = self.reader.from_file(data[i+1]).elem
      self.assertEqual(etree.tostring(r1), etree.tostring(r2))
      # self.assertEqual(r1.text, r2.text)
      # self.assertEqual(r1.attrib, r2.attrib)
      # self.assertEqual(len(r1), len(r2))
    
    # print(etree.tostring(r1, encoding=str, pretty_print=False))

  def check_attr_types(self, activity_elem, expected_attr_types):
    """Check that each attribute exists and is of the correct type.

    Args:
      activity_elem (ActivityElement): The ActivityElement instance 
        to be checked.
      expected_attr_types (dict): Maps attribute names to their expected
        type or class.

    """    
    for attr_name, expected_type in expected_attr_types.items():
      attr = getattr(activity_elem, attr_name)
      self.assertIsNotNone(attr, attr_name)
      self.assertIsInstance(attr, expected_type)


class TestTcxFileReader(ActivityElementTestMixin, unittest.TestCase):

  TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata.tcx')
  reader = tcx.Tcx

  def test_integration(self):
    """Integration test: create a Tcx object from .tcx file."""
    # fname = 'activity_files/activity_3993313372.tcx'
    # fname = 'activity_files/activity_4257833732.tcx'
    # This file contains no elevation, speed, or cadence data.
    # fname = 'activity_files/20190425_110505_Running.tcx'

    reader = self.reader.from_file(self.TESTDATA_FILENAME)

    # print(f'Laps: {len(reader.laps)}')
    # for lap in reader.laps:
    #   print(lap.start_time - reader.laps[0].start_time)
    #   print(datetime.timedelta(seconds=lap.total_time_s))


    self.assertIsInstance(reader.trackpoints, list)

    self.check_attr_types(
      reader,
      dict(
        creator=str,
        part_number=str,
        device=str,
        distance_m=float,
        calories=int,
        lap_time_s=float,
        num_laps=int,
        num_bouts=int,
        num_records=int,

        # Retired methods that get data from other elements:
        # start_time=datetime.datetime,
        # activity_start_time=datetime.datetime,
        # date=datetime.date,  # how to test tz-aware?
        # activity_start_time_local=datetime.datetime,
      )
    )

    activities = reader.activities
    self.assertIsInstance(activities, list)
    self.assertIsInstance(activities[0], tcx.Activity)

    laps = reader.laps
    self.assertIsInstance(laps, list)
    self.assertIsInstance(laps[0], tcx.Lap)

    tracks = reader.tracks
    self.assertIsInstance(tracks, list)
    self.assertIsInstance(tracks[0], tcx.Track)

    trackpoints = reader.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], tcx.Trackpoint)


  def test_activity(self):
    activity = self.reader.from_file(self.TESTDATA_FILENAME).activities[0]

    self.check_attr_types(
      activity,
      dict(
        start_time=datetime.datetime,
        device=str,
        device_id=int,
        product_id=int,
        sport=str,
      )
    )

    laps = activity.laps
    self.assertIsInstance(laps, list)
    self.assertIsInstance(laps[0], tcx.Lap)

    tracks = activity.tracks
    self.assertIsInstance(tracks, list)
    self.assertIsInstance(tracks[0], tcx.Track)

    trackpoints = activity.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], tcx.Trackpoint)

  def test_lap(self):
    lap = self.reader.from_file(self.TESTDATA_FILENAME).laps[0]

    self.check_attr_types(
      lap,
      dict(
        start_time=datetime.datetime,
        total_time_s=float,
        distance_m=float,
        max_speed_ms=float,
        avg_speed_ms=float,
        calories=int,
        hr_avg=int,
        hr_max=int,
        cadence_avg=int,
        cadence_max=int,
        intensity=str,
        trigger_method=str,
      )
    )

    tracks = lap.tracks
    self.assertIsInstance(tracks, list)
    self.assertIsInstance(tracks[0], tcx.Track)

    trackpoints = lap.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], tcx.Trackpoint)

  def test_track(self):
    track = self.reader.from_file(self.TESTDATA_FILENAME).tracks[0]

    trackpoints = track.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], tcx.Trackpoint)


  def test_trackpoint(self):
    """More like a running list of properties."""

    tp = self.reader.from_file(self.TESTDATA_FILENAME).trackpoints[0]

    self.check_attr_types(
      tp,
      dict(
        time=datetime.datetime,
        lat=float,
        lon=float,
        distance_m=float,
        altitude_m=float,
        hr=int,
        speed_ms=float,
        cadence_rpm=int,
      )
    )


class TestGpxFileReader(ActivityElementTestMixin, unittest.TestCase):

  TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata.gpx')
  reader = gpx.Gpx
 
  def test_integration(self):
    g = self.reader.from_file(self.TESTDATA_FILENAME)

    self.check_attr_types(
      g,
      dict(
        start_time=datetime.datetime,
        creator=str,
        version=str,
        name=str,
      )
    )
    
    tracks = g.tracks
    self.assertIsInstance(tracks, list)
    self.assertIsInstance(tracks[0], gpx.Track)

    segments = g.segments
    self.assertIsInstance(segments, list)
    self.assertIsInstance(segments[0], gpx.Segment)

    trackpoints = g.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.Trackpoint)

  def test_track(self):
    track = self.reader.from_file(self.TESTDATA_FILENAME).tracks[0]

    self.check_attr_types(
      track,
      dict(
        name=str,
        activity_type=str,
      )
    )
    
    segments = track.segments
    self.assertIsInstance(segments, list)
    self.assertIsInstance(segments[0], gpx.Segment)

    trackpoints = track.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.Trackpoint)

  def test_segment(self):
    segment = self.reader.from_file(self.TESTDATA_FILENAME).segments[0]

    trackpoints = segment.trackpoints
    self.assertIsInstance(trackpoints, list)
    self.assertIsInstance(trackpoints[0], gpx.Trackpoint)

  def test_trackpoint(self):
    """More like a running list of properties."""
    tp = self.reader.from_file(self.TESTDATA_FILENAME).trackpoints[0]

    self.check_attr_types(
      tp,
      dict(
        time=datetime.datetime,
        lat=float,
        lon=float,
        altitude_m=float,
        hr=int,
        cadence_rpm=int,
      )
    )


class TestGpxFileReaderCourse(ActivityElementTestMixin, unittest.TestCase):
  TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testcourse.gpx')
  reader = gpx.Gpx

  def test_gpx(self):
    """Integration test: create a Gpx object from .gpx file."""
    reader = self.reader.from_file(self.TESTDATA_FILENAME)
    # print(dir(reader))
    self.assertEqual(len(reader.tracks), 0)
    self.assertEqual(len(reader.segments), 0)
    self.assertEqual(len(reader.trackpoints), 0)
    self.assertGreater(len(reader.routepoints), 0)

  def test_routepoint(self):
    rp = self.reader.from_file(self.TESTDATA_FILENAME).routepoints[0]

    self.check_attr_types(
      rp,
      dict(
        time=datetime.datetime,
        lat=float,
        lon=float,
        altitude_m=float,
        # hr=int,
        # cadence_rpm=int,
      )
    )


class TestTcxFileReaderCourse(ActivityElementTestMixin, unittest.TestCase):
  TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testcourse.tcx')
  reader = tcx.Tcx

  def test_tcx(self):
    """Integration test: create a Tcx object from .tcx file."""
    reader = self.reader.from_file(self.TESTDATA_FILENAME)
    self.assertEqual(len(reader.activities), 0)
    self.assertEqual(len(reader.laps), 1)
    self.assertEqual(len(reader.tracks), 1)
    self.assertGreater(len(reader.trackpoints), 0)

  def test_trackpoint(self):
    tp = self.reader.from_file(self.TESTDATA_FILENAME).trackpoints[0]

    self.check_attr_types(
      tp,
      dict(
        time=datetime.datetime,
        lat=float,
        lon=float,
        distance_m=float,
        altitude_m=float,
        # hr=int,
        # speed_ms=float,
        # cadence_rpm=int,
      )
    )

if __name__ == '__main__':
  unittest.main()