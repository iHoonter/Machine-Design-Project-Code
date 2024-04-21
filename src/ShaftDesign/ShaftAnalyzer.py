from .shaft_point_data import ShaftPointData
from .shaft_designer import ShaftDesigner
from .enums import *
from .materials import *
from ..Common import DataPrinter

from dataclasses import dataclass
from typing import Callable
import pandas as pd

@dataclass
class PointProperties:
    # location should be within [0, Shaft.length]
    location: float
    stress_concentration: NotchType

@dataclass
class Shaft:
    '''
    Class to hold all the data defining a shaft, including each point to analyze
    '''
    # Shaft properties (US or SI units, the shaft material properties, and surface finish)
    units: units
    material: Strengths
    surface_finish: SurfaceFinish

    # The length of the shaft
    length: float

    # Functions that return the force at each point along the shaft, OR a constant value
    Ma: Callable[[float], float] | float
    Mm: Callable[[float], float] | float
    Ta: Callable[[float], float] | float
    Tm: Callable[[float], float] | float

    # Label your point properties with letters or such
    points: dict[str : PointProperties]

    # Provide only ONE of these, the other is solved for
    d: dict[str : float] | None = None
    n: float = 0

    # Only used for a specific stress criterion
    true_fracture: float | None = None


    # These allow a constant moment or torque to be entered
    # -----------------------------------------------------

    def MA(self, location: float):
        if isinstance(self.Ma, Callable):
            return self.Ma(location)
        else:
            return self.Ma
        
    def MM(self, location: float):
        if isinstance(self.Mm, Callable):
            return self.Mm(location)
        else:
            return self.Mm
        
    def TA(self, location: float):
        if isinstance(self.Ta, Callable):
            return self.Ta(location)
        else:
            return self.Ta
        
    def TM(self, location: float):
        if isinstance(self.Tm, Callable):
            return self.Tm(location)
        else:
            return self.Tm
        
    def __post_init__(self):
        if self.n != 0 and self.d == None:
            self.d = {}
            for name in self.points.keys():
                self.d[name] = 0
        if self.n == 0 and self.d == None:
            raise ValueError("Must specify either n or a dictionary of d's for each point in ShaftAnalyzer")

class Criterion(Enum):
    Goodman = 0,
    Yielding = 1,
    YieldingConservative = 2,

class ShaftAnalyzer:
    '''
    Class to perform analysis at each point the the shaft.
    '''
    def __init__(self, shaft: Shaft, printer: DataPrinter = DataPrinter('.3f')) -> None:
        self.shaft = shaft
        self.printer = printer

        self.shaft_point_datas = {}
        self.shaft_designers = {}
        self.point_shown = {}
        for name, properties in shaft.points.items():
            properties: PointProperties

            # Checking to make sure the analyzed point is within the shaft length
            if (properties.location > shaft.length):
                raise ValueError("A PointProperty can only have a location within the range [0, Shaft.length]")

            # Creating a ShaftPointData for each point along the shaft
            self.shaft_point_datas[name] = ShaftPointData(
                units = shaft.units,
                material = shaft.material,
                surface_finish = shaft.surface_finish,

                true_fracture = shaft.true_fracture,

                n = shaft.n,
                d = shaft.d[name],

                notch_type = properties.stress_concentration,

                # Finding the applied forces at each point location
                Ma = shaft.MA( properties.location ),
                Mm = shaft.MM( properties.location ),
                Ta = shaft.TA( properties.location ),
                Tm = shaft.TM( properties.location )
            )

            self.shaft_designers[name] = ShaftDesigner(
                shaft_data = self.shaft_point_datas[name],
                printer = self.printer
            )

            self.criterions = []
    
    def solveUsing(self, criterions: list[Criterion], importance = 1):
        
        all_results = {}
        for name, designer in self.shaft_designers.items():
            designer: ShaftDesigner

            point_data = self.shaft_point_datas[name]

            self.printer.section(f'--------\nPoint {name}\n--------', importance_level=0)

            self.printer.section('Stresses:', importance)
            self.printer.show(point_data.Ma, importance, 'Ma = ')
            self.printer.show(point_data.Mm, importance, 'Mm = ')
            self.printer.show(point_data.Ta, importance, 'Ta = ')
            self.printer.show(point_data.Tm, importance, 'Tm = ')

            point_results = []
            for criterion in criterions:
                match criterion:
                    case Criterion.Goodman:
                        point_results.append(designer.Goodman(importance = importance+1))
                    case Criterion.Yielding:
                        point_results.append(designer.yielding(conservative=False, importance = importance+1))
                    case Criterion.YieldingConservative:
                        point_results.append(designer.yielding(conservative=True, importance = importance+1))
                
            all_results[name] = point_results

        self.table = pd.DataFrame(all_results, index=criterions)

        return self.table

    # def Morrow(self, importance = 0):
    # def Gerber(self, importance = 0):
    # def SWT(self, importance = 0):
        

            
