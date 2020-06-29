# Synth Panels Designer - Free Inkscape extension to draw musical instruments user interfaces
# Copyright (C) 2020 Francesco Mulassano

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/python

import sys

import inkex
import argparse
import os
from inkex.elements import ShapeElement

from lxml import etree
from inkex.elements import Circle, PathElement, Rectangle, load_svg, Group, TextElement
from math import *

options = argparse.ArgumentParser(description='Panel parameters')

Orange = '#f6921e'
Blue =   '#0000FF'
White =  '#FFFFFF'

lasercut_width = '0.01mm'

class SynthPanelEffect(inkex.Effect):

    def add_arguments(self, pars):
        #Parts
        pars.add_argument('--part', type=int, default=1, help='Select which part you want to draw')

        #Panel standards
        pars.add_argument('--panel_type', default='e3u', help='Panel type')
        pars.add_argument('--panel_name', default='Panel', help='Panel name')
        pars.add_argument('--eurorack_panel_hp', type=int, default=1, help='Panel HP?')
        pars.add_argument('--api_panel_units', type=int, default=1, help='API Units?')
        pars.add_argument('--moog_panel_units', type=int, default=1, help='Moog Units?')
        pars.add_argument('--nineteen_panel_units', type=int, default=1, help='19inch Units?')
        pars.add_argument('--lw_panel_units', type=int, default=1, help='Loudest Warning Units?')
        pars.add_argument('--hammond_panel_units', type=int, default=1, help='Hammond Units?')
        pars.add_argument('--fracrack_panel_units', type=int, default=1, help='Frackrack Units?')

        #panel color
        pars.add_argument('--panel_color', type=inkex.Color, default='#e6e6e6', help='Panel color')

        #panel custom dimension
        pars.add_argument('--panel_custom_width', type=float, default='100', help='Set the panel custom width')
        pars.add_argument('--panel_custom_height', type=float, default='100', help='Set the panel custom height')

        #panel utility
        pars.add_argument('--panel_holes', type=inkex.Boolean, default='False', help='Want do drill the mounting holes?')
        pars.add_argument('--panel_centers', type=inkex.Boolean, default='False', help='Mark centers?')
        pars.add_argument('--panel_oval', type=inkex.Boolean, default='False', help='Oval holes?')
        pars.add_argument('--panel_lasercut', type=inkex.Boolean, default='False', help='Lasercut style?')
        
        #Screws
        pars.add_argument('--panel_screws', type=inkex.Boolean, default='False', help='Add screws')
        pars.add_argument('--panel_screw_radius', type=float, default='100', help='Screw radius')
        pars.add_argument('--panel_screw_type', type=int, default=1, help='Screw type')
        pars.add_argument('--panel_screw_color', type=inkex.Color, default='#e6e6e6', help='Screw color')
        pars.add_argument('--panel_screw_stroke_color', type=inkex.Color, default='#e6e6e6', help='Screw stroke color')
        pars.add_argument('--panel_screw_stroke_width', type=float, default='100', help='Screw stroke width')
        pars.add_argument('--panel_screw_tick_color', type=inkex.Color, default='#e6e6e6', help='Screw tick color')
        pars.add_argument('--panel_screw_tick_width', type=float, default='100', help='Screw tick width')

        #UI
        #KNOBS
        pars.add_argument('--knob_name', help='Knob name')
        pars.add_argument('--knob_main_style', type=int, default='False', help='Knob style')
        pars.add_argument('--knob_vintage_color', type=inkex.Color, default='#fefefe', help='Knob vintage color')
        pars.add_argument('--knob_vintage_dimension', type=float, default='10', help='Knob vintage dimension')
        pars.add_argument('--knob_vintage_stroke_color', type=inkex.Color, default='#fefefe', help='Knob vintage stroke color')
        pars.add_argument('--knob_vintage_stroke_width', type=float, default='10', help='Knob vintage stroke width')
        pars.add_argument('--knob_presets', type=int, default=1, help='Select the knob type')

        pars.add_argument('--knob_main_color', type=inkex.Color, default='#fefefe', help='Knob main color')
        pars.add_argument('--knob_main_stroke_color', type=inkex.Color, default='#333333', help='Knob stroke color')
        pars.add_argument('--knob_tick_color', type=inkex.Color, default='#333333', help='Knob tick color')
        pars.add_argument('--knob_tick_type', type=int, default=1, help='Select the tick type')

        pars.add_argument('--knob_add_skirt', type=inkex.Boolean, default='False', help='Add skirt')
        pars.add_argument('--knob_skirt_color', type=inkex.Color, default='#fefefe', help='Knob skirt color')
        pars.add_argument('--knob_skirt_stroke_color', type=inkex.Color, default='#333333', help='Knob skirt stroke color')

        pars.add_argument('--knob_main_dimension', type=float, default='12', help='Set the knob main dimension')
        pars.add_argument('--knob_main_stroke_width', type=float, default=1, help='Set the stroke width')
        
        pars.add_argument('--knob_tick_width', type=float, default=1, help='Set the tick width')
        pars.add_argument('--knob_tick_lenght', type=float, default=5.5, help='Set the tick lenght')

        pars.add_argument('--knob_skirt_dimension', type=float, default='12', help='Set the knob secondary dimension')
        pars.add_argument('--knob_skirt_stroke_width', type=float, default=1, help='Set the stroke width')

        #knobs scale
        pars.add_argument('--knob_scale_add_centering_circle', type=inkex.Boolean, default='False', help='Add centering circle')
        pars.add_argument('--knob_scale_add_arc', type=inkex.Boolean, default='False', help='Draw arc')
        pars.add_argument('--knob_scale_linlog', type=int, default='1', help='Lin/Log')
        pars.add_argument('--knob_scale_add_outer_arc', type=inkex.Boolean, default='False', help='Outer arc')
        pars.add_argument('--knob_scale_outer_arc_offset', type=float, default='0.5', help='Outer offset')
        pars.add_argument('--knob_scale_arc_width', type=float, default='0.5', help='Width')
        pars.add_argument('--knob_scale_arc_radius', type=float, default='10', help='Radius')
        pars.add_argument('--knob_scale_arc_angle', type=int, default='300', help='Angle')  
        pars.add_argument('--knob_scale_arc_rotation', type=int, default='300', help='Arc rotation')  
        pars.add_argument('--knob_scale_arc_angle_offset', type=float, default='10', help='Arc angle offset')
        pars.add_argument('--knob_scale_outer_arc_angle_offset', type=float, default='10', help='Outer arc angle offset')
        
        #knobs scale colors
        pars.add_argument('--knob_scale_arc_color', type=inkex.Color, default='#333333', help='Scale arc color')
        pars.add_argument('--knob_scale_ticks_color', type=inkex.Color, default='#333333', help='Scale ticks color')
        pars.add_argument('--knob_scale_subticks_color', type=inkex.Color, default='#333333', help='Scale subticks color')
        pars.add_argument('--knob_scale_label_color', type=inkex.Color, default='#333333', help='Scale label color')

        #knobs scale ticks
        pars.add_argument('--knob_scale_add_ticks', type=inkex.Boolean, default='True', help='Add ticks')
        pars.add_argument('--knob_scale_inner_ticks', type=inkex.Boolean, default='True', help='Add ticks')

        pars.add_argument('--knob_scale_ticks_type', type=int, default='300', help='Scale type')
        pars.add_argument('--knob_scale_ticks_number', type=int, default='300', help='Number of tick')
        pars.add_argument('--knob_scale_ticks_lenght', type=float, default='1', help='Ticks lenght')
        pars.add_argument('--knob_scale_ticks_width', type=float, default='0.1', help='Ticks width') 
        pars.add_argument('--knob_scale_ticks_accent_number', type=int, default='300', help='Accent number') 
        pars.add_argument('--Knob_scale_ticks_accent_lenght', type=float, default='1', help='Accent lenght')
        pars.add_argument('--knob_scale_ticks_accent_width', type=float, default='0.1', help='Accent width')
        pars.add_argument('--knob_scale_ticks_offset', type=float, default='0', help='Ticks offset')

        #knobs scale subticks
        pars.add_argument('--knob_scale_add_subticks', type=inkex.Boolean, default='False', help='Add sub ticks')
        pars.add_argument('--knob_scale_subticks_number', type=int, default='300', help='Number of subtick marks')
        pars.add_argument('--knob_scale_subticks_lenght', type=float, default='300', help='Subticks width')
        pars.add_argument('--knob_scale_subticks_width', type=float, default='300', help='Subticks lenght')  
        pars.add_argument('--knob_scale_subticks_type', type=int, default='False', help='Subticks type')
        pars.add_argument('--knob_scale_subticks_offset', type=float, default='300', help='Subticks offset')
        
        #knobs scale label
        pars.add_argument('--knob_scale_add_label', type=inkex.Boolean, default='False', help='Add label')
        pars.add_argument('--knob_scale_label_start_number', type=float, default='1', help='Start number')
        pars.add_argument('--knob_scale_label_end_number', type=float, default='10', help='End number')
        pars.add_argument('--knob_scale_add_plus_sign', type=inkex.Boolean, default='True', help='Add + sign to positive numebrs')
        pars.add_argument('--knob_scale_label_rounding_float', type=int, default='0', help='Rounding float')
        pars.add_argument('--knob_scale_label_leftright', type=inkex.Boolean, default='False', help='Left/Right')
        pars.add_argument('--knob_scale_label_reverse_order', type=inkex.Boolean, default='False', help='Reverse order')
        pars.add_argument('--knob_scale_label_font_size', type=float, default='10', help='Label size')
        pars.add_argument('--knob_scale_label_offset', type=float, default='10', help='Offset')
        pars.add_argument('--knob_scale_label_add_suffix', help='Label')

        #knobs scale utilities
        pars.add_argument('--knob_scale_utilities_color', type=inkex.Color, default='#333333', help='Utilities color')
        pars.add_argument('--knob_scale_utilities_add_drill_guide', type=inkex.Boolean, default='False', help='Add drill guide')
        pars.add_argument('--knob_scale_utilities_drill_guide_type', type=int, default='0', help='Drill guide type')
        pars.add_argument('--knob_scale_utilities_line_width', type=float, default='10', help='Line width')
        pars.add_argument('--knob_scale_utilities_guide_dimension', type=float, default='10', help='Guide dimension')

        #SLIDERS
        pars.add_argument('--slider_name', help='Slider name')
        pars.add_argument('--slider_orientation', type=int, default=1, help='Select the slider type') 
        pars.add_argument('--slider_scale_linlog', type=int, default='1', help='Lin/Log')
        pars.add_argument('--slider_presets', type=int, default=1, help='Select the knob type')

        #sliders colors
        #coarse
        pars.add_argument('--slider_coarse_color', type=inkex.Color, default='#fefefe', help='Slider coarse color')
        pars.add_argument('--slider_coarse_stroke_color', type=inkex.Color, default='#333333', help='Slider coarse stroke color')

        #cursor
        pars.add_argument('--slider_cursor_color', type=inkex.Color, default='#fefefe', help='Slider cursor color')
        pars.add_argument('--slider_cursor_stroke_color', type=inkex.Color, default='#fefefe', help='Slider cursor stroke color')
        pars.add_argument('--slider_cursor_type', type=int, default=1, help='Select the cursor type')
        pars.add_argument('--slider_cursor_tick_color', type=inkex.Color, default='#fefefe', help='Slider cursor tick color')

        #sliders dimension
        #coarse
        pars.add_argument('--slider_coarse_lenght', type=float, default=100, help='Coarse')
        pars.add_argument('--slider_coarse_gap', type=float, default=6, help='Gap')
        pars.add_argument('--slider_coarse_stroke_width', type=float, default=1, help='Coarse stroke width')
        pars.add_argument('--slider_coarse_round_edges', type=inkex.Boolean, default='False', help='Round the edges')

        #cursor
        pars.add_argument('--slider_cursor_height', type=float, default=100, help='Cursor height')
        pars.add_argument('--slider_cursor_width', type=float, default=100, help='Cursor width')
        pars.add_argument('--slider_cursor_stroke_width', type=float, default=100, help='Cursor stroke width')
        pars.add_argument('--slider_cursor_tick_width', type=float, default=0.1, help='Cursor tick width')
        pars.add_argument('--slider_cursor_round_edges', type=float, default='False', help='Round the edges')


        #SLIDER SCALES
        pars.add_argument('--slider_scale_position', type=int, default='1', help='Position')
        pars.add_argument('--slider_scale_h_offset', type=float, default='1', help='H offset')
        pars.add_argument('--slider_scale_v_offset', type=float, default='1', help='V offset')

        #slider scale colors
        pars.add_argument('--slider_scale_tick_color', type=inkex.Color, default='#fefefe', help='Slider tick color')
        pars.add_argument('--slider_scale_subtick_color', type=inkex.Color, default='#fefefe', help='Slider subtick color')
        pars.add_argument('--slider_scale_label_color', type=inkex.Color, default='#fefefe', help='Slider label color')
        
        #slider scale ticks
        pars.add_argument('--slider_scale_ticks_number', type=int, default='300', help='Number of tick marks')
        pars.add_argument('--slider_scale_ticks_start_size', type=float, default='1', help='Ticks start size')
        pars.add_argument('--slider_scale_ticks_end_size', type=float, default='1', help='Ticks end size')
        pars.add_argument('--slider_scale_ticks_start_lenght', type=float, default='10', help='Ticks start lenght')
        pars.add_argument('--slider_scale_ticks_end_lenght', type=float, default='10', help='Ticks end lenght')

        #slider scale subticks
        pars.add_argument('--slider_scale_add_subticks', type=inkex.Boolean, default='False', help='Add subticks')
        pars.add_argument('--slider_scale_subticks_number', type=int, default='300', help='Number of subtick marks')
        pars.add_argument('--slider_scale_subticks_size', type=float, default='300', help='Subticks size')
        pars.add_argument('--slider_scale_subtick_lenght', type=float, default='5', help='Subticks lenght')
        
        #slider scale perpendicular line
        pars.add_argument('--slider_scale_add_perpendicular_line', type=inkex.Boolean, default='False', help='Add perpendicular line')
        pars.add_argument('--slider_scale_perpendicular_line_width', type=float, default='300', help='Perpendicular line width')

        #sliders scale label
        pars.add_argument('--slider_scale_add_label', type=inkex.Boolean, default='False', help='Add label')
        pars.add_argument('--slider_scale_label_start', type=float, default='1', help='Start')
        pars.add_argument('--slider_scale_label_end', type=float, default='10', help='End')
        pars.add_argument('--slider_scale_add_plus_sign', type=inkex.Boolean, default='True', help='Add + sign to positive numebrs')
        pars.add_argument('--slider_scale_label_rounding_float', type=int, default='0', help='Rounding float')
        pars.add_argument('--slider_scale_label_reverse_order', type=inkex.Boolean, default='False', help='Reverse order')
        pars.add_argument('--slider_scale_label_position', type=int, default='0', help='Label position')
        pars.add_argument('--slider_scale_label_font_size', type=float, default='10', help='Label font size')
        pars.add_argument('--slider_scale_label_offset_tl', type=float, default='10', help='Offset')
        pars.add_argument('--slider_scale_label_offset_br', type=float, default='10', help='Offset') 
        pars.add_argument('--slider_scale_label_offset_adj', type=float, default='10', help='Offset') 

        pars.add_argument('--slider_scale_label_add_suffix', help='Label add suffix')

        #slider scale utilities
        pars.add_argument('--slider_scale_utilities_color', type=inkex.Color, default='#333333', help='Utilities color')
        pars.add_argument('--slider_scale_utilities_add_drill_guide', type=inkex.Boolean, default='False', help='Add drill guide')
        """ pars.add_argument('--slider_scale_utilities_drill_guide_type', type=int, default='0', help='Drill guide type') """
        pars.add_argument('--slider_scale_utilities_line_width', type=float, default='10', help='Line width')
        """ pars.add_argument('--slider_scale_utilities_guide_dimension', type=float, default='10', help='Guide dimension') """
        pars.add_argument('--slider_scale_utilities_guide_round_edges', type=inkex.Boolean, default='False', help='Round guide edges')

        #Settings
        pars.add_argument('--author', help='Author name')
        pars.add_argument('--brand', help='Company name')
        pars.add_argument('--copyright', help='Copyright')
        pars.add_argument('--releasedate', help='Release date')
        pars.add_argument('--moduleversion', help='Module version')
        pars.add_argument('--logo', help='Company Logo')
        pars.add_argument('--globalfont', help='Global font')
        pars.add_argument('--globalholecolor', type=inkex.Color, default='#cccccc', help='Global hole color')
        pars.add_argument('--globalstrokesize', help='Global stroke size')
        pars.add_argument('--globallasercutcolor', type=inkex.Color, default='#cccccc', help='Global lasercut color')
        pars.add_argument('--globallasercutstrokesize', help='Global lasercut stroke size')
        
        #About

        #Extra
        pars.add_argument('--paneltab')
        pars.add_argument('--uitab')

    def draw_rectangle(self, w, h, x, y, rx, ry):
        rect = Rectangle(
            x=str(x), y=str(y), width=str(w), height=str(h), rx=str(rx), ry=str(ry)
        )
        return rect

    def draw_circle(self, x, y, radius, mark_angle, mark_length):
        cx = x + radius * cos(mark_angle)
        cy = y + radius * sin(mark_angle)
        r = mark_length / 2.0
        circ = PathElement.arc((cx, cy), r)
        return circ

    def draw_vintage_circle(self, x, y, radius, radius2, sides):
        circ = inkex.PathElement()
        circ.set("sodipodi:type", "star")
        circ.set("sodipodi:cx", x)
        circ.set("sodipodi:cy", y)
        circ.set("sodipodi:arg1", 0.85)
        circ.set("sodipodi:arg2", 1.3)
        circ.set("inkscape:rounded", 0.5)
        circ.set("sodipodi:sides", sides)
        circ.set("sodipodi:r1", radius)
        circ.set("sodipodi:r2", radius2)
        return circ

    def draw_knurled_screw(self, x, y, radius, radius2, sides):
        knurled = inkex.PathElement()
        knurled.set("sodipodi:type", "star")
        knurled.set("sodipodi:cx", x)
        knurled.set("sodipodi:cy", y)
        knurled.set("sodipodi:arg1", 0.78539816)
        knurled.set("sodipodi:arg2", 0.84823001)
        knurled.set("inkscape:rounded", 0)
        knurled.set("sodipodi:sides", sides)
        knurled.set("sodipodi:r1", radius)
        knurled.set("sodipodi:r2", radius2)
        return knurled

    def draw_line_mark(self, x, y, radius, mark_angle, mark_length):
        x1 = x + radius * cos(mark_angle)
        y1 = y + radius * sin(mark_angle)
        x2 = x + (radius + mark_length) * cos(mark_angle)
        y2 = y + (radius + mark_length) * sin(mark_angle)

        line = inkex.PathElement()
        line.path = "M {},{} L {},{}".format(x1, y1, x2, y2)
        return line

    def draw_line(self, x1, y1, x2, y2):
        line = inkex.PathElement()
        line.path = "M {},{} L {},{}".format(x1, y1, x2, y2)
        return line

    def draw_knob_scale_arc(self, cx, cy, angle, rotation, radius):
        end = (angle + rotation - pi) / 2.0
        start = pi - end + rotation
        arc = PathElement.arc((cx, cy), radius, start=start, end=end, open=True)
        return arc

    def draw_text(self, x, y, textvalue, radius, angular_position, text_size):
        # Create text element
        text = TextElement()
        text.text = textvalue
        # Set text position to center of document.
        text.set("x", str(x + radius * cos(angular_position)))
        text.set("y", str(y + radius * sin(angular_position) + text_size / 2))
        return text

    def draw_slider_text(self, x, y, textvalue, text_size):
        # Create text element
        text = TextElement()
        text.text = textvalue
        # Set text position to center of document.
        text.set("x", str(x))
        text.set("y", str(y + text_size / 2))
        return text

    def effect(self):
        euro_hp = self.options.eurorack_panel_hp
        api_units = self.options.api_panel_units
        moog_units = {1: 53.721, 2: 107.696, 4: 215.646, 8: 431.546}[
            self.options.moog_panel_units
        ]
        fracrack_units = {1: 38.1, 2: 76.3, 3: 114.3}[
            self.options.fracrack_panel_units
        ]

        hammond_units_width = {1: 51, 2: 39, 3: 60, 4: 66, 5: 92 , 6: 99, 7: 108, 8: 114, 9: 118, 10: 119, 11: 145, 12: 170, 13: 131, 14: 190 }[
            self.options.hammond_panel_units
        ]

        hammond_units_height = {1: 51, 2: 93, 3: 112, 4: 121, 5: 92, 6: 112, 7: 108, 8: 114, 9: 133, 10: 94, 11: 95, 12: 138, 13: 130, 14: 122 }[
            self.options.hammond_panel_units
        ]

        nineteen_units = self.options.nineteen_panel_units
        lw_units = self.options.lw_panel_units

        oval = self.options.panel_oval
        centers = self.options.panel_centers
        unitfactor = self.svg.unittouu('1mm')
        part = self.options.part

        if part == 1: #panel
            # Dimensions
            # Eurorack 3U Doepfer standard
            # http://www.doepfer.de/a100_man/a100m_e.htm

            if self.options.panel_type == "e3u" or self.options.panel_type == "vcv" :
                height = 128.5
                #width = euro_hp                    
                width = 7.5 + (euro_hp - 3) * 5.08 + 7.5

            #Eurorack 1U Intellijel standard
            #https://intellijel.com/support/1u-technical-specifications/
            
            elif self.options.panel_type == "e1uij":
                height = 39.65
                width = 7.5 + (euro_hp - 3) * 5.08 + 7.5
                
            #Eurorack 1U Intellijel standard
            #https://intellijel.com/support/1u-technical-specifications/
            
            elif self.options.panel_type == "e1upl":
                height = 44.45
                width = 7.5 + (euro_hp - 3) * 5.08 + 7.5
            
            #API500 500 module series specification
            #https://www.barryrudolph.com/recall/manuals/api_vpr_%20500_spec.pdf
            
            elif self.options.panel_type == "api":
                height = 133.35
                width = api_units * 38.1

            #MOOG UNIT 5U
            #https://www.dsl-man.de/display/FRONTPANELS/5U+Format+specifications

            elif self.options.panel_type == "m5u" or self.options.panel_type == "d5u":
                height = 222.25
                width  = moog_units
            
            # Draw  19-inch standard
            # https://sdiy.info/w/index.php?title=19-inch_rack

            elif self.options.panel_type == "nineteen":
                height = nineteen_units * 44.50
                width = 482.60

            # Draw  Loudest Warning standard
            # http://www.loudestwarning.co.uk/portfolio/4u-modular-specs/

            elif self.options.panel_type == "lw" or self.options.panel_type == "serge" or self.options.panel_type == "buchla" :
                height = 175
                width = lw_units * 25.4 #25.4 correspond to 1 inch, real panels are "few tenths of a mm less..."

            # Draw  Fracrack standard
            # https://www.paia.com/fracrak.asp

            elif self.options.panel_type == "fracrack" :
                height = 133.35
                width = fracrack_units

            # Draw  Hammond standard
            # https://www.guitarpedalx.com/news/gpx-blog/the-key-pedal-enclosure-sizes-you-are-most-likely-to-encounter

            elif self.options.panel_type == "hammond" :
                height = hammond_units_height
                width = hammond_units_width
            
            #custom
            else:
                width = self.options.panel_custom_width
                height = self.options.panel_custom_height
                self.options.panel_holes = False
                self.options.panel_centers = False 

            # Calculate final width and height of panel
            pheight = height * unitfactor
            pwidth =  width * unitfactor

            # New panel group
            #panel_group = self.svg.add(inkex.Group.new('Panel Group'))

            panel_group = self.svg.add(inkex.Group.new(self.options.panel_name))
    
            # Panel sub layer
            panel_layer = panel_group.add(inkex.Layer.new('Panel'))  #panel

            #vcv components layer
            if self.options.panel_type == "vcv":
                vcv_layer = self.svg.add(inkex.Layer.new('Components'))  #vcv

            if self.options.panel_holes:
                holes_layer = panel_group.add(inkex.Layer.new('Holes'))  #holes
                holes_group = holes_layer.add(inkex.Group.new('Holes'))  #holes group

            if self.options.panel_screws:
                screws_layer = panel_group.add(inkex.Layer.new('Screws'))  #screws
                screws_group = screws_layer.add(inkex.Group.new('Screws'))  #screws group

            if self.options.panel_centers:
                center_layer = panel_group.add(inkex.Layer.new('Center')) #center
                center_layer_g = center_layer.add(inkex.Group.new('Center')) #center group

            # Draw Panel
            panel = self.draw_rectangle(pwidth, pheight, 0, 0, 0, 0)
            panel_layer.append(panel)
            panel_layer.set('id', 'panel')

            #panel style
            if self.options.panel_lasercut:
                panel.style['stroke'] = Blue
                panel.style['stroke-width'] = lasercut_width
                panel.style['fill'] = 'none'
            else:
                panel.style['stroke'] = 'none'
                panel.style['stroke-width'] =  '0mm'
                panel.style['fill'] = self.options.panel_color

            # Resize the document area
            pw = self.svg.uutounit(pwidth, 'px')
            ph = self.svg.uutounit(pheight, 'px')
            self.svg.set('width', str(pw))
            self.svg.set('height', str(ph))
            self.svg.set('viewBox', '{} {} {} {}'.format(0,0,str(pwidth),str(pheight)))

            #define
            TopHoles = 0
            BottomHoles = 0
            LeftHoles = 0
            RightHoles = 0
            HoleRadius = 0

            # Draw  Eurorack and VCV Holes
            # http://www.doepfer.de/a100_man/a100m_e.htm
            if self.options.panel_type == "e1uij" or self.options.panel_type == "e3u" or self.options.panel_type == "vcv"  :
                TopHoles = 3.0
                BottomHoles = height - 3.0

                if euro_hp <= 2:
                    LeftHoles = 4    
                else:
                    LeftHoles = 7.5
                
                RightHoles = ((euro_hp - 3.0) * 5.08) + 7.5
                HoleRadius = 1.6
            
            # Draw Eurorack 1U Pulp Logic
            # http://pulplogic.com/1u_tiles/
            if self.options.panel_type == "e1upl":
                TopHoles = 3.0
                BottomHoles = height - 3.0

                if euro_hp <= 2:
                    LeftHoles = 4    
                else:
                    LeftHoles = 7.5
                
                RightHoles = ((euro_hp - 3.0) * 5.08) + 7.5
                HoleRadius = 1.5857

            # Draw  API Holes
            # https://www.barryrudolph.com/recall/manuals/api_vpr_%20500_spec.pdf
            elif self.options.panel_type == "api":
                TopHoles = 4.35
                BottomHoles = height - 4.35
                LeftHoles = 19.05
                RightHoles = api_units * 38.1 - 38.1/2
                HoleRadius = 1.6

            # Draw  Moog Holes
            # https://www.dsl-man.de/display/FRONTPANELS/5U+Format+specifications
            elif self.options.panel_type == "m5u" or self.options.panel_type == "d5u":
                TopHoles = 4.445
                BottomHoles = height - 4.445
                LeftHoles = 26.86
                RightHoles = self.options.moog_panel_units * 53.975 - 53.975/2
                HoleRadius = 2.159

            # Draw  Loudest Warning Holes
            # http://www.loudestwarning.co.uk/portfolio/4u-modular-specs/
            elif self.options.panel_type == "lw" or self.options.panel_type == "serge" or self.options.panel_type == "buchla" :
                TopHoles = 3
                BottomHoles = height - 3
                LeftHoles = 12.7
                RightHoles = self.options.lw_panel_units * 25.4 - 12.7
                HoleRadius = 1.6

            # Draw  FracRack Holes
            # https://www.paia.com/fracrak.asp
            elif self.options.panel_type == "fracrack" :
                TopHoles = 3
                BottomHoles = height - 3
                
                if self.options.fracrack_panel_units == 2: #4 places
                    LeftHoles = width/2 - 19.05
                    RightHoles = width/2 + 19.05
                elif self.options.fracrack_panel_units == 3:    #6 places
                    LeftHoles = width/2 - 38.1
                    RightHoles = width/2 + 38.1
                else: #2 places
                    LeftHoles = width/2
                    RightHoles = 0
                
                HoleRadius = 1.524

            # Draw 19-inch standard Holes
            # https://sdiy.info/w/index.php?title=19-inch_rack
            elif self.options.panel_type == "nineteen":
                TopHoles = 6.35
                BottomHoles = TopHoles + self.options.nineteen_panel_units * (15.88*2) + self.options.nineteen_panel_units * 12.7 - 12.7
                LeftHoles = 7.928
                RightHoles = LeftHoles + 465.12
                HoleRadius = 2.18

            if self.options.panel_type != "custom" or self.options.panel_type != "hammond" :
                topH = TopHoles * unitfactor
                bottomH = BottomHoles * unitfactor
                leftH = LeftHoles * unitfactor
                rightH = RightHoles * unitfactor
                holeR = HoleRadius * unitfactor
                gap = holeR/2

            #screws
            if self.options.panel_screws == True and self.options.panel_type == "vcv" and self.options.panel_lasercut == False :
                self.options.panel_holes == False #remove holes

                screw_radius = self.options.panel_screw_radius /2
                screw_type = self.options.panel_screw_type
                screw_color  = self.options.panel_screw_color
                screw_stroke_color = self.options.panel_screw_stroke_color
                screw_stroke_width = self.options.panel_screw_stroke_width
                screw_tick_width = self.options.panel_screw_tick_width
                screw_tick_color = self.options.panel_screw_tick_color

                # Bottom Left
                if self.options.panel_screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(leftH), y=str(bottomH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(leftH), cy=str(bottomH), r=str(screw_radius)))
                        
                # Top Left
                if self.options.panel_screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(leftH), y=str(topH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(leftH), cy=str(topH), r=str(screw_radius)))
                    
                # Bottom Right
                if self.options.panel_screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(rightH), y=str(bottomH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(rightH), cy=str(bottomH), r=str(screw_radius)))
                
                # Top Right
                if self.options.panel_screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(rightH), y=str(topH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(rightH), cy=str(topH), r=str(screw_radius)))
                
                # screw type
                if self.options.panel_screw_type == 2 or self.options.panel_screw_type == 3 :
                    screws_group.append(self.draw_line(leftH-holeR, bottomH, leftH+holeR, bottomH))
                    screws_group.append(self.draw_line( leftH-holeR, topH, leftH+holeR, topH))
                    screws_group.append(self.draw_line(rightH-holeR, bottomH, rightH+holeR, bottomH))
                    screws_group.append(self.draw_line(rightH-holeR, topH, rightH+holeR, topH))
                    
                if self.options.panel_screw_type == 3 :
                    screws_group.append(self.draw_line( leftH, bottomH+holeR, leftH, bottomH-holeR))
                    screws_group.append(self.draw_line( leftH, topH+holeR, leftH, topH-holeR))
                    screws_group.append(self.draw_line(rightH, bottomH+holeR, rightH, bottomH-holeR))
                    screws_group.append(self.draw_line(rightH, topH+holeR, rightH, topH-holeR))
                    
                screws_group.style['transform'] = 'rotate(-10)'
                screws_group.style['stroke'] = screw_stroke_color
                screws_group.style['stroke-width'] = screw_stroke_width
                screws_group.style['fill'] = screw_color

            #holes
            if self.options.panel_holes == True and self.options.panel_type != "custom":
                if  self.options.panel_type == "api" or self.options.panel_type == "m5u" or self.options.panel_type == "d5u" or self.options.panel_type == "lw" or self.options.panel_type == "serge" or self.options.panel_type == "buchla" or self.options.panel_type == "fracrack" :
                    oval = False
                if oval == False:  # Draw Round holes
                    r = HoleRadius * unitfactor
                    # Bottom Left
                    holes_group.append(Circle(cx=str(leftH), cy=str(bottomH), r=str(r)))
                    # Top Left
                    holes_group.append(Circle(cx=str(leftH), cy=str(topH), r=str(r)))

                    if self.options.panel_type == "fracrack" and self.options.fracrack_panel_units >  2:
                        # Center top
                        holes_group.append(Circle(cx=str(width/2), cy=str(topH), r=str(r)))
                        
                        #Center bottom
                        holes_group.append(Circle(cx=str(width/2), cy=str(bottomH), r=str(r)))

                    # Draw Left-side Centers
                    if centers == True:
                        #only for fracrack
                        if self.options.panel_type == "fracrack":   
                            # Top center Centers
                            # Horizontal Line
                            center_layer_g.append(self.draw_line( width/2-holeR+gap, topH, width/2+holeR-gap, topH))

                            # Vertical Line
                            center_layer_g.append(self.draw_line( width/2, topH+holeR-gap, width/2, topH-holeR+gap))

                            #Bottom center centers
                            # Horizontal Line
                            center_layer_g.append(self.draw_line(width/2-holeR+gap, bottomH, width/2+holeR-gap, bottomH))
                            # Vertical Line
                            center_layer_g.append(self.draw_line( width/2, bottomH+holeR-gap, width/2, bottomH-holeR+gap))

                        # Bottom Left Centers
                        # Horizontal Line
                        center_layer_g.append(self.draw_line(leftH-holeR+gap, bottomH, leftH+holeR-gap, bottomH))

                        # Vertical Line
                        center_layer_g.append(self.draw_line( leftH, bottomH+holeR-gap, leftH, bottomH-holeR+gap))

                        # Top Left Centers
                        # Horizontal Line
                        center_layer_g.append(self.draw_line( leftH-holeR+gap, topH, leftH+holeR-gap, topH))

                        # Vertical Line
                        center_layer_g.append(self.draw_line( leftH, topH+holeR-gap, leftH, topH-holeR+gap))
                    # Draw the Righthand side Mounting holes
                    if (self.options.panel_type == "e3u" or self.options.panel_type == "e1uij" or self.options.panel_type == "e1upl" or self.options.panel_type == "vcv") and euro_hp > 10 or (self.options.panel_type == "api" and api_units >=2) or (self.options.panel_type == "m5u"  and self.options.moog_panel_units >=2) or (self.options.panel_type == "d5u"  and self.options.moog_panel_units >=2) or self.options.panel_type == "nineteen" or self.options.panel_type == "lw" or self.options.panel_type == "serge" or self.options.panel_type == "buchla" or (self.options.panel_type == "fracrack" and self.options.fracrack_panel_units >  1) :
                        # Bottom Right
                        holes_group.append(Circle(cx=str(rightH), cy=str(bottomH), r=str(r)))
                        # Top Right
                        holes_group.append(Circle(cx=str(rightH), cy=str(topH), r=str(r)))
                        # Draw Right-side Centers
                        if centers == True:
                            # Bottom Right Centers - Horizontal Line
                            center_layer_g.append(self.draw_line(rightH-holeR+gap, bottomH, rightH+holeR-gap, bottomH))
                            # Vertical Line
                            center_layer_g.append(self.draw_line(rightH, bottomH+holeR-gap, rightH, bottomH-holeR+gap))
                            # Top Right Centers - Horizontal Line
                            center_layer_g.append(self.draw_line(rightH-holeR+gap, topH, rightH+holeR-gap, topH))
                            # Vertical Line
                            center_layer_g.append(self.draw_line(rightH, topH+holeR-gap, rightH, topH-holeR+gap))

                else: # oval == True
                
                    # Oval Holes: (a square with rounded corners)
                    
                    if self.options.panel_type == "nineteen":
                        oval_size = 7
                    else:
                        oval_size = 5.5  # 3.2mm hole. Oval is 5.5mm across
                    oval_stretch = oval_size/2 # 2.75
                    gapH = oval_stretch*unitfactor - gap
                    oval_offset = (oval_stretch-HoleRadius)*unitfactor # 1.15
                    oval_width = oval_size*unitfactor
                    oval_height = HoleRadius*2*unitfactor

                    # Bottom Left
                    holes_group.append(self.draw_rectangle(oval_width,oval_height,leftH-oval_stretch*unitfactor,bottomH-holeR, holeR,0))
                    # Top Left
                    holes_group.append(self.draw_rectangle(oval_width,oval_height, leftH-oval_stretch*unitfactor,topH-holeR, holeR,0))

                    # Draw Left-side Centers
                    if centers == True:
                        # Bottom Left Centers - Horizontal Line
                        center_layer_g.append(self.draw_line( leftH-gapH, bottomH, leftH+gapH, bottomH))
                        # Vertical Lines
                        offset = -oval_offset
                        for i in range(3):
                            center_layer_g.append(self.draw_line( leftH+offset, bottomH+holeR-gap, leftH+offset, bottomH-holeR+gap))
                            offset += oval_offset
                        # Top Left Centers - Horizontal Line
                        center_layer_g.append(self.draw_line( leftH-gapH, topH, leftH+gapH, topH))
                        # Vertical Lines
                        offset = -oval_offset
                        for i in range(3):
                            center_layer_g.append(self.draw_line( leftH+offset, topH+holeR-gap, leftH+offset, topH-holeR+gap))
                            offset += oval_offset

                    # Draw the Righthand side Mounting holes

                    if (self.options.panel_type == "e3u" or self.options.panel_type == "e1uij" or self.options.panel_type == "e1upl" or self.options.panel_type == "vcv")  and euro_hp > 10 or (self.options.panel_type == "lw" and lw_units > 2) or (self.options.panel_type == "nineteen"):
                        # Bottom Right
                        holes_group.append(self.draw_rectangle(oval_width,oval_height, rightH-oval_stretch*unitfactor,bottomH-holeR, holeR,0))
                        # Top Right
                        holes_group.append(self.draw_rectangle(oval_width,oval_height, rightH-oval_stretch*unitfactor,topH-holeR, holeR,0))

                        # Draw Left-side Centers
                        if centers == True:
                            # Bottom Right Centers - Horizontal Line
                            center_layer_g.append(self.draw_line( rightH-gapH, bottomH, rightH+gapH, bottomH))
                            # Left Vertical Line
                            # Vertical Lines
                            offset = -oval_offset
                            for i in range(3):
                                center_layer_g.append(self.draw_line( rightH+offset, bottomH+holeR-gap, rightH+offset, bottomH-holeR+gap))
                                offset += oval_offset
                            # Top Right Centers
                            # Horizontal Line
                            center_layer_g.append(self.draw_line( rightH-gapH, topH, rightH+gapH, topH))
                            # Left Vertical Line
                            offset = -oval_offset
                            for i in range(3):
                                center_layer_g.append(self.draw_line( rightH+offset, topH+holeR-gap, rightH+offset, topH-holeR+gap))
                                offset += oval_offset

                #mounting hole style
                if self.options.panel_lasercut:
                    holes_group.style['stroke'] = Blue
                    holes_group.style['stroke-width'] = lasercut_width
                    holes_group.style['fill'] = 'none'
                else:
                    holes_group.style['stroke'] = 'none'
                    holes_group.style['stroke-width'] =  '0'
                    holes_group.style['fill'] = White

                #center
                if self.options.panel_centers:
                    center_layer_g.style['stroke'] = Orange
                    center_layer_g.style['stroke-width'] = lasercut_width
                    center_layer_g.style['fill'] = 'none'

        elif part == 2: #knobs

            if self.svg.getElementById('knobs-group') is not None:
                knobs = self.svg.getElementById('knobs-group')
            else:
                knobs = self.svg.add(inkex.Layer.new('Knobs Group'))
                knobs.set('id', 'knobs-group')

            # Knob sub layer
            if self.options.knob_name is None:
                inkex.errormsg(_('Please add the knob name, will be used to create layer with a proper name'))
            else:
                knob_layer = knobs.add(inkex.Layer.new(self.options.knob_name)) #knob layer

                if self.options.knob_add_skirt: #skirt is active on presets
                    knob_layer_skirt = knob_layer.add(inkex.Layer.new('Skirt'))
                if self.options.knob_main_style == 2:
                    knob_layer_vintage = knob_layer.add(inkex.Layer.new('Vintage knob'))
                knob_layer_main = knob_layer.add(inkex.Layer.new('Main color'))
                knob_layer_tick = knob_layer.add(inkex.Layer.new('Tick'))

                #append the knob layer to the knobs group
                knobs.append(knob_layer)
            
                #get the page's bounding box
                bbox_panel = self.svg.get_page_bbox()
                
                if self.options.knob_main_style == 2:
                    vintage_knob = self.draw_vintage_circle(x=str(bbox_panel.center_x), y=str(bbox_panel.center_y), radius=str(self.options.knob_vintage_dimension / 2), radius2 = str(self.options.knob_vintage_dimension / 2 + 1 ), sides = 7)
                    mainknob = Circle(cx=str(bbox_panel.center_x), cy=str(bbox_panel.center_y), r=str(self.options.knob_main_dimension / 2))
                
                    vintage_knob.style['fill'] = self.options.knob_vintage_color
                    vintage_knob.style['stroke'] = self.options.knob_vintage_stroke_color
                    vintage_knob.style['stroke-width'] = self.options.knob_vintage_stroke_width
                else:
                    mainknob = Circle(cx=str(bbox_panel.center_x), cy=str(bbox_panel.center_y), r=str(self.options.knob_main_dimension / 2))
                    
                mainknob.set('id', 'id_'+self.options.knob_name)
                
                if self.options.knob_main_style == 2:
                    knob_layer_vintage.append(vintage_knob)
                    knob_layer_main.append(mainknob)
                else:    
                    knob_layer_main.append(mainknob)

                if self.options.knob_add_skirt:
                    knob_skirt = Circle(cx=str(bbox_panel.center_x), cy=str(bbox_panel.center_y), r=str(self.options.knob_skirt_dimension / 2))
                    knob_skirt.set('id', 'id_s_'+self.options.knob_name)
                    knob_layer_skirt.append(knob_skirt)

                tlenght = self.options.knob_tick_lenght

                x2 = tlenght*sin(325*pi/180)
                y2 = tlenght*cos(325*pi/180)

                if self.options.knob_tick_type == 1:
                    thetick = self.draw_line(bbox_panel.center_x, bbox_panel.center_y, x2+bbox_panel.center_x, y2+bbox_panel.center_y)
                    thetick.style['fill'] = 'none'
                    thetick.style['stroke'] = self.options.knob_tick_color

                else:
                    thetick = Circle(cx=str(x2+bbox_panel.center_x), cy=str(y2+bbox_panel.center_y), r=str(self.options.knob_tick_width))
                    thetick.style['fill'] = self.options.knob_tick_color
                    thetick.style['stroke'] = 'none'

                thetick.style['stroke-width'] = self.options.knob_tick_width

                knob_layer_tick.append(thetick)

                mainknob.style['fill'] = self.options.knob_main_color
                mainknob.style['stroke'] = self.options.knob_main_stroke_color
                mainknob.style['stroke-width'] = self.options.knob_main_stroke_width

                if self.options.knob_add_skirt:
                    knob_skirt.style['fill'] = self.options.knob_skirt_color
                    knob_skirt.style['stroke'] = self.options.knob_skirt_stroke_color
                    knob_skirt.style['stroke-width'] = self.options.knob_skirt_stroke_width

                self.svg.append(knobs)

        elif part == 3: #knobs scales
                
            sknob = self.svg.get_selected()
            for knob in self.svg.get_selected():   
                bbox = knob.bounding_box(composed_transform(knob))
                break

            missing_knob = False

            #scale layers
            if self.svg.getElementById('knobs-group') is None:
                missing_knob = True
                inkex.errormsg(_("To draw a scale, you must first draw a knob.\n")) 

            if self.svg.getElementById('knob-scales-group') is not None:
                knob_scales = self.svg.getElementById('knob-scales-group')
            else:
                knob_scales = self.svg.add(inkex.Layer.new('Knob Scales Group'))
                knob_scales.set('id', 'knob-scales-group')

            if self.options.knob_scale_label_leftright:
                n_ticks  = 2
                n_subticks = 1
            else:
                n_ticks = self.options.knob_scale_ticks_number
                n_subticks = self.options.knob_scale_subticks_number

            start_num = self.options.knob_scale_label_start_number
            end_num = self.options.knob_scale_label_end_number
            text_spacing = self.options.knob_scale_label_offset
            text_size = self.options.knob_scale_label_font_size

            is_knob_selected = False

            for node in sknob:
                is_knob_selected = True
                
                bbox_parent =  node.getparent()
                layer = bbox_parent.getparent()
                selected_label = bbox_parent.get('inkscape:label')
            
                if(selected_label == 'none'):
                    inkex.errormsg(_("To draw a scale, you must first select the corresponding knob.\nPlease select the knob's main color.\nYou have selected the knob %s") % selected_label)
                else:    
                    knob_name = layer.get('inkscape:label')
                    knob_scale_layer = knob_scales.add(inkex.Layer.new(knob_name)) #new layer with the same name of the knob

                    angle = self.options.knob_scale_arc_angle*pi/180.0
                    arc_rotation = self.options.knob_scale_arc_rotation*pi/180.0 *2
                    
                    radius = self.options.knob_scale_arc_radius
                    offset_radius = self.options.knob_scale_arc_radius + self.options.knob_scale_outer_arc_offset - (self.options.knob_scale_arc_width /2)

                    if self.options.knob_scale_add_centering_circle:
                        knob_scale_cc = knob_scale_layer.add(inkex.Layer.new('Centering circle'))
                        centering_circle = Circle(cx=str(bbox.center_x), cy=str(bbox.center_y), r=str(radius + 3))

                        centering_circle.style['fill'] = "none"
                        centering_circle.style['stroke'] = self.options.knob_scale_utilities_color
                        centering_circle.style['stroke-width'] = self.options.knob_scale_utilities_line_width

                        knob_scale_cc.append(centering_circle)
                        
                    if self.options.knob_scale_utilities_add_drill_guide:
                        knob_scale_drill_guide = knob_scale_layer.add(inkex.Layer.new('Drill guide'))
                        if self.options.knob_scale_utilities_drill_guide_type == 2: #cross
                            cross_v = self.draw_line( 
                            bbox.center_x + self.options.knob_scale_utilities_guide_dimension /2, 
                            bbox.center_y, 
                            bbox.center_x - self.options.knob_scale_utilities_guide_dimension /2, 
                            bbox.center_y)
                            
                            cross_h = self.draw_line( 
                            bbox.center_x, 
                            bbox.center_y + self.options.knob_scale_utilities_guide_dimension /2, 
                            bbox.center_x, 
                            bbox.center_y - self.options.knob_scale_utilities_guide_dimension /2)
                            
                            cross_v.style['fill'] = cross_h.style['fill'] = "none"
                            cross_v.style['stroke'] = cross_h.style['stroke'] = self.options.knob_scale_utilities_color
                            cross_v.style['stroke-width'] = cross_h.style['stroke-width'] = self.options.knob_scale_utilities_line_width

                            knob_scale_drill_guide.append(cross_v)
                            knob_scale_drill_guide.append(cross_h)
                        
                        elif self.options.knob_scale_utilities_drill_guide_type == 3: #dot
                            drill_dot = Circle(cx=str(bbox.center_x), cy=str(bbox.center_y), r=str(self.options.knob_scale_utilities_guide_dimension /2))

                            drill_dot.style['fill'] = self.options.knob_scale_utilities_color
                            drill_dot.style['stroke'] = "none"
                            drill_dot.style['stroke-width'] = 0

                            knob_scale_drill_guide.append(drill_dot)

                        elif self.options.knob_scale_utilities_drill_guide_type == 4: #circle  
                            drill_circle = Circle(cx=str(bbox.center_x), cy=str(bbox.center_y), r=str(self.options.knob_scale_utilities_guide_dimension /2 - self.options.knob_scale_utilities_line_width /2))

                            drill_circle.style['fill'] = "none"
                            drill_circle.style['stroke'] = self.options.knob_scale_utilities_color
                            drill_circle.style['stroke-width'] = self.options.knob_scale_utilities_line_width

                            knob_scale_drill_guide.append(drill_circle)

                    knob_scale_arc = knob_scale_layer.add(inkex.Layer.new('Arcs'))
                    
                    if self.options.knob_scale_add_arc:
                        arc = self.draw_knob_scale_arc(bbox.center_x, bbox.center_y, angle + self.options.knob_scale_arc_angle_offset, arc_rotation, radius)
                        
                        arc.style['fill'] = 'none'
                        arc.style['stroke'] = self.options.knob_scale_arc_color
                        arc.style['stroke-width'] = self.options.knob_scale_arc_width
                        
                        knob_scale_arc.append(arc)
                    
                    if self.options.knob_scale_add_outer_arc:
                        outer_arc = self.draw_knob_scale_arc(bbox.center_x, bbox.center_y, angle + self.options.knob_scale_outer_arc_angle_offset, arc_rotation, offset_radius)

                        outer_arc.style['fill'] = 'none'
                        outer_arc.style['stroke'] = self.options.knob_scale_arc_color
                        outer_arc.style['stroke-width'] = self.options.knob_scale_arc_width

                        knob_scale_arc.append(outer_arc)

                        #draw the arc before when the mark are dots
                        if self.options.knob_scale_ticks_type == 2:
                            knob_scale_layer.append(knob_scale_arc)

                    if self.options.knob_scale_add_ticks:
                        if n_ticks > 0:
                            knob_scale_tick = knob_scale_layer.add(inkex.Layer.new('Ticks'))
                            if n_subticks > 0 and self.options.knob_scale_add_subticks:
                                    knob_scale_sub_tick_layer = knob_scale_layer.add(inkex.Layer.new('Subticks'))

                            ticks_start_angle = (1.5*pi - 0.5*angle) + (arc_rotation/2)

                            ticks_delta = angle / (n_ticks - 1)
                            knob_scale_label = knob_scale_layer.add(inkex.Layer.new('Labels'))
                            
                            for tick in range(n_ticks):
                                if self.options.knob_scale_ticks_type == 1:
                                    if(self.options.knob_scale_ticks_accent_number != 0):
                                        if(tick % self.options.knob_scale_ticks_accent_number):
                                            tick_length = self.options.knob_scale_ticks_lenght
                                        else:    
                                            tick_length = self.options.knob_scale_ticks_lenght + self.options.Knob_scale_ticks_accent_lenght
                                    else:
                                        tick_length = self.options.knob_scale_ticks_lenght
                                        
                                    if self.options.knob_scale_inner_ticks:
                                        scale_tick = self.draw_line_mark(bbox.center_x, bbox.center_y, radius - (self.options.knob_scale_arc_width / 2) - self.options.knob_scale_ticks_offset - tick_length , ticks_start_angle + ticks_delta*tick, tick_length)
                                    else:
                                        scale_tick = self.draw_line_mark(bbox.center_x, bbox.center_y, radius - (self.options.knob_scale_arc_width / 2) + self.options.knob_scale_ticks_offset, ticks_start_angle + ticks_delta*tick, tick_length)
                                            
                                    if(self.options.knob_scale_ticks_accent_number != 0):
                                        if(tick % self.options.knob_scale_ticks_accent_number):
                                            scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_width
                                        else:    
                                            scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_accent_width
                                    else:
                                        scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_width

                                    scale_tick.style['stroke'] = self.options.knob_scale_ticks_color    
                                    knob_scale_tick.append(scale_tick)    

                                else:
                                    tick_length = self.options.knob_scale_ticks_lenght
                                    scale_tick = self.draw_circle(bbox.center_x, bbox.center_y, radius , ticks_start_angle + ticks_delta*tick, tick_length)

                                    scale_tick.style['fill'] = self.options.knob_scale_ticks_color
                                    scale_tick.style['stroke'] = 'none'
                                    scale_tick.style['stroke-width'] = 0

                                    knob_scale_tick.append(scale_tick)

                                if self.options.knob_scale_add_label:
                                    if self.options.knob_scale_label_leftright:
                                        tick_text = ['L', 'R']
                                        label = self.draw_text(bbox.center_x, bbox.center_y, tick_text[tick], radius + tick_length + text_spacing,
                                                ticks_start_angle + ticks_delta*tick, text_size)
                                    else:    
                                        if self.options.knob_scale_label_rounding_float > 0:
                                            if self.options.knob_scale_label_reverse_order:
                                                #reverse
                                                tick_number = str(round(start_num +
                                                                    float(n_ticks - (tick +1)) * (end_num - start_num) / (n_ticks - 1),
                                                                    self.options.knob_scale_label_rounding_float))
                                            else:
                                                #forward
                                                tick_number = str(round(start_num +
                                                                    float(tick) * (end_num - start_num) / (n_ticks - 1),
                                                                    self.options.knob_scale_label_rounding_float))
                                        else:
                                            if self.options.knob_scale_label_reverse_order:
                                                #reverse
                                                tick_number = str(int(start_num + float(n_ticks - (tick +1)) * (end_num - start_num) / (n_ticks - 1)))
                                            else:
                                                #forward
                                                tick_number = str(int(start_num + float(tick) * (end_num - start_num) / (n_ticks - 1)))


                                        if (self.options.knob_scale_add_plus_sign and  int(tick_number) > 0):
                                            tick_text = "+" + tick_number
                                        else:
                                            tick_text = tick_number 
                                         

                                        label = self.draw_text(bbox.center_x, bbox.center_y, tick_text +  (str(self.options.knob_scale_label_add_suffix) if self.options.knob_scale_label_add_suffix else '' ), radius + tick_length + text_spacing,ticks_start_angle + ticks_delta*tick, text_size)

                                    label.style['text-align'] = 'center'
                                    label.style['text-anchor'] = 'middle'
                                    label.style['alignment-baseline'] = 'center'
                                    label.style['font-size'] = str(text_size)
                                    label.style['vertical-align'] = 'middle'
                                    label.style['fill'] = self.options.knob_scale_label_color

                                    knob_scale_label.append(label)

                                if tick == (n_ticks - 1) :
                                    break

                                if n_subticks > 0 and self.options.knob_scale_add_subticks:
                                    subticks_delta = ticks_delta / (n_subticks + 1)
                                    subtick_start_angle = ticks_start_angle + ticks_delta*tick + subticks_delta
                                    subtick_length = self.options.knob_scale_subticks_lenght

                                    for subtick in range(n_subticks):
                                        if self.options.knob_scale_subticks_type == 1:
                                            if self.options.knob_scale_inner_ticks:
                                                knob_scale_subtick = self.draw_line_mark(bbox.center_x, bbox.center_y, radius - self.options.knob_scale_subticks_offset - subtick_length - (self.options.knob_scale_arc_width / 2), subtick_start_angle + subticks_delta*subtick, subtick_length)
                                            else:
                                                knob_scale_subtick = self.draw_line_mark(bbox.center_x, bbox.center_y, radius + self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                                
                                            knob_scale_subtick.style['fill'] = 'none'
                                            knob_scale_subtick.style['stroke'] = self.options.knob_scale_subticks_color
                                            knob_scale_subtick.style['stroke-width'] = self.options.knob_scale_subticks_width
                                        else:
                                            if self.options.knob_scale_inner_ticks:
                                                knob_scale_subtick = self.draw_circle(bbox.center_x, bbox.center_y, radius - (self.options.knob_scale_arc_width / 2) - self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                            else:
                                                knob_scale_subtick = self.draw_circle(bbox.center_x, bbox.center_y, radius - (self.options.knob_scale_arc_width / 2) + self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                            knob_scale_subtick.style['fill'] = self.options.knob_scale_subticks_color
                                            knob_scale_subtick.style['stroke'] = 'none'
                                            knob_scale_subtick.style['stroke-width'] = 0

                                        knob_scale_sub_tick_layer.append(knob_scale_subtick)

                            #draw the arc on top of the tick when the tick are line
                            if (self.options.knob_scale_ticks_type == 1) and self.options.knob_scale_add_arc:
                                knob_scale_layer.append(knob_scale_arc)
                
            if is_knob_selected == False and missing_knob == False:
                inkex.errormsg(_("To draw a scale, you must first select the corresponding knob.\nPlease select the knob's main color."))

        elif part == 4: #sliders
            
            if self.options.slider_orientation == 1:
                coarse_width = self.options.slider_coarse_gap - self.options.slider_coarse_stroke_width
                coarse_lenght = self.options.slider_coarse_lenght - self.options.slider_coarse_stroke_width
            else:
                coarse_lenght = self.options.slider_coarse_gap - self.options.slider_coarse_stroke_width
                coarse_width = self.options.slider_coarse_lenght - self.options.slider_coarse_stroke_width

            #create main sliders layer 
            if self.svg.getElementById('sliders-group') is not None:
                sliders = self.svg.getElementById('sliders-group')
            else:
                sliders = self.svg.add(inkex.Layer.new('Sliders Group'))
                sliders.set('id', 'sliders-group')

            # Slider sub layer
            slider_layer = sliders.add(inkex.Layer.new(self.options.slider_name)) #slider layer
            slider_layer_coarse = slider_layer.add(inkex.Layer.new('Coarse'))

            #draw coarse
            if self.options.slider_coarse_round_edges:
                if self.options.slider_orientation == 2:
                    rx = ry = coarse_lenght /2
                else:
                    rx = ry = coarse_width /2
            else:
                rx = ry = 0
                
            if self.svg.set_selected('panel'):
                bbox = 0
                bbox = self.svg.get_selected_bbox()
            else:
                bbox = 0
                bbox = self.svg.get_page_bbox()

            coarse = self.draw_rectangle(coarse_width, coarse_lenght, bbox.center_x - coarse_width/2, bbox.center_y - coarse_lenght/2, rx, ry)

            coarse.style['fill'] = self.options.slider_coarse_color
            coarse.style['stroke'] = self.options.slider_coarse_stroke_color
            coarse.style['stroke-width'] = self.options.slider_coarse_stroke_width

            slider_layer_coarse.append(coarse)

            #draw cursor  
            cursor_radius = self.options.slider_cursor_width  - self.options.slider_cursor_stroke_width

            # Cursor sub layer
            slider_layer_cursor = slider_layer.add(inkex.Layer.new('Cursor'))
            
            #draw cursor
            #rounding edges
            rx = ry = self.options.slider_cursor_round_edges /2
            
            if self.options.slider_cursor_type == 1:
                cursor = Circle(cx=str(bbox.center_x ), cy=str(bbox.center_y), r=str(cursor_radius/2))
            else:
                if self.options.slider_orientation == 1:
                    cursor_width = self.options.slider_cursor_width 
                    cursor_height = self.options.slider_cursor_height - self.options.slider_cursor_stroke_width
                  
                    cursor = self.draw_rectangle(cursor_width - self.options.slider_cursor_stroke_width, cursor_height, bbox.center_x - cursor_width/2 + self.options.slider_cursor_stroke_width /2, bbox.center_y - cursor_height /2, rx, ry)
                else:
                    cursor_width = self.options.slider_cursor_width  - self.options.slider_cursor_stroke_width
                    cursor_height = self.options.slider_cursor_height - self.options.slider_cursor_stroke_width
                  
                    cursor = self.draw_rectangle(cursor_width, cursor_height, bbox.center_x - cursor_width/2, bbox.center_y - cursor_height /2, rx, ry)
            
            
            cursor.style['fill'] = self.options.slider_cursor_color
            cursor.style['stroke'] = self.options.slider_cursor_stroke_color
            cursor.style['stroke-width'] = self.options.slider_cursor_stroke_width

            slider_layer_cursor.append(cursor)

            #draw tick
            if self.options.slider_cursor_tick_width > 0:
                slider_layer_tick = slider_layer.add(inkex.Layer.new('Tick'))

                # Tick sub layer
                if self.options.slider_cursor_type == 2: #dot
                    
                    yp =   cursor.get('y') 
                    xp =   cursor.get('x')
                    
                    if self.options.slider_orientation == 1:      
                        cursor_tick = self.draw_line( 
                            float(xp) + self.options.slider_cursor_stroke_width /2, 
                            float(yp) + cursor_height /2, 
                            float(xp) + self.options.slider_cursor_width - self.options.slider_cursor_stroke_width - (self.options.slider_cursor_stroke_width/2), 
                            float(yp) + cursor_height /2)
                    else: 
                        cursor_tick = self.draw_line( 
                            float(xp) + cursor_width /2, 
                            float(yp) + self.options.slider_cursor_stroke_width /2 , 
                            float(xp) + cursor_width /2,
                            float(yp) + self.options.slider_cursor_height - self.options.slider_cursor_stroke_width - (self.options.slider_cursor_stroke_width/2))

                    cursor_tick.style['stroke'] = self.options.slider_cursor_tick_color
                    cursor_tick.style['stroke-width'] = self.options.slider_cursor_tick_width
                    
                    slider_layer_tick.append(cursor_tick)

        elif part == 5: #slider scales
                bbox = False
                sslider = self.svg.get_selected()
                for slider in self.svg.get_selected():   
                    bbox = slider.bounding_box(composed_transform(slider))
                    break

                missing_slider = False

                #scale layers
                if self.svg.getElementById('sliders-group') is None:
                    missing_slider = True
                    inkex.errormsg(_("To draw a scale, you must first draw a slider.\n")) 
                    
                if self.svg.getElementById('slider-scales-group') is not None:
                    slider_scales = self.svg.getElementById('slider-scales-group')
                else:
                    slider_scales = self.svg.add(inkex.Layer.new('Slider Scales Group'))
                    slider_scales.set('id', 'slider-scales-group')

                n_ticks = self.options.slider_scale_ticks_number
                n_subticks = self.options.slider_scale_subticks_number
                start_size = self.options.slider_scale_ticks_start_size
                end_size = self.options.slider_scale_ticks_end_size
                position = self.options.slider_scale_position

                start_num = self.options.slider_scale_label_start
                end_num = self.options.slider_scale_label_end

                #text_spacing = self.options.slider_scale_label_offset
                text_size = self.options.slider_scale_label_font_size

                missing_slider = True
                is_slider_selected = False
                if bbox != False:
                    #vertical    
                    if bbox.height > bbox.width:
                        ticks_delta = (bbox.height - self.options.slider_scale_v_offset) / (n_ticks - 1)
                        tick_length_start = self.options.slider_scale_ticks_start_lenght
                        tick_lenght_end = self.options.slider_scale_ticks_end_lenght
                        ticks_delta_lenght = (tick_lenght_end - tick_length_start) / (n_ticks -1)
                        
                        
                        for node in sslider:
                            is_slider_selected = True
                            bbox_parent =  node.getparent()
                            layer = bbox_parent.getparent()
                            selected_label = bbox_parent.get('inkscape:label')

                            if(selected_label == 'none'):
                                inkex.errormsg(_("To draw a scale, you must first select the corresponding slider.\nPlease select the slider's Coarse.\nYou have selected the slider %s") % selected_label)
                            
                            else:
                                l = layer.get('inkscape:label')
                                slider_scale_layer = slider_scales.add(inkex.Layer.new(l)) #new layer with the same name of the knob
                                slider_scale_label = slider_scale_layer.add(inkex.Layer.new('Label'))

                                if n_ticks > 0:
                                    slider_scale_ticks = slider_scale_layer.add(inkex.Layer.new('Ticks'))
                                    if self.options.slider_scale_add_perpendicular_line:

                                        pline_l = self.draw_line(
                                                        bbox.left - self.options.slider_scale_h_offset,  #x1
                                                        bbox.bottom - (self.options.slider_scale_v_offset /2) + start_size /2,                               #y1    
                                                        bbox.left - self.options.slider_scale_h_offset,  #x1
                                                        bbox.bottom - ticks_delta * (n_ticks -1) - (self.options.slider_scale_v_offset /2) - end_size /2)

                                        pline_r = self.draw_line(
                                                        bbox.right + self.options.slider_scale_h_offset, #x1
                                                        bbox.bottom - (self.options.slider_scale_v_offset /2) + start_size /2,                               #y1    
                                                        bbox.right + self.options.slider_scale_h_offset,
                                                        bbox.bottom - ticks_delta * (n_ticks -1) - (self.options.slider_scale_v_offset /2) - end_size /2)

                                    for tick in range(n_ticks):
                                        
                                        ticks_delta = (bbox.height - self.options.slider_scale_v_offset) / (n_ticks - 1)

                                        tick_length = (ticks_delta_lenght * tick) + tick_length_start
                                        
                                        #left
                                        scale_tick_l = self.draw_line(
                                                        bbox.left - self.options.slider_scale_h_offset,  
                                                        bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2), 
                                                        bbox.left - self.options.slider_scale_h_offset - tick_length,  
                                                        bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2))

                                        #right
                                        scale_tick_r = self.draw_line(
                                                        bbox.right + self.options.slider_scale_h_offset,  #x1
                                                        bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2),                               #y1    
                                                        bbox.right + self.options.slider_scale_h_offset + tick_length,  #x2
                                                        bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2))  

                                        scale_tick_l.style['stroke'] = scale_tick_r.style['stroke'] = self.options.slider_scale_tick_color

                                        delta_size =  (self.options.slider_scale_ticks_end_size - self.options.slider_scale_ticks_start_size) / (n_ticks - 1)
                                        ticksize = (delta_size * tick) + self.options.slider_scale_ticks_start_size
                                        scale_tick_l.style['stroke-width'] = scale_tick_r.style['stroke-width'] = ticksize

                                        if position == 1:
                                            slider_scale_ticks.append(scale_tick_l)

                                        elif position == 2:
                                            slider_scale_ticks.append(scale_tick_r)

                                        else:       
                                            slider_scale_ticks.append(scale_tick_r)
                                            slider_scale_ticks.append(scale_tick_l)

                                        #scale add label
                                        if self.options.slider_scale_add_label:
                                            if self.options.slider_scale_label_reverse_order:
                                                if self.options.slider_scale_label_rounding_float > 0:
                                                    tick_text = str(round(start_num +
                                                                        float(n_ticks - (tick +1)) * (end_num - start_num) / (n_ticks - 1),
                                                                        self.options.slider_scale_label_rounding_float))
                                                else:
                                                    tick_text = str(int(start_num + float(n_ticks -(tick +1)) * (end_num - start_num) / (n_ticks - 1)))
                                            else:
                                                if self.options.slider_scale_label_rounding_float > 0:
                                                    tick_text = str(round(start_num +
                                                                        float(tick) * (end_num - start_num) / (n_ticks - 1),
                                                                        self.options.slider_scale_label_rounding_float))
                                                else:
                                                    tick_text = str(int(start_num + float(tick) * (end_num - start_num) / (n_ticks - 1)))

                                            label_r = self.draw_slider_text(
                                                                    bbox.right + self.options.slider_scale_label_offset_br + tick_length + self.options.slider_scale_h_offset + text_size,                     
                                                                    bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2) + self.options.slider_scale_label_offset_adj,                                    #y
                                                                    tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),                                                                                                          #textvalue
                                                                    text_size)                                                                                                          #textsize

                                            label_l = self.draw_slider_text(
                                                                    bbox.left - self.options.slider_scale_label_offset_tl - tick_length - self.options.slider_scale_h_offset - text_size,                                        #x
                                                                    bbox.bottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2) + self.options.slider_scale_label_offset_adj,                                    #y
                                                                    tick_text  +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),                                                                                                          #textvalue
                                                                    text_size)                                                                                                          #textsize

                                            label_l.style['text-align'] = label_r.style['text-align'] ='center'
                                            label_l.style['text-anchor'] = label_r.style['text-anchor'] = 'middle'
                                            label_l.style['alignment-baseline'] = label_r.style['alignment-baseline'] = 'center'
                                            label_l.style['font-size'] = label_r.style['font-size'] = self.options.slider_scale_label_font_size
                                            label_l.style['vertical-align'] = label_r.style['vertical-align'] = 'middle'
                                            label_l.style['fill'] = label_r.style['fill'] = self.options.slider_scale_label_color

                                            if self.options.slider_scale_label_position == 1:
                                                slider_scale_label.append(label_l)
                                            elif self.options.slider_scale_label_position == 2:
                                                slider_scale_label.append(label_r)
                                            else:
                                                slider_scale_label.append(label_l)
                                                slider_scale_label.append(label_r)

                                        if tick == (n_ticks - 1) :
                                            break

                                        if n_subticks > 0 and self.options.slider_scale_add_subticks:
                                        
                                            subtick_length = self.options.slider_scale_subtick_lenght

                                            subticks_delta = ticks_delta / (n_subticks + 1)

                                            if self.options.slider_scale_linlog == 2:
                                                n_subticks = 0
                                            for subtick in range(n_subticks):
                                                

                                                scale_subtick_r = self.draw_line(
                                                    bbox.right + self.options.slider_scale_h_offset,  
                                                    bbox.bottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2), 
                                                    bbox.right + self.options.slider_scale_h_offset + subtick_length,  
                                                    bbox.bottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2))                #y2

                                                scale_subtick_l = self.draw_line(
                                                    bbox.left - self.options.slider_scale_h_offset,  
                                                    bbox.bottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2), 
                                                    bbox.left - self.options.slider_scale_h_offset - subtick_length,  
                                                    bbox.bottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2))

                                                scale_subtick_l.style['stroke'] = scale_subtick_r.style['stroke'] = self.options.slider_scale_subtick_color
                                                scale_subtick_l.style['stroke-width'] = scale_subtick_r.style['stroke-width'] = self.options.slider_scale_subticks_size

                                                if self.options.slider_scale_position == 1:
                                                    slider_scale_ticks.append(scale_subtick_l)

                                                elif self.options.slider_scale_position == 2:
                                                    slider_scale_ticks.append(scale_subtick_r)

                                                else:       
                                                    slider_scale_ticks.append(scale_subtick_r)
                                                    slider_scale_ticks.append(scale_subtick_l)

                                if self.options.slider_scale_add_perpendicular_line:

                                    if self.options.slider_scale_position == 1:
                                        slider_scale_ticks.append(pline_l)

                                    elif self.options.slider_scale_position == 2:
                                        slider_scale_ticks.append(pline_r)
                                    else:       
                                        slider_scale_ticks.append(pline_r)
                                        slider_scale_ticks.append(pline_l)

                                    pline_r.style['stroke'] = pline_l.style['stroke'] = self.options.slider_scale_tick_color
                                    pline_r.style['stroke-width'] = pline_l.style['stroke-width'] = self.options.slider_scale_perpendicular_line_width
                    
                    elif bbox.width > bbox.height: #horizontal
                        ticks_delta = (bbox.width - self.options.slider_scale_h_offset) / (n_ticks - 1)
                        tick_length_start = self.options.slider_scale_ticks_start_lenght
                        tick_lenght_end = self.options.slider_scale_ticks_end_lenght
                        ticks_delta_lenght = (tick_lenght_end - tick_length_start) / (n_ticks -1)

                        for node in sslider:
                            is_slider_selected = True
                            bbox_parent =  node.getparent()
                            layer = bbox_parent.getparent()
                            selected_label = bbox_parent.get('inkscape:label')

                            if(selected_label != 'Coarse'):
                                inkex.errormsg(_("To draw a scale, you must first select the corresponding slider.\nPlease select the slider's Coarse.\nYou have selected the slider %s") % selected_label)
                            
                            else:
                                l = layer.get('inkscape:label')
                                slider_scale_layer = slider_scales.add(inkex.Layer.new(l)) #new layer with the same name of the knob
                                slider_scale_label = slider_scale_layer.add(inkex.Layer.new('Label'))

                                if n_ticks > 0:
                                    slider_scale_ticks = slider_scale_layer.add(inkex.Layer.new('Ticks'))
                                    if self.options.slider_scale_add_perpendicular_line:

                                        pline_t = self.draw_line(
                                                        bbox.left + (self.options.slider_scale_h_offset /2) + start_size /2,
                                                        bbox.top - self.options.slider_scale_v_offset,  #x1
                                                        bbox.left + bbox.width - (self.options.slider_scale_h_offset /2) - end_size /2,
                                                        bbox.top - self.options.slider_scale_v_offset)  #x1

                                        pline_b = self.draw_line(
                                                        bbox.left + (self.options.slider_scale_h_offset /2) + start_size /2,
                                                        bbox.bottom + self.options.slider_scale_v_offset,  #x1
                                                        bbox.left + bbox.width - (self.options.slider_scale_h_offset /2) - end_size /2,
                                                        bbox.bottom + self.options.slider_scale_v_offset)  #x1

                                    for tick in range(n_ticks):
                                        ticks_delta = (bbox.width - self.options.slider_scale_h_offset) / (n_ticks - 1)
                                        tick_length = (ticks_delta_lenght * tick) + tick_length_start
                                        delta_size =  (self.options.slider_scale_ticks_end_size - self.options.slider_scale_ticks_start_size) / (n_ticks - 1)
                                        ticksize = (delta_size * tick) + self.options.slider_scale_ticks_start_size
                                            
                                        #top
                                        scale_tick_t = self.draw_line(
                                                    bbox.left +  ticks_delta * tick + self.options.slider_scale_h_offset /2 ,
                                                    bbox.top - self.options.slider_scale_v_offset + self.options.slider_scale_perpendicular_line_width /2,  
                                                    bbox.left +  ticks_delta * tick + self.options.slider_scale_h_offset /2,
                                                    bbox.top - self.options.slider_scale_v_offset - tick_length)

                                        #bottom
                                        scale_tick_b = self.draw_line(
                                                    bbox.left +  ticks_delta * tick + self.options.slider_scale_h_offset /2 ,
                                                    bbox.bottom + (self.options.slider_scale_v_offset) - self.options.slider_scale_perpendicular_line_width /2,  
                                                    bbox.left +  ticks_delta * tick + self.options.slider_scale_h_offset /2,
                                                    bbox.bottom + self.options.slider_scale_v_offset + tick_length)

                                        scale_tick_t.style['stroke'] = scale_tick_b.style['stroke'] = self.options.slider_scale_tick_color
                                        scale_tick_t.style['stroke-width'] = scale_tick_b.style['stroke-width'] = ticksize
                                        

                                        if position == 1:
                                            slider_scale_ticks.append(scale_tick_t)

                                        elif position == 2:
                                            slider_scale_ticks.append(scale_tick_b)

                                        else:       
                                            slider_scale_ticks.append(scale_tick_t)
                                            slider_scale_ticks.append(scale_tick_b)

                                        #scale add label
                                        if self.options.slider_scale_add_label:
                                            if self.options.slider_scale_label_reverse_order:
                                                if self.options.slider_scale_label_rounding_float > 0:
                                                    tick_number = str(round(start_num +
                                                                        float(n_ticks - (tick +1)) * (end_num - start_num) / (n_ticks - 1),
                                                                        self.options.slider_scale_label_rounding_float))
                                                else:
                                                    tick_number = str(int(start_num + float(n_ticks -(tick +1)) * (end_num - start_num) / (n_ticks - 1)))
                                            else:
                                                if self.options.slider_scale_label_rounding_float > 0:
                                                    tick_number = str(round(start_num +
                                                                        float(tick) * (end_num - start_num) / (n_ticks - 1),
                                                                        self.options.slider_scale_label_rounding_float))
                                                else:
                                                    tick_number = str(int(start_num + float(tick) * (end_num - start_num) / (n_ticks - 1)))


                                            if (self.options.slider_scale_add_plus_sign and  int(tick_number) > 0):
                                                tick_text = "+" + tick_number
                                            else:
                                                tick_text = tick_number 
                                         

                                        
                                                    
                                            label_t = self.draw_slider_text(
                                                                bbox.left + ticks_delta * tick + (self.options.slider_scale_h_offset /2),
                                                                bbox.top - self.options.slider_scale_v_offset - self.options.slider_scale_label_offset_tl - tick_length - text_size,
                                                                    tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),    
                                                                    text_size)   

                                            label_b = self.draw_slider_text(
                                                                bbox.left + ticks_delta * tick + (self.options.slider_scale_h_offset /2),
                                                                bbox.bottom + self.options.slider_scale_v_offset + self.options.slider_scale_label_offset_br + tick_length + text_size,
                                                                tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),        
                                                                text_size)        
                                            
                                            label_b.style['text-align'] = label_t.style['text-align'] ='center'
                                            label_b.style['text-anchor'] = label_t.style['text-anchor'] = 'middle'
                                            label_b.style['alignment-baseline'] = label_t.style['alignment-baseline'] = 'center'
                                            label_b.style['font-size'] = label_t.style['font-size'] = self.options.slider_scale_label_font_size
                                            label_b.style['vertical-align'] = label_t.style['vertical-align'] = 'middle'
                                            label_b.style['fill'] = label_t.style['fill'] = self.options.slider_scale_label_color

                                            if self.options.slider_scale_label_position == 1:
                                                slider_scale_label.append(label_t)
                                            elif self.options.slider_scale_label_position == 2:
                                                slider_scale_label.append(label_b)
                                            else:
                                                slider_scale_label.append(label_t)
                                                slider_scale_label.append(label_b)

                                        if tick == (n_ticks - 1) :
                                            break

                                        if n_subticks > 0 and self.options.slider_scale_add_subticks:
                                        
                                            subtick_length = self.options.slider_scale_subtick_lenght

                                            subticks_delta = ticks_delta / (n_subticks + 1)

                                            if self.options.slider_scale_linlog == 2:
                                                n_subticks = 0
                                            for subtick in range(n_subticks):
                                                

                                                scale_subtick_r = self.draw_line(
                                                    bbox.left + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                                    bbox.top - self.options.slider_scale_v_offset + self.options.slider_scale_ticks_start_size /2, 
                                                    bbox.left + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                                    bbox.top - self.options.slider_scale_v_offset - subtick_length)

                                                scale_subtick_l = self.draw_line(
                                                    bbox.left + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                                    bbox.bottom + self.options.slider_scale_v_offset - self.options.slider_scale_ticks_start_size /2, 
                                                    bbox.left + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                                    bbox.bottom + self.options.slider_scale_v_offset + subtick_length)        

                                                scale_subtick_l.style['stroke'] = scale_subtick_r.style['stroke'] = self.options.slider_scale_subtick_color
                                                scale_subtick_l.style['stroke-width'] = scale_subtick_r.style['stroke-width'] = self.options.slider_scale_subticks_size

                                                if self.options.slider_scale_position == 1:
                                                    slider_scale_ticks.append(scale_subtick_l)

                                                elif self.options.slider_scale_position == 2:
                                                    slider_scale_ticks.append(scale_subtick_r)

                                                else:       
                                                    slider_scale_ticks.append(scale_subtick_r)
                                                    slider_scale_ticks.append(scale_subtick_l)

                                    

                                if self.options.slider_scale_add_perpendicular_line:

                                    if self.options.slider_scale_position == 1:
                                        slider_scale_ticks.append(pline_t)

                                    elif self.options.slider_scale_position == 2:
                                        slider_scale_ticks.append(pline_b)
                                    else:       
                                        slider_scale_ticks.append(pline_b)
                                        slider_scale_ticks.append(pline_t)

                                    pline_t.style['stroke'] = pline_b.style['stroke'] = self.options.slider_scale_tick_color
                                    pline_t.style['stroke-width'] = pline_b.style['stroke-width'] = self.options.slider_scale_perpendicular_line_width     
                else:
                    inkex.errormsg(_("To draw a scale, you must first select the corresponding slider.\nPlease select the slider's coarse.")) 

                if self.options.slider_scale_utilities_add_drill_guide:
                    slider_scale_drill_guide = slider_scale_layer.add(inkex.Layer.new('Drill guide'))

                    if self.options.slider_scale_utilities_guide_round_edges:
                        if bbox.width > bbox.height:
                            rx = ry = bbox.height /2
                        elif bbox.width < bbox.height:
                            rx = ry = bbox.width /2
                    else:
                        rx = ry = 0

                    drill_guide = self.draw_rectangle(bbox.width, bbox.height, bbox.left , bbox.top, rx, ry)
                
                    drill_guide.style['fill'] = "none"
                    drill_guide.style['stroke'] = self.options.slider_scale_utilities_color
                    drill_guide.style['stroke-width'] = self.options.slider_scale_utilities_line_width

                    slider_scale_drill_guide.append(drill_guide)

# Borrowed from inkscape-extensions 1.1, remove when Inkscape 1.1 comes out
def composed_transform(elem, other=None):
    parent = elem.getparent()
    if parent is not None and isinstance(parent, ShapeElement):
        return parent.composed_transform() * elem.transform
    return elem.transform

if __name__ == '__main__':
    # Create effect instance and apply it.
    SynthPanelEffect().run()