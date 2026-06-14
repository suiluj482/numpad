from build123d import *
from ocp_vscode import *
from math import sqrt, sin, cos, radians

# Keys
key = 14
key_spacing = 19.05
key_space = key_spacing - key
key_height = 15 
key_depth = 9

# Layout
keys_dim = (5,4) # cols, rows
keys_size = tuple(n * key_spacing for n in keys_dim)

# Technical parts
usb = (9, 3.5)
xiao = (21.4, 18, 1.4)
xiao_height = 3.1
xiao_usb_indent = 10 # 6.1
xiao_usb_length = 12 # 8
xiao_usb_height = 1.4 + usb[1]
battery = (53, 21, 10)

### arrangement:
# ------------------
# | xiao | battery |
# ------------------
# |                |
# |     keys       |
# |                |
# ------------------

# General
wall = 2
walls = (1,1,1)
radius = 1

with BuildPart() as part:
    # key box

    inner = (*keys_size, key_depth)
    outer = (inner[0] + 2*walls[0], inner[1] + 2*walls[1], inner[2] + walls[2])
    with Locations((0, 0, walls[2] / 2)):
        Box(*outer)
    # with Locations((0, 0, -walls[2] / 2)):
    Box(*inner, mode=Mode.SUBTRACT)

    # control box
    cheight = 5
    cinner = (inner[0], xiao[0], inner[2] + cheight)
    couter = (cinner[0] + 2*walls[0], cinner[1] + 2*walls[1], cinner[2] + walls[2])
    cinner = (cinner[0] - 6, cinner[1], cinner[2])
    with Locations((0,outer[1]/2 + couter[1]/2, couter[2]/2 - outer[2]/2 +(walls[2])/2)):
        Box(*couter)
        with Locations((0,0,-(walls[2]+1)/2)):
            Box(cinner[0], cinner[1], cinner[2] - 1, mode=Mode.SUBTRACT)
    
    # round corners
    fillet(part.edges().filter_by(Axis.Z), radius) # round sides
    fillet(part.edges().sort_by(Axis.Z)[-4:], radius) # round ctops

    edges_at_z = [
        e for e in part.edges()
        if e.center().Z == (outer[2] + walls[2])/2
        and e.center().Y < 10
        and e.length > 70
    ]
    # print([(e.center().X, e.center().Y, e.center().Z, e.length) for e in edges_at_z])
    fillet(edges_at_z, radius) # round ctops

    # screw holes
    footprint = (outer[0], outer[1] + couter[1])
    trueMid = (0, couter[1]/2, 0)
    screwLength = 6
    screwDiameter = 2.2
    with Locations(trueMid):
        for x in (-1, 1):
            for y in (-1, 1):
                with Locations((x*(footprint[0]/2 - wall), y*(footprint[1]/2 - wall), -inner[2]/2 + screwLength/2)):
                    Cylinder(radius=wall, height=screwLength)
                    Cylinder(radius=screwDiameter/2, height=screwLength, mode=Mode.SUBTRACT)

    # connect boxes
    # with Locations((0, outer[1]/2 - 1, 0)): 
    #     # battery
    #     Box(inner[0], 2*walls[1], inner[2], mode=Mode.SUBTRACT)
    # with Locations((-inner[0]/4, outer[1]/2, 0)):
    #     # rest
    #     Box(inner[0]/2, 2*walls[1] + 2, inner[2], mode=Mode.SUBTRACT)
    battery_cable_hole = 3
    with Locations((cinner[0]/2 - battery[0] + battery_cable_hole/2, outer[1]/2, 0)):
        # rest
        Box(battery_cable_hole, 2*walls[1] + 2, inner[2], mode=Mode.SUBTRACT)
    power_hole = key - 1
    with Locations((-key_spacing+1/2, outer[1]/2,0)):
        Box(power_hole, 2*walls[1] + 2, inner[2], mode=Mode.SUBTRACT)
    xiao_hole = key
    with Locations((-key_spacing * 2, outer[1]/2, 0)):
        Box(xiao_hole, 2*walls[1] + 2, inner[2], mode=Mode.SUBTRACT)


    # key holes
    with BuildSketch() as sketch:
        for col in range(keys_dim[0]):
            for row in range(keys_dim[1]):
                x = col * key_spacing
                y = row * key_spacing

                with Locations((x - keys_size[0]/2 + key_spacing/2, y - keys_size[1]/2 + key_spacing/2)):
                    Rectangle(key, key)
    extrude(sketch.sketch, amount=20, mode=Mode.SUBTRACT)
    # key supports
    key_space_radius = sqrt(key_space*key_space/2)

    for col in range(1,keys_dim[0]):
        for row in range(1,keys_dim[1]):
            x = col * key_spacing
            y = row * key_spacing
            support_radius = 2
            key_space_radius = sqrt(key_space*key_space/2)
            with Locations((-inner[0]/2 + x, -inner[1]/2 + y, inner[2]/2-1/2)):
                Box(2*key_space_radius, 2*key_space_radius, 1, rotation=Rotation(0, 0, 45))
                Box(2*key_space_radius-1, 2*key_space_radius-1, 1, rotation=Rotation(0, 0, 45), mode=Mode.SUBTRACT)
    
    for row in range(1,keys_dim[1] +1):
        y = row * key_spacing
        with Locations((0, -inner[1]/2 + y, inner[2]/2 - 1.5)):
            Box(inner[0], 1/2, 3)
            if (row < keys_dim[1]):
                for x in (-1, 1):
                    with Locations((0, x * (key_space-1.5)/2, 3/4 + 0.5)):
                        Box(inner[0], 1.5, 1/2)
    for i in (-1, 1):
        with Locations((0, i * (inner[1] -key_space +1.5)/2, inner[2]/2 - 1 + 3/4)):
            Box(inner[0], 1.5, 1/2)
        for col in range(keys_dim[0]):
            x = col * key_spacing
            for j in (-1,1):
                with Locations((j*(-inner[0]/2 + x), i * ((inner[1] - key_space)/2), inner[2]/2 - 1/2)):
                    with Locations((j*key_space/2  ,0,0)):
                       Box( 1/2, key_space_radius *2, 1, rotation=(0,0,i*j*135))
    
    for col in range(1,keys_dim[0]):
        x = col * key_spacing
        with Locations((-inner[0]/2 + x, 1/2, inner[2]/2 - 1.5)):
            Box(1/2, inner[1] + 1, 3)
            for x in (-1, 1):
                with Locations((x * (key_space-1.5)/2, 0, 3/4 + 0.5)):
                    Box(1.5, inner[1]+1, 1/2)
    for i in (-1, 1):
        with Locations((i * (inner[0] -key_space +1.5)/2, 0, inner[2]/2 - 1 + 3/4)):
            Box(1.5, inner[1]+1, 1/2)
        for row in range(keys_dim[1]):
            y = row * key_spacing
            for j in (-1,1):
                with Locations((i * ((inner[0] - key_space)/2), j*(-inner[1]/2 + y), inner[2]/2 - 1/2)):
                    with Locations((0,j*key_space/2,0)):
                       Box(key_space_radius *2, 1/2, 1, rotation=(0,0,i*j*45))
        
    for col in range(1,keys_dim[0]):
        for row in range(1,keys_dim[1]):
            x = col * key_spacing
            y = row * key_spacing
            support_radius = screwDiameter/2 + 1 # 2
            with Locations((-inner[0]/2 + x, -inner[1]/2 + y, 0)):
                Cylinder(radius=support_radius, height=inner[2])
                Cylinder(radius=support_radius-1, height=inner[2], mode=Mode.SUBTRACT)

    # for col in range(1,3):
    #     x = col * key_spacing
    #     with Locations((-inner[0]/2 + x, inner[1]/2, 0)):
    #         Box(1, 1, inner[2])

    # control box details
    with Locations((0,outer[1]/2 + couter[1]/2, cinner[2]/2 - inner[2]/2)):
        battery_compartment = battery[0]
        xiao_compartment = xiao[1]
        compartment_wall = 1

        # battery_compartment
        with Locations((cinner[0]/2 - battery_compartment - compartment_wall/2, 0, 0)):
            # side wall (power switch)
            Box(compartment_wall, cinner[1], cinner[2])
        with Locations((cinner[0]/2 - battery_compartment/2, -1/2, -1)):
            Box(battery[0], cinner[1] -1, cinner[2]-1, mode=Mode.SUBTRACT)
        with Locations((cinner[0]/2 - battery_compartment/2, cinner[1]/2 - 1/2, 0)):
            # top wall, make outer thicker
            Box(battery[0], 1, cinner[2])
        # with Locations((cinner[0]/2 - battery_compartment/2, -cinner[1]/2, 0)):
        #     # top wall, make outer thicker
        #     Box(battery[0], 1, cinner[2])
        battery_num_beams = 40
        for i in range(battery_num_beams):
            x = (i + 1) * battery[0] / (battery_num_beams + 1)
            with Locations((cinner[0]/2 - x, 0, (cinner[2] -1/2)/2 -1)):
                Box(1/2, cinner[1], 1/2)

        cinner_offset = 3
        cinnert = (cinner[0] - battery[0] - 1,cinner[1],cinner[2]-cinner_offset)

        cinnert_r = cinner[0]/2 - battery[0] - 1
        with Locations((-(battery[0]+1)/2, 0, cinner[2]/2 - (cinner_offset - 1/2)/2)):
            Box(cinnert[0], cinnert[1], cinner_offset-1)
        cinnert_beam_width = 1
        for i in range(int(cinnert[1]/cinnert_beam_width)):
            y = i * cinnert_beam_width
            with Locations((-(battery[0]+1)/2,-cinnert[1]/2 + y,cinner[2]/2 - cinner_offset + 1/4)):
                Box(cinnert[0], cinnert_beam_width/2, 1/2)
        
        # power switch
        # p = (8.6, 3.8, 3.6)
        # p_thing = (3.8, 4, 1.6)
        p = (8.8, 4, 3.8)
        p_thing = (3.8, 4, 1.8)
        p_r = cinner[0]/2 - battery[0] - 1
        p_l = -cinner[0]/2 + xiao[1] + 1
        p_s = p_r - p_l
        print(p_s)
        with Locations((p_r - p_s/2, cinner[1]/2, 0)):
            wall_additional_thickness = p_thing[1] -walls[1]-2
            with Locations((0, -wall_additional_thickness/2, 0)):
                Box(p_s+2, wall_additional_thickness, cinner[2])
            with Locations((0, 1+ walls[1]-p_thing[1]/2, cinner[2]/2 - p[2]/2 - cinner_offset)):
                Box(*p_thing, mode=Mode.SUBTRACT)
            for x in (-1, 1):
                tmp = ((p_s-p[0])/2, p_thing[1])
                with Locations((x * (p_s-tmp[0])/2, -wall_additional_thickness-tmp[1]/2, 0)):
                    Box(tmp[0], tmp[1], cinner[2])
                with Locations((x * (p_s-tmp[0])/2, -wall_additional_thickness-tmp[1] -1.5 -1.5/2, 0)):
                    Box(tmp[0], 1.5, cinner[2])
                # p_hole_dif = 15
                # p_hole_height = 2
                # p_offset = p_thing[1] - wall - 1
                # with Locations((x * 14/2,-p_offset/2, 0)):
                #     Box(5, p_offset, 4)
                #     with Locations((0,-p_hole_height/2 -p_offset/2,0)):
                #         with Locations(Plane.XZ):
                #             Cylinder(radius=1, height=p_hole_height)

        # xiao
        xiao_hold_height = cheight + cinner_offset + 2
        with Locations((-cinner[0]/2 + xiao[1] + 1/2, 0, cinner[2]/2 - xiao_hold_height/2)):
            # side seperator
            Box(1, xiao[0], xiao_hold_height)
        xiao_tolerance = 0.4
        with Locations((-cinner[0]/2 + xiao[1]/2, cinner[1]/2, cinner[2]/2 - usb[1]/2 - cinner_offset - xiao_tolerance)):
            # usb
            Box(usb[0], 5, usb[1], mode=Mode.SUBTRACT)
        # with Locations((-cinner[0]/2 + xiao[1]/2, -xiao_usb_indent/2, cinner[2]/2 - (usb[1] - xiao_height)/2)):
        #     Box(xiao[1], xiao[0] - xiao_usb_indent, usb[1] - xiao_height)
        with Locations((-cinner[0]/2 + xiao[1]/2 - 2.5, -cinner[1]/2 -1/4, -cinner[2]/2 + inner[2] - (cinner_offset + xiao_tolerance)/2)):
            Box(xiao[1] - 6, 1/2, cinner_offset + xiao_tolerance)
            with Locations((0,1/2,-cinner_offset/2 - 1)):
                Wedge(xiao[1]-6, 1.5, 2, 0,2,xiao[1]-6,2)
            with Locations((0,0,-cinner_offset/2 -1.5)):
                Box(xiao[1], 1/2, 1/2)
            #     with BuildSketch(Plane.YZ):
            #         with Locations((0,0)):
            #             # Trapezoid: ramp on top, vertical/undercut back face
            #             Polygon([
            #                 (0, 0),
            #                 (2,0),
            #                 (0,2),
            #                 # (hook_height / tan(radians(lock_angle)), hook_height),
            #                 # (-hook_height / tan(radians(ramp_angle)), hook_height),
            #                 (0, 0),
            #             ], align=None)
            #     extrude(amount=xiao[1]-6)
                # with Locations(Plane.YZ):
                #     with BuildSketch() as sketch:
                #         with BuildLine() as l:
                #             Polyline((0,0), (2,0), (0,2),)
                #         make_face()
                #     extrude(sketch.sketch, amount=xiao[1]-6)


    print(cinner[0])
    print(battery[0] + xiao[1])
    print((xiao_compartment, compartment_wall, battery_compartment))

