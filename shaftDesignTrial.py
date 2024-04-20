from src import ShaftDesign as sd

def onePoint():
    shaft = sd.ShaftPointData(
        units = sd.units.Imperial,
        notch_type = sd.NotchType.Keyseat,
        surface_finish=sd.SurfaceFinish.As_Forged,

        material=sd.materials.AISI[1010].HR.MPa,

        Ma=50,
        Mm=0,
        Ta=0,
        Tm=50,

        n = 1.5
    )

    designer = sd.ShaftDesigner(shaft, printer=sd.DataPrinter('.3f', importance_cutoff=1, output_file='output.txt'))

    designer.Goodman(2)

def multPoints():
    L = 5.0

    def ma(x):
        if 0 <= x < L:
            return 2*x
        if L <= x <= 2*L:
            return -2*x + 4*L

    shaft = sd.Shaft(
        units=sd.units.Imperial,
        material=sd.materials.AISI[1010].CD.kpsi,
        surface_finish=sd.SurfaceFinish.Cold_Drawn,

        length=2*L,

        Ma=ma,
        Mm=0,
        Ta=0,
        Tm=10,

        points = {
            'A' : sd.PointProperties(location=1.0, stress_concentration=sd.NotchType.Keyseat, n=1.5),
            'B' : sd.PointProperties(location=9.0, stress_concentration=sd.NotchType.Retaining_Ring, n=1.5)
        }
    )

    analyzer = sd.ShaftAnalyzer(shaft, printer=sd.DataPrinter(format_spec='.3f', importance_cutoff=4, output_file='output.txt'))

    analyzer.Goodman()

multPoints()