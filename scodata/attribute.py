"""Attributes - Collection of classes and helper methods to handle key,value
pairs.

At this point attribute values can be of arbitrary type. Attributes are used
as parameters for SCO model runs. Attributes are associated either with an image
group or a model run.

When running a model instance the type of attribute values is validated agains
an expected data type. Because names and types of attributes may change (or vary
between model instances) the data store is agnostic to these type definitions.
"""

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

def parse_value(value, para_def):
    """Parse an attribute value (expected as string) into a value for a
    parameter of type as specified in the given definition.

    Raises a ValueError if value is not of expected type.

    Parameters
    ----------
    value : string
        String representation pf parameter value
    para_def : Dictionary
        Parameter definition

    Returns
    -------
    any
        Value of the specified type
    """
    # Get the type name from the definition
    type_name = para_def['type']['name']
    if type_name == 'int':
        return int(value)
    elif type_name == 'float':
        return float(value)
    elif type_name == 'enum':
        return value
    elif type_name == 'dict':
        return parse_dict(value)
    elif type_name == 'array':
        return parse_array(value)


def parse_array(value):
    """Parse a string value that is expected to be either a list of floats or
    a list of float pairs.

    Raises ValueError is value is not of expected format.

    Parameters
    ----------
    value : string
        String representation of the array

    Returns
    List
        List of floats of of float tuples.
    """
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


def parse_dict(value):
    """Parse a string value that is expected to be a list of integer:float
    pairs.

    Raises ValueError is value is not of expected format.

    Parameters
    ----------
    value : string
        String representation of the dictionary

    Returns
    List
        Dictionary of integer,float pairs.
    """
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


def to_dict(attributes):
    """Create a dictionary of attributes from a given list of attribute objects.
    Detects duplicate definitions of the same attribute and raises an exception.
    If the list of attributes is None an empty dictionary will be returned.

    Parameters
    ----------
    attributes : List(attribute.Attribute)
        List of image group options. If None, result will be empty.

    Returns
    -------
    Dictionary
        Dictionary of attribute instances keyed by their name
    """
    result = {}
    if not attributes is None:
        for attr in attributes:
            if attr.name in result:
                raise ValueError('duplicate attribute: ' + attr.name)
            result[attr.name] = attr
    return result