with BuildPart() as base:
    with Locations(trueMid):
        Box(outer[0], outer[1] + couter[1], 1.5)   
        fillet(base.edges().filter_by(Axis.Z), radius) # round sides    

        for x in (-1, 1):
            for y in (-1, 1):
                with Locations((x*(footprint[0]/2 - wall), y*(footprint[1]/2 - wall), 0)):
                    Cylinder(radius=screwDiameter/2, height=100, mode=Mode.SUBTRACT)

with BuildPart() as power_plate:
    Box(p_s -1,6,1.3)

with BuildPart() as battery_demo:
    with Locations((cinner[0]/2 - battery[0]/2, (outer[1] + couter[1])/2, (cinner[2] - battery[2])/2)):
        Box(*battery)

with BuildPart() as xiao_demo:
    with Locations((-cinner[0]/2 + xiao[1]/2, (outer[1] + couter[1])/2, (cinner[2] - xiao_usb_height)/2)):
        Box(xiao[1], xiao[0], xiao[2])
        with Locations((0,0,xiao_height/2)):
            Box(xiao[1] -1, xiao[0] -1, xiao_height)
        with Locations((0,xiao[0]/2 - xiao_usb_indent/2 + (xiao_usb_length - xiao_usb_indent)/2,usb[1]/2 + xiao[2]/2)):
            Box(usb[0], xiao_usb_length, usb[1])

export_step(part.part, "src/res/numpad.step")
export_step(base.part, "src/res/numpad_base.step")
export_step(power_plate.part, "src/res/numpad_power_plate.step")

export_stl(part.part, "src/res/numpad.stl")
export_stl(base.part, "src/res/numpad_base.stl")
export_stl(power_plate.part, "src/res/numpad_power_plate.stl")

base_preview = base.part.translate((0, 0, -20))
show_object(part.part)
# show_object(base_preview)
# show_object(battery_demo.part, options={"color": (255, 0, 0), "alpha": 0.5})
# show_object(xiao_demo.part, options={"color": (255, 0, 0), "alpha": 0.5})

print(footprint)