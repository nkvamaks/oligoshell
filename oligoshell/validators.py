from django.core.exceptions import ValidationError
from . import utils
import re


def validate_seq_name_regex(seq_name):
    seq_name_pattern = r'^[-a-zA-Z0-9_()]+$'
    message = "Name should contain letters, numbers and special characters:  _-()"
    if not re.match(seq_name_pattern, seq_name):
        raise ValidationError(message)
    else:
        return seq_name


def validate_sequence_regex(sequence):
    sequence_pattern = r'^(((\[[-\._a-zA-Z0-9]+\])*?[aAcCgGtTwWsSmMkKrRyYbBdDhHvVnN]*?)*?)$'
    message = ('Sequence should contain A/C/G/T, degenerated bases W/S/M/K/R/Y/B/D/H/V/N,'
               ' and modifications e.g. [FAM], [BHQ1] etc.')
    if not re.match(sequence_pattern, sequence):
        raise ValidationError(message)
    else:
        return sequence


def validate_modifications(sequence):
    modification_list = re.findall(utils.modification_pattern, sequence)
    modification_list_upper = [item.upper() for item in modification_list]
    message = 'Unovailable modifications: {}'
    if modification_list:
        modification_not_exist = [modification for modification in modification_list_upper
                                  if modification not in utils.modification_extinction_260]
        if modification_not_exist:
            raise ValidationError(message.format(', '.join(modification_not_exist)))
    else:
        return sequence


# def validate_seq_name_unique_within_order(seq_name):
#     message = 'Something went wrong'
#     raise ValidationError(message)