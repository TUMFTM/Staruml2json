######################################################################
#
# Class holding the conversion logic from .mdj / .xmi from json
# 
######################################################################
__author__ = "Lukas Merkle"
__copyright__ = "Copyright 2019, Institute of Automotive Technology"
__license__ = "LGPL V3"
__version__ = "1.0"
__maintainer__ = "Lukas Merkle"
__email__ = "lukas.merkle@tum.de"
######################################################################

import json
from UMLClasses import *
import networkx as nx
import time
import xmltodict
import helper
from copy import deepcopy
import dpath.util
import re

# MDJ_FILE = "Model9.mdj"
# key_list = ["name", "_type"]






class Mdj_parser:

    def __init__(self, file, file_mode):

        if file_mode == "mdj" or file_mode == ".mdj":
            self.MDJ_FILE = file
            self.file_mode = "mdj"

        if file_mode == "xmi" or file_mode == ".xmi":
            self.XMI_FILE = file
            self.file_mode = "xmi"

        self.key_list = ["name", "_type"]

        # Collector variables
        self.uml_class_list  = []
        self.uml_attr_list   = []
        self.uml_ass_list    = []
        self.uml_general_list= []
        self.virt_ass_list   = []
        self.uml_datatypes_list =[]
        self.uml_objects_list = []
        self.uml_slots_list = []
        self.uml_links_list = []

        self.VIRTUAL_ID = "001"
        self.VIRTUAL_PARENT = "0001"

        self.runtime = 0

        self.mode = None
        self.counter__scan_children  = 0

        self.object_tracker=None





    '''################################################################################################
    #   Collector Functions for .xmi
    ################################################################################################'''

    def collect_xmi_UMLClasses(self, input_dict):
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:Class" or input_dict['@xmi:type'] == "uml:Component" or input_dict['@xmi:type'] == "uml:Model":

                # scan found class for attributes
                self.collect_xmi_UMLAttributes(input_dict)

                # Set up class
                C = UMLClass(name=input_dict['@name'], id=input_dict['@xmi:id'], parent="None")
                return C
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLAssociations(self, input_dict):
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:Association":
                C = UMLAssociation(id=input_dict['@xmi:id'], parent="None")

                C.add_end1(id=input_dict['ownedEnd'][0]["@xmi:id"], reference=input_dict['ownedEnd'][0]["@type"], parent=None, multiplicity=None)
                C.add_end2(id=input_dict['ownedEnd'][1]['@xmi:id'], reference=input_dict['ownedEnd'][1]["@type"], parent=None, multiplicity=None)
                return C
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLAttributes(self, input_dict):
        if 'ownedAttribute' in input_dict:
            if isinstance(input_dict["ownedAttribute"], list):
                for attribute in input_dict["ownedAttribute"]:
                    if "@name" in attribute and "@type" in attribute:
                        C = UMLAttribute(name=attribute['@name'], id=attribute['@xmi:id'], parent={'$ref':input_dict['@xmi:id']}, type=attribute['@type'])
                        self.uml_attr_list.append(C)
                    else:
                        return -1
                else:
                    return -1
            else:
                if "@name" in input_dict["ownedAttribute"] and "@type" in input_dict["ownedAttribute"]:
                    C = UMLAttribute(name=input_dict["ownedAttribute"]['@name'], id=input_dict["ownedAttribute"]['@xmi:id'],
                                     parent={'$ref': input_dict['@xmi:id']}, type=input_dict["ownedAttribute"]['@type'])
                    self.uml_attr_list.append(C)
                else:
                    return -1
        else:
            return -1

    def collect_xmi_UMLGeneralization(self, input_dict):
        #uml:Generalization
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:Generalization":
                C = UMLGeneralization(id=input_dict['@xmi:id'], parent=None, source=input_dict["@specific"], target=input_dict['@general'])
                # print(C.source)
                return C
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLDatatypes(self, input_dict):
        #uml:DataType
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:DataType":

                # scan found class for attributes
                self.collect_xmi_UMLAttributes(input_dict)

                C = UMLDataType(name=input_dict['@name'], id=input_dict['@xmi:id'], parent=None)
                return C
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLObject(self, input_dict):
        ''' In xmi UMLObject === uml:InstanceSpecification '''
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:InstanceSpecification":
                if '@name' in input_dict:
                    #print(input_dict)
                    C = UMLObject(name=input_dict['@name'], id=input_dict['@xmi:id'], parent=None, classifier=input_dict['classifier']['@xmi:idref'])
                    return C
                else:
                    return -1
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLSlot(self, input_dict):
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:InstanceSpecification":
                if "slot" in input_dict:
                    
                    parent_id = input_dict['@xmi:id']
                    input_dict_nn = input_dict['slot']

                    if isinstance(input_dict_nn, dict):
                        input_dict_nn = [input_dict_nn]
                    
                    for input_dict_n in input_dict_nn:
                        #print('Neu:_')
                        #print(json.dumps(input_dict_n, indent=4))
                        if '@xmi:type' in input_dict_n:
                            if input_dict_n['@xmi:type'] == "uml:Slot" and '@definingFeature' in input_dict_n:
                                C = UMLSlot(name=input_dict_n['@name'], id=input_dict_n['@xmi:id'], parent=parent_id, defining_feature=input_dict_n['@definingFeature'], value=input_dict_n['value']['@body'])
                                return C
                    else:
                        return -1
                else:
                    return -1
            else:
                return -1
        else:
            return -1

    def collect_xmi_UMLLink(self, input_dict):
        if '@xmi:type' in input_dict:
            if input_dict['@xmi:type'] == "uml:InstanceSpecification":
                if 'ownedMember' in input_dict:
                    if input_dict['ownedMember']['@xmi:type'] == "uml:InstanceSpecification":
                        C = UMLLink(id=input_dict['ownedMember']['@xmi:id'], parent=input_dict['@xmi:id'], stereotype=input_dict['ownedMember']['xmi:Extension']["stereotype"]['@value'])

                        mlt1 = None
                        mlt2 = None

                        C.add_end1(id=None, reference=input_dict['ownedMember']['xmi:Extension']['linkEnd1']['@value'], parent=None, multiplicity=mlt1)
                        C.add_end2(id=None, reference=input_dict['ownedMember']['xmi:Extension']['linkEnd2']['@value'], parent=None, multiplicity=mlt2)
                        return C
                    else:
                        return -1
                else:
                    return -1
            else:
                return -1
        else:
            return -1




    ''''################################################################################################
    #   Collector Functions for .mdj
    ################################################################################################'''

    def collect_mdj_UMLClasses(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLClass" or input_dict['_type'] == "UMLSubsystem" or input_dict['_type'] == "UMLModel":
                C = UMLClass(input_dict['name'], input_dict['_id'], input_dict['_parent'])
                return C
            else:
                return -1
        else:
            return -1


    ###########################################
    # Virtual Assocaition Collector
    #
    # Virtual associations are ownedElements of a UMLsubsystem. The dont show as UMLassociation but
    # also kind of give an nested structure
    #
    def collect_mdj_virtual_assosiations(self, input_dict):
        if '_type' in input_dict:
            if (input_dict['_type'] == "UMLSubsystem" or input_dict['_type'] == "UMLModel") and ('ownedElements' in input_dict):
                o_list = []
                for oe in input_dict['ownedElements']:
                    if oe['_type'] == "UMLClass":
                        C = UMLAssociation(self.VIRTUAL_ID, input_dict['_parent'])
                        mlt1 = 1
                        mlt2 = 1
                        C.add_end1(id=self.VIRTUAL_ID, reference=input_dict['_id'], parent=self.VIRTUAL_PARENT, multiplicity=mlt1)
                        C.add_end2(id=self.VIRTUAL_ID, reference=oe['_id'],parent=self.VIRTUAL_PARENT, multiplicity=mlt2)
                        o_list.append(C)
                return o_list
            else:
                return -1
        else:
            return -1


    ###########################################
    # Attribute Collector
    #
    def collect_mdj_UMLAttributes(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLAttribute":

                if 'defaultValue' in input_dict:
                    default_value = input_dict["defaultValue"]
                    # Catch "[]" and convert them to real lists, since these are not strings, but control structures
                    eval_val = default_value
                    if re.match('^[0-9\.]+$', default_value) == None:  # if not a plain number or a 12.12
                        if helper.isevaluable(default_value):
                            eval_val = eval(default_value)
                else:
                    eval_val = None

                if '$ref' in input_dict['type']:
                    C = UMLAttribute(name=input_dict['name'], id=input_dict['_id'], parent=input_dict['_parent'],type=input_dict['type']['$ref'], default_value=eval_val)
                else:
                    C = UMLAttribute(name=input_dict['name'], id=input_dict['_id'], parent=input_dict['_parent'], type=None, default_value=eval_val)
                return C
            else:
                return -1
        else:
            return -1

    ###########################################
    # Association Collector
    #
    def collect_mdj_UMLAssociations(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLAssociation":
                C = UMLAssociation(input_dict['_id'], input_dict['_parent'])

                if not "multiplicity" in input_dict['end1']:
                    mlt1 = None
                else:
                    mlt1 = input_dict['end1']['multiplicity']

                if not "multiplicity" in input_dict['end2']:
                    mlt2 = None
                else:
                    mlt2 = input_dict['end1']['multiplicity']

                C.add_end1(input_dict['end1']['_id'], input_dict['end1']['reference']['$ref'], input_dict['end1']['_parent']['$ref'], mlt1)
                C.add_end2(input_dict['end2']['_id'], input_dict['end2']['reference']['$ref'], input_dict['end2']['_parent']['$ref'], mlt2)
                return C
            else:
                return -1
        else:
            return -1

    ###########################################
    # UMLGeneralization Collector
    #
    def collect_mdj_UMLGeneralization(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLGeneralization":
                C = UMLGeneralization(input_dict['_id'], input_dict['_parent'], input_dict['source']['$ref'], input_dict['target']['$ref'])
                # print(C.source)
                return C
            else:
                return -1
        else:
            return -1

    def collect_mdj_UMLdatatypes(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLDataType":
                C = UMLDataType(input_dict['name'], input_dict['_id'], input_dict['_parent'])
                return C
            else:
                return -1
        else:
            return -1

    def collect_mdj_UMLObject(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLObject":
                C = UMLObject(input_dict['name'], input_dict['_id'], input_dict['_parent'], input_dict['classifier'])
                return C
            else:
                return -1
        else:
            return -1

    def collect_mdj_UMLSlot(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLSlot" and 'definingFeature' in input_dict:

                # Catch "[]" and convert them to real lists, since these are not strings, but control structures
                eval_val = input_dict['value']
                if re.match('^[0-9\.]+$',input_dict['value']) == None: # if not a plain number or a 12.12
                    if helper.isevaluable(input_dict['value']):
                        eval_val = eval(input_dict['value'])


                C = UMLSlot(name=input_dict['name'], id=input_dict['_id'], parent=input_dict['_parent'], defining_feature=input_dict['definingFeature']['$ref'], value=eval_val)
                #print('found mdj slot!')
                return C
            else:
                return -1
        else:
            return -1

    def collect_mdj_UMLLink(self, input_dict):
        if '_type' in input_dict:
            if input_dict['_type'] == "UMLLink":

                C = UMLLink(id=input_dict['_id'], parent=input_dict['_parent'], stereotype=input_dict['stereotype'])

                mlt1 = None
                mlt2 = None

                C.add_end1(input_dict['end1']['_id'], input_dict['end1']['reference']['$ref'], input_dict['end1']['_parent']['$ref'], mlt1)
                C.add_end2(input_dict['end2']['_id'], input_dict['end2']['reference']['$ref'], input_dict['end2']['_parent']['$ref'], mlt2)
                return C
            else:
                return -1
        else:
            return -1



    ###################################################################################################


    ''' #################################################################################################
   # UML-graph-parsing Functions
   # These functions crawl the generated uml_xxx_list vectors for specific info
   ###############################################################################################'''
    def get_umlclass_by_id(self, id):
        for o in self.uml_class_list:
            if o.id == id:
                return o

    def get_umlobject_by_id(self, id):
        for o in self.uml_objects_list:
            if o.id == id:
                return o

    def get_umlclass_by_name(self, name):
        for o in self.uml_class_list:
            if o.name == name:
                return o

    def get_umlobject_by_name(self, name):
        for o in self.uml_objects_list:
            if o.name == name:
                return o

    def get_umldatatype_by_name(self, name):
        for o in self.uml_datatypes_list:
            if o.name == name:
                return o

    def get_umldatatype_by_id(self, id):
        for o in self.uml_datatypes_list:
            if o.id == id:
                return o

    def get_childs_of_parent(self, parent_id):
        child_list = []
        for o in self.uml_class_list:
            if o.parent['$ref'] == parent_id:
                child_list.append(o)
        return child_list

    def get_umlattribute_by_id(self, id):
        for o in self.uml_attr_list:
            if o.id == id:
                return o

    def nested_object_to_dict(self, object):
        if hasattr(object, '__dict__'):
            d = object.__dict__
        else:
            return

        for key, value in d.items():
            if hasattr(value, '__dict__'):
                print(value)
                d[key] = self.nested_object_to_dict(value)

        return d

    def get_datatypes_in_attributes(self, attr_object):

        # .XMI Files
        if self.file_mode == "xmi":
            if "type" in attr_object:
                for dt in self.uml_datatypes_list:
                    if dt.id == attr_object["type"]:
                        return [dt]
                else:
                    return -1
            else:
                return -1

        # # .MDJ Files
        # if self.file_mode == "mdj":
        #     if "type" in attr_object:
        #         if '$ref' in attr_object["type"]:
        #             for dt in self.uml_datatypes_list+self.uml_class_list:
        #                 #print(dt.id +" | "+ dt.name)
        #                 #print(attr_object["type"]['$ref'])
        #                 #print('-----------------------')
        #                 if dt.id == attr_object["type"]['$ref']:
        #                     #print('match! --------------------------------------------')
        #                     return [dt]
        #             else:
        #                 return -1
        #         else:
        #             return -1
        #     else:
        #         return -1

        # .MDJ Files
        if self.file_mode == "mdj":
            if "type" in attr_object:
                for dt in self.uml_datatypes_list + self.uml_class_list:
                    # print(dt.id +" | "+ dt.name)
                    # print(attr_object["type"]['$ref'])
                    # print('-----------------------')
                    if dt.id == attr_object["type"]:
                        # print('match! --------------------------------------------')
                        return [dt]
                else:
                    return -1
            else:
                return -1

    def get_attributes_of_element(self, id):
        attr_list_out = []
        for a in self.uml_attr_list:
            if a.parent['$ref'] == id:
                attr_list_out.append(a)

        return attr_list_out

    def get_general_attr_of_element(self, id):

        for idx, element in enumerate(self.uml_general_list):
            if element.source == id:
                attrr_of_general_class = self.get_attributes_of_element(element.target)
                handing_class = self.get_umlclass_by_id(element.target)
                return [attrr_of_general_class, handing_class]
        else:
            return [-1, None]

    def get_general_predecessors(self, id):
        for idx, element in enumerate(self.uml_general_list):
            if element.source == id:
                if self.G.has_node(element.target):
                    children = [self.get_umlclass_by_id(x) for x in self.G.predecessors(element.target)]
                    return children
        else:
            return -1

    def get_general_successor(self, id):
        general_successor_out = []

        for idx, element in enumerate(self.uml_general_list):
            if element.target == id:
                if self.get_umlclass_by_id(element.source) != None:
                    general_successor_out.append(self.get_umlclass_by_id(element.source))

        if len(general_successor_out) == 0:
            return -1
        else:
            return general_successor_out

    def get_classifying_element(self, instance_element):

        classifying_elements = []

        # XMI Files
        if self.file_mode == "xmi":
            if 'classifier' in instance_element:
                if instance_element['classifier'] == None or instance_element['classifier'] == 'undefined':
                    return -1

                for cl in self.uml_class_list:
                    if instance_element['classifier'] == cl.id:
                        classifying_elements.append(cl)

                if len(classifying_elements) == 0:
                    return -1
                else:
                    return classifying_elements
            else:
                return -1

        # .MDJ Files
        if self.file_mode == "mdj":

            if 'classifier' in instance_element:
                if instance_element['classifier'] == None or instance_element['classifier'] == 'None':
                    return -1

                for cl in self.uml_class_list + self.uml_datatypes_list:
                    if instance_element['classifier']['$ref'] == cl.id:
                        classifying_elements.append(cl)

                if len(classifying_elements) == 0:
                    return -1
                else:
                    return classifying_elements
            else:
                return -1

    def get_slot_of_element(self, instance_element):
        slots_list = []

        if self.file_mode == "mdj":
            if 'classifier' in instance_element:
                for s in self.uml_slots_list:
                    if s.parent['$ref'] == instance_element['id']:
                        slots_list.append(s)
                if len(slots_list) == 0:
                    return -1
                else:
                    return slots_list
            return -1

        if self.file_mode == "xmi":
            if 'classifier' in instance_element:
                for s in self.uml_slots_list:
                    if s.parent == instance_element['id']:
                        slots_list.append(s)
                if len(slots_list) == 0:
                    return -1
                else:
                    return slots_list
            return -1

    def get_defining_childs_object(self, parent_id):

        child_list = []

        for link in self.uml_links_list:
            if link.stereotype == "defining":
                if parent_id == link.end2.reference:
                    child_list.append(self.get_umlobject_by_id(link.end1.reference))

        return child_list

    def get_structural_childs_object(self, parent_id):

        child_list = []

        for link in self.uml_links_list:
            if 'structural' in link.stereotype:
                if parent_id == link.end2.reference:
                    child_list.append(self.get_umlobject_by_id(link.end1.reference))

        return child_list

    def get_defining_parent_object(self, child_id):
        flag_found=0
        for link in self.uml_links_list:
            # if link.stereotype == 'defining':
            if "defining" in link.stereotype:
                if child_id == link.end1.reference:
                    flag_found=1
                    parent_o = self.get_umlobject_by_id(link.end2.reference)
                    p = self.get_defining_parent_object(parent_o.id)
        if flag_found==0:
            return self.get_umlobject_by_id(child_id) # return child(input) if there is no link <<defining>> parent
        else:
            return p # return the found parent

    def get_association_between(self, end1_class_id, end2_class_id):
        return_ass = None
        for a in self.uml_ass_list:
            if a.end1.reference == end1_class_id and a.end2.reference == end2_class_id:
                return_ass=a
        return return_ass

    def get_slot_with_defining_feature(self, defining_feature_name):
        for s in self.uml_slots_list:
            class_defined = self.get_umlclass_by_id(s.defining_feature)
            attr_defined = self.get_umlattribute_by_id(s.defining_feature)

            if class_defined != None:
                if class_defined.name == defining_feature_name:
                    return s
            if attr_defined != None:
                if attr_defined.name == defining_feature_name:
                    return s

    '''###################################################################################################
    PROCESSOR FUNCTIONS
    ###################################################################################################'''

    def process_xmi_element(self, input):

        # process lists
        if isinstance(input, list):
            for l in input:
                self.process_xmi_element(l)

        # Process dicts
        if isinstance(input, dict):

            ret = self.collect_xmi_UMLClasses(input)
            if ret != -1:
                self.uml_class_list.append(ret)

            retAss = self.collect_xmi_UMLAssociations(input)
            if retAss != -1:
                self.uml_ass_list.append(retAss)

            genn = self.collect_xmi_UMLGeneralization(input)
            if genn != -1:
                self.uml_general_list.append(genn)

            ret_dt = self.collect_xmi_UMLDatatypes(input)
            if ret_dt != -1:
                self.uml_datatypes_list.append(ret_dt)

            ret_obj = self.collect_xmi_UMLObject(input)
            if ret_obj != -1:
                self.uml_objects_list.append(ret_obj)

            ret_links = self.collect_xmi_UMLLink(input)
            if ret_links != -1:
                self.uml_links_list.append(ret_links)

            ret_slots = self.collect_xmi_UMLSlot(input)
            if ret_slots != -1:
                self.uml_slots_list.append(ret_slots)

            for key, value in input.items():
                self.process_xmi_element(value)

    def process_mdj_element(self, input):

        # process lists
        if isinstance(input, list):
            for l in input:
                self.process_mdj_element(l)

        # Process dicts
        if isinstance(input, dict):

            # check_and_print(input)
            # print_specific_type('UMLClass', input)

            ret = self.collect_mdj_UMLClasses(input)
            if ret != -1:
                self.uml_class_list.append(ret)

            ret_A = self.collect_mdj_UMLAttributes(input)
            if ret_A != -1:
                self.uml_attr_list.append(ret_A)

            retAss = self.collect_mdj_UMLAssociations(input)
            if retAss != -1:
                self.uml_ass_list.append(retAss)

            virtAss = self.collect_mdj_virtual_assosiations(input)
            if virtAss != -1:
                self.virt_ass_list.extend(virtAss)

            genn = self.collect_mdj_UMLGeneralization(input)
            if genn != -1:
                self.uml_general_list.append(genn)

            ret_dt = self.collect_mdj_UMLdatatypes(input)
            if ret_dt != -1:
                self.uml_datatypes_list.append(ret_dt)

            ret_obj = self.collect_mdj_UMLObject(input)
            if ret_obj != -1:
                self.uml_objects_list.append(ret_obj)

            ret_slots = self.collect_mdj_UMLSlot(input)
            if ret_slots != -1:
                self.uml_slots_list.append(ret_slots)

            ret_links = self.collect_mdj_UMLLink(input)
            if ret_links != -1:
                self.uml_links_list.append(ret_links)

            for key, value in input.items():
                self.process_mdj_element(value)


    def scan_children_processing(self, input_dict):

        a_list = self.get_attributes_of_element(input_dict['id'])
        a_dict_list = [self.nested_object_to_dict(x) for x in a_list]

        for a in a_dict_list:
            if "default_value" in a:
                if a["default_value"] != None:
                    a.update({'is_attribute': True, 'value': a["default_value"]})
                    # del a["default_value"]
                else:
                    a.update({'is_attribute': True, 'value': None})
            else:
                a.update({'is_attribute': True, 'value': None})

            # try to resolve value from objects
            # for slot in self.uml_slots_list:
            #    if slot.defining_feature == a['id']:
            #        a['value'] = slot.value

            input_dict.update({a['name']: a})

        # get corresponding heritage / meta-classes of the connected elements.
        # Here, we find elements, which are IN the tree by aggregation, and inherit from other classes that are not nessesarily connected
        ga_list, handing_class = self.get_general_attr_of_element(input_dict['id'])
        if ga_list != -1:
            ga_dict_list = [self.nested_object_to_dict(x) for x in ga_list]
            for a in ga_dict_list:
                a.update({'is_attribute': True, 'is_derrived': True, 'value': None})

                # try to resolve default_value from inherited attributes
                if "default_value" in a:
                    if a["default_value"] != None:
                        a['value'] = a["default_value"]

                # try to resolve value from objects
                # for slot in self.uml_slots_list:
                #    if slot.defining_feature == a['id']:
                #        a['value'] = slot.value

                input_dict.update({a['name']: a})
        
        if handing_class != None:    
            input_dict.update({'inheriting_from': handing_class.name})


        ## get inherited structures
        gp_list = self.get_general_predecessors(input_dict['id'])
        if gp_list != -1:
            gp_dict_list = [self.nested_object_to_dict(x) for x in gp_list]
            for a in gp_dict_list:
                a.update({'is_attribute': False, 'is_derrived': True})
                input_dict.update({a['name']: a})


        ## resolve datatypes of attributes
        dt_list = self.get_datatypes_in_attributes(input_dict)
        if dt_list != -1:
            dt_list_list = [self.nested_object_to_dict(x) for x in dt_list]
            for a in dt_list_list:
                a.update({'is_datatype': True})
                # input_dict["type"].update({a['name']: a})
                input_dict["type"] = {a['name']:a}

                attrs_l = self.get_attributes_of_element(a['id'])

                if attrs_l != -1:
                    attrs_l_list = [self.nested_object_to_dict(x) for x in attrs_l]
                    dt_attrs = {}
                    for b in attrs_l_list:
                        dt_attrs.update(b)

                        if "default_value" in b:
                            if b["default_value"] != None:
                                b.update({'is_attribute': True, 'value': b["default_value"]})
                            else:
                                b.update({'is_attribute': True, 'value': None})
                        else:
                            b.update({'is_attribute': True, 'value': None})


                        # new:
                        input_dict.update({dt_attrs['name']: b})
                        # print(a['name'] +" | " +  str(dt_attrs))




        ## get Erben: only in "model-mode"
        if self.mode == "model-mode":
            gs_list = self.get_general_successor(input_dict['id'])
            if gs_list != -1:
                gs_list_list = [self.nested_object_to_dict(x) for x in gs_list]
                for a in gs_list_list:
                    a.update({'is_attribute': False, 'is_derrived': False, 'is_inheritor': True})
                    input_dict.update({a['name']: a})
                    # print(23)

        # resolve classifiers of objects
        # ce_list = self.get_classifying_element(input_dict)
        # if ce_list != -1:
        #     ce_list_list = [self.nested_object_to_dict(x) for x in ce_list]
        #     for ce in ce_list_list:
        #         ce.update({'is_attribute': False, 'is_derrived': True, 'object_name': input_dict['name']})
        #         # input_dict.update({ce['name']: ce})
        #
        #         input_dict.update(ce)
        #         input_dict.update({'inherited_type': ce['name']})


        # resolve slots of objects
        # slot_list = self.get_slot_of_element(input_dict)
        # if slot_list != -1:
        #     print(input_dict['name'])
        #     for s in slot_list:
        #         sl = self.nested_object_to_dict(s)
        #         input_dict.update({sl['name']: sl})
        #         print(s.name)



        return input_dict


    #### !!!! Recursive Function !!!
    # scanning the classes
    def scan_children(self, input_dict):

        if self.G.has_node(input_dict['id']):

            # First loop Root Node
            input_dict = self.scan_children_processing(input_dict)

            # Then loop Children Nodes of the root
            # first check: if we can find sth in uml_class_list
            children_classes = [self.get_umlclass_by_id(x) for x in self.G.predecessors(input_dict['id'])]

            # second check, if we can find sth. in uml_object_list
            children_objects = [self.get_umlobject_by_id(x) for x in self.G.predecessors(input_dict['id'])]

            # third check: classifiers
            ce_list = self.get_classifying_element(input_dict)
            if ce_list == -1:
                ce_list=[]
            # ce_list = []

            # merge both
            children = children_classes + children_objects + ce_list

            for c in children:
                if c != None:

                    # Transform to dict
                    c_dict = self.nested_object_to_dict(c)
                    c_dict = self.scan_children_processing(c_dict)

                    # Check the multiplicity
                    association = self.get_association_between(c.id, input_dict["id"])
                    if association != None:
                        if association.end1.multiplicity == "1":
                            # print("Multiplicity: 1")
                            input_dict[c.name] = c_dict
                        elif association.end1.multiplicity == "1..*" or association.end1.multiplicity == "0..*":
                            # print("Multiplicity: {}".format(association.end1.multiplicity))
                            input_dict[c.name] = [c_dict]
                        else:
                            try:
                                # First try to resolve mult-value from slots
                                slot = self.get_slot_with_defining_feature(association.end1.multiplicity)
                                if slot != None:
                                    mult_int = int(slot.value)
                                    # print("!!!!!1 Got slot value")
                                else:
                                    mult_int = int(association.end1.multiplicity)
                                input_dict[c.name] = [c_dict]*mult_int
                                # print("Multiplicity: {}".format(association.end1.multiplicity))
                            except:
                                input_dict[c.name] = c_dict
                                print("Exception: Multiplicity could not be retrieved. Normal Mode")


                    # input_dict.update(c_dict)
                    # input_dict[c.name] = c_dict


            for key, value in input_dict.items():
                if isinstance(value, dict) and 'id' in value.keys():
                    self.scan_children(value)
                if isinstance(value, list):
                    for l in value:
                        self.scan_children(l)

            return input_dict

    def recursive_find_value_caller(self, input_dict, defining_feature, value):
        subdict = deepcopy(input_dict)
        changed_dict = helper.recursive_find_value_in_dict(subdict, defining_feature, value)
        input_dict = changed_dict
        return input_dict



    def recursive_resolve_defining_links(self, input_o, classifying_meta_class):

        # 4. Step  scan for defining children links
        dchilds = self.get_defining_childs_object(input_o.id)

        for dc in dchilds:

            # get the name of the current objects classifying class to find the correct path below:
            nest_name_obj = self.get_umlclass_by_id(input_o.classifier['$ref'])

            for x in dpath.util.search(classifying_meta_class, "**/id", yielded=True):
                # print('class: ' + str(dc.classifier))
                # print('--------------------------------------_>' + x[0])
                if x[1] == dc.classifier['$ref'] and (nest_name_obj.name in x[0] or nest_name_obj.name == classifying_meta_class['name']):
                    print('----------------------------------------------_>' + x[0])

                    ########################## can go into fcn same like above ###################################################
                    # 2. Step: get the meta model data from the umlmodel
                    if dc.classifier != "None":
                        ce2 = self.get_classifying_element(self.nested_object_to_dict(dc))

                        if ce2 == -1:  # No classifying meta class found
                            classifying_meta_class2 = {}
                        else:  # Found a classifying meta class
                            # get the meta class
                            classifying_meta_class2 = deepcopy(self.compose_dict(subsystem=ce2[0].id, mode="dummy_mode", flag_remove_unecessary_keys=False))
                            # classifying_meta_class2 = {}
                    else:
                        classifying_meta_class2 = {}

                    # 3. Step  scan for slots in the current object
                    slots = self.get_slot_of_element(self.nested_object_to_dict(dc))
                    if slots != -1:
                        for s in slots:
                            classifying_meta_class2 = self.recursive_find_value_caller(classifying_meta_class2,
                                                                                       s.defining_feature, s.value)

                    #############################################################################################

                    childs = self.get_structural_childs_object(dc.id)

                    for sc in childs:
                        print('-----------------_STRUCTURAL CHILD: ' + sc.name)
                        self.scan_objects(dc, classifying_meta_class2)

                    # If its datatype, we rsplit 3. if not we rsplit 1
                    if "is_datatype" in classifying_meta_class2:
                        if classifying_meta_class2['is_datatype'] == True:
                            dpath.util.set(classifying_meta_class, x[0].rsplit('/', 3)[0], classifying_meta_class2)
                    else:
                        dpath.util.set(classifying_meta_class, x[0].rsplit('/', 1)[0], classifying_meta_class2)


                    # dpath.util.set(classifying_meta_class, x[0].rsplit('/', 1)[0], classifying_meta_class2)
                    # dpath.util.set(classifying_meta_class, x[0].rsplit('/', 3)[0], classifying_meta_class2)
                    # classifying_meta_class[x[0].rsplit('/', 1)[0]] = classifying_meta_class2
                    # print('integrated: ' + classifying_meta_class2['name'])



                    break




            self.recursive_resolve_defining_links(dc, classifying_meta_class)

        return classifying_meta_class

    def remove_from_dict_if_exist(self, key, input_dict):
        if key in input_dict.keys():
            input_dict.pop(key)

        return input_dict

    def del_unnessessary_keys(self, input_dict):

        not_needed_keys = ['parent', 'name', 'id', 'is_attribute', 'is_datatype', 'default_value']

        if isinstance(input_dict, dict):
            for nn in not_needed_keys:
                self.remove_from_dict_if_exist(nn, input_dict)

        for key, value in input_dict.items():
            if isinstance(value, dict):
                self.del_unnessessary_keys(value)
            if isinstance(value, list):
                for l in value:
                    if isinstance(l, dict):
                        self.del_unnessessary_keys(l)

        return input_dict

    # Function which creates a networkx graph containing all the classes (nodes) and associations (edges)
    # The graph is used for getting antecessors / Predecessors of elements along hte associations chain
    def generate_graph(self):
        start_time = time.time()
        ########################################################
        #
        # create Graph
        #
        self.G = nx.DiGraph()

        # add nodes from classes
        class_ids = [x.id for x in self.uml_class_list]
        self.G.add_nodes_from(class_ids)

        # add nodes from attributes
        attr_ids = [x.id for x in self.uml_attr_list]
        self.G.add_nodes_from(attr_ids)

        # add nodes from general attributes
        gen_ids = [x.id for x in self.uml_general_list]
        self.G.add_nodes_from(gen_ids)

        # add nodes from datatypes
        dt_ids = [x.id for x in self.uml_datatypes_list]
        self.G.add_nodes_from(dt_ids)

        # add nodes from uml objects
        obj_ids = [x.id for x in self.uml_objects_list]
        self.G.add_nodes_from(obj_ids)



        labeldict = {x.id: x.name for x in self.uml_class_list}

        # add edges from UMLassociations
        for a in self.uml_ass_list:
            e1 = self.get_umlclass_by_id(a.end1.reference)
            e2 = self.get_umlclass_by_id(a.end2.reference)

            if e1 != None and e2 != None:
                self.G.add_edge(e1.id, e2.id)

        # add edges from UMLLinks if they are of "stereotypes == structureal"
        for l in self.uml_links_list:
            # if l.stereotype == "structural":
            if "structural" in l.stereotype:
                e1 = self.get_umlobject_by_id(l.end1.reference)
                e2 = self.get_umlobject_by_id(l.end2.reference)

                if e1 != None and e2 != None:
                    self.G.add_edge(e1.id, e2.id)


        self.runtime = self.runtime + time.time() - start_time
        return self.G

    # Main function to scan in uml-objects
    # !! Recursive!!
    def scan_objects(self, root_obj, obj_dict):

        input_o = root_obj

        # 2. Step: get the meta model data from the umlmodel
        if input_o.classifier != "None":
            ce = self.get_classifying_element(self.nested_object_to_dict(input_o))

            if ce == -1:  # No classifying meta class found
                classifying_meta_class = {}
            else:  # Found a classifying meta class
                # get the meta class
                # classifying_meta_class = deepcopy(self.compose_dict(subsystem=ce[0].name, mode="dummy_mode", flag_remove_unecessary_keys=False))
                classifying_meta_class = deepcopy(self.compose_dict(subsystem=ce[0].id, mode="dummy_mode", flag_remove_unecessary_keys=False))
        else:
            classifying_meta_class = {}


        # 3. Step  scan for slots in the current object
        slots = self.get_slot_of_element(self.nested_object_to_dict(input_o))
        if slots != -1:
            for s in slots:
                classifying_meta_class = self.recursive_find_value_caller(classifying_meta_class, s.defining_feature, s.value)
                pass


        # 4. Step Refine defining links
        classifying_meta_class = self.recursive_resolve_defining_links(input_o, classifying_meta_class)


        # Update main dict
        # Check if we can delete a part of the meta-model, since we overwrite it with the object-one
        if 'name' in classifying_meta_class:
            if classifying_meta_class['name'] in obj_dict:
                del obj_dict[classifying_meta_class['name']]

        # check if parents are part of the meta-model. then overwrite too
        if 'inheriting_from' in classifying_meta_class:
            if classifying_meta_class['inheriting_from'] in obj_dict:
                del obj_dict[classifying_meta_class['inheriting_from']]
        else:
            if 'name' in classifying_meta_class:
                classifying_meta_class['inheriting_from'] = classifying_meta_class['name']

        if 'name' in classifying_meta_class:
            classifying_meta_class['classifier'] = classifying_meta_class['name']


        # Do the Update
        new_key = input_o.name
        obj_dict[new_key] = classifying_meta_class


        # 5. Step  scan for structural children links, if any, go nested
        structural_childs = []
        childs = self.get_structural_childs_object(input_o.id)

        for sc in childs:
            # print(sc.name)
            # self.scan_objects(sc, obj_dict)
            self.scan_objects(sc, obj_dict[new_key])

        return obj_dict

    ''' ###################################################################################################
    USER FUNCTIONS: Use only the three fkt. below
    ###################################################################################################'''

    

    # Function to automatically choose the correct decomposition function, respective to the filetype (mdj or xmi)
    # if filetype is known and set, one can also directly call therespective functions
    # decompose_xmi() or decompose_mdj()
    #
    def decompose(self):

        ### Mode xmi
        if self.file_mode == '.xmi' or self.file_mode == 'xmi':
            self.decompose_xmi()

        ### Mode mdj
        if self.file_mode == '.mdj' or self.file_mode == 'mdj':
            self.decompose_mdj()

    # Decomposing a .xmi file. This is still under development  
    def decompose_xmi(self):
        start_time = time.time()
        xmi_data = open(self.XMI_FILE, 'r')
        xmi_dict = xmltodict.parse(xmi_data.read())
        #print(xmi_dict)
        # print("yea")

        ###################################
        # Iteration over all elements
        # process_elemets calls itself recursively and processes the whole tree
        #
        for key, value in xmi_dict.items():
            # Process lists
            self.process_xmi_element(value)

        self.runtime = self.runtime + time.time() - start_time

        # automatically Generate Graph
        self.generate_graph()

        print('Finished .XMI decomposed!')

    # Decomposing a .mdj file
    def decompose_mdj(self):
        start_time = time.time()
        mdj_data = open(self.MDJ_FILE,'r')
        mdj_dict = json.loads(mdj_data.read())

        ###################################
        # Iteration over all elements
        # process_elemets calls itself recursively and processes the whole tree
        #
        for key, value in mdj_dict.items():
            # Process lists
            self.process_mdj_element(value)

        self.runtime = self.runtime + time.time() - start_time

        # automatically Generate Graph
        self.generate_graph()

        print('Finished. .MDJ decomposed!')
        ###################################################################################################

    # Recompose a dictionary / jsonobject form the decomposed input-file
    # This function handles classes
    def compose_dict(self, subsystem, mode, flag_remove_unecessary_keys=True):
        self.mode = mode
        start_time = time.time()

        subs = self.get_umlclass_by_id(subsystem)
        if subs == None:
            subs = self.get_umlobject_by_id(subsystem)
            if subs == None:
                subs = self.get_umldatatype_by_id(subsystem)
                if subs == None:
                    subs = self.get_umlclass_by_name(subsystem)
                    if subs == None:
                        subs = self.get_umlobject_by_name(subsystem)
                        if subs == None:
                            subs = self.get_umldatatype_by_name(subsystem)

        subs_dict = self.nested_object_to_dict(subs)

        # Scan object-structure to dict
        subs_dict = self.scan_children(subs_dict)


        # Remove unecessary keys from dict
        if flag_remove_unecessary_keys == True:
            subs_dict = self.del_unnessessary_keys(subs_dict)

        self.runtime = self.runtime + time.time() - start_time
        print('Composing of json finished! Total time: ' + str(round(self.runtime,2)) + ' s')
        return subs_dict

    # Recompose a dictionary / jsonobject form the decomposed input-file
    # This function is for instances/objects
    def compose_objects(self, top_level_obj):


        # 1 Step: find top level obj. to start
        for o in self.uml_objects_list:
            if o.name == top_level_obj:
                root_obj = o

        obj_dict = {}

        obj_dict = self.scan_objects(root_obj=root_obj,obj_dict=obj_dict)

        subs_dict = self.del_unnessessary_keys(obj_dict)

        return obj_dict


