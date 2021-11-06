from numpy import array
from pykicad.pcb import *
from pykicad.module import *

import math
import numpy as np

center_offset_x = 100
center_offset_y = 100

inside_radius = 33
outside_radius = 48
width = outside_radius-inside_radius

phases = 3
loops = 20
steps = 30
loop_angle = 2*math.pi/loops
phase_angle = loop_angle/phases

x_values = []
y_values = []

red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
purple = [255,0,255]

colors = [red,green,blue,purple]
point_colors = []

phase_values = [[],[],[],[]]

for loopnum in range(loops):
    for phasenum in range(phases):
        for idx in range(steps):
            factor = (math.sin(idx/steps*math.pi*2) + 1)/2
            angle = loop_angle*(idx/steps)+loopnum*loop_angle+phasenum*phase_angle
            radial_point_distance = inside_radius + factor * width
            y_value = math.sin(angle) * radial_point_distance + center_offset_x
            x_value = math.cos(angle) * radial_point_distance + center_offset_y

            phase_values[phasenum].append([x_value, y_value])


tx, rx1, rx2 = Net('TX'), Net('RX1'), Net('RX2')

nets=[tx, rx1, rx2]

segments = []

phase_layers = ['F.Cu', 'Inner1.Cu', 'B.Cu']

for phasenum in range(phases):
    for idx in range(len(phase_values[phasenum])-1):
        start = phase_values[phasenum][idx]
        end = phase_values[phasenum][idx+1]
        seg = Segment(start=start, end=end, layer=phase_layers[phasenum], net=nets[phasenum].code)
        segments.append(seg)


layers = [
Layer('F.Cu'),
Layer('Inner1.Cu'),
Layer('Inner2.Cu'),
Layer('B.Cu'),
Layer('Edge.Cuts', type='user')
]

for layer in ['Mask', 'Paste', 'SilkS', 'CrtYd', 'Fab']:
    for side in ['B', 'F']:
        layers.append(Layer('%s.%s' % (side, layer), type='user'))
        nc1 = NetClass('default', trace_width=1, nets=['TX', 'RX1', 'RX2'])

# Create PCB
pcb = Pcb()
pcb.title = 'A title'
pcb.comment1 = 'Comment 1'
pcb.page_type = [200, 200]
pcb.num_nets = 5
pcb.setup = Setup(grid_origin=[10, 10])
pcb.layers = layers
# pcb.modules += [r1, r2]
pcb.net_classes += [nc1]
pcb.nets += nets
pcb.segments += segments
# pcb.vias += [v1]
# pcb.zones += [gndplane_top]

pcb.to_file('project')

#export KISYSMOD=/usr/share/kicad-nightly/footprints/
