# -*- coding: utf-8 -*-
import unittest

import datetime

from activereader.tcx import TcxFileReader


class TestTcxFileReader(unittest.TestCase):

  @unittest.skip('Test with ya own damn files.')
  def test_create(self):
    """Integration test: create a TcxFileReader from .tcx file.
    
    TODO:
      * Test files with pauses and laps.
    """
    fname = 'activity_files/activity_3993313372.tcx'
    # fname = 'activity_files/activity_4257833732.tcx'
    # This file contains no elevation, speed, or cadence data.
    #fname = 'activity_files/20190425_110505_Running.tcx'

    tcx = TcxFileReader(fname)

    self.assertIsInstance(tcx, TcxFileReader)
    self.assertIsInstance(tcx.get_trackpoints(), list)
    self.assertIsInstance(tcx.activity_start_time, datetime.datetime)

  @unittest.skip('Test with ya own damn files.')
  def test_trackpoint(self):
    """More like a running list of properties."""
    fname = 'activity_files/activity_4257833732.tcx'

    tp = TcxFileReader(fname).get_trackpoints()[0]

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


  @unittest.skip('On hold - rethinking how this wants to work.')
  def test_header(self):
    print(tcx.date)
    print(tcx.device)
    print(tcx.distance)
    print(tcx.calories)
    print(tcx.lap_time_seconds)
    print(tcx.get_header_value('UnitId'))
    print(tcx.get_header_value('ProductID'))


if __name__ == '__main__':
  unittest.main()