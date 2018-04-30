#! /usr/bin/env python3

# Copyright (c) 2014-2015 Felix Knopf <felix.knopf@arcor.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License in the LICENSE.txt for more details.
#
# This part of the library is based on code128.py by Erik Karulf,
# found at https://gist.github.com/ekarulf/701416
# His original copyright and permission notice:
#    Copyright (c) 2010 Erik Karulf <erik@karulf.com>
#
#    Permission to use, copy, modify, and/or distribute this software for any
#    purpose with or without fee is hereby granted, provided that the above
#    copyright notice and this permission notice appear in all copies.
#

try: from PIL import Image, ImageDraw
except ImportError:
    try: import Image, ImageDraw
    except ImportError:
        Image = ImageDraw = None

from code128format import code128_format as _format

def code128_image(data, width=560, height=100, quiet_zone=True):
    thickness = 10
    """encodes 'data' in a code128 barcode and returns an Image object"""
    if (Image is None) or (ImageDraw is None):
        raise ImportError("PIL not found, only SVG output possible")

    barcode_widths = _format(data, thickness)
    _width = sum(barcode_widths)
    x = 0

    if quiet_zone:
        _width += 20 * thickness
        x = 10 * thickness

    # Monochrome Image
    img  = Image.new('1', (_width, height), 1)
    draw = ImageDraw.Draw(img)
    draw_bar = True
    for _width in barcode_widths:
        if draw_bar:
            draw.rectangle(((x, 0), (x + _width - 1, height)), fill=0)
        draw_bar = not draw_bar
        x += _width

    # print(img)
    # print('dimensions: {0}'.format((img.size[0], img.size[1], width, height)))

    return img.resize((width, height), Image.ANTIALIAS)
