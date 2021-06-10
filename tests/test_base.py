import datetime
import io
import unittest

from lxml import etree

from activereader import base

def get_attrs(clazz):
  return [attr_name for attr_name in dir(clazz) if not attr_name.startswith("_")]


class MySubSubElement(base.ActivityElement):
  TAG = 'sub_sub_element'

class MySubElement(base.ActivityElement):
  TAG = 'sub_element'
MySubElement._add_descendent_properties(**{
  'sub_sub_elements': MySubSubElement
})

class MyElement(base.ActivityElement):
  TAG = 'element'

MyElement._add_data_properties(
  # ${property_name}=( ${tag_text}, ${expected_type} )
  my_data=('MyDataTag', float)
)

MyElement._add_attr_properties(
  # ${property_name}=( ${attr_name}, ${expected_type} )
  my_attr=('MyAttrName', float) 
)

MyElement._add_descendent_properties(
  # ${property_name}=${descendent_class}
  sub_elements=MySubElement,
  sub_sub_elements=MySubSubElement
)


class TestActivityElement(unittest.TestCase):

  def test_add_properties(self):
    clazz = MyElement

    self.assertNotIn('my_data_prop', get_attrs(clazz))
    clazz._add_data_properties(
      my_data_prop=('tag_name', int),
    )
    self.assertIn('my_data_prop', get_attrs(clazz))

    self.assertNotIn('my_attr_prop', get_attrs(clazz))
    clazz._add_attr_properties(
      my_attr_prop=('attr_name', int),
    )
    self.assertIn('my_attr_prop', get_attrs(clazz))

    self.assertNotIn('my_desc_prop', get_attrs(clazz))
    clazz._add_descendent_properties(
      my_desc_prop=MySubElement,
    )
    self.assertIn('my_desc_prop', get_attrs(clazz))

    # Patterned off pandas custom accessor (refer to them)
    # with self.assertRaisesRegex(AttributeError, 'my_attr_prop'):
    #   clazz.add_data_property('my_attr_prop', 'attr_name_other', int)

    # do some "ensure_removed" riffraff here

  def test_get(self):
    for value, type in [
      ('45.0', float),
      ('2021-02-26T19:51:08.000Z', datetime.datetime),
      ('Running', str)
    ]:
      el_tag = MyElement(etree.fromstring(
        f'<element><Tag>{value}</Tag></element>'
      ))
      self.assertIsInstance(el_tag.get_data('Tag', type), type)

      el_path = MyElement(etree.fromstring(
        f'<element><Tag><Nested>{value}</Nested></Tag></element>'
      ))
      self.assertIsInstance(el_path.get_data('Tag/Nested', type), type)

      el_path = MyElement(etree.fromstring(
        f'<element KeyName="{value}"></element>'
      ))
      self.assertIsInstance(el_path.get_attr('KeyName', type), type)

  def test_props(self):

    my_element = MyElement(etree.fromstring(
      '<element MyAttrName="40.0">'
        '<MyDataTag>'
          '45.0'
        '</MyDataTag>'
        '<sub_element>'
          '<sub_sub_element>'
            'text'
          '</sub_sub_element>'
          '<sub_sub_element></sub_sub_element>'
          '<sub_sub_element></sub_sub_element>'
          '<sub_sub_element></sub_sub_element>'
        '</sub_element>'
        '<sub_element>'
          '<sub_sub_element></sub_sub_element>'
          '<sub_sub_element></sub_sub_element>'
        '</sub_element>'
      '</element>'
    ))

    attrs = get_attrs(my_element)
    self.assertIn('my_attr', attrs)
    self.assertEqual(my_element.my_attr, 40.0)
    self.assertIn('my_data', attrs)
    self.assertEqual(my_element.my_data, 45.0)
    self.assertIn('sub_elements', attrs)
    self.assertIsInstance(my_element.sub_elements, list)
    # print(my_element)
    # print(my_element.sub_elements)
    self.assertIn('sub_sub_elements', attrs)
    self.assertIsInstance(my_element.sub_sub_elements, list)
    self.assertEqual(my_element.sub_sub_elements[0].elem.text, 'text')
    self.assertEqual(len(my_element.sub_sub_elements), 6)
    self.assertEqual(len(my_element.sub_elements), 2)
    self.assertEqual(len(my_element.sub_elements[0].sub_sub_elements), 4)
    self.assertEqual(len(my_element.sub_elements[1].sub_sub_elements), 2)

  def test_raises(self):

    with self.assertRaisesRegex(TypeError, 'Expected lxml element, not *.'):
      my_element = MyElement(etree.parse(io.StringIO(
        '<sub_element></sub_element>'
      )))

    with self.assertRaisesRegex(
      ValueError, 
      'Expected lxml element with "element" tag, not "sub_element".'
    ):
      my_element = MyElement(etree.fromstring(
        '<sub_element></sub_element>'
      ))


if __name__ == '__main__':
  unittest.main()