from dataclasses import dataclass

#-------------------------------#
#      MATERIALS DATABASE       #
#-------------------------------#
# This file contains material properties from the appendix in the textbook

@dataclass
class Strengths:
    S_ut: float     # Ultimate Strength
    S_y: float      # Yield Strength

@dataclass
class units:
    MPa : Strengths
    kpsi : Strengths

@dataclass
class Processing:
    HR : units
    CD : units
    
# Table A-20
AISI = {
    1006 : Processing(
        HR = units(
            MPa = Strengths(330, 280),
            kpsi = Strengths(48, 41)
        ),
        CD = units(
            MPa = Strengths(330, 280),
            kpsi = Strengths(48, 41)
        )
    ),
    1010 : Processing(
        HR = units(
            MPa = Strengths(320, 180),
            kpsi = Strengths(47, 26)
        ),
        CD = units(
            MPa = Strengths(370, 300),
            kpsi = Strengths(53, 44)
        )
    ),
    1015 : Processing(
        HR = units(
            MPa = Strengths(340, 190),
            kpsi = Strengths(50, 27.5)
        ),
        CD = units(
            MPa = Strengths(390, 320),
            kpsi = Strengths(56, 47)
        )
    ),
    1030 : Processing(
        HR = units(
            MPa = Strengths(470, 260),
            kpsi = Strengths(68, 37.5)
        ),
        CD = units(
            MPa = Strengths(520, 440),
            kpsi = Strengths(76, 64)
        )
    )
}