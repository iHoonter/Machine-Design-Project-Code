import numpy as np

import shaft_point_data
import data_printer

class DE_shaft_stress_criterions:
    '''
    Class storing all of the distortional energy (DE) fatigue criterions for shafts

    Parameters
    ----------
    data : shaft_point_data.ShaftPointData

        Data object for the shaft point

    printer : data_printer.DataPrinter

        DataPrinter object to specify how data is shown when calculated. Default is DataPrinter('.3f').

    importance : int

        Importance value to pass to all printer.show() statements after calculations. Default is 0 (show everything).
    '''
    def __init__(self, data : shaft_point_data.ShaftPointData, units , printer : data_printer.DataPrinter = data_printer.DataPrinter('.3f'), importance : int = 0) -> None:
        self.shaft = data    # Shaft data object
        
        # Change material properties into base units
        if units == 0:      # Convert from ksi to psi
            self.shaft.material.S_ut *= 10**3
            self.shaft.material.S_y *= 10**3
            self.shaft.Se *= 10**3
        else:                                           # Convert from MPa to Pa
            self.shaft.material.S_ut *= 10**6
            self.shaft.material.S_y *= 10**6
            self.shaft.Se *= 10**6
        
        self.printer = printer          # DataPrinter object to specify how results are printed
        self.importance = importance    # Importance to apply to all printer.show() calls (To control if data is printed or not)

        self._get_A()
        self._get_B()
    
    def _get_A(self):
        ''''A' constant used in other equations'''
        self.A = np.sqrt(4*(self.shaft.Kf*self.shaft.Ma)**2 + 3*(self.shaft.Kfs*self.shaft.Ta)**2)
        self.printer.show(self.A, self.importance + 1, label='A = ')

    def _get_B(self):
        ''''B' constant used in other equations'''
        self.B = np.sqrt(4*(self.shaft.Kf*self.shaft.Mm)**2 + 3*(self.shaft.Kfs*self.shaft.Tm)**2)
        self.printer.show(self.A, self.importance + 1, label='B = ')

    def Goodman(self, importance):
        '''DE Goodman shaft design criterion equations'''

        if self.shaft.solve_for == 'n':
            # Equation solving for safety factor
            solution = ((np.pi * self.shaft.d**3)/16) * ( (self.A/self.shaft.Se) + (self.B/self.shaft.material.S_ut) )**-1
        
        elif self.shaft.solve_for == 'd':
            # Equation solving for diameter
            solution = ( ((16*self.shaft.n)/np.pi) * ((self.A/self.shaft.Se) + (self.B/self.shaft.material.S_ut)) )**(1/3)

        else:
            raise RuntimeError("In Goodman: shaft_data.solve_for unspecified")
        
        return solution


    def Morrow(self, importance):
        '''DE Morrow shaft design criterion equations'''

        if self.shaft.solve_for == 'n':
            # Solving for safety factor
            solution = ((np.pi*self.d**3)/16) * ((self.A/self.shaft.Se) + (self.B/self.true_fracture))**-1
        
        elif self.shaft.solve_for == 'd':
            # Solving for diameter
            solution = ( ((16*self.n)/np.pi) * ((self.A/self.shaft.Se) + (self.B/self.true_fracture)) )**(1/3)

        else:
            raise RuntimeError("In Morrow: shaft_data.solve_for unspecified")
        
        return solution
    
    def Gerber(self, importance):
        '''DE Gerber shaft design criterion equations'''
        if self.shaft.solve_for == 'n':
            # Solving for safety factor
            solution = ((8*self.A)/(np.pi * self.shaft.d**3 * self.shaft.Se)) * ( 1 + ( 1 + ((2*self.B*self.shaft.Se)/(self.A*self.shaft.material.S_ut))**2 )**(1/2) )
            solution = solution**-1
        
        elif self.shaft.solve_for == 'd':
            # Solving for diameter
            solution = ( ((8*self.shaft.n*self.A)/(np.pi*self.shaft.Se)) * (1 + ( 1 + ((2*self.B*self.shaft.Se)/(self.A*self.shaft.material.S_ut))**2 )**(1/2)))**(1/3)

        else:
            raise RuntimeError("In Gerber: shaft_data.solve_for unspecified")
        
        return solution

    def SWT(self, importance):
        '''DE SWT shaft design criterion equations'''
        if self.shaft.solve_for == 'n':
            # Solving for safety factor
            solution = ((np.pi*self.shaft.d**3)/16) * (self.shaft.Se/np.sqrt(self.A**2 + self.A))
        
        elif self.shaft.solve_for == 'd':
            # Solving for diameter
            solution = ( ((16*self.shaft.n)/(np.pi*self.shaft.Se)) * np.sqrt(self.A**2 + self.A*self.B) )**(1/3)

        else:
            raise RuntimeError("In SWT: shaft_data.solve_for unspecified")
        
        return solution
    
    def yielding(self, importance = None, conservative = True):
        '''Checking for first-cycle yield'''
        # Get importance for printing
        if importance == None:
            importance = self.importance

        if self.shaft.solve_for == 'n':     # Solving for safety factor

            if conservative:
                sig_a = ( ((32*self.shaft.Kf*self.shaft.Ma)/(np.pi*self.shaft.d**3))**2 + 3*((16*self.shaft.Kfs*self.shaft.Ta)/(np.pi*self.shaft.d**3))**2 )**(1/2)
                sig_m = ( ((32*self.shaft.Kf*self.shaft.Mm)/(np.pi*self.shaft.d**3))**2 + 3*((16*self.shaft.Kfs*self.shaft.Tm)/(np.pi*self.shaft.d**3))**2 )**(1/2)
                sigmax = sig_a + sig_m
            else:
                sigmax = ( ((32*self.shaft.Kf*(self.shaft.Mm + self.shaft.Ma))/(np.pi*self.shaft.d**3))**2 + 3*((16*self.shaft.Kfs*(self.shaft.Tm + self.shaft.Ta))/(np.pi*self.shaft.d**3))**2 )**(1/2)

            solution = self.shaft.material.S_y/sigmax

        else:                               # Solving for diameter

            solution = np.cbrt( ((16*self.shaft.n)/(np.pi*self.shaft.material.S_y)) * np.sqrt( 4*(self.shaft.Kf*(self.shaft.Ma + self.shaft.Mm))**2 + 3*(self.shaft.Kfs*(self.shaft.Ta + self.shaft.Tm))**2 ))


        self.printer.show(solution, importance, label=f"Yielding: {self.shaft.solve_for} = ")

        return solution
        