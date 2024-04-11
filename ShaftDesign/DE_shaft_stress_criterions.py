import numpy as np
import copy

from . import shaft_point_data
from . import enums as en

def _reduce_units(shaft : shaft_point_data.ShaftPointData):
    '''Function to reduce the material strengths into base units for calculation'''
    new_shaft = copy.deepcopy(shaft)    # All changes are made to a copy to leave original shaft strengths unchanged

    # Change material properties into base units
    if shaft.units == en.units.Imperial:      # Convert from ksi to psi
        new_shaft.material.S_ut *= 10**3
        new_shaft.material.S_y *= 10**3
        new_shaft.Se *= 10**3
    else:                                     # Convert from MPa to Pa
        new_shaft.material.S_ut *= 10**6
        new_shaft.material.S_y *= 10**6
        new_shaft.Se *= 10**6

    return new_shaft

#----------------------------#
#   DE Criterion Constants   #
#----------------------------#

def _get_A(shaft : shaft_point_data.ShaftPointData):
    ''''A' constant used in other equations'''
    A = np.sqrt(4*(shaft.Kf*shaft.Ma)**2 + 3*(shaft.Kfs*shaft.Ta)**2)
    return A

def _get_B(shaft : shaft_point_data.ShaftPointData):
    ''''B' constant used in other equations'''
    B = np.sqrt(4*(shaft.Kf*shaft.Mm)**2 + 3*(shaft.Kfs*shaft.Tm)**2)
    return B


#--------------------------#
#        Criterions        #
#--------------------------#

def Goodman(shaft : shaft_point_data.ShaftPointData):
    '''DE-Modified Goodman shaft design criterion'''
    shaft = _reduce_units(shaft)
    A = _get_A(shaft)
    B = _get_B(shaft)

    if shaft.solve_for == 'n':
        # Equation solving for safety factor
        solution = ((np.pi * shaft.d**3)/16) * ( (A/shaft.Se) + (B/shaft.material.S_ut) )**-1
        
    elif shaft.solve_for == 'd':
        # Equation solving for diameter
        solution = ( ((16*shaft.n)/np.pi) * ((A/shaft.Se) + (B/shaft.material.S_ut)) )**(1/3)

    else:
        raise RuntimeError("In Goodman: shaft_data.solve_for unspecified")
    
    return solution

def Morrow(shaft : shaft_point_data.ShaftPointData):
    '''DE-Morrow shaft design criterion'''
    shaft = _reduce_units(shaft)
    A = _get_A(shaft)
    B = _get_B(shaft)

    if shaft.solve_for == 'n':
        # Solving for safety factor
        solution = ((np.pi*shaft.d**3)/16) * ((A/shaft.Se) + (B/shaft.true_fracture))**-1
    
    elif shaft.solve_for == 'd':
        # Solving for diameter
        solution = ( ((16*shaft.n)/np.pi) * ((A/shaft.Se) + (B/shaft.true_fracture)) )**(1/3)

    else:
        raise RuntimeError("In Morrow: shaft_data.solve_for unspecified")
    
    return solution

def Gerber(shaft : shaft_point_data.ShaftPointData):
    '''DE-Gerber shaft design criterion'''
    shaft = _reduce_units(shaft)
    A = _get_A(shaft)
    B = _get_B(shaft)

    if shaft.solve_for == 'n':
        # Solving for safety factor
        solution = ((8*A)/(np.pi * shaft.d**3 * shaft.Se)) * ( 1 + ( 1 + ((2*B*shaft.Se)/(A*shaft.material.S_ut))**2 )**(1/2) )
        solution = solution**-1
        
    elif shaft.solve_for == 'd':
        # Solving for diameter
        solution = ( ((8*shaft.n*A)/(np.pi*shaft.Se)) * (1 + ( 1 + ((2*B*shaft.Se)/(A*shaft.material.S_ut))**2 )**(1/2)))**(1/3)

    else:
        raise RuntimeError("In Gerber: shaft_data.solve_for unspecified")
    
    return solution


def SWT(shaft : shaft_point_data.ShaftPointData):
    '''DE-SWT shaft design criterion'''
    shaft = _reduce_units(shaft)
    A = _get_A(shaft)
    B = _get_B(shaft)

    if shaft.solve_for == 'n':
        # Solving for safety factor
        solution = ((np.pi*shaft.d**3)/16) * (shaft.Se/np.sqrt(A**2 + A))
    
    elif shaft.solve_for == 'd':
        # Solving for diameter
        solution = ( ((16*shaft.n)/(np.pi*shaft.Se)) * np.sqrt(A**2 + A*B) )**(1/3)

    else:
        raise RuntimeError("In SWT: shaft_data.solve_for unspecified")

    return solution

def yielding(shaft : shaft_point_data.ShaftPointData, conservative = True):
    '''Checking for first-cycle yield'''
    shaft = _reduce_units(shaft)

    if shaft.solve_for == 'n':      # Solving for safety factor

        if conservative:            # Conservative estimation of maximum stress (sig'a + sig'm)
            sig_a = ( ((32*shaft.Kf*shaft.Ma)/(np.pi*shaft.d**3))**2 + 3*((16*shaft.Kfs*shaft.Ta)/(np.pi*shaft.d**3))**2 )**(1/2)
            sig_m = ( ((32*shaft.Kf*shaft.Mm)/(np.pi*shaft.d**3))**2 + 3*((16*shaft.Kfs*shaft.Tm)/(np.pi*shaft.d**3))**2 )**(1/2)
            sigmax = sig_a + sig_m
        else:                       # Full von-mises maximum stress
            sigmax = ( ((32*shaft.Kf*(shaft.Mm + shaft.Ma))/(np.pi*shaft.d**3))**2 + 3*((16*shaft.Kfs*(shaft.Tm + shaft.Ta))/(np.pi*shaft.d**3))**2 )**(1/2)

        solution = shaft.material.S_y/sigmax

    else:                           # Solving for diameter
        if conservative:
            solution = 2*np.cbrt( (1/(np.pi*shaft.material.S_y)) * (2*shaft.n*( np.sqrt(4 * shaft.Kf**2 * shaft.Ma**2 + 3 * shaft.Kfs**2 * shaft.Ta**2) + np.sqrt(4 * shaft.Kf**2 * shaft.Mm**2 + 3 * shaft.Kfs**2 * shaft.Tm**2))))
        else:
            solution = np.cbrt( ((16*shaft.n)/(np.pi*shaft.material.S_y)) * np.sqrt( 4*(shaft.Kf*(shaft.Ma + shaft.Mm))**2 + 3*(shaft.Kfs*(shaft.Ta + shaft.Tm))**2 ))

    return solution
