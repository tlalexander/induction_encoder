from numpy import array
from pykicad.pcb import *
from pykicad.module import *

import math
import numpy as np

center_offset_x = 100
center_offset_y = 100

inside_radius = 33
outside_radius = 47
width = outside_radius-inside_radius

phases = 8
# loops = 20
loops = 10
steps = 30
loop_angle = 2*math.pi/loops
phase_angle = loop_angle/phases
angle_offset = 0-phase_angle/2.5

x_values = []
y_values = []

red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
purple = [255,0,255]

colors = [red,green,blue,purple]
point_colors = []

phase_values = [[],[],[],[]]

tx, rx1, rx2 = Net('TX'), Net('RX1'), Net('RX2')

nets=[rx1, rx1, rx2, rx2, rx1, rx1, rx2, rx2]

segments = []

phase_layers = ['F.Cu', 'Inner1.Cu', 'B.Cu']

via_list = []
last_point = [None, None, None, None, None, None, None, None]

for loopnum in range(loops):
    for phasenum in range(phases):
        for idx in range(steps+1):

            if idx == steps and loopnum!=loops-1:
                # The extra step on the last loop closes a gap created
                # because last_point was none for the very first point.
                continue


            factor = (math.sin(idx/steps*math.pi*2) + 1)/2
            angle = loop_angle*(idx/steps)+loopnum*loop_angle+phasenum*phase_angle + angle_offset
            radial_point_distance = inside_radius + factor * width
            y_value = math.sin(angle) * radial_point_distance + center_offset_x
            x_value = math.cos(angle) * radial_point_distance + center_offset_y
            current_point = [x_value, y_value]

            top_layer = True

            if last_point[phasenum]:
                if idx<=steps/4:
                    top_layer = True
                if idx==int(steps/4) or idx==int(3*steps/4):
                    via_list.append(Via(at=current_point, size=.8, drill=.6, net=nets[phasenum].code))
                if idx>steps/4 and idx < 3*steps/4:
                    top_layer = False
                if idx>3*steps/4:
                    top_layer = True

                if loopnum == int(loops/2)-1 and phasenum>=phases/2:
                    if idx==int(steps/2)+1:
                        via_list.append(Via(at=current_point, size=.8, drill=.6, net=nets[phasenum].code))
                        top_layer = not top_layer

                if loopnum == int(loops/2) and phasenum<phases/2:
                    if idx==0:
                        via_list.append(Via(at=last_point[phasenum], size=.8, drill=.6, net=nets[phasenum].code))
                        top_layer = not top_layer

                layer = 'B.Cu'if top_layer else 'F.Cu'
                segments.append(Segment(start=last_point[phasenum], end=current_point, layer=layer, net=nets[phasenum].code))

            last_point[phasenum] = current_point

            # phase_values[phasenum].append([x_value, y_value])
# print(last_point)
# for phasenum in range(phases):
#     for idx in range(len(phase_values[phasenum])-1):
#         start = phase_values[phasenum][idx]
#         end = phase_values[phasenum][idx+1]
#         seg = Segment(start=start, end=end, layer=phase_layers[phasenum], net=nets[phasenum].code)
#         segments.append(seg)
coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
gndplane_top = Zone(net_name='GND', layer='F.Cu', polygon=coords, clearance=0.3)

layers = [
Layer('F.Cu'),
# Layer('Inner1.Cu'),
# Layer('Inner2.Cu'),
Layer('B.Cu'),
Layer('Edge.Cuts', type='user')
]

for layer in ['Mask', 'Paste', 'SilkS', 'CrtYd', 'Fab']:
    for side in ['B', 'F']:
        layers.append(Layer('%s.%s' % (side, layer), type='user'))
        nc1 = NetClass('default', trace_width=1, nets=['TX', 'RX1', 'RX2'])

# print(via_list)

# Create PCB
pcb = Pcb()
pcb.title = 'A title'
pcb.comment1 = 'Comment 1'
pcb.page_type = [200, 200]
pcb.num_nets = 3
pcb.setup = Setup(grid_origin=[10, 10])
pcb.layers = layers
# pcb.modules += [r1, r2]
pcb.net_classes += [nc1]
pcb.nets += nets
pcb.segments += segments
pcb.vias += via_list
pcb.zones += [gndplane_top]

pcb.to_file('project')

#export KISYSMOD=/usr/share/kicad-nightly/footprints/
