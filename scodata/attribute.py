"""Attributes - Collection of classes and helper methods to handle key,value
pairs.

At this point attribute values can be of arbitrary type. Attributes are used
as parameters for SCO model runs. Attributes are associated either with an image
group or a model run.

When running a model instance the type of attribute values is validated agains
an expected data type. Because names and types of attributes may change (or vary
between model instances) the data store is agnostic to these type definitions.
"""

from abc import abstractmethod


# ------------------------------------------------------------------------------
#
# Global Variables
#
# ------------------------------------------------------------------------------

ATTR_TYPE_DICT = 'dict'
ATTR_TYPE_ENUM = 'enum'
ATTR_TYPE_FLOAT = 'float'
ATTR_TYPE_INT = 'int'
ATTR_TYPE_LIST = 'array'


# ------------------------------------------------------------------------------
#
# Attribute definitions and instances
#
# ------------------------------------------------------------------------------

class Attribute(object):
    """Attributes are simple key, value pairs.

    Attributes
    ----------
    name : string
        Attribute name
    value : any
        Attribute value. Can be of any type
    """
    def __init__(self, name, value):
        """Initialize the attribute name and value.

        Parameters
        ----------
        name : string
            Attribute name
        value : any
            Associated value for the property. Can be of any type
        """
        self.name = name
        self.value = value


class AttributeDefinition(object):
    """Definition of a types attribute. Each attribute has an identifier, name,
    description, and a type definition. The type definition determines the
    values that are valid for the attribute.

    Five different attribute types are currently supported: int, float, dict,
    list, and enumeration. The keys for dictionaries are expected to be integers
    and the values floeas. Lists contain tuples of floats. Enumerations are
    enumerations of strings.

    Attributes
    ----------
    identifier : string
        Unique attribute identifier
    name : string
        Short attribute name
    description : string
        Detai;ed attribute descritption
    data_type : AttributeType
        Type defining valid attribute values
    default: any, optional
        Optional default value for attributes of this type
    """
    def __init__(self, identifier, name, description, data_type, default=None):
        self.identifier = identifier
        self.name = name
        self.description = description
        self.data_type = data_type
        self.default = default

    @staticmethod
    def from_json(document):
        """Create attribute definition form Json-like object represenation.

        Parameters
        ----------
        document : dict
            Json-like object represenation

        Returns
        -------
        AttributeDefinition
        """
        if 'default' in document:
            default = document['default']
        else:
            default = None
        return AttributeDefinition(
            document['id'],
            document['name'],
            document['description'],
            AttributeType.from_json(document['type']),
            default=default
        )

    def to_json(self):
        """Convert attribute definition into a dictionary.

        Returns
        -------
        dict
            Json-like dictionary representation of the attribute definition
        """
        obj = {
            'id' : self.identifier,
            'name' : self.name,
            'description' : self.description,
            'type' : self.data_type.to_json()
        }
        if not self.default is None:
            obj['default'] = self.default
        return obj


class AttributeType(object):
    """Abstract attribute data type. Defines abstract methods to parse and
    validate attribute values. Each type has a unique identifier.

    Attributes
    ----------
    identifier : string
        Unique data type identifier
    """
    def __init__(self, identifier):
        """Initialize the type identifier.

        Parameters
        ----------
        identifier : string
            Unique data type identifier
        """
        self.identifier = identifier

    @staticmethod
    def from_json(document):
        """Create data type definition form Json-like object represenation.

        Parameters
        ----------
        document : dict
            Json-like object represenation

        Returns
        -------
        AttributeType
        """
        # Get the type name from the document
        type_name = document['name']
        if type_name == ATTR_TYPE_INT:
            return IntType()
        elif type_name == ATTR_TYPE_FLOAT:
            return FloatType()
        elif type_name == ATTR_TYPE_ENUM:
            return EnumType(document['values'])
        elif type_name == ATTR_TYPE_DICT:
            return DictType()
        elif type_name == ATTR_TYPE_LIST:
            return ListType()
        else:
            raise ValueError('invalid attribute type: ' + str(type_name))


    @abstractmethod
    def from_string(self, value):
        """Method to convert given string into a value of this data type.

        Will throw a ValueError if the given value is not a valid representation
        of a value of this type.

        Parameters
        ----------
        value : string
            String representation of a value of this data type

        Returns
        -------
        any
        """
        pass

    @abstractmethod
    def test_value(self, value):
        """Test if a given value is of type that matches the given data type.
        Raises ValueError if value is not of valid type.

        Parameters
        ----------
        value : any
        """
        pass

    def to_json(self):
        """Convert attribute data type definition into a dictionary.

        Returns
        -------
        dict
            Json-like dictionary representation of the attribute data type
        """
        return {'name' : self.identifier}


