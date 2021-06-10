"""Provides the tools to build classes corresponding to XML elements
in GPX and TCX files.
"""

import datetime

from lxml import etree

from . import util

def create_data_prop(path, conv_type=int):
  """Add property inside an ActivityElement class definition that accesses data
  using :meth:`~ActivityElement.get_data`.

  Args:
    path (str): The tag name or path of the desired subelement of the
      contained lxml element whose text will be retrieved. Text will be
      retrieved from the first matching subelement.
    conv_type (data type): Data type that the element text will
      be converted to. Python type, or datetime.datetime to read a time using
      :meth:`dateutil.parser.isoparse`. Defaults to ``int``.
  Returns:
    property: accessor for the underlying lxml element's data.

  Examples:

    >>> class MyElement(ActivityElement):
    ...   my_prop = create_data_prop('Time', datetime.datetime)
    ...   \"\"\"Property docstring goes here (if desired).\"\"\"
    ...   [...]

  """
  return property(
    lambda self: self.get_data(path, conv_type=conv_type), 
    # doc=f':obj:`{conv_type.__name__}`'
  )


def create_attr_prop(key, conv_type=int):
  """Add property inside an ActivityElement class definition that accesses data
  using :meth:`~ActivityElement.get_attr`.

  Args:
    key (str): The attribute name within the contained lxml element.
    conv_type (data type): Data type that the element text will
      be converted to. Python type, or datetime.datetime to read a time using
      :meth:`dateutil.parser.isoparse`. Defaults to ``int``.
  Returns:
    property: accessor for underlying lxml element's attribute data.

  Examples:

    >>> class MyElement(ActivityElement):
    ...   my_prop = create_attr_prop('Time', datetime.datetime)
    ...   \"\"\"Property docstring goes here (if desired)\"\"\"
    ...   [...]

  """
  return property(
    lambda self: self.get_attr(key, conv_type=conv_type),
    # doc=f':obj:`{conv_type.__name__}`'
  )


def create_descendent_prop(descendent_class):
  """Add descendent list accessor property inside an ActivityElement class
  definition.

  The property returns all the current element's descendents matching the
  tag name defined in the descendent class.

  Args:
    descendent_class (ActivityElement): Must be a subclass of :class:`ActivityElement`.
  Returns:
    property: accessor for underlying lxml element's descendent list.

  Examples:

    >>> class MyElement(ActivityElement):
    ...   my_prop = create_descendent_prop(MySubElement)
    ...   \"\"\"Property docstring goes here (if desired)\"\"\"
    ...   [...]

  """
  return property(
    lambda self: [
      descendent_class(e) 
      for e in self.elem.xpath(f'.//{descendent_class.TAG}')
    ],
    doc=f':obj:`list` of :class:`{descendent_class.__name__}`: '
    # f'All descendents of the contained lxml element with tag name '
    f'All element descendents with tag name "{descendent_class.TAG}".',
  )


