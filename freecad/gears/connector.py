# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# * This program is free software: you can redistribute it and/or modify    *
# * it under the terms of the GNU General Public License as published by    *
# * the Free Software Foundation, either version 3 of the License, or       *
# * (at your option) any later version.                                     *
# *                                                                         *
# * This program is distributed in the hope that it will be useful,         *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of          *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           *
# * GNU General Public License for more details.                            *
# *                                                                         *
# * You should have received a copy of the GNU General Public License       *
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.   *
# *                                                                         *
# ***************************************************************************

import os
import copy
import numpy as np
import FreeCAD
from pygears import __version__
from .features import InvoluteGear

class ViewProviderGearConnector(object):
    def __init__(self, vobj, icon_fn=None):
        # Set this object to the proxy object of the actual view provider
        vobj.Proxy = self
        dirname = os.path.dirname(__file__)
        self.icon_fn = icon_fn or os.path.join(dirname, "icons", "gearconnector.svg")
            
    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return self.icon_fn

    def claimChildren(self):
        return [self.vobj.Object.master_gear, self.vobj.Object.slave_gear]

    def __getstate__(self):
        return {"icon_fn": self.icon_fn}

    def __setstate__(self, state):
        self.icon_fn = state["icon_fn"]


class GearConnector(object):
    def __init__(self, obj, master_gear, slave_gear):
        obj.addProperty("App::PropertyString", "version", "version", "freecad.gears-version", 1)
        obj.addProperty("App::PropertyLink","master_gear","gear","master gear", 1)
        obj.addProperty("App::PropertyLink","slave_gear","gear","slave gear", 1)
        obj.addProperty("App::PropertyAngle", "angle1", "gear", "angle at which second gear is placed", 0)
        obj.addProperty("App::PropertyAngle", "angle2", "gear", "angle at which second gear is placed", 0)
        obj.version = __version__
        obj.master_gear = master_gear
        obj.slave_gear = slave_gear
        obj.angle1 = 0
        obj.angle2 = 0
        obj.Proxy = self

    def onChanged(self, fp, prop):
        print(fp.master_gear.Proxy)
        if isinstance(fp.master_gear.Proxy, InvoluteGear) and isinstance(fp.slave_gear.Proxy, InvoluteGear):
            fp.master_gear.Placement.Rotation.Angle = np.deg2rad(fp.angle2.Value)
            angle_master = fp.master_gear.Placement.Rotation.Angle
            dw_master = fp.master_gear.dw
            dw_slave = fp.slave_gear.dw
            mat0 = FreeCAD.Matrix()  # unity matrix
            trans = FreeCAD.Vector(dw_master + dw_slave) / 2
            mat0.move(trans)
            rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), fp.angle1).toMatrix()
            angle2 = dw_master / dw_slave * fp.angle1.Value
            angle4 = dw_master / dw_slave * np.rad2deg(angle_master)
            rot2 = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), angle2).toMatrix()
            angle3 = abs(fp.slave_gear.teeth % 2 - 1) * 180. / fp.slave_gear.teeth
            rot3 = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), angle3).toMatrix()
            rot4 = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), -angle4).toMatrix()
            mat1 = rot * mat0 * rot2 * rot3 * rot4
            mat1.move(fp.master_gear.Placement.Base)
            fp.slave_gear.Placement = mat1

            


