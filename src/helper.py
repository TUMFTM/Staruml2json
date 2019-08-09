######################################################################
#
# This file holds helper functions for the mdj_to_json class
#
######################################################################
__author__ = "Lukas Merkle"
__copyright__ = "Copyright 2019, Institute of Automotive Technology"
__license__ = "LGPL V3"
__version__ = "1.0"
__maintainer__ = "Lukas Merkle"
__email__ = "lukas.merkle@tum.de"
######################################################################
from copy import deepcopy



def recursive_find_value_in_dict(in_dict, search_value, set_value):


    if isinstance(in_dict, dict):

        for key, value in in_dict.items():

            if value == search_value:
                # print(set_value)
                in_dict['value'] = set_value
                print(set_value)
                return
            else:
                recursive_find_value_in_dict(value, search_value, set_value)
    return in_dict



class Recursive_Dict_Finder:

    def __init__(self):

        self.flag_replaced = False

    def recursive_find_dict_with_id_replace(self, in_dict, search_id, set_dict):

        if isinstance(in_dict, dict):

            for key, value in in_dict.items():
                if value == search_id and key == 'id':
                    in_dict = set_dict
                    self.flag_replaced = True
                    return
                else:
                    self.recursive_find_dict_with_id_replace(value, search_id, set_dict)

        return in_dict



def isevaluable(s):
    try:
        eval_s = eval(s)
        return True
    except:
        return False