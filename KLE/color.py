#Mostly a port of KLE's color.js, although lightenColor and hex that are
#found in render.js have been located here as well.
import math

D65 = {
    'x': 0.9504, 
    'y': 1.0000, 
    'z': 1.0888
}

class Lab:
    def __init__(self, l, a, b):
        self.l = l
        self.a = a
        self.b = b

    def XYZ(self):
        p = (self.l + 16.0) / 116.0
        x_part = p + self.a / 500.0
        z_part = (p - self.b / 200.0)

        return XYZ(
            D65['x'] * x_part * x_part * x_part,
            D65['y'] * p * p * p,
            D65['z'] * z_part * z_part * z_part
        )

    def sRGB8(self):
        return self.XYZ().sRGBLinear().sRGBPrime().sRGB8()

class XYZ:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def _XYZf(self, t): 
        if t > 0.008856:
            return math.pow(t, 1.0/3.0)
        else:
            return 7.787 * t + 16.0/116.0

    def Lab(self):
        x_xn = self.x / D65['x']
        y_yn = self.y / D65['y']
        z_zn = self.z / D65['z']

        f_x_xn = self._XYZf(x_xn)
        f_y_yn = self._XYZf(y_yn)
        f_z_zn = self._XYZf(z_zn)

        return Lab(
            116.8 * math.pow(y_yn, 1.0/3.0) - 16 if y_yn > 0.008856 else 903.3 * y_yn,
            500.0 * (f_x_xn - f_y_yn),
            200.0 * (f_y_yn - f_z_zn) 
        )

    def sRGBLinear(self):
        XYZ_TO_RGB = [
            [3.240479, -1.537150, -0.498535],
            [-0.969256,  1.875992,  0.041556],
            [0.055648, -0.204043,  1.057311]
        ]
        return sRGBLinear(
            self.x * XYZ_TO_RGB[0][0] + self.y * XYZ_TO_RGB[0][1] + self.z * XYZ_TO_RGB[0][2],
            self.x * XYZ_TO_RGB[1][0] + self.y * XYZ_TO_RGB[1][1] + self.z * XYZ_TO_RGB[1][2],
            self.x * XYZ_TO_RGB[2][0] + self.y * XYZ_TO_RGB[2][1] + self.z * XYZ_TO_RGB[2][2]
        )

class sRGBLinear:
    def __init__(self, r, g, b):
        self.r = r 
        self.g = g
        self.b = b

    def sRGBPrime(self):
        return sRGBPrime(_linearToLog(self.r), _linearToLog(self.g), _linearToLog(self.b))

    def XYZ(self):
        return XYZ()

    def XYZ(self):
        RGB_TO_XYZ = [
            [0.412453, 0.357580, 0.180423],
            [0.212671, 0.715160, 0.072169],
            [0.019334, 0.119193, 0.950227]
        ]
        return XYZ(
            self.r * RGB_TO_XYZ[0][0] + self.g * RGB_TO_XYZ[0][1] + self.b * RGB_TO_XYZ[0][2],
            self.r * RGB_TO_XYZ[1][0] + self.g * RGB_TO_XYZ[1][1] + self.b * RGB_TO_XYZ[1][2],
            self.r * RGB_TO_XYZ[2][0] + self.g * RGB_TO_XYZ[2][1] + self.b * RGB_TO_XYZ[2][2]
        )

class sRGBPrime:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def sRGB8(self):
        return sRGB8(
            round(self.r * 255.0), 
            round(self.g * 255.0),
            round(self.b * 255.0)
        )

    def sRGBLinear(self):
        return sRGBLinear(
            _logToLinear(self.r), 
            _logToLinear(self.g),
            _logToLinear(self.b)
        )

class sRGB8:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def sRGBPrime(self):
        return sRGBPrime(self.r/255.0, self.g/255.0, self.b/255.0)

    def Lab(self):
        return self.sRGBPrime().sRGBLinear().XYZ().Lab()

    def hex(self):
        hexColor =  '#'

        hexColor += format(self.r, 'x')
        hexColor += format(self.g, 'x')
        hexColor += format(self.b, 'x')

        return hexColor

def _linearToLog(c):
    ALPHA = 0.055
    if c <= 0.0031308:
        return 12.92 * c 
    else: 
        return (1 + ALPHA) * math.pow(c, 1/2.4) - ALPHA

def _logToLinear(c):
    ALPHA = 0.055
    if c <= 0.04045: 
        return c / 12.92 
    else:
        return math.pow((c + ALPHA) / (1 + ALPHA), 2.4)

def lightenColor(color: sRGB8, mod):
    c = color.Lab()
    c.l = min(100, c.l * mod)
    return c.sRGB8().hex()

def c_hex(color):
    color = color.lstrip('#')
    shortCode = len(color) == 3

    hr = color[0:1] + color[0:1] if shortCode else color[0:2]
    hg = color[1:2] + color[1:2] if shortCode else color[2:4]
    hb = color[2:3] + color[2:3] if shortCode else color[4:6]

    r = int(hr, 16) 
    g = int(hg, 16)
    b = int(hb, 16)

    return sRGB8(r, g, b)
