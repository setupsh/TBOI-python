def clamp(number, lower, upper):
    return max(lower, min(number, upper))
    # return min(max(max(number, lower), min(number, upper)), upper)

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]

def get_magnitude(v):
    return (v[0] ** 2 + v[1] ** 2) ** 0.5

def get_cos(a, b):
    return dot(a, b) / (get_magnitude(a) * get_magnitude(b))

def get_angle_between(a, b):
    print(get_cos(a, b) ** -1)
    return get_cos(a, b) ** -1