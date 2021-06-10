# activereader

> Python library for reading Garmin TCX and GPX running activity files.

<!--[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)-->
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

<!-- ## Table of Contents    
- [Example](#example)                                                                
- [Background](#background)
- [Dependencies and Installation](#dependencies-and-installation)
- [License](#license)
- [Project Status](#project-status)
- [Contact](#contact) -->

## Example

activereader provides the `Tcx` and `Gpx` file reader classes.

TCX and GPX files can be exported from 
[Garmin Connect](http://connect.garmin.com/).

Use `Tcx` to read and access data from a TCX file:
```python
import pandas as pd

from activereader import Tcx

reader = Tcx.from_file('tests/testdata.tcx')

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
  } for tp in reader.trackpoints
]

df = pd.DataFrame.from_records(records)
```

## Background

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

## Dependencies and Installation

[lxml](https://lxml.de/) and [python-dateutil](https://dateutil.readthedocs.io/en/stable/)
are required.

The package is available on [PyPi](https://pypi.org/project/activereader) and can be installed with `pip`:

```
$ pip install activereader
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

This project is licensed under the MIT License. See
[LICENSE](https://github.com/aaron-schroeder/activereader/blob/master/LICENSE)
file for details.

## Project Status

The project has reached a stable point and I don't expect to be changing much
for now - future versions will likely build on what's here. But sometimes I
change my mind and tear everything apart, so who knows. This package will
remain focused on extracting data from GPX and TCX files...of that I feel sure.

### Complete

- Develop capability to read running `tcx` and `gpx` files.

### Current Activities

- Handle pauses and laps in files (things I avoid in my own workouts
  because they complicate and obscure the DATA!). The body keeps the score,
  but the watch keeps the stats.

### Future Work
  
- Expand capability to read running activity files
  - `.pwx` (is this Garmin?)

- Make a project wiki so I can be as verbose as I please.
  (*You mean this isn't you being verbose?*)

## Contact

Reach out to me at one of the following places!

- Website: [trailzealot.com](https://trailzealot.com)
- LinkedIn: [linkedin.com/in/aarondschroeder](https://www.linkedin.com/in/aarondschroeder/)
- Twitter: [@trailzealot](https://twitter.com/trailzealot)
- Instagram: [@trailzealot](https://instagram.com/trailzealot)
- GitHub: [github.com/aaron-schroeder](https://github.com/aaron-schroeder)