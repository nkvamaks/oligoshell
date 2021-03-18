import re


degeneration_pattern = r'[wWsSmMkKrRyYbBdDhHvVnN]'
modification_pattern = r'\[[-\._a-zA-Z0-9]+\]'


# Extinction coefficients of single nucleotides:
# https://www.sigmaaldrich.com/technical-documents/articles/biology/quantitation-of-oligos.html
# https://en.wikipedia.org/wiki/Nucleic_acid_notation for degenerate base symbols.
nucleotide_extinction = {'A': 15400, 'C': 7400,  'G': 11500, 'T': 8700,
                         'W': 12050, 'S': 9450,  'M': 11400, 'K': 10050, 'R': 13450, 'Y': 8050,
                         'B': 9200,  'D': 11867, 'H': 10500, 'V': 11433,
                         'N': 10750,
                         }


# Extinction coefficients of dinucleotides:
# https://www.sigmaaldrich.com/technical-documents/articles/biology/quantitation-of-oligos.html
dinucleotide_extinction = {'AA': 27400, 'AC': 21200, 'AG': 25000, 'AT': 22800,
                           'CA': 21200, 'CC': 14600, 'CG': 18000, 'CT': 15200,
                           'GA': 25200, 'GC': 17600, 'GG': 21600, 'GT': 20000,
                           'TA': 23400, 'TC': 16200, 'TG': 19000, 'TT': 16800,
                           }


# Extinction coefficients of popular modifications:
modification_extinction_260 = {
    '[FAM]': 21000, '[5FAM]': 21000, '[6FAM]': 21000,
    '[TET]': 16300, '[5TET]': 16300, '[6TET]': 16300,
    '[HEX]': 31600, '[5HEX]': 31600, '[6HEX]': 31600,
    '[JOE]': 12000, '[5JOE]': 12000, '[6JOE]': 12000,
    '[TAMRA]': 32300, '[5TAMRA]': 32300, '[6TAMRA]': 32300,
    '[R6G]': 18000, '[5R6G]': 18000, '[6R6G]': 18000,
    '[CY3]': 4930, '[CY3.5]': 24000, '[CY5]': 10000, '[CY5.5]': 28800,
    '[ROX]': 22600, '[5ROX]': 22600, '[6ROX]': 22600,
    '[BHQ1]': 8000, '[BHQ2]': 8000,
    '[YAKIMAYELLOW]': 23700, '[TEXASRED]': 14400, '[IOWABLACKRQ]': 44510,
    '[+A]': 15400, '[+C]': 7400, '[+G]': 11500, '[+T]': 8700,
    '[LNA-A]': 15400, '[LNA-C]': 7400, '[LNA-G]': 11500, '[LNA-T]': 8700,
}


def sequence2lists(sequence):
    """The function takes raw sequence as a string and converts it into three lists:
    e.g. NN[6FAM]AACTNRG[BHQ1dT]TTACGTC[DABCYL]TT is converted to
    unmodified_list: ['TTACGTC', 'TT']
    unmodified_degenerated_list: ['AT', 'NN', 'AACTNRG']
    modification_list: ['[6FAM]', '[BHQ1dT]', '[DABCYL]']
    """
    modification_list = [item.upper() for item in re.findall(modification_pattern, sequence)]
    without_modifications_list = re.split(modification_pattern, sequence)
    unmodified_degenerated_list = [item for item in without_modifications_list
                                   if item and len(item) < 2 or re.search(degeneration_pattern, item)]
    unmodified_list = [item for item in without_modifications_list
                       if len(item) >= 2 and not re.search(degeneration_pattern, item)]

    return unmodified_list, unmodified_degenerated_list, modification_list


def extinction_dna_nn(sequence):
    """Takes sequence as a string and calculates extinction coefficient of non-modified
    single-stranded oligodeoxynucleotide using nearest neighbour method"""

    extinction = 0

    # extinction coefficients are determined for pairs by reading from the 5' to 3' position.
    # extinction of overlapping nucleotides then subtracted
    for dinucleotide in range(len(sequence) - 1):
        extinction += dinucleotide_extinction[sequence.upper()[dinucleotide:dinucleotide + 2]]
    for nucleotide in range(1, len(sequence) - 1):
        extinction -= nucleotide_extinction[sequence.upper()[nucleotide]]
    return extinction


def extinction_dna_simple(sequence):
    """Takes sequence as a string and calculates extinction coefficient of non-modified
    single-stranded oligodeoxynucleotides containing degenerate bases"""

    extinction = 0

    for nucleotide in sequence.upper():
        extinction += nucleotide_extinction[nucleotide]

    return extinction
