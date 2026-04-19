#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCAD Bridge - AI Controlled AutoCAD for Roll Forming Drawings
Connects with OpenClaw/Opus 4.7

USAGE:
    python autocad_bridge.py --draw c-channel
    python autocad_bridge.py --profile C-150
    python autocad_bridge.py --flower 7pass
    python autocad_bridge.py --rolls shaft-50mm
"""

import os
import sys
import time
import win32com.client
from win32com.client import constants
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoCADBridge:
    """Control AutoCAD via COM for Roll Forming Drawings"""

    def __init__(self):
        self.acad = None
        self.doc = None
        self.model_space = None

    def connect(self):
        """Connect to running AutoCAD or start new instance"""
        try:
            logger.info("Connecting to AutoCAD...")
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.doc = self.acad.ActiveDocument
            self.model_space = self.doc.ModelSpace
            self.acad.Visible = True
            logger.info("[OK] AutoCAD connected!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def start_autocad(self):
        """Start AutoCAD if not running"""
        try:
            logger.info("Starting AutoCAD...")
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acad.Visible = True
            self.doc = self.acad.ActiveDocument
            self.model_space = self.doc.ModelSpace
            logger.info("[OK] AutoCAD started!")
            return True
        except Exception as e:
            logger.error(f"Failed to start AutoCAD: {e}")
            return False

    def set_layer(self, layer_name, color=7):
        """Create or set layer"""
        try:
            layers = self.doc.Layers
            try:
                layer = layers.Add(layer_name)
            except:
                layer = layers.Item(layer_name)
            layer.Color = color
            return layer
        except Exception as e:
            logger.error(f"Layer error: {e}")
            return None

    def draw_line(self, start, end, layer="0"):
        """Draw a line"""
        try:
            self.set_layer(layer)
            line = self.model_space.AddLine(
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3, start),
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3, end)
            )
            line.Layer = layer
            return line
        except Exception as e:
            logger.error(f"Line error: {e}")
            return None

    def draw_polyline(self, points, layer="0"):
        """Draw a polyline (for profiles)"""
        try:
            self.set_layer(layer)
            # Create array of doubles
            import pythoncom
            points_array = pythoncom.MakeVariants(pythoncom.VT_R8, points)
            polyline = self.model_space.AddPolyline(points_array)
            polyline.Layer = layer
            return polyline
        except Exception as e:
            logger.error(f"Polyline error: {e}")
            return None

    def draw_text(self, point, text, height=2.5, layer="TEXT"):
        try:
            self.set_layer(layer, 1)  # Red
            text_obj = self.model_space.AddText(
                text,
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3, point),
                height
            )
            text_obj.Layer = layer
            return text_obj
        except Exception as e:
            logger.error(f"Text error: {e}")
            return None

    def add_dimension(self, point1, point2, text="", layer="DIM"):
        """Add dimension"""
        try:
            self.set_layer(layer, 3)  # Green
            dim = self.model_space.AddDimAligned(
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3, point1),
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3, point2),
                win32com.client.VARIANT(win32com.clientVT_BYREF, 3,
                    [(point1[0]+point2[0])/2, (point1[1]+point2[1])/2, 0])
            )
            dim.Layer = layer
            return dim
        except Exception as e:
            logger.error(f"Dimension error: {e}")
            return None

    def draw_c_channel(self, web=100, flange=50, lip=15, thickness=2, scale=1):
        """Draw C-Channel profile"""
        logger.info(f"Drawing C-Channel: {web}x{flange}x{flange}x{lip}")

        web_h = web * scale
        flange_w = flange * scale
        lip_h = lip * scale
        t = thickness * scale

        # Points for C-Channel profile (unfolded view)
        #     ┌────┐ ← Web top
        #   ┌─┘    └─┐ ← Flanges + Lips
        #   │        │
        #   └─┬──────┘ ← Web bottom
        #     │

        points = [
            0, 0, 0,                    # Start bottom-left
            0, web_h, 0,                 # Top of web
            flange_w, web_h, 0,           # Top of flange
            flange_w, web_h + lip_h, 0,    # Lip outer top
            flange_w - t, web_h + lip_h, 0, # Lip inner
            flange_w - t, web_h + t, 0,   # Flange inner top
            t, web_h + t, 0,              # Web inner top
            t, t, 0,                      # Web inner bottom
            flange_w - t, t, 0,           # Flange inner bottom
            flange_w - t, 0, 0,           # Flange outer bottom
            flange_w, 0, 0,               # Flange bottom
            0, 0, 0                       # Close
        ]

        self.draw_polyline(points, "PROFILE")

        # Add dimensions
        # Web height dimension
        self.add_dimension([20, 0, 0], [20, web_h, 0], f"Web: {web}")

        # Flange width dimension
        self.add_dimension([0, -10, 0], [flange_w, -10, 0], f"Flange: {flange}")

        # Lip dimension
        self.add_dimension([flange_w + 10, web_h, 0],
                          [flange_w + 10, web_h + lip_h, 0], f"Lip: {lip}")

        # Add title
        self.draw_text([flange_w + 30, web_h/2, 0],
                       f"C-CHANNEL PROFILE\nWeb: {web}mm\nFlange: {flange}mm\nLip: {lip}mm\nThickness: {thickness}mm",
                       height=5)

        logger.info("[OK] C-Channel profile drawn!")
        return True

    def draw_z_purlin(self, web=150, flange=50, lip=15, thickness=2, scale=1):
        """Draw Z-Purlin profile"""
        logger.info(f"Drawing Z-Purlin: {web}x{flange}")

        # Z-Profile shape
        #         ┌────┐
        #     ┌───┘    └──┐
        #     │            │ ← Beak
        #     │            └──┐
        #     └───────────────┘

        web_h = web * scale
        flange_w = flange * scale
        lip_h = lip * scale
        t = thickness * scale

        # Simplified Z shape
        points = [
            0, 0, 0,
            0, web_h - flange_w - lip_h, 0,    # Up web
            flange_w, web_h - lip_h, 0,        # Bottom flange
            flange_w, web_h, 0,                 # Beak start
            flange_w - t, web_h, 0,             # Beak inner
            flange_w - t, web_h - lip_h, 0,     # Beak inner
            t, web_h - flange_w - lip_h, 0,     # Web inner
            t, t, 0,                           # Bottom
            0, 0, 0
        ]

        self.draw_polyline(points, "PROFILE")

        # Title
        self.draw_text([flange_w + 20, web_h/2, 0],
                       f"Z-PURLIN PROFILE\nWeb: {web}mm\nFlange: {flange}mm\nLip: {lip}mm",
                       height=5)

        logger.info("[OK] Z-Purlin profile drawn!")
        return True

    def draw_flower_pattern(self, num_passes=7, profile="C-Channel"):
        """Draw flower pattern (pass sequence)"""
        logger.info(f"Drawing Flower Pattern for {num_passes} passes")

        layer_name = "FLOWER"
        self.set_layer(layer_name, 4)  # Cyan

        # Draw 7 passes for C-Channel
        y_start = 100
        spacing = 60

        for i in range(num_passes):
            y = y_start + i * spacing
            pass_num = i + 1

            # Draw partial profile at each pass
            if profile == "C-Channel":
                # Simplified flower pattern visualization
                angle = (pass_num / num_passes) * 90  # Progressive bending

                # Draw pass shape
                points = [
                    50, y, 0,
                    50, y + 30 + angle/3, 0,
                    100, y + 30 + angle/3, 0,
                    100, y + 35 + angle/3, 0,
                    95, y + 40 + angle/3, 0,
                    55, y + 40, 0,
                    55, y + 5, 0,
                    50, y + 5, 0,
                    50, y, 0
                ]

                self.draw_polyline(points, layer_name)

                # Pass number
                self.draw_text([20, y + 20, 0], f"Pass {pass_num}", height=4)

                # Angle indicator
                self.draw_text([110, y + 20, 0], f"{angle:.0f}°", height=3)

        # Title
        self.draw_text([200, y_start + spacing * num_passes / 2, 0],
                       f"FLOWER PATTERN\nProfile: {profile}\nTotal Passes: {num_passes}",
                       height=6)

        logger.info("[OK] Flower pattern drawn!")
        return True

    def draw_roll_assembly(self, shaft_dia=50, roll_dia=160, num_rolls=6):
        """Draw roll assembly side view"""
        logger.info(f"Drawing Roll Assembly: {num_rolls} rolls")

        self.set_layer("ROLLS", 5)  # Blue

        spacing = 200
        x_start = 100
        shaft_y = 50

        # Draw main shaft
        shaft_length = num_rolls * spacing + 100
        self.draw_line([x_start - 50, shaft_y, 0],
                      [x_start + shaft_length, shaft_y, 0], "SHAFT")

        for i in range(num_rolls):
            x = x_start + i * spacing
            pass_num = i + 1

            # Draw top roll
            self.draw_line([x - roll_dia/2, shaft_y, 0],
                          [x - roll_dia/2, shaft_y + roll_dia, 0], "ROLLS")
            self.draw_line([x + roll_dia/2, shaft_y, 0],
                          [x + roll_dia/2, shaft_y + roll_dia, 0], "ROLLS")
            self.draw_line([x - roll_dia/2, shaft_y + roll_dia, 0],
                          [x + roll_dia/2, shaft_y + roll_dia, 0], "ROLLS")

            # Draw bottom roll
            self.draw_line([x - roll_dia/2, shaft_y - roll_dia, 0],
                          [x + roll_dia/2, shaft_y - roll_dia, 0], "ROLLS")
            self.draw_line([x - roll_dia/2, shaft_y - roll_dia, 0],
                          [x - roll_dia/2, shaft_y, 0], "ROLLS")
            self.draw_line([x + roll_dia/2, shaft_y - roll_dia, 0],
                          [x + roll_dia/2, shaft_y, 0], "ROLLS")

            # Pass number
            self.draw_text([x - 5, shaft_y + roll_dia + 15, 0], f"P{pass_num}", height=4)

        # Shaft label
        self.draw_text([x_start - 70, shaft_y - 20, 0],
                       f"Main Shaft: Ø{shaft_dia}mm\nRoll Diameter: Ø{roll_dia}mm\nPasses: {num_rolls}",
                       height=4)

        logger.info("[OK] Roll assembly drawn!")
        return True

    def draw_shaft_detail(self, shaft_dia=50, length=350):
        """Draw shaft detail with keyway"""
        logger.info(f"Drawing Shaft Detail: Ø{shaft_dia}x{length}")

        # Front view (circle)
        center = [100, 200, 0]
        import pythoncom
        circle = self.model_space.AddCircle(
            win32com.client.VARIANT(win32com.clientVT_BYREF, 3, center),
            shaft_dia / 2
        )
        circle.Layer = "SHAFT"

        # Center lines
        self.draw_line([100 - shaft_dia, 200, 0],
                      [100 + shaft_dia, 200, 0], "CENTER")
        self.draw_line([100, 200 - shaft_dia, 0],
                      [100, 200 + shaft_dia, 0], "CENTER")

        # Keyway detail
        keyway_w = shaft_dia * 0.3
        keyway_h = shaft_dia * 0.15
        kv_points = [
            100 - keyway_w/2, 200, 0,
            100 - keyway_w/2, 200 + keyway_h, 0,
            100 + keyway_w/2, 200 + keyway_h, 0,
            100 + keyway_w/2, 200, 0,
            100 - keyway_w/2, 200, 0
        ]
        self.draw_polyline(kv_points, "KEYWAY")

        # Side view
        side_x = 300
        self.draw_line([side_x, 200 - shaft_dia/2, 0],
                      [side_x + length, 200 - shaft_dia/2, 0], "SHAFT")
        self.draw_line([side_x, 200 + shaft_dia/2, 0],
                      [side_x + length, 200 + shaft_dia/2, 0], "SHAFT")
        self.draw_line([side_x, 200 - shaft_dia/2, 0],
                      [side_x, 200 + shaft_dia/2, 0], "SHAFT")
        self.draw_line([side_x + length, 200 - shaft_dia/2, 0],
                      [side_x + length, 200 + shaft_dia/2, 0], "SHAFT")

        # Keyway in side view
        kv_pos = length * 0.2
        kv_len = shaft_dia * 0.8
        self.draw_line([side_x + kv_pos, 200 - shaft_dia/2, 0],
                      [side_x + kv_pos, 200 - shaft_dia/2 - 10, 0], "KEYWAY")
        self.draw_line([side_x + kv_pos + kv_len, 200 - shaft_dia/2, 0],
                      [side_x + kv_pos + kv_len, 200 - shaft_dia/2 - 10, 0], "KEYWAY")
        self.draw_line([side_x + kv_pos, 200 - shaft_dia/2 - 10, 0],
                      [side_x + kv_pos + kv_len, 200 - shaft_dia/2 - 10, 0], "KEYWAY")

        # Dimensions
        self.add_dimension([side_x, 200 - shaft_dia - 30, 0],
                          [side_x + length, 200 - shaft_dia - 30, 0], f"Length: {length}mm")
        self.add_dimension([side_x - 30, 200 - shaft_dia/2, 0],
                          [side_x - 30, 200 + shaft_dia/2, 0], f"Ø{shaft_dia}mm")

        # Title
        self.draw_text([side_x, 200 + shaft_dia + 30, 0],
                       f"SHAFT DETAIL\nDiameter: Ø{shaft_dia}mm\nLength: {length}mm\nMaterial: EN8",
                       height=5)

        logger.info("[OK] Shaft detail drawn!")
        return True

    def draw_bearing_mount(self, shaft_dia=50, bearing="6310"):
        """Draw bearing mounting detail"""
        logger.info(f"Drawing Bearing Mount: {bearing} on Ø{shaft_dia}mm shaft")

        # Bearing outer diameter lookup
        bearing_sizes = {
            "6308": (40, 90, 23),
            "6310": (50, 110, 27),
            "6312": (60, 130, 31),
        }

        if bearing in bearing_sizes:
            bore, od, width = bearing_sizes[bearing]
        else:
            bore, od, width = shaft_dia, shaft_dia * 2.2, shaft_dia * 0.5

        center = [200, 150, 0]

        # Shaft (center)
        self.draw_line([center[0], center[1] - shaft_dia/2, 0],
                      [center[0], center[1] + shaft_dia/2, 0], "SHAFT")

        # Bearing outer
        import pythoncom
        outer = self.model_space.AddCircle(
            win32com.client.VARIANT(win32com.clientVT_BYREF, 3, center),
            od / 2
        )
        outer.Layer = "BEARING"

        # Bearing inner
        inner = self.model_space.AddCircle(
            win32com.client.VARIANT(win32com.clientVT_BYREF, 3, center),
            bore / 2
        )
        inner.Layer = "BEARING"

        # Dimension
        self.add_dimension([center[0] + od/2 + 20, center[1] - shaft_dia/2, 0],
                          [center[0] + od/2 + 20, center[1] + shaft_dia/2, 0],
                          f"Shaft: Ø{shaft_dia}mm")
        self.add_dimension([center[0] + od/2 + 40, center[1] - od/2, 0],
                          [center[0] + od/2 + 40, center[1] + od/2, 0],
                          f"OD: Ø{od}mm")

        # Title
        self.draw_text([center[0], center[1] - 80, 0],
                       f"BEARING MOUNT\nBearing: {bearing}\nBore: Ø{bore}mm\nOD: Ø{od}mm",
                       height=4)

        logger.info("[OK] Bearing mount drawn!")
        return True

    def setup_layers(self):
        """Setup standard layers"""
        layers_config = [
            ("0", 7, "Default layer"),
            ("PROFILE", 1, "Roll Forming Profile"),
            ("FLOWER", 4, "Flower Pattern"),
            ("ROLLS", 5, "Roll Assembly"),
            ("SHAFT", 2, "Shaft and keyway"),
            ("BEARING", 3, "Bearing details"),
            ("CENTER", 1, "Center lines"),
            ("DIM", 3, "Dimensions"),
            ("TEXT", 1, "Text and labels"),
            ("KEYWAY", 6, "Keyway details"),
        ]

        for name, color, desc in layers_config:
            self.set_layer(name, color)

        logger.info("[OK] Layers configured!")

    def new_drawing(self):
        """Create new drawing"""
        import time
        try:
            time.sleep(0.5)  # Wait for AutoCAD to be ready
            self.doc = self.acad.Documents.Add()
            time.sleep(0.5)
            self.model_space = self.doc.ModelSpace
            self.setup_layers()
            logger.info("OK - New drawing created!")
            return True
        except Exception as e:
            logger.error(f"New drawing error: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AutoCAD Bridge for Roll Forming")
    parser.add_argument("--draw", choices=["c-channel", "z-purlin", "omega", "hat"],
                       help="Draw profile type")
    parser.add_argument("--profile", help="Profile dimensions (e.g., C-150)")
    parser.add_argument("--flower", type=int, help="Draw flower pattern with N passes")
    parser.add_argument("--rolls", help="Draw roll assembly")
    parser.add_argument("--shaft", help="Draw shaft detail")
    parser.add_argument("--bearing", help="Draw bearing mount")
    parser.add_argument("--all", action="store_true", help="Draw complete set")
    parser.add_argument("--new", action="store_true", help="Start new drawing")

    args = parser.parse_args()

    acad = AutoCADBridge()

    if args.new:
        acad.connect()
        acad.new_drawing()
    else:
        acad.connect()

    if args.draw == "c-channel" or args.profile:
        acad.draw_c_channel(web=150, flange=50, lip=15, thickness=2)

    if args.draw == "z-purlin":
        acad.draw_z_purlin(web=150, flange=50, lip=15)

    if args.flower:
        acad.draw_flower_pattern(num_passes=args.flower)

    if args.rolls:
        acad.draw_roll_assembly()

    if args.shaft:
        acad.draw_shaft_detail()

    if args.bearing:
        acad.draw_bearing_mount()

    if args.all:
        acad.new_drawing()
        acad.draw_c_channel()
        acad.draw_flower_pattern()
        acad.draw_roll_assembly()
        acad.draw_shaft_detail()
        acad.draw_bearing_mount()

    print("\n" + "="*50)
    print("[OK] AutoCAD Bridge Complete!")
    print("="*50)


if __name__ == "__main__":
    main()
