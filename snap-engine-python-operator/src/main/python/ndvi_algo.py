import numpy


class NdviAlgo:

    def __init__(self, low_threshold, high_threshold):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def compute_ndvi(self, lower_data, upper_data):
        ndvi = (upper_data - lower_data) / (upper_data + lower_data)
        return ndvi

    def compute_flags(self, ndvi):
        ndvi_low = ndvi < self.low_threshold
        ndvi_high = ndvi > self.high_threshold
        ndvi_neg = ndvi < 0.0
        ndvi_pos = ndvi >= 0.0
        ndvi_flags = ((ndvi_pos << 3) + (ndvi_neg << 2) + (ndvi_high << 1) + ndvi_low).astype(numpy.uint8)
        return ndvi_flags

