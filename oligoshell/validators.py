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


# def validate_sequence_regex(sequence):
#         # sequence_pattern = r'^(((\[[-\._a-zA-Z0-9]+\])*?[aAcCgGtTwWsSmMkKrRyYbBdDhHvVnN]*?)*?)$'
#     # message = ('Sequence should contain A/C/G/T, degenerated bases W/S/M/K/R/Y/B/D/H/V/N,'
#     #            ' and modifications e.g. [FAM], [BHQ1] etc.')
#     sequence_pattern = r''
#     message = ('Sequence should contain A/C/G/T, degenerated bases W/S/M/K/R/Y/B/D/H/V/N,'
#                 ' and modifications e.g. [FAM], [BHQ1] etc.')
#     if not re.match(sequence_pattern, sequence):
#         raise ValidationError(message)
#     else:
#         return sequence


# def validate_modifications(sequence):
#     modification_list = re.findall(utils.modification_pattern, sequence)
#     modification_list_upper = [item.upper() for item in modification_list]
#     message = 'Unovailable modifications: {}'
#     if modification_list:
#         modification_not_exist = [modification for modification in modification_list_upper
#                                   if modification not in utils.modification_extinction_260]
#         if modification_not_exist:
#             raise ValidationError(message.format(', '.join(modification_not_exist)))
#     else:
#         return sequence


def validate_syntax(sequence):
    """
        Validates a sting on a right syntax. Case-sensitive.
        String should be presented in a format:
        [VinylP-A] dC fT ps rA [Spacer-18] moeG rU lG ps [Cy3]

        Available deoxynucleosides: dA, dC, dG, dT, dC_5me
        Available ribonucleosides: rA, rC, rG, rU
        Available 2'-fluoro-2'-deoxynucleosides: fA, fC, fG, fU
        Available 2'-methoxyribonucleosides: mA, mC, mG, mU
        Available locked nucleosides: lA, lC, lG, lT (lC is lC_5me by default)
        Available 2'-MOE nucleosides: moeA, moeC, moeG, moeT (moeC is moeC_5me by default)

        Available phosphate modifications: po - phosphate, ps - phosphothyoate (po by default)
        """

    sequence_spl = utils.sequence_split(sequence)
    modification_not_exist = {index: nt for index, nt in enumerate(sequence_spl) if nt not in utils.modification_extinction_260}

    if modification_not_exist:
        message = 'Unovailable modifications: ' + ', '.join(['{1} at position {0}'.format(index, nt) for (index, nt) in modification_not_exist.items()])
        raise ValidationError(message)
    else:
        return sequence