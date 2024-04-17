from dataclasses import dataclass

from shaft_point_data import ShaftPointData
import materials

@dataclass
class Shaft:
    '''
    This class holds the points to analyze along the shaft. This allows the program to know where analysis should be performed, and with what criteria.

    Parameters
    ----------
    length : float
        Length of the entire shaft

    points_of_interest : dict[float, ShaftPointData] 
        Points at which to analyze the shaft. 
    '''
