import datetime

from dateutil import parser
from lxml import objectify


def get_conv_func(conv_type):
  if conv_type == datetime.datetime:
    return parser.isoparse
  
  # Assume this is a Python type
  return conv_type


def get_time(time_text):
  """Returns a tz-aware datetime."""
  try:
    return parser.isoparse(time_text)
  except TypeError:
    return None


def strip_namespaces(element):
  """Strip namespaces from an elements to permit easier operations.

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