class ActivityElement(object):
  """Base class for creating compositions with :class:`~lxml.etree._Element`.

  TCX and GPX files are both XML documents that follow their own particular
  schema. ActivityElement subclasses provide access to the underlying XML
  elements' data, attributes, descendent elements.
  
  Args:
    lxml_elem (:class:`~lxml.etree._Element`): XML element object that has
      been read in by the :mod:`lxml.etree` package. The tag name of the
      element must match the :attr:`TAG` attribute of this class, or else
      a TypeError will be raised.
  """

  TAG = 'element'
  """XML tag name of the element. 
  
  If an instance of the class is initialized from a 
  :class:`lxml.etree._Element` with any other tag name, a TypeError will
  be raised.
  """

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

  @classmethod
  def _add_data_properties(cls, **property_paths_types):
    """Add properties to cls that access specific paths using :meth:`get_data`.
    
    Args:
      cls: Class to add the properties to.
      **property_paths_types: kwargs mapping property_name : tuple(path, data_type)

        - property_name will be added to cls.
        - path is the tag name or path of the desired subelement of the 
          contained lxml element whose text will be retrieved
        - data_type is the type that the subelement's text will be converted
          to. A python type, or datetime.datetime to read a timestamp using 
          :meth:`dateutil.parser.isoparse`.

    Examples:

      >>> class MyElement(ActivityElement):
      ...   [...]
      >>> MyElement._add_data_properties(time=('Time', datetime.datetime))

    See also:
      `pandas.core.accessor.PandasDelegate._add_delegate_accessors <https://github.com/pandas-dev/pandas/blob/v1.2.4/pandas/core/accessor.py#L57-L108>`_

    """
    for prop_name, (path, data_type) in property_paths_types.items():
      f = create_data_prop(path, conv_type=data_type)
      setattr(cls, prop_name, f)

  @classmethod
  def _add_attr_properties(cls, **property_keys_types):
    """Add properties to cls that access specific keys using :meth:`get_attr`.
    
    Args:
      cls: Class to add the properties to.
      **property_keys_types: kwargs mapping property_name : tuple(key, data_type)

        - property_name will be added to cls.
        - key is the attribute name within the contained lxml element whose 
          text will be retrieved. 
        - data_type is the type that the subelement's text will be converted
          to. A python type, or datetime.datetime to read a timestamp using 
          :meth:`dateutil.parser.isoparse`.

    Examples:

      >>> class MyElement(ActivityElement):
      ...   [...]
      >>> MyElement._add_attr_properties(start_time=('StartTime', datetime.datetime))
    """
    for prop_name, (key, data_type) in property_keys_types.items():
      f = create_attr_prop(key, conv_type=data_type)
      setattr(cls, prop_name, f)

  @classmethod
  def _add_descendent_properties(cls, **descendent_classes):
    """Add properties to cls that return all descendents matching a path.
    
    Args:
      cls: Class to add the properties to.

      **descendent_classes: kwargs mapping property_name : descendent class.
    
        - property_name will be added to cls.
        - All values must be a subclass of :class:`ActivityElement`.

    Examples:

      >>> class MyElement(ActivityElement):
      ...   [...]
      >>> MyElement._add_descendent_properties(subelements=MySubElement)
    """
    for prop_name, descendent_class in descendent_classes.items():
      f = create_descendent_prop(descendent_class)
      setattr(cls, prop_name, f)
      # cls.add_descendent_list_property(prop_name, descendent_class)    

  def get_data(self, path, conv_type=str):
    """Retrieve data using the contained lxml element's 
    :meth:`~lxml.etree._Element.findtext` and convert its type.
    
    TODO: 
      * Consider if this wants to be a delegated ``findtext`` method, which
        could be accomplished by moving the type conversion out of this method.

    Args:
      path (str): The tag name or path of the desired subelement of the
        contained lxml element whose text will be retrieved. Text will be
        retrieved from the first matching subelement.
      conv_type (data type): Data type that the element text will
        be converted to. Python type, or datetime.datetime to read a time using
        :meth:`dateutil.parser.isoparse`. Defaults to ``str``.

    Returns:
      The retrieved data in the requested type, or None if no subelements
      match ``path``.

    Examples:
      Text can be converted to another Python type:

      >>> e_lat = ActivityElement(etree.fromstring(
      ...   '<element><Position><LatitudeDegrees>40.0</LatitudeDegrees></Position></element>'
      ... ))
      >>> e_lat.get_data('Position/LatitudeDegrees', conv_type='float')
      40.0
      
      Or a timestamp can be read in:

      >>> e_time = ActivityElement(etree.fromstring(
      ...   '<element><Time>2021-02-26T19:51:08.000Z</Time></element>'
      ... ))
      >>> e_time.get_data('Time', conv_type=datetime.datetime)
      datetime.datetime(2021, 2, 26, 19, 51, 8, tzinfo=tzutc())

    """
    data = self.elem.findtext(path)

    if data is None:
      return None

    conv_func = util.get_conv_func(conv_type)

    return conv_func(data)

  def get_attr(self, key, conv_type=str):
    """Retrieve data using contained lxml element's 
    :meth:`~lxml.etree._Element.get` and convert its type.

    Args:
      key (str): The attribute name within the contained lxml element.
      conv_type (data type): Data type that the attribute text will
        be converted to. Python type, or datetime.datetime to read a time using
        :meth:`dateutil.parser.isoparse`. Defaults to ``str``.

    Returns:
      The retrieved attribute data in the requested type, or None if 
      the contained lxml element does not have an attribute named ``key``.

    Examples:

      >>> e = ActivityElement(etree.fromstring(
      ...   '<element StartTime="2021-02-26T19:51:07.000Z"></element>
      ... ))
      >>> e.get_attr('StartTime', conv_type=datetime.datetime)
      datetime.datetime(2021, 2, 26, 19, 51, 7, tzinfo=tzutc())

    """
    attr = self.elem.get(key)

    if attr is None:
      return None

    conv_func = util.get_conv_func(conv_type)

    return conv_func(attr)


