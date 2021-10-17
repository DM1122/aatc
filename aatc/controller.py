class AATC:
    def __init__(self):
        return


class Map:
    def __init__(self):
        self.map_radius = 10
        self.strips = [
            LandingStrip(id="A", start=(-0.5, -0.5), end=(-0.5, 0.5)),
            LandingStrip(id="B", start=(0.5, -0.5), end=(0.5, 0.5)),
        ]
