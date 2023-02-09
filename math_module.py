def clamp(number, lower, upper):
    return max(lower, min(number, upper))
    # return min(max(max(number, lower), min(number, upper)), upper)