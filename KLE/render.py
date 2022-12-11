# Mostly a port of KLE's render.js 
# https://github.com/ijprest/keyboard-layout-editor/blob/master/render.js
# the color function got moved to the color module compared to render.js
import serial
import math
import color
from types import SimpleNamespace


def getProfile(key):
    None

class Matrix():
    def __init__(self, a=1, b=0, c=0, d=1, e=0, f=0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def mult(self, Y):
        return Matrix(
            self.a*Y.a + self.c*Y.b, self.b*Y.a + self.d*Y.b,
            self.a*Y.c + self.c*Y.d, self.b*Y.c + self.d*Y.d,
            self.a*Y.e + self.c*Y.f + self.e,
            self.b*Y.e + self.d*Y.f + self.f)

    def transformPt(self, pt):
        return {
            'x': (self.a*pt['x'] + self.c*pt['y'] + self.e),
            'y': (self.b*pt['x'] + self.d*pt['y'] + self.f)
        }

    def transMatrix(x, y):
        return Matrix(1, 0, 0, 1, x, y)

    def rotMatrix(angleInDegrees):
        angleInRad = (angleInDegrees*math.pi/180.0)
        cos = math.cos(angleInRad)
        sin = math.sin(angleInRad)
        return Matrix(cos, sin, -sin, cos, 0, 0)

# Some predefined sizes for our caps:
# - unit == size of 1 unit, e.g., 0.75", or 19.05mm is standard
# - keySpacing == distance from edge of unit-square to keycap, e.g., (0.75" - 0.715")/2 (for DCS)
# - bevelMargin == distance from edge of keycap(at bottom) to edge of keycap(at top), e.g., (0.715" - 0.470")/2 (for DCS)
# - padding == distance between text & edge of keycap
# - strokeWidth == thickness of the outline strokes
# - roundInner/roundOuter == corner roundness for inner/outer borders
#
# Simplified compared to render.js to contain just the mm sizes rather than pixel sizes as well
#
class UnitSizes:
    def __init__(
            self, profile, keySpacing, 
            bevelMargin, bevelOffsetTop, bevelOffsetBottom,
            padding, roundOuter, roundInner,
            
            unit = 19.05, strokeWidth = 0.20,
        ):
        self.profile = profile
        self.keySpacing = keySpacing
        self.bevelMargin = bevelMargin
        self.bevelOffsetTop = bevelOffsetTop
        self.bevelOffsetBottom = bevelOffsetBottom
        self.padding = padding
        self.roundOuter = roundOuter
        self.roundInner = roundInner

        self.unit = unit
        self.strokeWidth = strokeWidth

class GfxKeyboard(serial.Keyboard):
    kbdMargin = 5
    kbdPadding = 3

    unitSizes = SimpleNamespace(
        DCS = UnitSizes(
            profile = 'DCS', keySpacing = 0.4445, 
            bevelMargin = 3.1115, bevelOffsetTop = 3, bevelOffsetBottom = 3, 
            padding = 0, roundOuter = 1.0, roundInner = 2.0
        ),
        DSA = UnitSizes(
            profile = "DSA", keySpacing = 0.4445, 
            bevelMargin = 3.1115, bevelOffsetTop = 0, bevelOffsetBottom = 0,
            padding = 0, roundOuter = 1.0, roundInner = 2.0
        ),
        SA = UnitSizes(
            profile = "SA", keySpacing = 0.4445,
            bevelMargin = 3.1115, bevelOffsetTop = 2, bevelOffsetBottom = 2,
            padding = 0, roundOuter = 1.0, roundInner = 2.0
        ),
        CHICKLET = UnitSizes(
            profile = "CHICKLET", keySpacing = 0.4445, 
            bevelMargin = 3.1115, bevelOffsetTop = 0, bevelOffsetBottom = 2,
            padding = 0, roundOuter = 1.0, roundInner = 2.0 
        ),
        FLAT = UnitSizes(
            profile = "FLAT", keySpacing = 0.4445, 
            bevelMargin = 3.1115, bevelOffsetTop = 0, bevelOffsetBottom = 0,
            padding = 0, roundOuter = 1.0, roundInner = 2.0 
        )
    )

    #Type hinting for clarity and IDE autocomplete
    def getUnitSizes(self, profile: str) -> UnitSizes:
        if profile == '':
            profile = 'DCS'
        return getattr(self.unitSizes, profile)

    def getRenderParms(self, key, profile: str):
        sizes = self.getUnitSizes(profile)

        parms = {}
        parms['jShaped'] = key.width != key.width2 or key.height != key.height2 or key.x2 or key.y2
        # I don't know where to place the stabilizers / switch position for 
        # irregular shaped keys so these are unsupported for now.
        if parms['jShaped']: 
            self.hasUnsupportedKey = True

        # Overall dimensions of the unit square(s)  that the cap occupies
        parms['capwidth'] = sizes.unit * key.width
        parms['capheight'] = sizes.unit * key.height
        parms['capx'] = sizes.unit * key.x
        parms['capy'] = sizes.unit * key.y
        if parms['jShaped']:
            parms['capwidth2'] = sizes.unit * key.width2
            parms['capheight2'] = sizes.unit * key.height2
            parms['capx2'] = sizes.unit * (key.x + key.x2)
            parms['capy2'] = sizes.unit * (key.y + key.y2)

        # Dimensions of the outer part of the cap
        parms['outercapwidth'] = parms['capwidth'] - sizes.keySpacing
        parms['outercapheight'] = parms['capheight'] - sizes.keySpacing
        parms['outercapx'] = parms['capx'] + sizes.keySpacing
        parms['outercapy'] = parms['capy'] + sizes.keySpacing
        
        if parms['jShaped']:
            parms['outercapy2'] = parms['capy2'] + sizes.keyspacing
            parms['outercapx2'] = parms['capx2'] + sizes.keyspacing
            parms['outercapwidth2'] = parms['capwidth2'] - sizes.keyspacing * 2
            parms['outercapheight2'] = parms['capheight2'] - sizes.keyspacing * 2

        # Dimensions of the top of the cap
        parms['innercapwidth'] = parms['outercapwidth'] - sizes.bevelMargin * 2
        parms['innercapheight'] = parms['outercapheight'] - sizes.bevelMargin * 2 - (sizes.bevelOffsetBottom - sizes.bevelOffsetTop)
        parms['innercapx'] = parms['outercapx'] + sizes.bevelMargin
        parms['innercapy'] = parms['outercapy'] + sizes.bevelMargin - sizes.bevelOffsetTop
        if parms['jShaped']:
            parms['innercapwidth2'] = parms['outercapwidth2'] - bevelMargin * 2
            parms['innercapheight2'] = parms['outercapheight2'] - bevelMargin * 2
            parms['innercapx2'] = parms['outercapx2'] + sizes.bevelMargin
            parms['innercapy2'] = parms['outercapy2'] + sizes.bevelMargin - sizes.bevelOffsetTop

        # Dimensions of the text part of the cap
        parms['textcapwidth'] = parms['innercapwidth'] - sizes.padding * 2
        parms['textcapheight'] = parms['innercapheight'] - sizes.padding * 2
        parms['textcapx'] = parms['innercapx'] + sizes.padding
        parms['textcapy'] = parms['innercapy'] + sizes.padding

        parms['darkColor'] = key.color
        parms['lightColor'] = color.lightenColor(color.c_hex(key.color), 1.2)

        # Rotation matrix about the origin
        parms['origin_x'] = sizes.unit * key.rotation_x
        parms['origin_y'] = sizes.unit * key.rotation_y
        
        mat = Matrix.transMatrix(parms['origin_x'], parms['origin_y']).mult(
            Matrix.rotMatrix(key.rotation_angle)
        ).mult(Matrix.transMatrix(-parms['origin_x'], -parms['origin_y']))

        # Construct the *eight* corner points, transform them, and determine the transformed bbox
        parms['rect'] = {
            'x': parms['capx'], 'y': parms['capy'], 'w': parms['capwidth'], 'h': parms['capheight'],
            'x2': parms['capx']+parms['capwidth'], 'y2': parms['capy']+parms['capheight']
        }
        parms['rect2'] = {
            'x': parms['capx2'], 'y': parms['capy2'], 'w': parms['capwidth2'], 'h': parms['capheight2'],
            'x2': parms['capx2'] + parms['capwidth2'], 'y2': parms['capy2']+parms['capheight2']
        } if parms['jShaped'] else parms['rect']
        parms['bbox'] = {
            "x": 99999999, "y": 99999999,
            "x2": -99999999, "y2": -99999999
        }
        corners = [
            {'x': parms['rect']['x'], 'y': parms['rect']['y']},
            {'x': parms['rect']['x'], 'y': parms['rect']['y2']},
            {'x': parms['rect']['x2'], 'y': parms['rect']['y']},
            {'x': parms['rect']['x2'], 'y': parms['rect']['y2']}
        ]
        if parms['jShaped']:
            {'x': parms['rect2']['x'], 'y': parms['rect2']['y']},
            {'x': parms['rect2']['x'], 'y': parms['rect2']['y2']},
            {'x': parms['rect2']['x2'], 'y': parms['rect2']['y']},
            {'x': parms['rect2']['x2'], 'y': parms['rect2']['y2']}

        for i, corner in enumerate(corners):
            corners[i] = mat.transformPt(corners[i])
            parms['bbox']['x'] = min(parms['bbox']['x'], corners[i]['x'])
            parms['bbox']['y'] = min(parms['bbox']['y'], corners[i]['y'])
            parms['bbox']['x2'] = max(parms['bbox']['x2'], corners[i]['x'])
            parms['bbox']['y2'] = max(parms['bbox']['y2'], corners[i]['y'])

        return parms
