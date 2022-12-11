# Inspired by kb.html from KLE
import serial
import render
import color
import xml.etree.ElementTree as ET
import math

class SvgKeyboard(render.GfxKeyboard):
    def getByteArray(self):
        renderParms = []

        # Can't draw keys until keyboard is drawn, can't draw the keyboard until
        #  the size of all keys is figured out. First figure out key size/pos
        for key_i, key in enumerate(self.keys):
            renderParms.append({ 
                'key': key, 
                'parms': self.getRenderParms(key, 'DCS') #figures out size/pos
            })
        # Draw the keyboard big enough to fit all keys.
        self.__drawKeyboardBackground(renderParms)
        # Draw all the keys on top of the keyboard.
        for keyAndParms in renderParms:
            self.__drawKey(keyAndParms['key'], keyAndParms['parms'])

        #Pretty print
        ET.indent(self.root, space = '    ')
        return ET.tostring(self.root)

    def __getSizeForKeys(self, renderParms):
        widestX = 0
        highestY = 0
        for keyAndParms in renderParms:
            parms = keyAndParms['parms']
            widestX = max([widestX, parms['bbox']['x'], parms['bbox']['x2']])
            highestY = max([highestY, parms['bbox']['y'], parms['bbox']['y2']])

        return {
            'x': widestX,
            'y': highestY
        }

    def __drawKeyboardBackground(self, renderParms):
        sizeForKeys = self.__getSizeForKeys(renderParms)

        keyboardWidth = sizeForKeys['x'] + self.kbdPadding * 2 
        keyboardHeight = sizeForKeys['y'] + self.kbdPadding * 2

        viewBoxWidth = keyboardWidth + self.kbdMargin * 2 
        viewBoxHeight = keyboardHeight + self.kbdMargin * 2

        #print(renderParms)
        self.root = ET.Element(
            'svg', version = '1.1', xmlns = 'http://www.w3.org/2000/svg', 
            width = str(viewBoxWidth), height = str(viewBoxHeight),
            viewBox = '0 0 {} {}'.format(str(viewBoxWidth), str(viewBoxHeight))
        )
        self.root.set('font-family', 'Verdana, sans-serif')
        self.__addStyle()

        self.keyboardGrouping = ET.SubElement(
            self.root, 'g', 
            transform = 'translate({},{})'.format(self.kbdMargin, self.kbdMargin),
            id = 'kbdMargin'
        )
        svgKeyboard = ET.SubElement(
            self.keyboardGrouping, 'rect', 
            x = '0', y = '0',
            width = str(keyboardWidth), height = str(keyboardHeight),
            fill = self.meta.backcolor, id = 'keyboard'
        )

        self.keyGrouping = ET.SubElement(
            self.keyboardGrouping, 'g',
            transform = 'translate({},{})'.format(self.kbdPadding, self.kbdPadding),
            id = 'kbdPadding'
        )

    def __addStyle(self):
        style = ET.SubElement(self.root, 'style', type = 'text/css')
        
        style.text = '\n    .keycap .border { stroke: black; stroke-width: '
        #FIXME technically should be sizes.strokewidth * 2, but that's per
        #key and this is a global style?
        style.text += "0.4"
        style.text += '}\n'

        style.text += '    .keycap .inner.border { stroke: rgba(0,0,0,.1) }\n'
    def __drawLabels(self, key, parms, grouping):
        # Labels are rather illogical but consider the ASCII square below
        # to be keycap and the numbers are which index should go where
        # +----------+
        # |0    8   2|
        # |6    9   7|
        # |1   10   3|
        # +----------+
        # 4    11   5 <=== These indexes go on the bottom bevel
        xHalfKeyCap = parms['capwidth'] * 0.5
        yHalfKeyCap = parms['capheight'] * 0.5
        yOnBottomBevel = parms['innercapheight']
        sizes = self.getUnitSizes(key.profile)

        for i, label in enumerate(key.labels):
            if label != None:
                xOffset = sizes.bevelMargin
                yOffset = sizes.bevelOffsetTop

                textColor = key.textColor[i] or key.default.textColor
                textSize = key.textColor[i] or key.default.textSize

                xOffset += textSize * 0.5
                yOffset += textSize * 0.5

                if i == 4:
                    yOffset += parms['innercapheight']
                if i == 6: 
                    yOffset += parms['innercapheight'] - (textSize * 0.5)
                elif i == 0:
                    yOffset += textSize
                    
                textOnKey = ET.SubElement(
                    grouping, 'text',
                    x=str(parms['rect']['x'] + xOffset),
                    y=str(parms['rect']['y'] + yOffset),
                    fill = textColor
                )
                textOnKey.set('font-size', str(textSize))
                textOnKey.text = label

    def __drawKey(self, key, parms):
        grouping = ET.SubElement(self.keyGrouping, 'g')
        if parms['origin_x'] != 0:
            grouping.set('transform', 'rotate({} {} {})'.format(
                str(key.rotation_angle),
                str(parms['origin_x']),
                str(parms['origin_y'])
            ))
        if(key.ghost):
            grouping.set('class', 'ghosted')
        grouping.set('class', 'keycap')

        self.__drawKeyOuter(key, parms, grouping, 'outer border')
        self.__drawKeyOuter(key, parms, grouping)
        self.__drawKeyInner(key, parms, grouping, 'inner border')
        self.__drawKeyInner(key, parms, grouping)
        self.__drawLabels(key, parms, grouping)

    def __drawKeyOuter(self, key, parms, grouping, classes = None):
        sizes = self.getUnitSizes(key.profile)
        outerBorder = ET.SubElement(grouping, 'rect', 
            x = str(parms['outercapx'] + sizes.strokeWidth),
            y = str(parms['outercapy'] + sizes.strokeWidth),
            width = str(parms['outercapwidth'] - (sizes.strokeWidth * 2)),
            height = str(parms['outercapheight']- (sizes.strokeWidth * 2)),
            rx = str(sizes.roundOuter),
            fill = parms['darkColor']
        )
        if classes != None: outerBorder.set('class', classes)

        if parms['jShaped']:
            outerBorder2 = ET.SubElement(grouping, 'rect', 
                x = str(parms['outercapx2'] + sizes.strokeWidth),
                y = str(parms['outercapy2'] + sizes.strokeWidth),
                width = str(parms['outercapwidth2'] - (sizes.strokeWidth * 2)),
                height = str(parms['outercapheight2']- (sizes.strokeWidth * 2)),
                rx = str(self.unitSizes['FLAT']['roundOuter']),
                fill = parms['darkColor']
            )
            if classes != None: outerBorder2.set('class', classes)

    def __drawKeyInner(self, key, parms, grouping, classes = None):
        sizes = self.getUnitSizes(key.profile)
        innerBorder = ET.SubElement(grouping, 'rect', 
            x = str(parms['innercapx'] + sizes.strokeWidth),
            y = str(parms['innercapy'] + sizes.strokeWidth),
            width = str(parms['innercapwidth'] - (sizes.strokeWidth * 2)),
            height = str(parms['innercapheight'] - (sizes.strokeWidth * 2)),
            rx = str(sizes.roundOuter),
            fill = parms['lightColor']
        )
        if classes != None: innerBorder.set('class', classes)
        
        if parms['jShaped'] and not key.stepped:
            innerBorder2 = ET.SubElement(grouping, 'rect', 
                x = str(parms['innercapx2'] + sizes.strokeWidth),
                y = str(parms['innercapy2'] + sizes.strokeWidth),
                width = str(parms['innercapwidth2'] - (sizes.strokeWidth * 2)),
                height = str(parms['innercapheight2']- (sizes.strokeWidth * 2)),
                rx = str(self.unitSizes['FLAT']['roundOuter']),
                fill = parms['lightColor']
            )
            if classes != None: innerBorder2.set('class', classes)

    def __string__(self):
        return self.getByteArray().decode("utf-8")