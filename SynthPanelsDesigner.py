#!/usr/bin/env python
# coding=utf-8

'''
Synth Panels Designer - Free Inkscape extension to draw musical instruments user interfaces
Copyright (C) 2020 Francesco Mulassano

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Added suggestions - GaryA 15/8/2020
Added jacks with options for 3.5mm & 1/4in
Added option to define position of knobs, sliders & jacks 

July 2023 Update 1.8
- migrated to inkscape 1.2+
- fixed centering to knob for Knob scale
- fixed centering to slider for Slider scale
- improved layers and elements naming
- add new sponsor: Alphalab Audio (Would you sponsor Synth Panel Designer? info@synthpanels.design)

'''

import sys
from textwrap import fill

import inkex
import argparse
import os
from inkex.elements import ShapeElement

from lxml import etree
from inkex.elements import Circle, PathElement, Rectangle, TextElement
from math import *

options = argparse.ArgumentParser(description='Panel parameters')

Orange = '#f6921e'
Blue =   '#0000FF'
White =  '#FFFFFF'
Green = '#32a852'

lasercut_width = '0.01mm'

class SynthPanelEffect(inkex.Effect):
    
    def __init__(self):
        # Call the base class constructor.
        inkex.Effect.__init__(self)
  
        #Parts
        self.arg_parser.add_argument('--part', type=int, default=1, help='Select which part you want to draw')

        #Panel standards
        self.arg_parser.add_argument('--panel_type', default='e3u', help='Panel type')
        self.arg_parser.add_argument('--panel_name', default='Panel', help='Panel name')
        self.arg_parser.add_argument('--eurorack_panel_hp', type=int, default=1, help='Panel HP?')
        self.arg_parser.add_argument('--api_panel_units', type=int, default=1, help='API Units?')
        self.arg_parser.add_argument('--moog_panel_units', type=int, default=1, help='Moog Units?')
        self.arg_parser.add_argument('--nineteen_panel_units', type=int, default=1, help='19inch Units?')
        self.arg_parser.add_argument('--lw_panel_units', type=int, default=1, help='Loudest Warning Units?')
        self.arg_parser.add_argument('--hammond_panel_units', type=int, default=1, help='Hammond Units?')
        self.arg_parser.add_argument('--fracrack_panel_units', type=int, default=1, help='Frackrack Units?')

        #panel color
        self.arg_parser.add_argument('--panel_color', type=inkex.Color, default='#e6e6e6', help='Panel color')

        #panel custom dimension
        self.arg_parser.add_argument('--panel_custom_width', type=float, default='100', help='Set the panel custom width')
        self.arg_parser.add_argument('--panel_custom_height', type=float, default='100', help='Set the panel custom height')

        #panel utility
        self.arg_parser.add_argument('--panel_holes', type=inkex.Boolean, default='False', help='Want do drill the mounting holes?')
        self.arg_parser.add_argument('--panel_centers', type=inkex.Boolean, default='False', help='Mark centers?')
        self.arg_parser.add_argument('--panel_oval', type=inkex.Boolean, default='False', help='Oval holes?')
        self.arg_parser.add_argument('--panel_lasercut', type=inkex.Boolean, default='False', help='Lasercut style?')
        
        #Screws
        self.arg_parser.add_argument('--panel_screws', type=inkex.Boolean, default='False', help='Add screws')
        self.arg_parser.add_argument('--panel_screw_radius', type=float, default='100', help='Screw radius')
        self.arg_parser.add_argument('--panel_screw_type', type=int, default=1, help='Screw type')
        self.arg_parser.add_argument('--panel_screw_color', type=inkex.Color, default='#e6e6e6', help='Screw color')
        self.arg_parser.add_argument('--panel_screw_stroke_color', type=inkex.Color, default='#e6e6e6', help='Screw stroke color')
        self.arg_parser.add_argument('--panel_screw_stroke_width', type=float, default='100', help='Screw stroke width')
        self.arg_parser.add_argument('--panel_screw_tick_color', type=inkex.Color, default='#e6e6e6', help='Screw tick color')
        self.arg_parser.add_argument('--panel_screw_tick_width', type=float, default='100', help='Screw tick width')

        #UI
        #KNOBS
        self.arg_parser.add_argument('--knob_name', help='Knob name')
        self.arg_parser.add_argument('--knob_main_style', type=int, default='False', help='Knob style')
        self.arg_parser.add_argument('--knob_vintage_color', type=inkex.Color, default='#fefefe', help='Knob vintage color')
        self.arg_parser.add_argument('--knob_vintage_dimension', type=float, default='10', help='Knob vintage dimension')
        self.arg_parser.add_argument('--knob_vintage_stroke_color', type=inkex.Color, default='#fefefe', help='Knob vintage stroke color')
        self.arg_parser.add_argument('--knob_vintage_stroke_width', type=float, default='10', help='Knob vintage stroke width')
        self.arg_parser.add_argument('--knob_vintage_sides', type=float, default='10', help='Knob vintage sides')
        self.arg_parser.add_argument('--knob_vintage_transform', type=float, default='10', help='Knob vintage transformation')
        self.arg_parser.add_argument('--knob_presets', type=int, default=1, help='Select the knob type')

        self.arg_parser.add_argument('--knob_main_color', type=inkex.Color, default='#fefefe', help='Knob main color')
        self.arg_parser.add_argument('--knob_main_stroke_color', type=inkex.Color, default='#333333', help='Knob stroke color')
        self.arg_parser.add_argument('--knob_tick_color', type=inkex.Color, default='#333333', help='Knob tick color')
        self.arg_parser.add_argument('--knob_tick_type', type=int, default=1, help='Select the tick type')

        self.arg_parser.add_argument('--knob_add_skirt', type=inkex.Boolean, default='False', help='Add skirt')
        self.arg_parser.add_argument('--knob_skirt_color', type=inkex.Color, default='#fefefe', help='Knob skirt color')
        self.arg_parser.add_argument('--knob_skirt_stroke_color', type=inkex.Color, default='#333333', help='Knob skirt stroke color')

        self.arg_parser.add_argument('--knob_main_dimension', type=float, default='12', help='Set the knob main dimension')
        self.arg_parser.add_argument('--knob_main_stroke_width', type=float, default=1, help='Set the stroke width')
        
        self.arg_parser.add_argument('--knob_add_tick', type=inkex.Boolean, default='False', help='Add tick')
        self.arg_parser.add_argument('--knob_tick_width', type=float, default=1, help='Set the tick width')
        self.arg_parser.add_argument('--knob_tick_lenght', type=float, default=5.5, help='Set the tick lenght')

        self.arg_parser.add_argument('--knob_skirt_dimension', type=float, default='12', help='Set the knob secondary dimension')
        self.arg_parser.add_argument('--knob_skirt_stroke_width', type=float, default=1, help='Set the stroke width')

        self.arg_parser.add_argument('--knob_add_arrow', type=inkex.Boolean, default='False', help='Add arrow')
        self.arg_parser.add_argument('--knob_arrow_color', type=inkex.Color, default='#fefefe', help='Knob arrow color') 
        self.arg_parser.add_argument('--knob_arrow_width', type=float, default='0', help='Knob arrow width') 

        self.arg_parser.add_argument('--knob_pos_define', type=inkex.Boolean, default='False', help='Define knob position')
        self.arg_parser.add_argument('--knob_pos_x', type=float, default='10', help='X position')
        self.arg_parser.add_argument('--knob_pos_y', type=float, default='10', help='Y position')

        #knobs scale
        self.arg_parser.add_argument('--knob_scale_add_arc', type=inkex.Boolean, default='False', help='Draw arc')
        self.arg_parser.add_argument('--knob_scale_linlog', type=int, default='1', help='Lin/Log')
        self.arg_parser.add_argument('--knob_scale_add_outer_arc', type=inkex.Boolean, default='False', help='Outer arc')
        self.arg_parser.add_argument('--knob_scale_outer_arc_offset', type=float, default='0.5', help='Outer offset')
        self.arg_parser.add_argument('--knob_scale_arc_width', type=float, default='0.5', help='Width')
        self.arg_parser.add_argument('--knob_scale_arc_radius', type=float, default='10', help='Radius')
        self.arg_parser.add_argument('--knob_scale_arc_angle', type=int, default='300', help='Angle')  
        self.arg_parser.add_argument('--knob_scale_arc_rotation', type=int, default='300', help='Arc rotation')  
        self.arg_parser.add_argument('--knob_scale_arc_angle_offset', type=float, default='10', help='Arc angle offset')
        self.arg_parser.add_argument('--knob_scale_outer_arc_angle_offset', type=float, default='10', help='Outer arc angle offset')
        self.arg_parser.add_argument('--knob_scale_close_arcs', type=inkex.Boolean, default='True', help='Close arcs')
        self.arg_parser.add_argument('--knob_scale_close_arcs_lr', type=int, default='0', help='Type of closure')
        
       
        
        #knobs scale colors
        self.arg_parser.add_argument('--knob_scale_arc_color', type=inkex.Color, default='#333333', help='Scale arc color')
        self.arg_parser.add_argument('--knob_scale_ticks_color', type=inkex.Color, default='#333333', help='Scale ticks color')
        self.arg_parser.add_argument('--knob_scale_subticks_color', type=inkex.Color, default='#333333', help='Scale subticks color')
        self.arg_parser.add_argument('--knob_scale_label_color', type=inkex.Color, default='#333333', help='Scale label color')

        #knobs scale ticks
        self.arg_parser.add_argument('--knob_scale_add_ticks', type=inkex.Boolean, default='True', help='Add ticks')
        self.arg_parser.add_argument('--knob_scale_inner_ticks', type=inkex.Boolean, default='True', help='Add ticks')

        self.arg_parser.add_argument('--knob_scale_ticks_type', type=int, default='300', help='Scale type')
        self.arg_parser.add_argument('--knob_scale_ticks_number', type=int, default='300', help='Number of tick')
        self.arg_parser.add_argument('--knob_scale_ticks_lenght', type=float, default='1', help='Ticks lenght')
        self.arg_parser.add_argument('--knob_scale_ticks_width', type=float, default='0.1', help='Ticks width') 
        self.arg_parser.add_argument('--knob_scale_ticks_accent_number', type=int, default='300', help='Accent number') 
        self.arg_parser.add_argument('--Knob_scale_ticks_accent_lenght', type=float, default='1', help='Accent lenght')
        self.arg_parser.add_argument('--knob_scale_ticks_accent_width', type=float, default='0.1', help='Accent width')
        self.arg_parser.add_argument('--knob_scale_ticks_offset', type=float, default='0', help='Ticks offset')
        self.arg_parser.add_argument('--knob_scale_ticks_start_lenght', type=float, default='10', help='Ticks start lenght')
        self.arg_parser.add_argument('--knob_scale_ticks_end_lenght', type=float, default='10', help='Ticks end lenght')

        self.arg_parser.add_argument('--knob_scale_add_tick_dots', type=inkex.Boolean, default='True', help='Add tick dots')
        self.arg_parser.add_argument('--knob_scale_add_tick_dots_offset', type=float, default='10', help='Tick dots offset')
        self.arg_parser.add_argument('--knob_scale_add_tick_dots_radius', type=float, default='10', help='Tick dots radius')
        self.arg_parser.add_argument('--knob_scale_multiple_dots_number', type=int, default='2', help='Multiple dots number')
        self.arg_parser.add_argument('--knob_scale_multiple_dots_offset', type=float, default='10', help='Multiple dots offset')

        #knobs scale subticks
        self.arg_parser.add_argument('--knob_scale_add_subticks', type=inkex.Boolean, default='False', help='Add sub ticks')
        self.arg_parser.add_argument('--knob_scale_subticks_number', type=int, default='300', help='Number of subtick marks')
        self.arg_parser.add_argument('--knob_scale_subticks_lenght', type=float, default='300', help='Subticks width')
        self.arg_parser.add_argument('--knob_scale_subticks_width', type=float, default='300', help='Subticks lenght')  
        self.arg_parser.add_argument('--knob_scale_subticks_type', type=int, default='False', help='Subticks type')
        self.arg_parser.add_argument('--knob_scale_subticks_offset', type=float, default='300', help='Subticks offset')
        
        #knobs scale label
        self.arg_parser.add_argument('--knob_scale_add_label', type=inkex.Boolean, default='False', help='Add label')
        self.arg_parser.add_argument('--knob_scale_label_start_number', type=float, default='1', help='Start number')
        self.arg_parser.add_argument('--knob_scale_label_end_number', type=float, default='10', help='End number')
        self.arg_parser.add_argument('--knob_scale_add_plus_sign', type=inkex.Boolean, default='True', help='Add + sign to positive numebrs')
        self.arg_parser.add_argument('--knob_scale_label_rounding_float', type=int, default='0', help='Rounding float')
        self.arg_parser.add_argument('--knob_scale_label_reverse_order', type=inkex.Boolean, default='False', help='Reverse order')
        self.arg_parser.add_argument('--knob_scale_label_font_size', type=float, default='10', help='Label size')
        self.arg_parser.add_argument('--knob_scale_label_offset', type=float, default='10', help='Offset')
        self.arg_parser.add_argument('--knob_scale_label_add_suffix', help='Label add suffix') 
        self.arg_parser.add_argument('--knob_scale_label_add_customtext', type=inkex.Boolean, help='Label add customtext')
        self.arg_parser.add_argument('--knob_scale_label_customtext', help='Label customtex')

        #knobs scale utilities
        self.arg_parser.add_argument('--knob_scale_add_centering_circle', type=inkex.Boolean, default='False', help='Add centering circle')
        self.arg_parser.add_argument('--knob_scale_utilities_centering_color', type=inkex.Color, default='#008000', help='Centering stroke color')
        self.arg_parser.add_argument('--knob_scale_utilities_centering_line_width', type=float, default='10', help='Centering line width')
        self.arg_parser.add_argument('--knob_scale_utilities_centering_guide_offset', type=float, default='10', help='Centering guide offset')

        self.arg_parser.add_argument('--knob_scale_utilities_color', type=inkex.Color, default='#ff00ff', help='Drill stroke color')
        self.arg_parser.add_argument('--knob_scale_utilities_add_drill_guide', type=inkex.Boolean, default='False', help='Add drill guide')
        self.arg_parser.add_argument('--knob_scale_utilities_drill_guide_type', type=int, default='0', help='Drill guide type')
        self.arg_parser.add_argument('--knob_scale_utilities_line_width', type=float, default='10', help='Drill line width')
        self.arg_parser.add_argument('--knob_scale_utilities_guide_dimension', type=float, default='10', help='Drill guide dimension')


        self.arg_parser.add_argument('--knob_scale_utilities_pcb_color', type=inkex.Color, default='#ff00ff', help='Utilities color')
        self.arg_parser.add_argument('--knob_scale_utilities_add_pcb_component_guide', type=inkex.Boolean, default='False', help='Add PCB drill guide')
        self.arg_parser.add_argument('--knob_scale_utilities_component_guide_type', type=int, default='0', help='Drill guide type')
        self.arg_parser.add_argument('--knob_scale_utilities_pcb_line_width', type=float, default='10', help='Line width')
        self.arg_parser.add_argument('--knob_scale_utilities_pcb_guide_dimension', type=float, default='10', help='Guide dimension')

        #SLIDERS
        self.arg_parser.add_argument('--slider_name', help='Slider name')
        self.arg_parser.add_argument('--slider_orientation', type=int, default=1, help='Select the slider type') 
        self.arg_parser.add_argument('--slider_scale_linlog', type=int, default='1', help='Lin/Log')
        self.arg_parser.add_argument('--slider_presets', type=int, default=1, help='Select the knob type')

        #sliders colors
        #coarse
        self.arg_parser.add_argument('--slider_coarse_color', type=inkex.Color, default='#fefefe', help='Slider coarse color')
        self.arg_parser.add_argument('--slider_coarse_stroke_color', type=inkex.Color, default='#333333', help='Slider coarse stroke color')

        #cursor
        self.arg_parser.add_argument('--slider_cursor_color', type=inkex.Color, default='#fefefe', help='Slider cursor color')
        self.arg_parser.add_argument('--slider_cursor_stroke_color', type=inkex.Color, default='#fefefe', help='Slider cursor stroke color')
        self.arg_parser.add_argument('--slider_cursor_type', type=int, default=1, help='Select the cursor type')
        self.arg_parser.add_argument('--slider_cursor_tick_color', type=inkex.Color, default='#fefefe', help='Slider cursor tick color')

        #sliders dimension
        #coarse
        self.arg_parser.add_argument('--slider_coarse_lenght', type=float, default=100, help='Coarse')
        self.arg_parser.add_argument('--slider_coarse_gap', type=float, default=6, help='Gap')
        self.arg_parser.add_argument('--slider_coarse_stroke_width', type=float, default=1, help='Coarse stroke width')
        self.arg_parser.add_argument('--slider_coarse_round_edges', type=inkex.Boolean, default='False', help='Round the edges')

        #cursor
        self.arg_parser.add_argument('--slider_cursor_height', type=float, default=100, help='Cursor height')
        self.arg_parser.add_argument('--slider_cursor_width', type=float, default=100, help='Cursor width')
        self.arg_parser.add_argument('--slider_cursor_stroke_width', type=float, default=100, help='Cursor stroke width')
        self.arg_parser.add_argument('--slider_cursor_tick_width', type=float, default=0.1, help='Cursor tick width')
        self.arg_parser.add_argument('--slider_cursor_round_edges', type=float, default='False', help='Round the edges')

        self.arg_parser.add_argument('--slider_pos_define', type=inkex.Boolean, default='False', help='Define slider position')
        self.arg_parser.add_argument('--slider_pos_x', type=float, default='10', help='X position')
        self.arg_parser.add_argument('--slider_pos_y', type=float, default='10', help='Y position')

        #SLIDER SCALES
        self.arg_parser.add_argument('--slider_scale_position', type=int, default='1', help='Position')
        self.arg_parser.add_argument('--slider_scale_h_offset', type=float, default='1', help='H offset')
        self.arg_parser.add_argument('--slider_scale_v_offset', type=float, default='1', help='V offset')

        #slider scale colors
        self.arg_parser.add_argument('--slider_scale_tick_color', type=inkex.Color, default='#fefefe', help='Slider tick color')
        self.arg_parser.add_argument('--slider_scale_subtick_color', type=inkex.Color, default='#fefefe', help='Slider subtick color')
        self.arg_parser.add_argument('--slider_scale_label_color', type=inkex.Color, default='#fefefe', help='Slider label color')
        
        #slider scale ticks
        self.arg_parser.add_argument('--slider_scale_ticks_number', type=int, default='300', help='Number of tick marks')
        self.arg_parser.add_argument('--slider_scale_ticks_start_size', type=float, default='1', help='Ticks start size')
        self.arg_parser.add_argument('--slider_scale_ticks_end_size', type=float, default='1', help='Ticks end size')
        self.arg_parser.add_argument('--slider_scale_ticks_start_lenght', type=float, default='10', help='Ticks start lenght')
        self.arg_parser.add_argument('--slider_scale_ticks_end_lenght', type=float, default='10', help='Ticks end lenght')

        #slider scale subticks
        self.arg_parser.add_argument('--slider_scale_add_subticks', type=inkex.Boolean, default='False', help='Add subticks')
        self.arg_parser.add_argument('--slider_scale_subticks_number', type=int, default='300', help='Number of subtick marks')
        self.arg_parser.add_argument('--slider_scale_subticks_size', type=float, default='300', help='Subticks size')
        self.arg_parser.add_argument('--slider_scale_subtick_lenght', type=float, default='5', help='Subticks lenght')
        
        #slider scale perpendicular line
        self.arg_parser.add_argument('--slider_scale_add_perpendicular_line', type=inkex.Boolean, default='False', help='Add perpendicular line')
        self.arg_parser.add_argument('--slider_scale_perpendicular_line_width', type=float, default='300', help='Perpendicular line width')

        #sliders scale label
        self.arg_parser.add_argument('--slider_scale_add_label', type=inkex.Boolean, default='False', help='Add label')
        self.arg_parser.add_argument('--slider_scale_label_start', type=float, default='1', help='Start')
        self.arg_parser.add_argument('--slider_scale_label_end', type=float, default='10', help='End')
        self.arg_parser.add_argument('--slider_scale_add_plus_sign', type=inkex.Boolean, default='True', help='Add + sign to positive numebrs')
        self.arg_parser.add_argument('--slider_scale_label_rounding_float', type=int, default='0', help='Rounding float')
        self.arg_parser.add_argument('--slider_scale_label_reverse_order', type=inkex.Boolean, default='False', help='Reverse order')
        self.arg_parser.add_argument('--slider_scale_label_position', type=int, default='0', help='Label position')
        self.arg_parser.add_argument('--slider_scale_label_font_size', type=float, default='10', help='Label font size')
        self.arg_parser.add_argument('--slider_scale_label_offset_tl', type=float, default='10', help='Offset')
        self.arg_parser.add_argument('--slider_scale_label_offset_br', type=float, default='10', help='Offset') 
        self.arg_parser.add_argument('--slider_scale_label_offset_adj', type=float, default='10', help='Offset') 

        self.arg_parser.add_argument('--slider_scale_label_add_suffix', help='Label add suffix')

        #slider scale utilities
        self.arg_parser.add_argument('--slider_scale_utilities_add_drill_guide', type=inkex.Boolean, default='True', help='Add drill guide')
        self.arg_parser.add_argument('--slider_scale_utilities_drill_color', type=inkex.Color, default='#333333', help='Utilities color')
        self.arg_parser.add_argument('--slider_scale_utilities_drill_line_width', type=float, default='10', help='Line width')
        self.arg_parser.add_argument('--slider_scale_utilities_guide_round_edges', type=inkex.Boolean, default='False', help='Round guide edges')

        self.arg_parser.add_argument('--slider_scale_utilities_add_pcb_component_guide', type=inkex.Boolean, default='True', help='Add drill guide')
        self.arg_parser.add_argument('--slider_scale_utilities_pcb_color', type=inkex.Color, default='#333333', help='Utilities color')
        self.arg_parser.add_argument('--slider_scale_utilities_pcb_line_width', type=float, default='10', help='Line width')
        self.arg_parser.add_argument('--slider_scale_utilities_pcb_guide_dimension', type=float, default='10', help='Guide dimension')


        #JACKS
        self.arg_parser.add_argument('--jack_name', help='Jack name')
        self.arg_parser.add_argument('--jack_type', type=int, default=1, help='Select the jack type') 
        self.arg_parser.add_argument('--jack_nut_type', type=int, default=1, help='Select the nut type') 
        self.arg_parser.add_argument('--jack_color', type=inkex.Color, default='#000000', help='Jack color')
        self.arg_parser.add_argument('--jack_nut_color', type=inkex.Color, default='#808080', help='Jack nut color')
        self.arg_parser.add_argument('--jack_nut_outline_color', type=inkex.Color, default='#000000', help='Jack nut outline')
        #jack position
        self.arg_parser.add_argument('--jack_pos_define', type=inkex.Boolean, default='False', help='Define jack position')
        self.arg_parser.add_argument('--jack_pos_x', type=float, default='10', help='X position')
        self.arg_parser.add_argument('--jack_pos_y', type=float, default='10', help='Y position')

        #jack utilities
        self.arg_parser.add_argument('--jack_utilities_add_centering_circle', type=inkex.Boolean, default='False', help='Add centering circle')
        self.arg_parser.add_argument('--jack_utilities_centering_color', type=inkex.Color, default='#008000', help='Centering stroke color')
        self.arg_parser.add_argument('--jack_utilities_centering_line_width', type=float, default='10', help='Centering line width')
        self.arg_parser.add_argument('--jack_utilities_centering_guide_offset', type=float, default='10', help='Centering guide offset')

        self.arg_parser.add_argument('--jack_utilities_color', type=inkex.Color, default='#ff00ff', help='Drill stroke color')
        self.arg_parser.add_argument('--jack_utilities_add_drill_guide', type=inkex.Boolean, default='False', help='Add drill guide')
        self.arg_parser.add_argument('--jack_utilities_drill_guide_type', type=int, default='0', help='Drill guide type')
        self.arg_parser.add_argument('--jack_utilities_line_width', type=float, default='10', help='Drill line width')
        self.arg_parser.add_argument('--jack_utilities_guide_dimension', type=float, default='10', help='Drill guide dimension')


        self.arg_parser.add_argument('--jack_utilities_pcb_color', type=inkex.Color, default='#ff00ff', help='Utilities color')
        self.arg_parser.add_argument('--jack_utilities_add_pcb_component_guide', type=inkex.Boolean, default='False', help='Add PCB drill guide')
        self.arg_parser.add_argument('--jack_utilities_component_guide_type', type=int, default='0', help='Drill guide type')
        self.arg_parser.add_argument('--jack_utilities_pcb_line_width', type=float, default='10', help='Line width')
        self.arg_parser.add_argument('--jack_utilities_pcb_guide_dimension', type=float, default='10', help='Guide dimension')
        #Settings
        self.arg_parser.add_argument('--author', help='Author name')
        self.arg_parser.add_argument('--brand', help='Company name')
        self.arg_parser.add_argument('--copyright', help='Copyright')
        self.arg_parser.add_argument('--releasedate', help='Release date')
        self.arg_parser.add_argument('--moduleversion', help='Module version')
        self.arg_parser.add_argument('--logo', help='Company Logo')
        self.arg_parser.add_argument('--globalfont', help='Global font')
        self.arg_parser.add_argument('--globalholecolor', type=inkex.Color, default='#cccccc', help='Global hole color')
        self.arg_parser.add_argument('--globalstrokesize', help='Global stroke size')
        self.arg_parser.add_argument('--globallasercutcolor', type=inkex.Color, default='#cccccc', help='Global lasercut color')
        self.arg_parser.add_argument('--globallasercutstrokesize', help='Global lasercut stroke size')
        
        #About

        #Extra
        self.arg_parser.add_argument('--paneltab')
        self.arg_parser.add_argument('--uitab')

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

    def draw_hex_nut(self, x, y, radius):
        hex = inkex.PathElement()
        hex.set("sodipodi:type", "star")
        hex.set("sodipodi:cx", x)
        hex.set("sodipodi:cy", y)
        hex.set("sodipodi:arg1", 0.0)
        hex.set("sodipodi:arg2", 1.0)
        hex.set("inkscape:rounded", 0)
        hex.set("sodipodi:sides", 3)
        hex.set("sodipodi:r1", radius)
        hex.set("sodipodi:r2", radius)
        return hex
        
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

    def draw_arrow(self, x1, y1, x2, y2, x3, y3, x4, y4, name):
        line = inkex.PathElement()
        line.path = "M {},{} {},{} {},{} {},{} Z".format(x1, y1, x2, y2, x3, y3, x4, y4)
        line.set('inkscape:type', 'line')
        line.set('inkscape:label', name)    
        return line

    def draw_knob_scale_arc(self, cx, cy, angle, rotation, radius, name):
        end = (angle + rotation - pi) / 2.0
        start = pi - end + rotation
        arc = PathElement.arc((cx, cy), radius, start=start, end=end, open=True)
        arc.set('inkscape:type', 'arc')
        arc.set('inkscape:open', 'true')
        arc.set('inkscape:label', name)
        return arc

    def draw_knob_scale_closed_arc(self, cx, cy, angle, rotation, radius):
        end = (angle + rotation - pi) / 2.0
        start = pi - end + rotation
        arc = PathElement.arc((cx, cy), radius, start=start, end=end, open=True)
        arc.set('sodipodi:arc-type', 'arc')
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
    
    def draw_cross(self, x, y, dimension):
        half_dimension = dimension / 2
        path_data = f"M {x} {y - half_dimension} L {x} {y + half_dimension} M {x - half_dimension} {y} L {x + half_dimension} {y}"

        cross = inkex.PathElement()
        cross.path = path_data
        return cross

    def drill_guide(self, parent, x, y, fill, stroke, stroke_width, dimension, type):
        # Create drill guide
        if type == 2: #cross
            cross = self.draw_cross(x, y, dimension)

            cross.style['fill'] = fill
            cross.style['stroke'] = stroke
            cross.style['stroke-width'] = stroke_width
            cross.set('inkscape:label','cross')

            group = inkex.Group.new('Drilling mark')
            group.append(cross)
            parent.append(group)
            
        elif type == 3: #dot
            drill_dot = Circle(cx=str(x), cy=str(y), r=str(dimension /2))

            drill_dot.style['fill'] = stroke
            drill_dot.style['stroke'] = "none"
            drill_dot.style['stroke-width'] = 0

            group = inkex.Group.new('Component mark')
            group.append(drill_dot)
            parent.append(group)

        elif type == 4: #circle  
            drill_circle = Circle(cx=str(x), cy=str(y), r=str(dimension /2 - stroke_width /2))

            drill_circle.style['fill'] = "none"
            drill_circle.style['stroke'] = stroke
            drill_circle.style['stroke-width'] = stroke_width

            group = inkex.Group.new('Component mark')
            group.append(drill_circle)
            parent.append(group)

    def pcb_guide(self, parent, x, y, fill, stroke, stroke_width, dimension):
        # Create pcb guide     
        cross = self.draw_cross(x, y, dimension)

        cross.style['fill'] = fill
        cross.style['stroke'] = stroke
        cross.style['stroke-width'] = stroke_width
        cross.set('inkscape:label','cross')

        group = inkex.Group.new('PCB mark')
        group.append(cross)
        parent.append(group)
        
    def sharecropping_guide(self, parent, w, h, l, t):

        # Create sharecropping guide
        cross_v = self.draw_line( 
        l + w/2, 
        t -2, 
        l + w/2, 
        t + h + 2)

        cross_h = self.draw_line( 
        l - 2,
        t + h/2, 
        l + w + 2,
        t + h/2, 
        )

        if w > h: #horizontal
            cross_h_left = self.draw_line( 
            l + h/2, 
            t - 2, 
            l + h/2, 
            t + h + 2)

            cross_h_right = self.draw_line( 
            l + w - h/2, 
            t -2, 
            l + w - h/2, 
            t + h + 2)

            cross_h_left.style['fill'] = cross_h_right.style['fill'] = "none"
            cross_h_left.style['stroke'] = cross_h_right.style['stroke'] = self.options.slider_scale_utilities_pcb_color
            cross_h_left.style['stroke-width'] = cross_h_right.style['stroke-width'] = self.options.slider_scale_utilities_pcb_line_width

            parent.append(cross_h_left)
            parent.append(cross_h_right)

        else:
            cross_v_top = self.draw_line( 
            l - 2,
            t + w/2, 
            l + w + 2,
            t + w/2, 
            )

            cross_v_bottom = self.draw_line( 
            l - 2,
            t + h - w/2, 
            l + w + 2,
            t + h - w/2, 
            )

            cross_v_top.style['fill'] = cross_v_bottom.style['fill'] = "none"
            cross_v_top.style['stroke'] = cross_v_bottom.style['stroke'] = self.options.slider_scale_utilities_pcb_color
            cross_v_top.style['stroke-width'] = cross_v_bottom.style['stroke-width'] = self.options.slider_scale_utilities_pcb_line_width

            parent.append(cross_v_top)
            parent.append(cross_v_bottom)
        
        cross_v.style['fill'] = cross_h.style['fill'] = "none"
        cross_v.style['stroke'] = cross_h.style['stroke'] = self.options.slider_scale_utilities_pcb_color
        cross_v.style['stroke-width'] = cross_h.style['stroke-width'] = self.options.slider_scale_utilities_pcb_line_width

        parent.append(cross_v)
        parent.append(cross_h)           

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

            if self.options.panel_type == "e3u" :
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

            # Main layer
            main_layer = self.svg.add(inkex.Group.new('Project ' + self.options.panel_name))
            main_layer.set('inkscape:highlight-color', self.options.panel_color)
            main_layer.set('sodipodi:insensitive', 'true')
            main_layer.set('id', 'main-layer')

            # New panel group
            panel_name = self.options.panel_name
            panel_group = main_layer.add(inkex.Group.new('Panel'))
            panel_group.set('sodipodi:insensitive', 'true')
    
            # Panel sub layer
            panel_layer = panel_group.add(inkex.Layer.new(panel_name + '\'s Panel'))  #panel
            panel_layer.set('inkscape:highlight-color','#3ea4e3')
            panel_layer.set('sodipodi:insensitive', 'true')

            if self.options.panel_holes:
                holes_layer = panel_group.add(inkex.Layer.new('Holes layer'))
                holes_layer.set('inkscape:highlight-color','#3ea4e3')
                holes_layer.set('sodipodi:insensitive', 'true')
                holes_group = holes_layer.add(inkex.Group.new('Holes group'))

            if self.options.panel_screws:
                screws_layer = panel_group.add(inkex.Layer.new('Screws layer')) 
                screws_layer.set('inkscape:highlight-color',Green) 
                screws_layer.set('sodipodi:insensitive', 'true')  
                screws_group = screws_layer.add(inkex.Group.new('Screws group'))

            if self.options.panel_centers:
                center_layer = panel_group.add(inkex.Layer.new('Drilling layer'))
                center_layer.set('inkscape:highlight-color', Orange)
                center_layer.set('sodipodi:insensitive', 'true')
                center_layer_g = center_layer.add(inkex.Group.new('Drilling group'))


            # Draw Panel
            panel = self.draw_rectangle(pwidth, pheight, 0, 0, 0, 0)
            panel.set('inkscape:label', 'Panel')
            
            panel_layer.append(panel)
            panel_layer.set('id', 'panel')
            panel_layer.set('inkscape:highlight-color', self.options.panel_color)

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

            # Draw  Eurorack Holes
            # http://www.doepfer.de/a100_man/a100m_e.htm
            if self.options.panel_type == "e1uij" or self.options.panel_type == "e3u" :
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
            #if self.options.panel_screws and self.options.panel_lasercut == False :
            #    self.options.panel_holes == False #remove holes
            if self.options.panel_screws:
                screw_radius = self.options.panel_screw_radius /2
                screw_type = self.options.panel_screw_type
                screw_color  = self.options.panel_screw_color
                screw_stroke_color = self.options.panel_screw_stroke_color
                screw_stroke_width = self.options.panel_screw_stroke_width
                screw_tick_width = self.options.panel_screw_tick_width
                screw_tick_color = self.options.panel_screw_tick_color

                # Bottom Left
                if screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(leftH), y=str(bottomH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(leftH), cy=str(bottomH), r=str(screw_radius)))
                        
                # Top Left
                if screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(leftH), y=str(topH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(leftH), cy=str(topH), r=str(screw_radius)))
                    
                # Bottom Right
                if screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(rightH), y=str(bottomH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(rightH), cy=str(bottomH), r=str(screw_radius)))
                
                # Top Right
                if screw_type == 1:
                    screws_group.append(self.draw_knurled_screw(x=str(rightH), y=str(topH), radius=str(screw_radius), radius2 = str(screw_radius/1.1), sides = 50))
                else:
                    screws_group.append(Circle(cx=str(rightH), cy=str(topH), r=str(screw_radius)))
                
                # screw type
                if screw_type == 2 or screw_type == 3 :
                    screws_group.append(self.draw_line(leftH-holeR, bottomH, leftH+holeR, bottomH))
                    screws_group.append(self.draw_line( leftH-holeR, topH, leftH+holeR, topH))
                    screws_group.append(self.draw_line(rightH-holeR, bottomH, rightH+holeR, bottomH))
                    screws_group.append(self.draw_line(rightH-holeR, topH, rightH+holeR, topH))
                    
                if screw_type == 3 :
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
                    bottom_left_hole = Circle(cx=str(leftH), cy=str(bottomH), r=str(r))
                    bottom_left_hole.set('inkscape:label', 'Bottom left')
                    holes_group.append(bottom_left_hole)

                    # Top Left
                    top_left_hole = Circle(cx=str(leftH), cy=str(topH), r=str(r))
                    top_left_hole.set('inkscape:label', 'Top left')
                    holes_group.append(top_left_hole)

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
                        center_cross_bottom_left = self.draw_cross(leftH, bottomH, 2 * (holeR - gap))
                        center_cross_bottom_left.set('inkscape:label', 'Bottom left')
                        center_layer_g.append(center_cross_bottom_left)

                        #top left centers
                        center_cross_top_left = self.draw_cross(leftH, topH, 2 * (holeR - gap))
                        center_cross_top_left.set('inkscape:label', 'Top left')

                        center_layer_g.append(center_cross_top_left)

                    # Draw the Righthand side Mounting holes
                    if (self.options.panel_type == "e3u" or self.options.panel_type == "e1uij" or self.options.panel_type == "e1upl") and euro_hp > 10 or (self.options.panel_type == "api" and api_units >=2) or (self.options.panel_type == "m5u"  and self.options.moog_panel_units >=2) or (self.options.panel_type == "d5u"  and self.options.moog_panel_units >=2) or self.options.panel_type == "nineteen" or self.options.panel_type == "lw" or self.options.panel_type == "serge" or self.options.panel_type == "buchla" or (self.options.panel_type == "fracrack" and self.options.fracrack_panel_units >  1) :
                        # Bottom Right
                        bottom_right_hole = Circle(cx=str(rightH), cy=str(bottomH), r=str(r))
                        bottom_right_hole.set('inkscape:label', 'Bottom right')
                        holes_group.append(bottom_right_hole)

                        # Top Right
                        top_right_hole = Circle(cx=str(rightH), cy=str(topH), r=str(r))
                        top_right_hole.set('inkscape:label', 'Top right')
                        holes_group.append(top_right_hole)
                        # Draw Right-side Centers
                        if centers == True:
                            center_cross_bottom_right = self.draw_cross(rightH, bottomH, 2 * (holeR - gap))
                            center_cross_bottom_right.set('inkscape:label', 'Bottom right')
                            center_layer_g.append(center_cross_bottom_right)

                            # Top Right Centers
                            center_cross_top_right = self.draw_cross(rightH, topH, 2 * (holeR - gap))
                            center_cross_top_right.set('inkscape:label', 'Top right')
                            center_layer_g.append(center_cross_top_right)

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
                    bottom_left = self.draw_rectangle(oval_width,oval_height,leftH-oval_stretch*unitfactor,bottomH-holeR, holeR,0)
                    bottom_left.set('inkscape:label', 'Bottom left')
                    holes_group.append( bottom_left )

                    # Top Left
                    top_left = self.draw_rectangle(oval_width,oval_height, leftH-oval_stretch*unitfactor,topH-holeR, holeR,0)
                    top_left.set('inkscape:label', 'Top left')
                    holes_group.append(top_left)

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

                    if (self.options.panel_type == "e3u" or self.options.panel_type == "e1uij" or self.options.panel_type == "e1upl")  and euro_hp > 10 or (self.options.panel_type == "lw" and lw_units > 2) or (self.options.panel_type == "nineteen"):
                        # Bottom Right
                        bottom_right = self.draw_rectangle(oval_width,oval_height, rightH-oval_stretch*unitfactor,bottomH-holeR, holeR,0)
                        bottom_right.set('inkscape:label', 'Bottom right')
                        holes_group.append(bottom_right)

                        # Top Right
                        top_right = self.draw_rectangle(oval_width,oval_height, rightH-oval_stretch*unitfactor,topH-holeR, holeR,0)
                        top_right.set('inkscape:label', 'Top right')
                        holes_group.append(top_right)

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
                
                if (self.options.knob_add_arrow and self.options.knob_add_skirt):
                    knob_layer_arrow = knob_layer.add(inkex.Layer.new('Arrow'))
                
                if self.options.knob_main_style == 2:
                    knob_layer_vintage = knob_layer.add(inkex.Layer.new('Vintage knob'))

                knob_layer_main = knob_layer.add(inkex.Layer.new('Main color'))
                

                #append the knob layer to the knobs group
                knobs.append(knob_layer)
            
                #get the page's bounding box
                bbox_panel = self.svg.get_page_bbox()

                if self.options.knob_pos_define:
                    center_x = self.options.knob_pos_x
                    center_y = self.options.knob_pos_y
                else:
                    center_x = bbox_panel.center_x
                    center_y = bbox_panel.center_y
                
                if self.options.knob_main_style == 2:
                    vintage_knob = self.draw_vintage_circle(x=str(center_x), y=str(center_y), radius=str(self.options.knob_vintage_dimension / 2), radius2 = str(self.options.knob_vintage_dimension / 2 + self.options.knob_vintage_transform ), sides = self.options.knob_vintage_sides)
                
                    vintage_knob.style['fill'] = self.options.knob_vintage_color
                    vintage_knob.style['stroke'] = self.options.knob_vintage_stroke_color
                    vintage_knob.style['stroke-width'] = self.options.knob_vintage_stroke_width
                    
                    vintage_knob.set('inkscape:label', 'Vintage')

                mainknob = Circle(cx=str(center_x), cy=str(center_y), r=str(self.options.knob_main_dimension / 2))
                    
                mainknob.set('inkscape:label', 'Main')
                
                if self.options.knob_main_style == 2:
                    knob_layer_vintage.append(vintage_knob)
                    knob_layer_main.append(mainknob)
                else:    
                    knob_layer_main.append(mainknob)

                if self.options.knob_add_skirt:
                    knob_skirt = Circle(cx=str(center_x), cy=str(center_y), r=str(self.options.knob_skirt_dimension / 2))
                    knob_skirt.set('inkscape:label', 'Skirt')
                    knob_layer_skirt.append(knob_skirt)

                tlenght = self.options.knob_tick_lenght

                x2 = tlenght*sin(315*pi/180)
                y2 = tlenght*cos(315*pi/180)

                if self.options.knob_add_tick:
                    knob_layer_tick = knob_layer.add(inkex.Layer.new('Tick'))
                    if self.options.knob_tick_type == 1:
                        thetick = self.draw_line(center_x, center_y, x2+center_x, y2+center_y)
                        thetick.set('inkscape:label', 'Tick')
                        thetick.style['fill'] = 'none'
                        thetick.style['stroke'] = self.options.knob_tick_color

                    else:
                        thetick = Circle(cx=str(x2+center_x), cy=str(y2+center_y), r=str(self.options.knob_tick_width))
                        thetick.style['fill'] = self.options.knob_tick_color
                        thetick.style['stroke'] = 'none'

                    thetick.style['stroke-width'] = self.options.knob_tick_width

                    knob_layer_tick.append(thetick)

                #add arrow

                alenght = self.options.knob_skirt_dimension / 2

                ax2 = alenght*sin(315*pi/180)
                ay2 = alenght*cos(315*pi/180)

                if (self.options.knob_add_arrow and self.options.knob_add_skirt):
                    thearrow = self.draw_arrow(
                                center_x, center_y, 
                                center_x - (self.options.knob_main_dimension/2) - self.options.knob_arrow_width, center_y, 
                                ax2+center_x, ay2+center_y, 
                                center_x, (center_y + self.options.knob_main_dimension /2) + self.options.knob_arrow_width, 'Arrow'
                            )


                    thearrow.style['fill'] = self.options.knob_arrow_color
                    thearrow.style['stroke'] = 'none'
                    thearrow.style['stroke-width'] =  'none'
                    knob_layer_arrow.append(thearrow)

                mainknob.style['fill'] = self.options.knob_main_color
                mainknob.style['stroke'] = self.options.knob_main_stroke_color
                mainknob.style['stroke-width'] = self.options.knob_main_stroke_width

                if self.options.knob_add_skirt:
                    knob_skirt.style['fill'] = self.options.knob_skirt_color
                    knob_skirt.style['stroke'] = self.options.knob_skirt_stroke_color
                    knob_skirt.style['stroke-width'] = self.options.knob_skirt_stroke_width

                self.svg.append(knobs)

        elif part == 3: #knobs scales
            sknob = self.svg.selected
            bboxes = [node.bounding_box().center for node in self.svg.selected.values()]
            centers = [ (c.x,c.y) for c in bboxes] # turn vectors into lists
			
            # find average of all centers.
            if len(centers) > 0:
                center_x = sum([c[0] for c in centers]) / len(centers)
                center_y = sum([c[1] for c in centers]) / len(centers)
                                
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

            #utilities layer
            if self.options.knob_scale_utilities_add_pcb_component_guide or self.options.knob_scale_utilities_add_drill_guide or self.options.knob_scale_add_centering_circle:

                if self.svg.getElementById('knob-scales-utilities') is not None:
                    knob_scales_utilities = self.svg.getElementById('knob-scales-utilities')
                else:
                    knob_scales_utilities = self.svg.add(inkex.Layer.new('Knob Scales Utilities'))
                    knob_scales_utilities.set('id', 'knob-scales-utilities')

            if self.options.knob_scale_add_centering_circle:
                if self.svg.getElementById('knob-scales-utilities-centering') is not None:
                    knob_scales_utilities_centering = self.svg.getElementById('knob-scales-utilities-centering')
                else:
                    knob_scales_utilities_centering = knob_scales_utilities.add(inkex.Layer.new('Centering circles'))
                    knob_scales_utilities_centering.set('id', 'knob-scales-utilities-centering')

            if self.options.knob_scale_utilities_add_drill_guide:
                if self.svg.getElementById('knob-scales-utilities-drilling') is not None:  
                    knob_scales_utilities_drilling = self.svg.getElementById('knob-scales-utilities-drilling') 
                else:            
                    knob_scales_utilities_drilling = knob_scales_utilities.add(inkex.Layer.new('Drill plan'))
                    knob_scales_utilities_drilling.set('id', 'knob-scales-utilities-drilling')

            if self.options.knob_scale_utilities_add_pcb_component_guide:
                if self.svg.getElementById('knob-scales-utilities-pcb') is not None:  
                    knob_scales_utilities_pcb = self.svg.getElementById('knob-scales-utilities-pcb')
                else:
                    knob_scales_utilities_pcb = knob_scales_utilities.add(inkex.Layer.new('PCB plan'))
                    knob_scales_utilities_pcb.set('id', 'knob-scales-utilities-pcb')

            n_ticks = self.options.knob_scale_ticks_number
            n_subticks = self.options.knob_scale_subticks_number

            start_num = self.options.knob_scale_label_start_number
            end_num = self.options.knob_scale_label_end_number
            text_spacing = self.options.knob_scale_label_offset +3
            text_size = self.options.knob_scale_label_font_size

            is_knob_selected = False

            layer = self.svg.get_current_layer()
            parent = layer.getparent()
            selected_label = parent.label

            if sknob:
                is_knob_selected = True

            if( not is_knob_selected):
                inkex.errormsg(_("To draw a scale, you must first select the corresponding knob.\nPlease select the knob's main color."))
            else:   
                knob_name = selected_label
                knob_scale_layer = knob_scales.add(inkex.Layer.new(knob_name)) #new layer with the same name of the knob
                
                angle = self.options.knob_scale_arc_angle*pi/180.0
                arc_rotation = self.options.knob_scale_arc_rotation*pi/180.0 *2
                
                radius = self.options.knob_scale_arc_radius
                offset_radius = self.options.knob_scale_arc_radius + self.options.knob_scale_outer_arc_offset - (self.options.knob_scale_arc_width /2)

                if self.options.knob_scale_add_centering_circle:
                    knob_scale_centering_layer = knob_scales_utilities_centering.add(inkex.Layer.new(knob_name)) #new layer with the same name of the knob
                    centering_circle = Circle(cx=str(center_x), cy=str(center_y), r=str(offset_radius + self.options.knob_scale_utilities_centering_guide_offset)) 

                    centering_circle.style['fill'] = "none"
                    centering_circle.style['stroke'] = self.options.knob_scale_utilities_centering_color
                    centering_circle.style['stroke-width'] = self.options.knob_scale_utilities_centering_line_width

                    centering_circle.set('inkscape:label', 'Circle')

                    knob_scale_centering_layer.append(centering_circle)
                    
                if self.options.knob_scale_utilities_add_drill_guide:
                    knob_scale_drilling_layer = knob_scales_utilities_drilling.add(inkex.Layer.new(knob_name)) #new layer with the same name of the knob

                    fill = "none"
                    stroke = self.options.knob_scale_utilities_color
                    stroke_width = self.options.knob_scale_utilities_line_width
                    dimension = self.options.knob_scale_utilities_guide_dimension
                    type = self.options.knob_scale_utilities_drill_guide_type
                    self.drill_guide(knob_scale_drilling_layer, center_x, center_y, fill, stroke, stroke_width, dimension, type)

                if self.options.knob_scale_utilities_add_pcb_component_guide:
                    knob_scale_pcb_layer = knob_scales_utilities_pcb.add(inkex.Layer.new(knob_name)) #new layer with the same name of the knob

                    fill = "none"
                    stroke = self.options.knob_scale_utilities_pcb_color
                    stroke_width = self.options.knob_scale_utilities_pcb_line_width
                    dimension = self.options.knob_scale_utilities_pcb_guide_dimension
                    self.pcb_guide(knob_scale_pcb_layer, center_x, center_y, fill, stroke, stroke_width, dimension)

                if self.options.knob_scale_add_arc or self.options.knob_scale_add_outer_arc:
                    knob_scale_arc = knob_scale_layer.add(inkex.Layer.new('Arcs'))
                
                if self.options.knob_scale_add_arc:
                    arc = self.draw_knob_scale_arc(center_x, center_y, angle + self.options.knob_scale_arc_angle_offset, arc_rotation, radius, 'Main arc')
                    
                    arc.style['fill'] = 'none'
                    arc.style['stroke'] = self.options.knob_scale_arc_color
                    arc.style['stroke-width'] = self.options.knob_scale_arc_width
                    
                    knob_scale_arc.append(arc)
                
                if self.options.knob_scale_add_outer_arc:
                    outer_arc = self.draw_knob_scale_arc(center_x, center_y, angle + self.options.knob_scale_outer_arc_angle_offset, arc_rotation, offset_radius, 'Outer arc')

                    outer_arc.style['fill'] = 'none'
                    outer_arc.style['stroke'] = self.options.knob_scale_arc_color
                    outer_arc.style['stroke-width'] = self.options.knob_scale_arc_width

                    knob_scale_arc.append(outer_arc)

                    #draw the arc before when the mark are dots
                    if self.options.knob_scale_ticks_type == 2:
                        knob_scale_layer.append(knob_scale_arc)

                if self.options.knob_scale_add_ticks:
                    if n_ticks > 0:
                        knob_scale_ticks = knob_scale_layer.add(inkex.Layer.new('Ticks'))
                        knob_scale_mainticks = knob_scale_ticks.add(inkex.Layer.new('Main ticks'))
                        
                        if self.options.knob_scale_add_subticks:
                            knob_scale_subticks = knob_scale_ticks.add(inkex.Layer.new('Sub ticks'))
                        
                        if self.options.knob_scale_add_tick_dots:
                            knob_scale_dotticks = knob_scale_ticks.add(inkex.Layer.new('Dots ticks'))

                        ticks_start_angle = (1.5*pi - 0.5*angle) + (arc_rotation/2)

                        ticks_delta = angle / (n_ticks - 1)
                        if self.options.knob_scale_add_label:
                            knob_scale_label = knob_scale_layer.add(inkex.Layer.new('Labels'))

                        if self.options.knob_scale_label_customtext:
                            customText = self.options.knob_scale_label_customtext.split(',')
                        
                        count = 1
                        for count, tick in enumerate(range(n_ticks), start=1):
                            
                            if self.options.knob_scale_ticks_type == 1:
                                if(self.options.knob_scale_ticks_accent_number != 0):
                                    if(tick % self.options.knob_scale_ticks_accent_number):
                                        tick_length = self.options.knob_scale_ticks_lenght
                                    else:    
                                        tick_length = self.options.knob_scale_ticks_lenght + self.options.Knob_scale_ticks_accent_lenght
                                else:
                                    ###
                                    ticks_delta =  angle / (n_ticks - 1)
                                    tick_length_start = self.options.knob_scale_ticks_start_lenght
                                    tick_lenght_end = self.options.knob_scale_ticks_end_lenght
                                    ticks_delta_lenght = (tick_lenght_end - tick_length_start) / (n_ticks -1)
                                    tick_length = (ticks_delta_lenght * tick) + tick_length_start
                                    ###
                                    
                                if self.options.knob_scale_inner_ticks:
                                    scale_tick = self.draw_line_mark(center_x, center_y, radius - (self.options.knob_scale_arc_width / 2) - self.options.knob_scale_ticks_offset - tick_length , ticks_start_angle + ticks_delta*tick, tick_length)
                                else:
                                    scale_tick = self.draw_line_mark(center_x, center_y, radius - (self.options.knob_scale_arc_width / 2) + self.options.knob_scale_ticks_offset, ticks_start_angle + ticks_delta*tick, tick_length)
                                        
                                if(self.options.knob_scale_ticks_accent_number != 0):
                                    if(tick % self.options.knob_scale_ticks_accent_number):
                                        scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_width
                                    else:    
                                        scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_accent_width
                                else:
                                    scale_tick.style['stroke-width'] = self.options.knob_scale_ticks_width
                                    
                                scale_tick.set('inkscape:label', 'tick_'+ str(count))

                                scale_tick.style['stroke'] = self.options.knob_scale_ticks_color      
                                knob_scale_mainticks.append(scale_tick) 

                                #add point to the main ticks
                                if self.options.knob_scale_add_tick_dots:
                                    multiple_dots_offset = 0
                                    i = 0
                                    while i < self.options.knob_scale_multiple_dots_number:
                                        tick_dots = self.draw_circle(center_x, center_y, radius +  tick_length + self.options.knob_scale_add_tick_dots_offset + multiple_dots_offset, ticks_start_angle + ticks_delta*tick, self.options.knob_scale_add_tick_dots_radius) 
                                        multiple_dots_offset = multiple_dots_offset + self.options.knob_scale_multiple_dots_offset
                                        i = i+1
                                        knob_scale_dotticks.append(tick_dots)  
                                  
                                        tick_dots.style['fill'] = self.options.knob_scale_ticks_color
                                        tick_dots.style['stroke'] = 'none'
                                        tick_dots.style['stroke-width'] = 0
                                        tick_dots.set('inkscape:label', 'tick_dot_'+ str(count))

                            else:
                                tick_length = self.options.knob_scale_ticks_lenght
                                scale_tick = self.draw_circle(center_x, center_y, radius , ticks_start_angle + ticks_delta*tick, tick_length)
                                
                                scale_tick.set('inkscape:label', 'main_tick_'+ str(count))                                

                                scale_tick.style['fill'] = self.options.knob_scale_ticks_color
                                scale_tick.style['stroke'] = 'none'
                                scale_tick.style['stroke-width'] = 0
                                knob_scale_mainticks.append(scale_tick)
                                

                                #add point to the main ticks
                                if self.options.knob_scale_add_tick_dots:
                                    multiple_dots_offset = 0
                                    i = 0
                                    while i < self.options.knob_scale_multiple_dots_number:
                                        tick_points = self.draw_circle(center_x, center_y, radius +  tick_length + self.options.knob_scale_add_tick_dots_offset + multiple_dots_offset, ticks_start_angle + ticks_delta*tick, self.options.knob_scale_add_tick_dots_radius) 
                                        multiple_dots_offset = multiple_dots_offset + self.options.knob_scale_multiple_dots_offset
                                        i = i+1
                                        
                                        tick_points.set('inkscape:label', 'tick_dot_'+ str(i) + str(count))    
                                        
                                        knob_scale_dotticks.append(tick_points)  

                            if self.options.knob_scale_add_label:
                                if (self.options.knob_scale_label_add_customtext and self.options.knob_scale_label_customtext and len(customText) == n_ticks ):
                                    label = self.draw_text(center_x, center_y, customText[tick], radius + tick_length + text_spacing,
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
                                        

                                    label = self.draw_text(center_x, center_y, tick_text +  (str(self.options.knob_scale_label_add_suffix) if self.options.knob_scale_label_add_suffix else '' ), radius + tick_length + text_spacing, ticks_start_angle + ticks_delta*tick, text_size)
                                
                                    label.set('inkscape:label', tick_text)

                                label.style['text-anchor'] = 'middle'
                                label.style['font-size'] = str(text_size)
                                label.style['dominant-baseline'] = 'auto'
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
                                            knob_scale_subtick = self.draw_line_mark(center_x, center_y, radius - self.options.knob_scale_subticks_offset - subtick_length - (self.options.knob_scale_arc_width / 2), subtick_start_angle + subticks_delta*subtick, subtick_length)
                                        else:
                                            knob_scale_subtick = self.draw_line_mark(center_x, center_y, radius + self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                            
                                        knob_scale_subtick.style['fill'] = 'none'
                                        knob_scale_subtick.style['stroke'] = self.options.knob_scale_subticks_color
                                        knob_scale_subtick.style['stroke-width'] = self.options.knob_scale_subticks_width
                                    else:
                                        if self.options.knob_scale_inner_ticks:
                                            knob_scale_subtick = self.draw_circle(center_x, center_y, radius - (self.options.knob_scale_arc_width / 2) - self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                        else:
                                            knob_scale_subtick = self.draw_circle(center_x, center_y, radius - (self.options.knob_scale_arc_width / 2) + self.options.knob_scale_subticks_offset, subtick_start_angle + subticks_delta*subtick, subtick_length)
                                        knob_scale_subtick.style['fill'] = self.options.knob_scale_subticks_color
                                        knob_scale_subtick.style['stroke'] = 'none'
                                        knob_scale_subtick.style['stroke-width'] = 0

                                    knob_scale_subticks.append(knob_scale_subtick)

                        #draw the arc on top of the tick when the tick are line
                        if (self.options.knob_scale_ticks_type == 1) and self.options.knob_scale_add_arc:
                            knob_scale_layer.append(knob_scale_arc)
                
            #if is_knob_selected == False and missing_knob == False:
            #    inkex.errormsg(_("To draw a scale, you must first select the corresponding knob.\nPlease select the knob's main color."))

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

            bbox = self.svg.get_page_bbox()
            if bbox:
                center_x, center_y = bbox.center

            if self.options.slider_pos_define:
                center_x = self.options.slider_pos_x
                center_y = self.options.slider_pos_y
            else:
                center_x = bbox.center_x
                center_y = bbox.center_y

            coarse = self.draw_rectangle(coarse_width, coarse_lenght, center_x - coarse_width/2, center_y - coarse_lenght/2, rx, ry)

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
                cursor = Circle(cx=str(center_x ), cy=str(center_y), r=str(cursor_radius/2))
            else:
                if self.options.slider_orientation == 1:
                    cursor_width = self.options.slider_cursor_width 
                    cursor_height = self.options.slider_cursor_height - self.options.slider_cursor_stroke_width
                  
                    cursor = self.draw_rectangle(cursor_width - self.options.slider_cursor_stroke_width, cursor_height, center_x - cursor_width/2 + self.options.slider_cursor_stroke_width /2, center_y - cursor_height /2, rx, ry)
                else:
                    cursor_width = self.options.slider_cursor_width  - self.options.slider_cursor_stroke_width
                    cursor_height = self.options.slider_cursor_height - self.options.slider_cursor_stroke_width
                  
                    cursor = self.draw_rectangle(cursor_width, cursor_height, center_x - cursor_width/2, center_y - cursor_height /2, rx, ry)
            
            
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
                sslider = self.svg.selection.first()
                bbox = sslider.bounding_box()

                bboxes = [node.bounding_box().center for node in self.svg.selected.values()]
                centers = [ (c.x,c.y) for c in bboxes] # turn vectors into lists
			
                # find average of all centers.
                if len(centers) > 0:
                    center_x = sum([c[0] for c in centers]) / len(centers)
                    center_y = sum([c[1] for c in centers]) / len(centers)

                     # Calculate bounding box dimensions
                    bboxwidth =  bbox.width
                    bboxheight = bbox.height

                    bboxleft = bbox.left
                    bboxright = bbox.right
                    bboxtop = bbox.top
                    bboxbottom = bbox.bottom
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

                
                if  self.options.slider_scale_utilities_add_drill_guide or self.options.slider_scale_utilities_add_pcb_component_guide:
                    if self.svg.getElementById('slider-scales-utilities') is not None:
                        slider_scales_utilities = self.svg.getElementById('slider-scales-utilities')
                    else:
                        slider_scales_utilities = self.svg.add(inkex.Layer.new('slider Scales Utilities'))
                        slider_scales_utilities.set('id', 'slider-scales-utilities')

                    if self.options.slider_scale_utilities_add_drill_guide: 
                        if self.svg.getElementById('slider-scales-utilities-drilling') is not None:
                            slider_scales_utilities_drilling = self.svg.getElementById('slider-scales-utilities-drilling')
                        else:                     
                            slider_scales_utilities_drilling = slider_scales_utilities.add(inkex.Layer.new('Drilling plan'))
                            slider_scales_utilities_drilling.set('id', 'slider-scales-utilities-drilling')

                    if self.options.slider_scale_utilities_add_pcb_component_guide:
                        if self.svg.getElementById('slider-scales-utilities-pcb') is not None:
                            slider_scales_utilities_pcb = self.svg.getElementById('slider-scales-utilities-pcb')
                        else:                     
                            slider_scales_utilities_pcb = slider_scales_utilities.add(inkex.Layer.new('PCB plan'))
                            slider_scales_utilities_pcb.set('id', 'slider-scales-utilities-pcb')    

                n_ticks = self.options.slider_scale_ticks_number
                n_subticks = self.options.slider_scale_subticks_number
                start_size = self.options.slider_scale_ticks_start_size
                end_size = self.options.slider_scale_ticks_end_size
                position = self.options.slider_scale_position

                start_num = self.options.slider_scale_label_start
                end_num = self.options.slider_scale_label_end

                text_size = self.options.slider_scale_label_font_size

                is_slider_selected = False

                if sslider is not None:
                    is_slider_selected = True
                    layer = self.svg.get_current_layer()
                    parent = layer.getparent()
                    selected_label = parent.label
                    
                if( not is_slider_selected):
                    inkex.errormsg(_("To draw a scale, you must first select the corresponding slider.\nPlease select the slider's course."))
                else:   
                    #vertical  
                   
                    if bboxheight > bboxwidth:
                        ticks_delta = (bboxheight - self.options.slider_scale_v_offset) / (n_ticks - 1)
                        tick_length_start = self.options.slider_scale_ticks_start_lenght
                        tick_lenght_end = self.options.slider_scale_ticks_end_lenght
                        ticks_delta_lenght = (tick_lenght_end - tick_length_start) / (n_ticks -1)

                        layer_name = selected_label
                        slider_scale_layer = slider_scales.add(inkex.Layer.new(layer_name)) #new layer with the same name of the slider
                       
                        slider_scale_label = slider_scale_layer.add(inkex.Layer.new('Label'))

                        if n_ticks > 0:
                            slider_scale_ticks = slider_scale_layer.add(inkex.Layer.new('Ticks'))
                            if self.options.slider_scale_add_perpendicular_line:

                                pline_l = self.draw_line(
                                                bboxleft - self.options.slider_scale_h_offset,  #x1
                                                bboxbottom - (self.options.slider_scale_v_offset /2) + start_size /2,                               #y1    
                                                bboxleft - self.options.slider_scale_h_offset,  #x1
                                                bboxbottom - ticks_delta * (n_ticks -1) - (self.options.slider_scale_v_offset /2) - end_size /2)

                                pline_r = self.draw_line(
                                                bboxright + self.options.slider_scale_h_offset, #x1
                                                bboxbottom - (self.options.slider_scale_v_offset /2) + start_size /2,                               #y1    
                                                bboxright + self.options.slider_scale_h_offset,
                                                bboxbottom - ticks_delta * (n_ticks -1) - (self.options.slider_scale_v_offset /2) - end_size /2)

                            for tick in range(n_ticks):
                                
                                ticks_delta = (bboxheight - self.options.slider_scale_v_offset) / (n_ticks - 1)

                                tick_length = (ticks_delta_lenght * tick) + tick_length_start
                                
                                #left
                                scale_tick_l = self.draw_line(
                                                bboxleft - self.options.slider_scale_h_offset,  
                                                bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2), 
                                                bboxleft - self.options.slider_scale_h_offset - tick_length,  
                                                bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2))

                                #right
                                scale_tick_r = self.draw_line(
                                                bboxright + self.options.slider_scale_h_offset,  #x1
                                                bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2),                               #y1    
                                                bboxright + self.options.slider_scale_h_offset + tick_length,  #x2
                                                bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2))  

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
                                                            bboxright + self.options.slider_scale_label_offset_br + tick_length + self.options.slider_scale_h_offset + text_size,                     
                                                            bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2) + self.options.slider_scale_label_offset_adj,                                    #y
                                                            tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),                                                                                                          #textvalue
                                                            text_size)                                                                                                          #textsize

                                    label_l = self.draw_slider_text(
                                                            bboxleft - self.options.slider_scale_label_offset_tl - tick_length - self.options.slider_scale_h_offset - text_size,                                        #x
                                                            bboxbottom - ticks_delta * tick - (self.options.slider_scale_v_offset /2) + self.options.slider_scale_label_offset_adj,                                    #y
                                                            tick_text  +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),                                                                                                          #textvalue
                                                            text_size)                                                                                                          #textsize

                                    label_l.style['text-anchor'] = label_r.style['text-anchor'] = 'middle'
                                    label_l.style['font-size'] = label_r.style['font-size'] = self.options.slider_scale_label_font_size
                                    label_l.style['dominant-baseline'] = label_r.style['dominant-baseline'] = 'auto'
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
                                            bboxright + self.options.slider_scale_h_offset,  
                                            bboxbottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2), 
                                            bboxright + self.options.slider_scale_h_offset + subtick_length,  
                                            bboxbottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2))                #y2

                                        scale_subtick_l = self.draw_line(
                                            bboxleft - self.options.slider_scale_h_offset,  
                                            bboxbottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2), 
                                            bboxleft - self.options.slider_scale_h_offset - subtick_length,  
                                            bboxbottom - ticks_delta * tick - subticks_delta * (subtick +1) - (self.options.slider_scale_v_offset /2))

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
                    
                    #horizontal
                    elif bboxwidth > bboxheight: 
                        ticks_delta = (bboxwidth - self.options.slider_scale_h_offset) / (n_ticks - 1)
                        tick_length_start = self.options.slider_scale_ticks_start_lenght
                        tick_lenght_end = self.options.slider_scale_ticks_end_lenght
                        ticks_delta_lenght = (tick_lenght_end - tick_length_start) / (n_ticks -1)

                        layer_name = selected_label
                        slider_scale_layer = slider_scales.add(inkex.Layer.new(layer_name)) #new layer with the same name of the slider
                        
                        slider_scale_label = slider_scale_layer.add(inkex.Layer.new('Label'))

                        if n_ticks > 0:
                            slider_scale_ticks = slider_scale_layer.add(inkex.Layer.new('Ticks'))
                            if self.options.slider_scale_add_perpendicular_line:

                                pline_t = self.draw_line(
                                                bboxleft + (self.options.slider_scale_h_offset /2) + start_size /2,
                                                bboxtop - self.options.slider_scale_v_offset,  #x1
                                                bboxleft + bboxwidth - (self.options.slider_scale_h_offset /2) - end_size /2,
                                                bboxtop - self.options.slider_scale_v_offset)  #x1

                                pline_b = self.draw_line(
                                                bboxleft + (self.options.slider_scale_h_offset /2) + start_size /2,
                                                bboxbottom + self.options.slider_scale_v_offset,  #x1
                                                bboxleft + bboxwidth - (self.options.slider_scale_h_offset /2) - end_size /2,
                                                bboxbottom + self.options.slider_scale_v_offset)  #x1

                            for tick in range(n_ticks):
                                ticks_delta = (bboxwidth - self.options.slider_scale_h_offset) / (n_ticks - 1)
                                tick_length = (ticks_delta_lenght * tick) + tick_length_start
                                delta_size =  (self.options.slider_scale_ticks_end_size - self.options.slider_scale_ticks_start_size) / (n_ticks - 1)
                                ticksize = (delta_size * tick) + self.options.slider_scale_ticks_start_size
                                    
                                #top
                                scale_tick_t = self.draw_line(
                                            bboxleft +  ticks_delta * tick + self.options.slider_scale_h_offset /2 ,
                                            bboxtop - self.options.slider_scale_v_offset + self.options.slider_scale_perpendicular_line_width /2,  
                                            bboxleft +  ticks_delta * tick + self.options.slider_scale_h_offset /2,
                                            bboxtop - self.options.slider_scale_v_offset - tick_length)

                                #bottom
                                scale_tick_b = self.draw_line(
                                            bboxleft +  ticks_delta * tick + self.options.slider_scale_h_offset /2 ,
                                            bboxbottom + (self.options.slider_scale_v_offset) - self.options.slider_scale_perpendicular_line_width /2,  
                                            bboxleft +  ticks_delta * tick + self.options.slider_scale_h_offset /2,
                                            bboxbottom + self.options.slider_scale_v_offset + tick_length)

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
                                                        bboxleft + ticks_delta * tick + (self.options.slider_scale_h_offset /2),
                                                        bboxtop - self.options.slider_scale_v_offset - self.options.slider_scale_label_offset_tl - tick_length - text_size,
                                                            tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),    
                                                            text_size)   

                                    label_b = self.draw_slider_text(
                                                        bboxleft + ticks_delta * tick + (self.options.slider_scale_h_offset /2),
                                                        bboxbottom + self.options.slider_scale_v_offset + self.options.slider_scale_label_offset_br + tick_length + text_size,
                                                        tick_text +  ((self.options.slider_scale_label_add_suffix) if self.options.slider_scale_label_add_suffix  else '' ),        
                                                        text_size)        
                                    
                                    label_b.style['text-anchor'] = label_t.style['text-anchor'] = 'middle'
                                    label_b.style['font-size'] = label_t.style['font-size'] = self.options.slider_scale_label_font_size
                                    label_b.style['dominant-baseline'] = label_t.style['dominant-baseline'] = 'auto'
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
                                            bboxleft + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                            bboxtop - self.options.slider_scale_v_offset + self.options.slider_scale_ticks_start_size /2, 
                                            bboxleft + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                            bboxtop - self.options.slider_scale_v_offset - subtick_length)

                                        scale_subtick_l = self.draw_line(
                                            bboxleft + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                            bboxbottom + self.options.slider_scale_v_offset - self.options.slider_scale_ticks_start_size /2, 
                                            bboxleft + ticks_delta * tick + subticks_delta * (subtick +1) + (self.options.slider_scale_h_offset /2),
                                            bboxbottom + self.options.slider_scale_v_offset + subtick_length)        

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

                    if self.options.slider_scale_utilities_add_drill_guide: 
                        slider_scale_drilling_layer = slider_scales_utilities_drilling.add(inkex.Layer.new(layer_name)) #new layer with the same name of the slider

                        if self.options.slider_scale_utilities_guide_round_edges:
                            if bboxwidth > bboxheight:
                                rx = ry = bboxheight /2
                            elif bboxwidth < bboxheight:
                                rx = ry = bboxwidth /2
                        else:
                            rx = ry = 0

                        drill_guide = self.draw_rectangle(bboxwidth, bboxheight, bboxleft , bboxtop, rx, ry)
                    
                        drill_guide.style['fill'] = "none"
                        drill_guide.style['stroke'] = self.options.slider_scale_utilities_drill_color
                        drill_guide.style['stroke-width'] = self.options.slider_scale_utilities_drill_line_width

                        slider_scale_drilling_layer.append(drill_guide)

                    #pcb guide     
                    if self.options.slider_scale_utilities_add_pcb_component_guide: 
                        slider_scale_pcb_layer = slider_scales_utilities_pcb.add(inkex.Layer.new(layer_name)) #new layer with the same name of the slider

                        if self.options.slider_scale_utilities_guide_round_edges:
                            if bboxwidth > bboxheight:
                                rx = ry = bboxheight /2
                            elif bboxwidth < bboxheight:
                                rx = ry = bboxwidth /2
                        else:
                            rx = ry = 0

                        pcb_guide = self.draw_rectangle(bboxwidth, bboxheight, bboxleft , bboxtop, rx, ry)
                        pcb_guide.style['fill'] = "none"
                        pcb_guide.style['stroke'] = self.options.slider_scale_utilities_pcb_color
                        pcb_guide.style['stroke-width'] = self.options.slider_scale_utilities_pcb_line_width
                        slider_scale_pcb_layer.append(pcb_guide)

                        #sharecropping line
                        sharecropping = self.sharecropping_guide(slider_scale_pcb_layer, bboxwidth, bboxheight, bboxleft , bboxtop)   

        elif part == 6: #jacks
            if self.svg.getElementById('jacks-group') is not None:
                jacks = self.svg.getElementById('jacks-group')
            else:
                jacks = self.svg.add(inkex.Layer.new('Jacks Group'))
                jacks.set('id', 'jacks-group')

            #utilities layer
            if self.options.jack_utilities_add_pcb_component_guide or self.options.jack_utilities_add_drill_guide or self.options.jack_utilities_add_centering_circle :
                if self.svg.getElementById('jacks-utilities') is not None:
                    jack_utilities = self.svg.getElementById('jacks-utilities')
                else:
                    jack_utilities = self.svg.add(inkex.Layer.new('Jacks Utilities'))
                    jack_utilities.set('id', 'jacks-utilities')
                if self.options.jack_utilities_add_centering_circle:
                    jack_utilities_centering = jack_utilities.add(inkex.Layer.new('Centering circles'))
                    jack_utilities_centering.set('id', 'jacks-utilities-centering')
                if self.options.jack_utilities_add_drill_guide:
                    jack_utilities_drilling = jack_utilities.add(inkex.Layer.new('Drill plan'))
                    jack_utilities_drilling.set('id', 'jacks-utilities-drilling')
                if self.options.jack_utilities_add_pcb_component_guide:
                    jack_utilities_pcb = jack_utilities.add(inkex.Layer.new('PCB plan'))
                    jack_utilities_pcb.set('id', 'jacks-utilities-pcb')

            # Jack sub layer
            if self.options.jack_name is None:
                inkex.errormsg(_('Please add the jack name, will be used to create layer with a proper name'))
            else:
                if self.options.jack_type == 1:
                    jack_radius = 2.375
                    jack_thickness = 1.25
                    if self.options.jack_nut_type == 1:
                        nut_radius = 4.0
                    elif self.options.jack_nut_type == 2:
                        nut_radius = 4.0
                    else:
                        nut_radius = 4.5
                elif self.options.jack_type == 2:
                    jack_radius = 3.85
                    jack_thickness = 1.3
                    if self.options.jack_nut_type == 1:
                        nut_radius = 6.0
                    elif self.options.jack_nut_type == 2:
                        nut_radius = 6.25
                    else:
                        nut_radius = 7.5

                jack_layer = jacks.add(inkex.Layer.new(self.options.jack_name)) #jack layer
                jack_layer_main = jack_layer.add(inkex.Layer.new('Main color'))

                #append the jack layer to the jacks group
                jacks.append(jack_layer)
            
                #get the panel's bounding box
                panel = self.svg.get_page_bbox()
                p_center_x, p_center_y = panel.center

                if self.options.jack_pos_define:
                    center_x = self.options.jack_pos_x
                    center_y = self.options.jack_pos_y
                else:
                    center_x = p_center_x
                    center_y = p_center_y

                mainjack = Circle(cx=str(center_x), cy=str(center_y), r=str(jack_radius))
                    
                mainjack.set('id', 'id_'+self.options.jack_name)
                jack_layer_main.append(mainjack)
                mainjack.style['fill'] = '#000000'
                mainjack.style['stroke'] = self.options.jack_color
                mainjack.style['stroke-width'] = str(jack_thickness)

                if self.options.jack_nut_type == 1:
                    # knurled nut
                    thenut = self.draw_knurled_screw(x=str(center_x), y=str(center_y), radius=str(nut_radius), radius2 = str(nut_radius/1.05), sides = 50)
                    thenut.style['fill'] = self.options.jack_nut_color
                    thenut.style['stroke'] = self.options.jack_nut_outline_color
                    thenut.style['stroke-width'] = str(0.1)
                    jack_layer_nut = jack_layer.add(inkex.Layer.new('Nut'))
                    jack_layer_nut.append(thenut)

                elif self.options.jack_nut_type == 2:
                    # metal hex nut
                    thenut = self.draw_hex_nut(x=str(center_x), y=str(center_y), radius=str(nut_radius))
                    thenut.style['fill'] = self.options.jack_nut_color
                    thenut.style['stroke'] = self.options.jack_nut_outline_color
                    thenut.style['stroke-width'] = str(0.1)
                    jack_layer_nut = jack_layer.add(inkex.Layer.new('Nut'))
                    jack_layer_nut.append(thenut)

                elif self.options.jack_nut_type == 3:
                    # plastic hex nut (with skirt)
                    thenutskirt = Circle(cx=str(center_x), cy=str(center_y), r=str(nut_radius + 2))
                    thenutskirt.style['fill'] = self.options.jack_nut_color
                    thenutskirt.style['stroke'] = self.options.jack_nut_outline_color
                    thenutskirt.style['stroke-width'] = str(0.1)
                    jack_layer_nut_skirt = jack_layer.add(inkex.Layer.new('Nut skirt'))
                    jack_layer_nut_skirt.append(thenutskirt)


                if self.options.jack_utilities_add_drill_guide:
                    jack_drilling_layer = jack_utilities_drilling.add(inkex.Layer.new(self.options.jack_name)) #new layer with the same name of the jack

                    fill = "none"
                    stroke = self.options.jack_utilities_color
                    stroke_width = self.options.jack_utilities_line_width
                    dimension = self.options.jack_utilities_guide_dimension
                    type = self.options.jack_utilities_drill_guide_type
                    self.drill_guide(jack_drilling_layer, center_x, center_y, fill, stroke, stroke_width, dimension, type)

                if self.options.jack_utilities_add_pcb_component_guide:
                    jack_pcb_layer = jack_utilities_pcb.add(inkex.Layer.new(self.options.jack_name)) #new layer with the same name of the jack

                    fill = "none"
                    stroke = self.options.jack_utilities_pcb_color
                    stroke_width = self.options.jack_utilities_pcb_line_width
                    dimension = self.options.jack_utilities_pcb_guide_dimension
                    self.pcb_guide(jack_pcb_layer, center_x, center_y, fill, stroke, stroke_width, dimension)

                if self.options.jack_utilities_add_centering_circle:
                    jack_cc = jack_utilities_centering.add(inkex.Layer.new(self.options.jack_name))
                    centering_circle = Circle(cx=str(center_x), cy=str(center_y), r=str(nut_radius + self.options.jack_utilities_centering_guide_offset))

                    centering_circle.style['fill'] = "none"
                    centering_circle.style['stroke'] = self.options.jack_utilities_centering_color
                    centering_circle.style['stroke-width'] = self.options.jack_utilities_centering_line_width

                    jack_cc.append(centering_circle)

                self.svg.append(jacks)


# Borrowed from inkscape-extensions 1.1, remove when Inkscape 1.1 comes out
def composed_transform(elem, other=None):
    parent = elem.getparent()
    if parent is not None and isinstance(parent, ShapeElement):
        return parent.composed_transform() * elem.transform
    return elem.transform

if __name__ == '__main__':
    # Create effect instance and apply it.
    SynthPanelEffect().run()