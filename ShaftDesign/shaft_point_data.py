from dataclasses import dataclass

from . import materials
from . import enums as en

#----------------------#
#   Shaft dataclass    #
#----------------------#
@dataclass
class ShaftPointData:
    '''
    Dataclass for holding data at a point in the shaft
    '''
    # Basic data (needed for calculation)
    units : en.units

    Ma : float  # Alternating bending moment
    Mm : float  # Midrange bending
    Ta : float  # Alternating torque
    Tm : float  # Midrange torque

    notch_type : en.NotchType  # The severity of notch (for calculating stress concentrations)

    material : materials.Strengths      # Ultimate and yield strength
    surface_finish : en.SurfaceFinish      # Surface finish condition

    true_fracture : float = None   # True fracture strength for Morrow criterion

    # Solve-for-variables (Only one is provided, the other is solved for)
    d : float = 0
    n : float = 0

    # Calculated values (Calculated and stored while running)
    Kt : float = None  # Theoretical bending stress concentration at point
    Kts : float = None # Theoretical torsion stress concentration at point
    Kf : float = None  # Fatigue bending stress concentration
    Kfs : float = None # Fatigue torsion stress concentration
    Se : float = None  # Endurance Limit

    solve_for : str = None      # Either 'd' or 'n' depending on which is unassigned

    def __post_init__(self):
        '''
        Checks to make sure either n or d is provided, not both, not neither, else an error is raised.
        ALso, if no error has occured, this stores which variable needs to be solved for.
        '''
        if self.n == 0 and self.d == 0:     # Neither Specified Error
            raise ValueError(f'In Shaft_point_data: Either n or d *must* be specified. Note: only *one* must be specified, not both.')
        elif self.n != 0 and self.d != 0:   # Both Specified Error
            raise ValueError(f'In Shaft_point_data: Only one of n or d must be specified, both cannot be specified. n = {self.n}  d = {self.d}')
        
        elif self.n == 0:           # No error, find what we're solving for
            self.solve_for = 'n'
        else:
            self.solve_for = 'd'