def add_xml_data(**property_paths_types):
  """Add properties to a class that access data using :meth:`get_data`.

  This provides an alternative usage to directly calling 
  :meth:`ActivityElement._add_data_properties` below a class definition.

  Args:
    **property_paths_types: kwargs mapping property_name : tuple(path, data_type)

    - property_name will be added to the decorated class.
    - path is the tag name or path of the desired subelement of the 
      contained lxml element whose text will be retrieved
    - data_type is the type that the subelement's text will be converted
      to. A python type, or datetime.datetime to read a timestamp using 
      :meth:`dateutil.parser.isoparse`.
  Returns:
    callable: A class decorator.
  
  Examples:
  
    >>> @add_xml_data(time=('Time', datetime.datetime))
    ... class MyElement(ActivityElement):
    ...   [...]

  See also:
    :meth:`ActivityElement._add_data_properties`
  """

  def add_data_properties(cls):
    cls._add_data_properties(**property_paths_types)
    return cls

  return add_data_properties


def add_xml_attr(**property_keys_types):
  """Add properties to a class that access data using :meth:`get_attr`.

  This provides an alternative usage to directly calling 
  :meth:`ActivityElement._add_attr_properties` below a class definition.

  Args:
    **property_keys_types: kwargs mapping property_name : tuple(key, data_type)

      - property_name will be added to the decorated class.
      - key is the attribute name within the contained lxml element whose 
        text will be retrieved. 
      - data_type is the type that the subelement's text will be converted
        to. A python type, or datetime.datetime to read a timestamp using 
        :meth:`dateutil.parser.isoparse`.
  Returns:
    callable: A class decorator.
  
  Examples:

    >>> @add_xml_attr(start_time=('StartTime', datetime.datetime))
    ... class MyElement(ActivityElement):
    ...   [...]

  See also:
    :meth:`ActivityElement._add_attr_properties`
  """
  def add_attr_properties(cls):
    cls._add_attr_properties(**property_keys_types)
    return cls

  return add_attr_properties


def add_xml_descendents(**descendent_classes):
  """Add properties to a class that return all descendents matching a path.

  This provides an alternative usage to directly calling 
  :meth:`ActivityElement._add_descendent_properties` below a class definition.

  Args:
    **descendent_classes: kwargs mapping property_name : descendent class.
    
      - Each key will be a property name added to the decorated class.
      - All values must be a subclass of :class:`ActivityElement`.
  Returns:
    callable: A class decorator 

  Examples:

    >>> @add_xml_descendents(subelements=MySubElement)
    ... class MyElement(ActivityElement):
    ...   [...]

  See also:
    :meth:`ActivityElement._add_descendent_properties`
  """
  def add_descendent_properties(cls):
    cls._add_descendent_properties(**descendent_classes)
    return cls

  return add_descendent_properties
