from enum import Enum

#------------------#
#   Enumerations   #
#------------------#

class LoadType(Enum):
    Bending = 0
    Torsion = 1
    Axial = 2

class NotchType(Enum):
    Sharp = 0
    Well_Rounded = Wide = 1
    Keyseat = Keyway = 2
    Retaining_Ring = 3

class SurfaceFinish(Enum):
    Ground = 0
    Machined = Cold_Drawn = 1
    Hot_Rolled = 2
    As_Forged = 3

class units(Enum):
    Imperial = 0
    Metric = 1