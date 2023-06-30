#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#


@staticmethod
def merge_dict(source_dict, overrides_dict):
    """Recursively merge two nested dictionaries. The 'overrides_dict'
    is merged into 'source_dict'

    """

    for k, v in overrides_dict.items():
        if isinstance(v, dict):
            source_dict[k] = merge_dict(source_dict.get(k, {}), v)
        else:
            source_dict[k] = v

    return source_dict


@staticmethod
def get_value_from_nested_dict(nested_dict, composite_key, default_value=None,
                               key_separator='.'):
    """Searches a composite key in the multidimensional dictionary

    :param nested_dict: multidimensional dict
    :param composite_key: key to search
    :param default_value: default value to return
    :param key_separator: character used to split the key
    :return key value or the default value if not found
    """

    for key in composite_key.split(key_separator):
        nested_dict = nested_dict.get(key, {})

    return nested_dict or default_value
