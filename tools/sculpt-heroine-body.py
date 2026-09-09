"""Anatomical profile helpers, authored in Python and used by the skinned mesh baker.
Monotone cubic interpolation gives smooth clavicle/waist/hip and limb contours.
"""
import math,numpy as np
from scipy.interpolate import PchipInterpolator
body_x=PchipInterpolator([1.30,1.39,1.50,1.61,1.73,1.84,1.92,1.99],[.224,.236,.194,.162,.189,.227,.222,.191])
body_z=PchipInterpolator([1.30,1.4,1.52,1.65,1.78,1.88,1.99],[.135,.143,.119,.119,.143,.157,.106])
leg_r=PchipInterpolator([0,.11,.25,.43,.51,.62,.76,.9,1],[.098,.12,.121,.085,.065,.081,.089,.061,.047])
arm_r=PchipInterpolator([0,.10,.23,.43,.5,.65,.80,1],[.064,.071,.068,.053,.049,.060,.052,.035])
def sculpt_torso(x,y,z):
 front=max(0,z)/.16
 # Clothed bust and shoulder-blade planes, rather than a rotational cylinder.
 bust=.037*math.exp(-((abs(x)-.105)/.085)**2-((y-1.825)/.105)**2)*front
 sternum=-.008*math.exp(-(x/.035)**2-((y-1.84)/.1)**2)*front
 blade=-.015*math.exp(-((abs(x)-.115)/.075)**2-((y-1.85)/.12)**2) if z<0 else 0
 return [x,y,z+bust+sternum+blade]
