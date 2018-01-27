class fieldCalculation:
    def __init__(self,lengths, user):
        # Lengths is the sum of all lines in m so we create a new array with individual lengths in cm
        difs = [float(t) - float(s) for s, t in zip(lengths, lengths[1:])]
        shortest = sorted(difs)[0]
        # Now we've got the shortest side we can use this te calculate the number of beds
        self.numberOfBeds = (shortest - float(user.row_spacing)/100) / (float(user.row_width)/100 + float(user.row_spacing)/100)
        # And the areable area
        self.areableArea = self.numberOfBeds * (float(user.row_width)/100 * float(user.row_length)/100)
