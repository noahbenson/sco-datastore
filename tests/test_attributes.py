import unittest

import scodata.attribute as attributes

class TestAttributes(unittest.TestCase):

    def setUp(self):
        """Create list of attribute data types."""
        self.data_types = [
            attributes.IntType(),
            attributes.FloatType(),
            attributes.DictType(),
            attributes.ListType(),
            attributes.EnumType(['A', 'B'])
        ]

    def test_json_conversion(self):
        """Test converting attribute definitions from and to Json."""
        # Create attribute defintion
        for datatype in self.data_types:
            attr_def = attributes.AttributeDefinition(
                'id',
                'name',
                'description',
                datatype
            )
            from_def = attributes.AttributeDefinition.from_json(
                attr_def.to_json()
            )
            self.assertEqual(attr_def.identifier, from_def.identifier)
            self.assertEqual(attr_def.name, from_def.name)
            self.assertEqual(attr_def.description, from_def.description)
            self.assertEqual(
                attr_def.data_type.identifier,
                from_def.data_type.identifier
            )

    def test_parse_value(self):
        """Check test_value methods for data types."""
        # Float
        t = attributes.FloatType()
        t.from_string('0.1')
        with self.assertRaises(ValueError):
            t.from_string('abc')
        # Int
        t = attributes.IntType()
        t.from_string('1')
        with self.assertRaises(ValueError):
            t.from_string('0.45')
        # Enum
        t = attributes.EnumType(['A', 'B'])
        t.from_string('A')
        with self.assertRaises(ValueError):
            t.from_string('0.45')
        # Dict
        t = attributes.DictType()
        t.from_string('{1:0.3, 2:0.6}')
        with self.assertRaises(ValueError):
            t.from_string('abc')
        # List
        t = attributes.ListType()
        t.from_string('[1, 2, 3]')
        with self.assertRaises(ValueError):
            t.from_string('abc')

    def test_type_check(self):
        """Check test_value methods for data types."""
        # Float
        t = attributes.FloatType()
        t.test_value(0.1)
        with self.assertRaises(ValueError):
            t.test_value('abc')
        # Int
        t = attributes.IntType()
        t.test_value(1)
        with self.assertRaises(ValueError):
            t.test_value(0.45)
        # Enum
        t = attributes.EnumType(['A', 'B'])
        t.test_value('A')
        with self.assertRaises(ValueError):
            t.test_value('0.45')
        # Dict
        t = attributes.DictType()
        t.test_value({'A': 1})
        with self.assertRaises(ValueError):
            t.test_value('abc')
        # List
        t = attributes.ListType()
        t.test_value([1, 2, 3])
        with self.assertRaises(ValueError):
            t.test_value('abc')


if __name__ == '__main__':
    unittest.main()
