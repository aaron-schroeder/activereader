.. _data:

Notes about file data
=======================

Device data
-----------

.. _data.distance:

Distance
^^^^^^^^

What your device reports as distance is usually not strictly the distance
between recorded GPS points. Most devices rely on a combination of GPS 
readings and accelerometer data, inferring the true distance travelled
using a cool process known as `sensor fusion`. Since GPS readings have a
bit of noise to them (see GPS section), the device's reported distance
is typically a little shorter than the sum of GPS point-to-point distances
(unless the GPS was malfunctioning badly or had no signal at all, in which
case the distance is inferred from the accelerometer data alone).

.. _data.cadence:

Cadence
^^^^^^^

For whatever reason, activity files report running cadence in RPM. In running,
we typically deal with cadence in strides per minute, which is twice the
RPM value. I think the use of RPM is a relic of the fact that cyclists, who use RPM,
tend to adopt new technology faster than runners. They were data-obsessed way before
we strapped on our first GPS-enabled watch. They got here first,
and they wanted cadence in RPM, and these file formats want to stay consistent.

.. _data.timestamp:

Timestamps
^^^^^^^^^^

Usually timestamp strings are timezone-aware, but that depends on how the input file is
formatted. Files exported from Garmin Connect have timestamps in 
`Coordinated Universal Time <https://en.wikipedia.org/wiki/Coordinated_Universal_Time>`_,
but different services or devices may generate different timestamp formats.
:math:`dateutil.parser.isoparse` processes the timestamp strings from the file.

TCX Files
---------

.. _data.tcx.start_stop_pause:

Starts, stops, and pauses
^^^^^^^^^^^^^^^^^^^^^^^^^

Unfortunately, although TCX files create a new lap
element when the lap button is pressed, they do not explicitly create
an artifact when the pause button is pressed. Trackpoints are simply 
not recorded. The only definitive proof that the pause button was pressed
is that the lap's :meth:`~activereader.tcx.Lap.total_time_s` is less than
its elapsed time (the difference between subsequent laps' 
:meth:`~activereader.tcx.Lap.start_time`).