from django.utils.translation import ugettext as _

days_data = {
    1: {'name': _(u'Monday'), 'index': 0},
    2: {'name': _(u'Tuesday'), 'index': 1},
    4: {'name': _(u'Wednesday'), 'index': 2},
    8: {'name': _(u'Thursday'), 'index': 3},
    16: {'name': _(u'Friday'), 'index': 4},
    32: {'name': _(u'Saturday'), 'index': 5},
    64: {'name': _(u'Sunday'), 'index': 6},
}

days_bit = {'monday': 1, 'tuesday': 2, 'wednesday': 4, 'thursday': 8, 'friday': 16, 'saturday': 32, 'sunday': 64}


def get_active_days(days_16, value_type='index', days_dict=days_data):
    """Get list of days' indices [0..6] or days' names [Monday..Sunday]"""
    if value_type not in days_dict[1]:
        raise KeyError('type parameter is not a key of days_dict parameter')
    days_keys = list(days_dict.keys())
    days_keys.sort()  # Make sure they're always in correct order
    return [days_dict[bit_key][value_type] for bit_key in days_keys if bit_key & days_16]


def get_first_letters_of_active_days(days_16, days_dict=days_data):
    """Get first letters of enabled days.\ne.g.: if only Friday is enabled, the result would be '_,_,_,_,F,_,_'"""
    days_keys = list(days_dict.keys())
    days_keys.sort()  # Make sure they're always in correct order
    # return [days[bit_key][type] for bit_key in days_keys if bit_key & days_16]
    letters = []
    for bit_key in days_keys:
        letters.append(days_dict[bit_key]['name'][0].upper() if bit_key & days_16 else '_')
    return ','.join(letters)
