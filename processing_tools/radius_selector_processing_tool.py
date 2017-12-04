# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SamplePlugin
                                 A QGIS plugin
 SamplePlugin
                              -------------------
        begin                : 2017-09-29
        copyright            : (C) 2017 by Viktor Sklencar
        email                : viktor.sklencar@lutraconsulting.co.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'vsklencar'
__date__ = '2017-09-29'
__copyright__ = '(C) 2017 by vsklencar'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from processing.core.Processing import Processing
from radius_selector_provider import SamplePluginProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class RadiusSelectorProcessingTool:

    def __init__(self):
        self.provider = SamplePluginProvider()

    def initGui(self):
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)