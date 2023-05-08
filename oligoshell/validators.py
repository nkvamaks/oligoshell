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


def validate_seq(sequence):
    """
        Validates a sting of sequence on a right syntax. It is case-sensitive.
        String should be presented in a format:
        vinylPA dCm fT * rA spacer18 moeG rU +G * Cy3
        where the name of common nucleotides begin with small letters that represent sugar moiety
        followed by the capital letter representing nucleobase. After nucleobase it may be
        a combination of numbers and small letters indicating a modification of nucleotide.

        Available 2'-deoxynucleosides: dA, dC, dG, dT, dCm
        Available ribonucleosides: rA, rC, rG, rU
        Available 2'-fluoro-2'-deoxynucleosides: fA, fC, fG, fU
        Available 2'-methoxyribonucleosides: mA, mC, mG, mU
        Available locked nucleosides: +A, +Cm, +G, +T
        Available 2'-MOE nucleosides: moeA, moeCm, moeG, moeT

        Available phosphate modifications: 'space' or po - phosphate, * or ps - phosphorothyoate (po by default)
        """
    modification_error = []

    sequence_spl = utils.sequence_split(sequence)

    if sequence_spl[0] not in set(utils.modification_5_position + utils.nucleotide_any_position):
        modification_error.append("5'-Modification does not exist: " + sequence_spl[0])
    if len(sequence_spl) > 1:
        if sequence_spl[-1] not in set(utils.modification_3_position + utils.nucleotide_any_position):
            modification_error.append("3'-Modification does not exist: " + sequence_spl[-1])
        for i in range(len(sequence_spl)-1):
            if i == 0: continue
            if sequence_spl[i] not in set( utils.modification_int_position +
                                           utils.modification_phosphorus +
                                           utils.nucleotide_any_position ):
                modification_error.append("Internal modification does not exist: " + sequence_spl[i] + " at position " + str(i+1))
            if (sequence_spl[i] in utils.modification_phosphorus) and (sequence_spl[i+1] in utils.modification_phosphorus):
                modification_error.append("Two phosphate residues at positions " + str(i+1) + " and " + str(i+2) + " cannot be nearby")
    if modification_error:
        raise ValidationError(modification_error)
    else:
        return sequence