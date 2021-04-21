import datetime

from dateutil import parser
from lxml import etree

class ActivityElement(object):
  TAG = 'element'
  DATA_TAGS = {
    # ${property_name}: ( ${tag_text}, ${expected_type} )
    # 'lat': ('Position/LatitudeDegrees', float)
  }
  ATTR_NAMES = {
    # ${property_name}: ( ${attr_name}, ${expected_type} )
    # 'lat': ('lat', float)  
  }
  DESCENDENT_CLASSES = {
    # ${property_name}: ${descendent_class}
    # 'trackpoints: TrackPoint
  }

  def __init__(self, lxml_elem):

    if not isinstance(lxml_elem, etree._Element):
      raise TypeError(
        f'Expected lxml element, not {type(lxml_elem).__name__}'
      )
    
    if lxml_elem.tag != self.TAG:
      raise ValueError(
        f'Expected lxml element with "{self.TAG}" tag, not "{lxml_elem.tag}".'
      )

    self.elem = lxml_elem

    for prop_name, (tag_text, conv_type) in self.DATA_TAGS.items():
      self.add_data_property(prop_name, tag_text, conv_type)

    for prop_name, (attr_name, conv_type) in self.ATTR_NAMES.items():
      self.add_attr_property(prop_name, attr_name, conv_type)

    for prop_name, descendent_class in self.DESCENDENT_CLASSES.items():
      self.add_descendent_list_property(prop_name, descendent_class)

  @classmethod
  def add_data_property(cls, prop_name, tag, conv_type=str):
    setattr(
      cls,
      prop_name,
      property(lambda self: self.get_data(tag, conv_type))
    )

  @classmethod
  def add_attr_property(cls, prop_name, attr_name, conv_type=str):
    setattr(
      cls,
      prop_name,
      property(lambda self: self.get_attr(attr_name, conv_type))
    )

  @classmethod
  def add_descendent_list_property(cls, prop_name, descendent_class):
    setattr(
      cls,
      prop_name,
      property(lambda self: [descendent_class(e) for e in self.elem.xpath(f'.//{descendent_class.TAG}')])
    )

  def get_data(self, tag, conv_type=str):
    if conv_type == datetime.datetime or conv_type == 'time':
      conv_func = parser.isoparse
    else:
      conv_func = conv_type

    data = self.elem.findtext(tag)

    if data is None:
      return None

    return conv_func(data)


  def get_attr(self, attr_name, conv_type=str):
    if conv_type == datetime.datetime or conv_type == 'time':
      conv_func = parser.isoparse
    else:
      conv_func = conv_type

    attr = self.elem.get(attr_name)

    if attr is None:
      return None

    return conv_func(attr)