class DictType(AttributeType):
    """Dictionary attribute data type."""
    def __init__(self):
        """Initialize the type identifier in the super class."""
        super(DictType, self).__init__(ATTR_TYPE_DICT)

    def from_string(self, value):
        """Convert string to dictionary."""
        # Remove optional {}
        if value.startswith('{') and value.endswith('}'):
            text = value[1:-1].strip()
        else:
            text = value.strip()
        # Result is a dictionary
        result = {}
        # Convert each pair of <int>:<float> into a key, value pair.
        for val in text.split(','):
            tokens = val.split(':')
            if len(tokens) != 2:
                raise ValueError('invalid entry in dictionary: ' + val)
            result[str(int(tokens[0].strip()))] = float(tokens[1].strip())
        return result

    def test_value(self, value):
        """Test if value is an instance of dict."""
        if not isinstance(value, dict):
            raise ValueError('expected dict value: ' + str(type(value)))


class EnumType(AttributeType):
    """Enumeration attribute data type."""
    def __init__(self, values):
        """Initialize the type identifier in the super class and list of values
        in the enumeration.

        Parameters
        ----------
        values : list(string)
            List of values in the enumeration
        """
        super(EnumType, self).__init__(ATTR_TYPE_ENUM)
        self.values = values

    def from_string(self, value):
        """Convert string to enum value."""
        if not isinstance(value, basestring):
            raise ValueError('expected string value: ' + str(type(value)))
        self.test_value(value)
        return value

    def test_value(self, value):
        """Test if value is an instance of enum."""
        # Make sure that the value appears in the value list
        if not value in self.values:
            raise ValueError('unknown enumeration value: ' + str(value))

    def to_json(self):
        """Convert enum data type definition into a dictionary. Overrides the
        super class method to add list of enumeration values.

        Returns
        -------
        dict
            Json-like dictionary representation of the attribute data type
        """
        obj = super(EnumType, self).to_json()
        obj['values'] = self.values
        return obj


class FloatType(AttributeType):
    """Float attribute data type."""
    def __init__(self):
        """Initialize the type identifier in the super class."""
        super(FloatType, self).__init__(ATTR_TYPE_FLOAT)

    def from_string(self, value):
        """Convert string to float."""
        return float(value)

    def test_value(self, value):
        """Test if value is an instance of float."""
        if not isinstance(value, float):
            raise ValueError('expected float value: ' + str(type(value)))


class IntType(AttributeType):
    """Integer attribute data type."""
    def __init__(self):
        """Initialize the type identifier in the super class."""
        super(IntType, self).__init__(ATTR_TYPE_INT)

    def from_string(self, value):
        """Convert string to int."""
        return int(value)

    def test_value(self, value):
        """Test if value is an instance of int."""
        if not isinstance(value, int):
            raise ValueError('expected int value: ' + str(type(value)))


