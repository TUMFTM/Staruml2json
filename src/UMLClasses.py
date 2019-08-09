######################################################################
#  UML Classes
# Predefinitions of the UMLClasses
######################################################################
__author__ = "Lukas Merkle"
__copyright__ = "Copyright 2019, Institute of Automotive Technology"
__license__ = "LGPL V3"
__version__ = "1.0"
__maintainer__ = "Lukas Merkle"
__email__ = "lukas.merkle@tum.de"
######################################################################

class UMLAttribute:
    def __init__(self, name, id, parent, type, default_value):
        self.name = name
        self.id = id
        self.parent = parent
        self.type = type
        self.default_value = default_value


class UMLClass:
    def __init__(self, name, id, parent):
        self.name = name
        self.id = id
        self.parent = parent


class UMLLink:
    def __init__(self, id, parent, stereotype):
        self.id = id
        self.parent = parent
        self.stereotype = stereotype

    def add_end1(self, id, reference, parent, multiplicity):
        self.end1 = End(id, reference, parent, multiplicity)

    def add_end2(self, id, reference, parent, multiplicity):
        self.end2 = End(id, reference, parent, multiplicity)

class UMLAssociation:
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent

    def add_end1(self, id, reference, parent, multiplicity):
        self.end1 = End(id, reference, parent, multiplicity)

    def add_end2(self, id, reference, parent, multiplicity):
        self.end2 = End(id, reference, parent, multiplicity)



class UMLGeneralization:
    def __init__(self, id, parent, source, target):
        self.id = id
        self.parent = parent
        self.source = source
        self.target = target


class End:
    def __init__(self, id, reference, parent, multiplicity):
        self.id = id
        self.parent = parent
        self.reference = reference
        self.multiplicity = multiplicity

class UMLDataType:
    def __init__(self, name,  id, parent):
        self.name = name
        self.id = id
        self.parent = parent


class UMLObject:
    def __init__(self, name, id, parent, classifier):
        self.name = name
        self.id = id
        self.parent = parent
        self.classifier = classifier

class UMLSlot:
    def __init__(self, name, id, parent, defining_feature, value):
        self.name = name
        self.id = id
        self.parent = parent
        self.defining_feature = defining_feature
        self.value = value


