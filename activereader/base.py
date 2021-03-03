import datetime

from dateutil import parser
from lxml import etree

class ActivityElement(object):
  TAG = 'element'
  CHILD_TAG = None
  DATA_TAGS = {
    # ${property_name}: ( ${tag_text}, ${expected_type} )
    # 'lat': ('Position/LatitudeDegrees', float)
  }
  ATTR_NAMES = {
    # ${property_name}: ( ${attr_name}, ${expected_type} )
    # 'lat': ('lat', float)  
  }

  def __init__(self, lxml_elem):

    if not isinstance(lxml_elem, etree._Element):
      raise TypeError(
        f'Expected lxml element, not f{typle(lxml_elem).__name__}'
      )
    
    if lxml_elem.tag != self.TAG:
      raise ValueError(
        f'Expected a {self.TAG} tag.'
      )

    self.elem = lxml_elem

    for prop_name, (tag_text, conv_type) in self.DATA_TAGS.items():
      self.add_data_property(prop_name, tag_text, conv_type)

    for prop_name, (attr_name, conv_type) in self.ATTR_NAMES.items():
      self.add_attr_property(prop_name, attr_name, conv_type)

    # if self.CHILD_TAG is not None:
    #   setattr(self,)

  @classmethod
  def add_data_property(cls, name, text, conv_type=str):
    setattr(
      cls,
      name,
      property(lambda self: self.get_data(text, conv_type))
    )

  @classmethod
  def add_attr_property(cls, name, attr_name, conv_type=str):
    setattr(
      cls,
      name,
      property(lambda self: self.get_attr(attr_name, conv_type))
    )

  def get_data(self, text, conv_type=str):
    if conv_type == datetime.datetime or conv_type == 'time':
      conv_func = parser.isoparse
    else:
      conv_func = conv_type

    try:
      return conv_func(self.elem.findtext(text))
    except TypeError:
      return None

  def get_attr(self, attr_name, conv_type=str):
    if conv_type == datetime.datetime or conv_type == 'time':
      conv_func = parser.isoparse
    else:
      conv_func = conv_type

    try:
      return conv_func(self.elem.get(attr_name))
    except TypeError:
      return None