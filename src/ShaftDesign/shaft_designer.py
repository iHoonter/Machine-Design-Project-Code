import numpy as np
from enum import Enum
from dataclasses import dataclass

from . import DE_shaft_stress_criterions
from . import shaft_point_data
from ..Common import DataPrinter
from . import enums as en

@dataclass
class IterationParams:
    d_initial : float   # Initial diameter to use in calculations
    max_error : float   # Error percentage to stop at

class ShaftDesigner:
    '''
    Class to solve shaft design problems. Manages shaft data and other solvers. 

    Parameters
    ----------
    ### shaft_data : shaft_point_data.ShaftPointData

        Object holding data for a point in the shaft

    ### printer : data_printer.DataPrinter

        Printer object to specify formatting when printing. Default printer is DataPrinter('.3f')
    '''
    def __init__(self, shaft_data : shaft_point_data.ShaftPointData, printer : DataPrinter = DataPrinter('.3f'), d_iteration_params : IterationParams | None = None) -> None:
        self.shaft = shaft_data
        self.printer = printer

        # Create defualt iteration parameters if solving for d, and no other parameters provided
        if self.shaft.solve_for == 'd' and d_iteration_params == None:
            if self.shaft.units == en.units.Imperial:     # d0 = 3 in., max error is 5%
                self.iter_params = IterationParams(d_initial=3, max_error=0.05)
            else:                                   # d0 = 15mm, max error is 5%
                self.iter_params = IterationParams(d_initial=15, max_error=0.05)

    def Goodman(self, importance = 1):
        '''Method to calculate answer using the Goodman criterion'''
        return self._begin_solving(criterion=DE_shaft_stress_criterions.Goodman, name="Goodman", importance=importance)

    def Morrow(self, importance = 1):
        '''Method to calculate answer using the Morrow criterion'''
        return self._begin_solving(criterion=DE_shaft_stress_criterions.Morrow, name="Goodman", importance=importance)

    def Gerber(self, importance = 1):
        '''Method to calculate answer using the Gerber criterion'''
        return self._begin_solving(criterion=DE_shaft_stress_criterions.Gerber, name="Gerber", importance=importance)

    def SWT(self, importance = 1):
        '''Method to calculate answer using the SWT criterion'''
        return self._begin_solving(criterion=DE_shaft_stress_criterions.SWT, name="SWT", importance=importance)

    def yielding(self, importance = 1, conservative = True):
        '''
        Method for calculating answer using first-cycle yielding

        Paramters
        ---------
        ### conservative:

            Whether or not to use the conservative approximation for maximum stress. Conservative is sig_max = sig'a + sig'm.
        '''
        return self._begin_solving(criterion=DE_shaft_stress_criterions.yielding, name="yielding", importance=importance, conservative=conservative)

    def _begin_solving(self, criterion, name, importance, **kwargs):
        '''Internal method to call the proper method to solve for n or d, depending on what is needed'''
        if self.shaft.solve_for == 'n':
            return self._n_solver(criterion, name, importance, **kwargs)
        else:
            return self._d_solver(criterion, name, importance, **kwargs)

    def _n_solver(self, criterion, name, importance, **kwargs):
        '''Solves for factor of safety using the provided DE-Criterion'''
        # Calculations
        # ------------
        self.shaft.Se = self.get_endurance_limit(importance=importance)                          # Calculating endurance limit
        self.shaft.Kf, self.shaft.Kfs = self.get_stress_concentrations(importance=importance)    # Calculating fatigue stress concentrations
        self.shaft.n = criterion(self.shaft, **kwargs)                                             # Calculating factor of safety

        # Printing
        # --------
        self.printer.section(f"#--- Solving for n using {name} criterion ---#", importance_level=importance)    # Supporting calculations
        self.printer.show(self.shaft.Se, label="Se = ", importance_level=importance)
        self.printer.show(self.shaft.Kf, label="Kf = ", importance_level=importance)

        self.printer.show(self.shaft.n, importance_level = 0, label=f"{name}: n = ")                              # Final result

        return self.shaft.n


    def _d_solver(self, criterion, name, importance, **kwargs):
        '''
        Solves for the diameter using the provided criterion and initial diameter specified in iter_params

        Pseudocode
        ----------
        
        d = initial_guess
        loop until error is below max_error
            Se = calculate endurance limit
            Kf, Kfs = calculate stress concentrations

            new_d = calculate d based on criterion using previously calculated data

            error = |(new_d - old_d)/new_d|   (Percent error of guesses)

        return final d
        
        '''
        self.shaft.d = self.iter_params.d_initial
        MAX_ITER = 100

        self.printer.section(f"#--- Solving for d using {name} ---#", importance_level=importance)

        iteration_print_vals = ""
        

        iter = 0
        self.printer.show(self.shaft.d, label=f"Iter {iter}: d = ", importance_level=importance)          # Printing first iteration
        while True:
            self.shaft.Se = self.get_endurance_limit(importance=importance)                               # Endurance limit calculation with d guess
            self.shaft.Kf, self.shaft.Kfs = self.get_stress_concentrations(importance=importance)         # Fatigue stress concentrations with d guess
            
            new_d = criterion(self.shaft, **kwargs)                                                         # Calculation of new d using criterion

            self.printer.show(new_d, label=f"\nIter {iter+1}: d = ", importance_level=importance)         # Printing iterations

            if np.abs((new_d - self.shaft.d)/new_d) <= self.iter_params.max_error:                          # Exit loop if error is below specified value
                self.shaft.d = new_d
                break

            self.shaft.d = new_d

            if iter > MAX_ITER:                                                 # Raising an error if the answer isn't converging
                raise RuntimeError("d solver max iterations reached")
            
            iter += 1

        if self.printer.importance_cutoff > importance:                                                     # Printing final result
            self.printer.section("#--- Final Results ---#")

        self.printer.show(self.shaft.d, importance_level = 0, label=f"{name}: d = ")

        return self.shaft.d


    def get_endurance_limit(self, importance = 3):
        '''
        Method to calculate the endurance limit based on shaft point data
        '''
        self.printer.section("Endurance Limit", importance+1)

        # Calculating S'e via eq 6-10
        # ---------------------------
        if self.shaft.units == en.units.Imperial:    # kpsi version of the equation
            if self.shaft.material.S_ut <= 200:
                Spe = 0.5 * self.shaft.material.S_ut
            else:
                Spe = 100
        else:                               # MPa version
            if self.shaft.material.S_ut <= 1400:
                Spe = 0.5 * self.shaft.material.S_ut
            else:
                Spe = 700

        self.printer.show(Spe, importance + 1, label="S'e = ")

        # Calculating ka via eq 6-18 and associated table
        # -----------------------------------------------
        T618_a = np.array([
            #Ground, Machined/CD, Hot-Rolled, As-Forged
            [1.21,   2.00,        11.0,       12.7],   # kpsi
            [1.38,   3.04,        38.6,       54.9]    # MPa
        ])
        T618_b = np.array([-0.067, -0.217, -0.650, -0.758])

        a = T618_a[self.shaft.units.value][self.shaft.surface_finish.value]     # Getting a coefficent from table
        b = T618_b[self.shaft.surface_finish.value]                             # b exponent from table
        self.printer.show(a, importance+2, label='a = ')
        self.printer.show(b, importance+2, label='b = ')

        ka = a*self.shaft.material.S_ut**b      # Eq 6-18

        self.printer.show(ka, importance + 1, label="ka = ")

        # Calculating kb via eq 6-19
        # --------------------------
        if self.shaft.units == en.units.Imperial:    # in. part of equation 6-19
            if 0.11 <= self.shaft.d <= 2:
                kb = 0.879*self.shaft.d**(-0.107)
            elif 2 < self.shaft.d <= 10:
                kb = 0.91*self.shaft.d**(-0.157)
        else:                               # mm part of equation 6-19
            if 2.79 <= self.shaft.d <= 51:
                kb = 1.24*self.shaft.d**(-0.107)
            elif 51 <= self.shaft.d <= 254:
                kb = 1.51*self.shaft.d**(-0.157)

        self.printer.show(kb, importance + 1, label="kb = ")
        
        # Calculating kc for combined loads
        # ---------------------------------
        if self.shaft.Ma == 0 and self.shaft.Mm == 0:       # If no bending is present
            kc = 0.59   # Torsion loading factor
        else:
            kc = 1

        self.printer.show(kc, importance + 1, label="kc = ")
        
        # Final calculation of endurance limit
        # ------------------------------------
        Se = ka*kb*kc*Spe

        self.printer.show(Se, importance, label="Se = ")

        return Se

    def get_stress_concentrations(self, importance = 3):
        '''
        Calculate Kf and Kfs using shaft data
        '''
        self.printer.section("Stress Concentrations", importance+1)

        if self.shaft.notch_type == en.NotchType.Nothing:
            self.printer.show(1, label = "No stress concentration, Kf = Kfs = ", importance_level=importance+1)
            self.shaft.Kt = self.shaft.Kts = self.shaft.Kf = self.shaft.Kfs = 1
            return (1, 1)

        def find_Kt_T71(load : en.LoadType, notch : en.NotchType):
            '''Find initial theoretical stress concentrations based on Table 7-1'''
            Table_71 = np.array([
                # Bending, Torsion, Axial
                [ 2.7,     2.2,     3.0],    # Sharp
                [ 1.7,     1.5,     1.9],    # Well Rounded
                [ 2.14,    3.0,     None],   # End-Mill Keyseat
                [ 5.0,     3.0,     5.0]     # Retaining Ring Groove
            ])
            
            return Table_71[notch.value][load.value]
        
        # Find Kt and Kts values from table T7-1
        # --------------------------------------
        self.shaft.Kt = find_Kt_T71(load = en.LoadType.Bending, notch = self.shaft.notch_type)
        self.shaft.Kts = find_Kt_T71(load = en.LoadType.Torsion, notch = self.shaft.notch_type)

        self.printer.show(self.shaft.Kt, label="Kt = ", importance_level=importance+1)
        self.printer.show(self.shaft.Kts, label="Kts = ", importance_level=importance+1)

        # Find r based on stress concentration type and diameter
        # ------------------------------------------------------
        match self.shaft.notch_type:    # Data from table 7-1
            case en.NotchType.Sharp:
                r = self.shaft.d*0.02   # r/d = 0.02
            case en.NotchType.Well_Rounded:
                r = self.shaft.d*0.1    # r/d = 0.1
            case en.NotchType.Keyseat:
                r = self.shaft.d*0.02   # r/d = 0.02
            case en.NotchType.Retaining_Ring:
                r = 0.01    # From assignment

        self.printer.show(r, label="r = ", importance_level=importance+1)

        # Find Neuber factor using r and S_ut
        # -----------------------------------
        S_ut = self.shaft.material.S_ut
        if self.shaft.units == en.units.Imperial:    # kpsi version
            sqrt_a_bending = 0.246 - 3.08e-3*S_ut + 1.51e-5*S_ut**2 - 2.67e-8*S_ut**3
            sqrt_a_torsion = 0.190 - 2.51e-3*S_ut + 1.35e-5*S_ut**2 - 2.67e-8*S_ut**3
        else:                               # MPa version
            sqrt_a_bending = 1.24 - 2.25e-3*S_ut + 1.60e-6*S_ut**2 - 4.11e-10*S_ut**3
            sqrt_a_torsion = 0.958 - 1.83e-3*S_ut + 1.43e-6*S_ut**2 - 4.11e-10*S_ut**3

        self.printer.show(sqrt_a_bending, label="sqrt(a) [bending] = ", importance_level=importance+1)
        self.printer.show(sqrt_a_torsion, label="sqrt(a) [torsion] = ", importance_level=importance+1)

        # Calculate fatigue stress concentrations based on Neuber constants
        # -----------------------------------------------------------------
        def calc_Kf(Kt, sqrt_a):
            return 1 + ((Kt - 1)/(1 + (sqrt_a/np.sqrt(r))))
        
        Kf = calc_Kf(self.shaft.Kt, sqrt_a_bending)
        Kfs = calc_Kf(self.shaft.Kts, sqrt_a_torsion)

        self.printer.show(Kf, label="Kf = ", importance_level=importance)
        self.printer.show(Kfs, label="Kfs = ", importance_level=importance)

        return (Kf, Kfs)