class ListType(AttributeType):
    """Integer attribute data type."""
    def __init__(self):
        """Initialize the type identifier in the super class."""
        super(ListType, self).__init__(ATTR_TYPE_INT)

    def from_string(self, value):
        """Convert string to list."""
        # Remove optional []
        if value.startswith('[') and value.endswith(']'):
            text = value[1:-1].strip()
        else:
            text = value.strip()
        # Result is a list
        result = []
        # If value starts with '(' assume a list of pairs
        if text.startswith('('):
            tokens = text.split(',')
            if len(tokens) % 2 != 0:
                raise ValueError('not a valid list of pairs')
            pos = 0
            while (pos < len(tokens)):
                val1 = float(tokens[pos].strip()[1:].strip())
                val2 = float(tokens[pos + 1].strip()[:-1])
                result.append((val1, val2))
                pos += 2
        else:
            for val in text.split(','):
                result.append(float(val))
        # Ensure that the result contains at least two elements
        if len(result) < 2:
            raise ValueError('invalid number of elements in list: ' + str(len(result)))
        return result

    def test_value(self, value):
        """Test if value is an instance of list."""
        if not isinstance(value, list):
            raise ValueError('expected list value: ' + str(type(value)))


# ------------------------------------------------------------------------------
#
# Helper methods
#
# ------------------------------------------------------------------------------

def attributes_from_json(document):
    """Convert a Json representation of a set of attribute instances into a
    dictionary.

    Parameters
    ----------
    document : Json object
        Json serialization of attribute instances

    Returns
    -------
    dict(Attribute)
        Dictionary of attribute instance objects keyed by their name
    """
    attributes = dict()
    for attr in document:
        name = str(attr['name'])
        attributes[name] = Attribute(
            name,
            attr['value']
        )
    return attributes


def attributes_to_json(attributes):
    """Transform a dictionary of attribute instances into a list of Json
    objects, i.e., list of key-value pairs.

    Parameters
    ----------
    attributes : dict(Attribute)
        Dictionary of attribute instances

    Returns
    -------
    list(dict(name:..., value:...))
        List of key-value pairs.
    """
    result = []
    for key in attributes:
        result.append({
            'name' : key,
            'value' : attributes[key].value
        })
    return result


def to_dict(attributes, definitions):
    """Create a dictionary of attributes from a given list of key-value pairs.
    Detects duplicate definitions of the same attribute and raises an exception.

    Expects a list of dictionaries (e.g., Json object) objects having 'name'
    and 'value' keys. The type of the element associated with the 'value' key is
    arbitrary. Raises a ValueError exception if the given array violates the
    expected format.

    The list of attribute definitions defines the set valid attribute names .
    Raises an ValueError exception if an attribute with an invalid name is
    in the attributes array.

    If the list of attributes is None an empty dictionary will be returned.

    Parameters
    ----------
    attributes : list()
        Expects a list of Attributes of dictionaries with 'name' and 'value'
        elements.
    definitions: list(dict('id': ..., ...))
        List of attribute definitons.

    Returns
    -------
    Dictionary
        Dictionary of attribute instances keyed by their name
    """
    # Create a list of valis parameter names
    valid_names = {}
    for para in definitions:
        valid_names[para.identifier] = para
    result = {}
    if not attributes is None:
        for element in attributes:
            if isinstance(element, dict):
                # Create attribute from dictionary
                for key in ['name', 'value']:
                    if not key in element:
                        raise ValueError('object has no key ' + key + ': ' + str(element))
                name = str(element['name'])
                if not name in valid_names:
                    raise ValueError('invalid parameter name: ' + name)
                try:
                    value = valid_names[name].data_type.from_string(
                        element['value']
                    )
                except ValueError as ex:
                    raise ValueError(str(ex))
                attr = Attribute(name, value)
            else:
                # Element is expected to be an attribute object
                attr = element
                # Make sure that the attribute value is of valid type. Make
                # sure that attr.name is valid.
                if attr.name in valid_names:
                    valid_names[attr.name].data_type.test_value(attr.value)
                else:
                    raise ValueError('invalid parameter name: ' + attr.name)
            if attr.name in result:
                raise ValueError('duplicate attribute: ' + attr.name)
            result[attr.name] = attr
    return result
