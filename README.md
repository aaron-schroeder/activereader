# py-activityreaders

> Python library for reading Garmin's running activity files.

<!--[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)-->
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

---

## Table of Contents                                                                    
- [Introduction](#introduction)
- [Dependencies and Installation](#dependencies-and-installation)
- [Example](#example)
- [Project Status](#project-status) <!-- - [References](#references) -->
- [Contact](#contact)
- [License](#license)

---

## Introduction

This project originated as the file-reading part of my 
[heartandsole package](https://github.com/aaron-schroeder/heartandsole).
Lately, I've been interested in keeping my work in more self-contained modules
with lighter dependencies, so I split it out.

The idea is to provide a simple API for accessing data from Garmin files, similar
to the way [`python-fitparse`](https://github.com/dtcooper/python-fitparse) 
provides access to Garmin's impenetrable `.fit` files. I don't aim to do everything,
though; I want to just focus on activity files that represent runs (and maybe walks/hikes)
for now. When I try to cover all cases, the schemas and profiles quickly grow out of 
control. Garmin seems to have a reputation for making their files indecipherable, and
I like solving puzzles, so I will focus on translating Garmin's language into human language.
This is in opposition to waiting for Garmin to document all the features of all its files. 

Tangent time: when I was working on picking apart Garmin's`.fit` file structure with my own
device's files, there were a number of undocumented, indecipherable fields. Add to that,
Garmin does not seem to keep documentation online for its older `.fit` SDKs, so if your
device uses an older one, you might just be out of luck trying to decipher it. I would
rather keep my own separate source of truth, than count on Garmin's being forthcoming 
with info.

---

## Dependencies and Installation

[lxml](https://lxml.de/) and [python-dateutil](https://dateutil.readthedocs.io/en/stable/)
are required.

To install (since I am not on pypi yet), first clone this repo.
```
git clone https://github.com/aaron-schroeder/py-activityreaders.git
```
Now you have a local version of this package that you can install with `pip`
(the `setup.py` file is configured to make this work).

Activate whatever virtual environment where you wish to install `activereader`,
and then:
```
pip install ${local_path_to_py-activityreader_dir}
```

---

## Example

`py-activityreaders` provides the `activereader` package.

Use `TcxFileReader` to read and access data from a `tcx` file. 
This file type can be exported from 
[Garmin Connect](http://connect.garmin.com/).
```python
import pandas as pd

from activereader import TcxFileReader

reader = TcxFileReader('activity_files/activity_3993313372.tcx')

# Build a DataFrame using only trackpoints (as records).
initial_time = reader.activity_start_time
records = [
  {
    'time': int((tp.time - initial_time).total_seconds()),
    'lat': tp.lat,
    'lon': tp.lon,
    'distance': tp.distance_m,
    'elevation': tp.altitude_m,
    'heart_rate': tp.hr,
    'speed': tp.speed_ms,
    'cadence': tp.cadence_rpm,
  } for tp in reader.get_trackpoints()
]

df = pd.DataFrame.from_records(records)
```
---

## Project Status

### Complete

- Develop capability to read running `tcx` and `gpx` files.
- 

### Current Activities

- Expand capability to read running activity files
  - `.pwx` (is this Garmin?)

### Future Work

- Handle pauses and laps in files (things I avoid in my own workouts
  because they complicate and obscure the DATA!). The body keeps the score,
  but the watch keeps the stats.

- Make a project wiki so I can be as verbose as I please.
  (*You mean this isn't you being verbose?*)

---

## Contact

You can get in touch with me at the following places:

<!-- - Website: <a href="https://trailzealot.com" target="_blank">trailzealot.com</a>-->
- GitHub: <a href="https://github.com/aaron-schroeder" target="_blank">github.com/aaron-schroeder</a>
- LinkedIn: <a href="https://www.linkedin.com/in/aarondschroeder/" target="_blank">linkedin.com/in/aarondschroeder</a>
- Twitter: <a href="https://twitter.com/trailzealot" target="_blank">@trailzealot</a>
- Instagram: <a href="https://instagram.com/trailzealot" target="_blank">@trailzealot</a>

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

This project is licensed under the MIT License. See
[LICENSE](https://github.com/aaron-schroeder/py-activityreaders/blob/master/LICENSE)
file for details.
