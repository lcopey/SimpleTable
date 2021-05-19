import six


def get_datatypes(dtype):
    if isinstance(dtype, float):
        return 'REAL'
    elif isinstance(dtype, six.integer_types):
        return 'INTEGER'
    elif isinstance(dtype, six.string_types):
        return 'TEXT'
    else:
        return 'NONE'
