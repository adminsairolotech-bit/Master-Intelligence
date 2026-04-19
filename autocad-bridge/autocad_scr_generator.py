# -*- coding: utf-8 -*-
"""
AutoCAD SCR Script Generator for Roll Forming Machine Drawings
AI generates .scr commands → AutoCAD runs them

USAGE:
    python autocad_scr_generator.py --type c-channel --save machine.scr
"""

class RollFormingSCRGenerator:
    """Generate AutoCAD .scr scripts for roll forming machine parts"""

    def __init__(self):
        self.commands = []
        self.header = """UNITS
2
LIMITS
0,0
1000,1000
GRID
10
SNAP
5
LAYER
N PROFILE C 1
N CENTER C 2
N DIM C 3
N TEXT C 4
N ROLLS C 5
N SHAFT C 6
N BEARING C 7
N TITLE C 8
LAYER
S PROFILE
ZOOM
A
"""

    def add(self, *args):
        """Add command"""
        cmd = " ".join(str(a) for a in args)
        self.commands.append(cmd)

    def add_comment(self, text):
        """Add comment"""
        self.commands.append(f"; {text}")

    # ==========================================
    # BASIC SHAPES
    # ==========================================

    def draw_rectangle(self, x1, y1, x2, y2, layer="PROFILE"):
        self.add(f"-LAYER S {layer}")
        self.add("RECTANG", f"{x1},{y1}", f"{x2},{y2}")

    def draw_circle(self, x, y, r, layer="PROFILE"):
        self.add(f"-LAYER S {layer}")
        self.add("CIRCLE", f"{x},{y}", r)

    def draw_line(self, x1, y1, x2, y2, layer="PROFILE"):
        self.add(f"-LAYER S {layer}")
        self.add("LINE", f"{x1},{y1}", f"{x2},{y2}", "")

    def draw_polyline(self, points, layer="PROFILE"):
        self.add(f"-LAYER S {layer}")
        # points = [(x1,y1), (x2,y2), ...]
        for i, pt in enumerate(points):
            if i == 0:
                self.add("PLINE", f"{pt[0]},{pt[1]}")
            else:
                self.add(f"{pt[0]},{pt[1]}")
        self.add("")

    def draw_arc(self, x1, y1, x2, y2, radius, layer="PROFILE"):
        self.add(f"-LAYER S {layer}")
        self.add("ARC", f"{x1},{y1}", f"{x2},{y2}", f"{radius}")

    # ==========================================
    # DIMENSIONS
    # ==========================================

    def dim_linear(self, x1, y1, x2, y2, layer="DIM"):
        self.add(f"-LAYER S {layer}")
        self.add("DIMLINEAR", f"{x1},{y1}", f"{x2},{y2}")

    def dim_aligned(self, x1, y1, x2, y2, layer="DIM"):
        self.add(f"-LAYER S {layer}")
        self.add("DIMALIGNED", f"{x1},{y1}", f"{x2},{y2}")

    def dim_radius(self, x, y, layer="DIM"):
        self.add(f"-LAYER S {layer}")
        self.add("DIMRADIUS", f"{x},{y}")

    def dim_diameter(self, x, y, layer="DIM"):
        self.add(f"-LAYER S {layer}")
        self.add("DIMDIAMETER", f"{x},{y}")

    # ==========================================
    # TEXT
    # ==========================================

    def draw_text(self, x, y, text, height=5, layer="TEXT"):
        self.add(f"-LAYER S {layer}")
        self.add("TEXT", f"JC {x},{y}", height, f"0 {text}")

    def draw_mtext(self, x, y, text, width=50, layer="TEXT"):
        self.add(f"-LAYER S {layer}")
        # Replace newlines with #
        text_clean = text.replace("\n", "#")
        self.add("MTEXT", f"{x},{y}", f"J ML {width}", text_clean)

    # ==========================================
    # CENTER LINES
    # ==========================================

    def center_line_horizontal(self, x1, y, x2, layer="CENTER"):
        self.add(f"-LAYER S {layer}")
        self.add("LINE", f"{x1},{y}", f"{x2},{y}", "")
        # Extension lines
        self.add("LINE", f"{x1},{y-3}", f"{x1},{y+3}", "")
        self.add("LINE", f"{x2},{y-3}", f"{x2},{y+3}", "")

    def center_line_vertical(self, x, y1, y2, layer="CENTER"):
        self.add(f"-LAYER S {layer}")
        self.add("LINE", f"{x},{y1}", f"{x},{y2}", "")
        # Extension lines
        self.add("LINE", f"{x-3},{y1}", f"{x+3},{y1}", "")
        self.add("LINE", f"{x-3},{y2}", f"{x+3},{y2}", "")

    def center_mark(self, x, y, size=5, layer="CENTER"):
        self.add(f"-LAYER S {layer}")
        self.add("LINE", f"{x-size},{y}", f"{x+size},{y}", "")
        self.add("LINE", f"{x},{y-size}", f"{x},{y+size}", "")

    # ==========================================
    # ROLL FORMING PROFILES
    # ==========================================

    def c_channel(self, web=100, flange=50, lip=15, thickness=2,
                  offset_x=50, offset_y=50, scale=1):
        """Draw C-Channel profile"""
        self.add_comment(f"C-CHANNEL: {web}x{flange}x{flange}x{lip}")
        self.add(f"-LAYER S PROFILE")

        w = web * scale
        f = flange * scale
        l = lip * scale
        t = thickness * scale

        # Profile points (unfolded)
        #     A----B
        #   H        C
        #   |        | G
        #   |   E    | F
        #   |        |
        #   D--------I

        # Outer profile
        pts = [
            (offset_x, offset_y),
            (offset_x, offset_y + w),           # A
            (offset_x + f, offset_y + w),       # B
            (offset_x + f, offset_y + w + l),   # C
            (offset_x + f - t, offset_y + w + l), # D
            (offset_x + f - t, offset_y + w + t), # E
            (offset_x + t, offset_y + w + t),     # F
            (offset_x + t, offset_y + t),         # G
            (offset_x + f - t, offset_y + t),     # H
            (offset_x + f, offset_y),             # I
            (offset_x + f, offset_y + w),         # Back to B
        ]

        self.draw_polyline(pts)

        # Dimensions
        # Web height
        self.add("-LAYER S DIM")
        self.dim_linear(offset_x - 15, offset_y,
                        offset_x - 15, offset_y + w)
        self.draw_text(offset_x - 25, offset_y + w/2, f"Web: {web}", 3)

        # Flange width
        self.dim_linear(offset_x, offset_y - 15,
                        offset_x + f, offset_y - 15)
        self.draw_text(offset_x + f/2, offset_y - 25, f"Flange: {flange}", 3)

        # Lip
        self.dim_aligned(offset_x + f + 15, offset_y + w,
                         offset_x + f + 15, offset_y + w + l)
        self.draw_text(offset_x + f + 20, offset_y + w + l/2, f"Lip: {lip}", 3)

        # Thickness
        self.draw_line(offset_x + 5, offset_y + w + l + 10,
                       offset_x + f - 5, offset_y + w + l + 10)
        self.draw_line(offset_x + 5, offset_y + w + l + 8,
                       offset_x + 5, offset_y + w + l + 12)
        self.draw_line(offset_x + f - 5, offset_y + w + l + 8,
                       offset_x + f - 5, offset_y + w + l + 12)
        self.draw_text(offset_x + f/2, offset_y + w + l + 15, f"t={thickness}", 3)

        # Title
        self.add("-LAYER S TITLE")
        self.draw_mtext(offset_x + f + 50, offset_y + w/2,
                        f"C-CHANNEL PROFILE#Web: {web}mm#Flange: {flange}mm#Lip: {lip}mm#Thickness: {thickness}mm",
                        width=80)

    def z_purlin(self, web=150, flange=50, lip=15, thickness=2,
                 offset_x=50, offset_y=50, scale=1):
        """Draw Z-Purlin profile"""
        self.add_comment(f"Z-PURLIN: {web}x{flange}x{lip}")
        self.add(f"-LAYER S PROFILE")

        w = web * scale
        f = flange * scale
        l = lip * scale
        t = thickness * scale

        # Z shape points
        pts = [
            (offset_x, offset_y),
            (offset_x, offset_y + w - f - l),    # Up web
            (offset_x + f, offset_y + w - l),      # Bottom flange
            (offset_x + f, offset_y + w),          # Beak end
            (offset_x + f - t, offset_y + w),      # Beak inner
            (offset_x + f - t, offset_y + w - l),  # Beak inner
            (offset_x + t, offset_y + w - f - l),  # Web inner
            (offset_x + t, offset_y + t),          # Bottom
            (offset_x + f - t, offset_y + t),     # Bottom flange inner
            (offset_x + f - t, offset_y),           # Bottom flange
            (offset_x, offset_y),                   # Close
        ]

        self.draw_polyline(pts)

        # Dimensions
        self.add("-LAYER S DIM")
        self.draw_text(offset_x + f/2, offset_y + w/2,
                        f"Z-PURLIN#{web}x{flange}x{lip}")

    def omega_profile(self, width=100, depth=40, flange=20, thickness=1.5,
                      offset_x=50, offset_y=50, scale=1):
        """Draw Omega/Hat section"""
        self.add_comment(f"OMEGA: {width}x{depth}x{flange}")
        self.add(f"-LAYER S PROFILE")

        w = width * scale
        d = depth * scale
        f = flange * scale
        t = thickness * scale

        pts = [
            (offset_x, offset_y),
            (offset_x + w, offset_y),               # Top left
            (offset_x + w, offset_y + f),           # Top right
            (offset_x + w - t, offset_y + f),      # Inner right
            (offset_x + w - t, offset_y + f + d),  # Inner bottom right
            (offset_x + t, offset_y + f + d),       # Inner bottom left
            (offset_x + t, offset_y + f),           # Inner left
            (offset_x, offset_y + f),               # Top left inner
            (offset_x, offset_y),                   # Close
        ]

        self.draw_polyline(pts)

    # ==========================================
    # SHAFT DETAIL
    # ==========================================

    def shaft_side_view(self, diameter=50, length=350,
                        offset_x=50, offset_y=150, scale=1):
        """Draw shaft side view"""
        self.add_comment(f"SHAFT: Ø{diameter}x{length}")
        self.add(f"-LAYER S SHAFT")

        d = diameter * scale
        l = length * scale

        # Main shaft rectangle
        self.draw_rectangle(offset_x, offset_y - d/2,
                           offset_x + l, offset_y + d/2)

        # Keyway
        kv_pos = offset_x + l * 0.2
        kv_len = d * 0.8
        kv_depth = d * 0.15
        self.draw_rectangle(kv_pos, offset_y - d/2,
                          kv_pos + kv_len, offset_y - d/2 - kv_depth)

        # Center line
        self.center_line_horizontal(offset_x, offset_y, offset_x + l)

        # Dimensions
        self.add("-LAYER S DIM")
        # Length
        self.dim_linear(offset_x, offset_y - d - 20,
                        offset_x + l, offset_y - d - 20)
        self.draw_text(offset_x + l/2, offset_y - d - 35, f"Length: {length}", 3)

        # Diameter
        self.dim_linear(offset_x - 20, offset_y - d/2,
                        offset_x - 20, offset_y + d/2)
        self.draw_text(offset_x - 40, offset_y, f"Ø{diameter}", 4)

        # Keyway
        self.draw_text(offset_x + l * 0.2, offset_y - d/2 - 15,
                      f"Keyway: {int(kv_len)}x{int(kv_depth*2)}")

    def shaft_front_view(self, diameter=50, offset_x=100, offset_y=100, scale=1):
        """Draw shaft front view (circle)"""
        self.add_comment(f"SHAFT FRONT: Ø{diameter}")
        self.add(f"-LAYER S SHAFT")

        d = diameter * scale

        self.draw_circle(offset_x, offset_y, d/2)

        # Center marks
        self.center_mark(offset_x, offset_y, d/4)

        # Keyway (half visible)
        kv_w = d * 0.3
        kv_h = d * 0.15
        pts = [
            (offset_x - kv_w/2, offset_y),
            (offset_x - kv_w/2, offset_y + kv_h),
            (offset_x + kv_w/2, offset_y + kv_h),
            (offset_x + kv_w/2, offset_y),
        ]
        self.draw_polyline(pts)

        # Dimension
        self.add("-LAYER S DIM")
        self.dim_diameter(offset_x + d/2 + 10, offset_y)
        self.draw_text(offset_x, offset_y + d/2 + 20, f"Ø{diameter}mm", 4)

    # ==========================================
    # ROLL ASSEMBLY
    # ==========================================

    def roll_assembly(self, shaft_dia=50, roll_dia=160,
                      num_passes=6, spacing=180,
                      offset_x=50, offset_y=100, scale=1):
        """Draw roll assembly side view"""
        self.add_comment(f"ROLL ASSEMBLY: {num_passes} passes")
        self.add(f"-LAYER S ROLLS")

        s = shaft_dia * scale
        r = roll_dia * scale
        n = num_passes
        sp = spacing * scale

        # Draw each roll stand
        for i in range(n):
            x = offset_x + i * sp

            # Top roll
            self.draw_rectangle(x - r/2, offset_y + s/2,
                               x + r/2, offset_y + s/2 + r)

            # Bottom roll
            self.draw_rectangle(x - r/2, offset_y - s/2 - r,
                               x + r/2, offset_y - s/2)

            # Shaft
            self.draw_rectangle(offset_x - 30, offset_y - s/2,
                               offset_x + n * sp + 30, offset_y + s/2)

            # Pass number
            self.draw_text(x, offset_y + s/2 + r + 20, f"P{i+1}", 5)

        # Main shaft label
        self.draw_line(offset_x - 10, offset_y,
                       offset_x - 10, offset_y + s/2 + r + 60)
        self.draw_text(offset_x - 20, offset_y + s/2 + r + 70,
                      f"Shaft: Ø{shaft_dia}mm#Roll Ø: {roll_dia}mm#Passes: {num_passes}")

    # ==========================================
    # BEARING MOUNT
    # ==========================================

    def bearing_detail(self, shaft_dia=50, bearing="6310",
                       offset_x=100, offset_y=100, scale=1):
        """Draw bearing mount detail"""
        # Bearing sizes lookup
        bearings = {
            "6308": (40, 90, 23),
            "6310": (50, 110, 27),
            "6312": (60, 130, 31),
            "6315": (75, 160, 37),
        }

        bore, od, width = bearings.get(bearing, (shaft_dia, shaft_dia*2, shaft_dia*0.5))
        bore *= scale
        od *= scale
        width *= scale

        self.add_comment(f"BEARING: {bearing} - Bore:{bore} OD:{od}")

        # Shaft (center line)
        self.center_line_horizontal(offset_x - 50, offset_y, offset_x + 50 + width)

        # Bearing outer circle
        self.draw_circle(offset_x + width/2, offset_y, od/2)

        # Bearing inner circle (shaft)
        self.draw_circle(offset_x + width/2, offset_y, bore/2)

        # Housing outline
        housing_dia = od + 20
        self.draw_circle(offset_x + width/2, offset_y, housing_dia/2)

        # Dimensions
        self.add("-LAYER S DIM")
        self.dim_diameter(offset_x + width/2 + od/2 + 10, offset_y)
        self.draw_text(offset_x + width/2 + od/2 + 20, offset_y - 20,
                      f"OD: {int(od/scale)}")

        self.dim_diameter(offset_x + width/2 + bore/2 + 5, offset_y)
        self.draw_text(offset_x + width/2 + bore/2 + 15, offset_y - 20,
                      f"Bore: {int(bore/scale)}")

        # Title
        self.draw_text(offset_x, offset_y - housing_dia/2 - 20,
                      f"BEARING: {bearing}")

    # ==========================================
    # FLOWER PATTERN
    # ==========================================

    def flower_pattern(self, profile="C", num_passes=7,
                      offset_x=50, offset_y=50, scale=1):
        """Draw flower pattern (pass sequence)"""
        self.add_comment(f"FLOWER PATTERN: {profile} - {num_passes} passes")
        self.add(f"-LAYER S PROFILE")

        spacing_y = 60 * scale
        spacing_x = 80 * scale

        for i in range(num_passes):
            y = offset_y + i * spacing_y
            pass_num = i + 1

            # Progressive forming angle
            angle_pct = pass_num / num_passes

            if profile == "C":
                # C-Channel progressive forming
                web = 100 * scale
                flange = 40 * scale * angle_pct
                lip = 15 * scale * min(angle_pct * 1.5, 1)

                # Draw simplified C shape at this stage
                pts = [
                    (offset_x, y),
                    (offset_x, y + web),
                    (offset_x + flange, y + web),
                    (offset_x + flange, y + web + lip),
                    (offset_x + flange - 2, y + web + lip),
                    (offset_x + flange - 2, y + web + 2),
                    (offset_x + 2, y + web + 2),
                    (offset_x + 2, y + 2),
                    (offset_x + flange - 2, y + 2),
                    (offset_x + flange, y),
                    (offset_x, y),
                ]
                self.draw_polyline(pts)

            elif profile == "Z":
                # Z-Purlin progressive forming
                web = 100 * scale
                flange = 40 * scale * angle_pct

                pts = [
                    (offset_x, y),
                    (offset_x, y + web),
                    (offset_x + flange, y + web),
                    (offset_x + flange, y + web + 15 * scale),
                    (offset_x + flange - 2, y + web + 15 * scale),
                    (offset_x + flange - 2, y + web),
                    (offset_x + 2, y + web - flange),
                    (offset_x + 2, y + 2),
                    (offset_x, y),
                ]
                self.draw_polyline(pts)

            # Pass number
            self.draw_text(offset_x - 30, y + 50, f"P{pass_num}", 5)

            # Angle indicator
            self.draw_text(offset_x + 60 * scale, y + 50,
                          f"{int(angle_pct * 90)}deg", 4)

        # Title
        self.add("-LAYER S TITLE")
        self.draw_text(offset_x + 100, offset_y + num_passes * spacing_y / 2,
                      f"FLOWER PATTERN#{profile}-Section#{num_passes} Passes")

    # ==========================================
    # TITLE BLOCK
    # ==========================================

    def title_block(self, title="ROLL FORMING MACHINE",
                    subtitle="", scale=1,
                    offset_x=50, offset_y=50):
        """Add title block"""
        self.add_comment("TITLE BLOCK")
        self.add(f"-LAYER S TITLE")

        width = 300 * scale
        height = 80 * scale

        # Border
        self.draw_rectangle(offset_x, offset_y, offset_x + width, offset_y + height)

        # Divider lines
        self.draw_line(offset_x, offset_y + height * 0.4,
                       offset_x + width, offset_y + height * 0.4)
        self.draw_line(offset_x + width * 0.6, offset_y,
                       offset_x + width * 0.6, offset_y + height * 0.4)

        # Title text
        self.draw_text(offset_x + width/2, offset_y + height * 0.7,
                      title, 8)

        # Subtitle
        self.draw_text(offset_x + width * 0.3, offset_y + height * 0.2,
                      subtitle, 4)

        # Date
        from datetime import datetime
        date = datetime.now().strftime("%d-%m-%Y")
        self.draw_text(offset_x + width * 0.8, offset_y + height * 0.2,
                      f"Date: {date}", 4)

    # ==========================================
    # GENERATE OUTPUT
    # ==========================================

    def generate(self):
        """Generate final script"""
        script = self.header + "\n".join(self.commands) + "\nZOOM\nE\n"
        return script

    def save(self, filename):
        """Save to file"""
        with open(filename, 'w') as f:
            f.write(self.generate())
        print(f"[OK] Saved: {filename}")

    def preview(self):
        """Print script to console"""
        print(self.generate())


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AutoCAD SCR Generator")
    parser.add_argument("--type", choices=["c-channel", "z-purlin", "omega",
                        "shaft", "rolls", "bearing", "flower", "all"],
                       help="Drawing type")
    parser.add_argument("--save", help="Save to file")
    parser.add_argument("--preview", action="store_true", help="Preview script")

    args = parser.parse_args()

    gen = RollFormingSCRGenerator()

    if args.type == "c-channel" or args.type is None:
        gen.c_channel(web=150, flange=50, lip=15, thickness=2)

    if args.type == "z-purlin":
        gen.z_purlin(web=150, flange=50, lip=15)

    if args.type == "omega":
        gen.omega_profile(width=100, depth=40, flange=20)

    if args.type == "shaft":
        gen.shaft_side_view(diameter=50, length=350)
        gen.shaft_front_view(diameter=50)

    if args.type == "rolls":
        gen.roll_assembly(shaft_dia=50, roll_dia=160, num_passes=6)

    if args.type == "bearing":
        gen.bearing_detail(shaft_dia=50, bearing="6310")

    if args.type == "flower":
        gen.flower_pattern(profile="C", num_passes=7)

    if args.type == "all":
        gen.c_channel()
        gen.shaft_side_view()
        gen.roll_assembly()
        gen.flower_pattern()
        gen.title_block(title="ROLL FORMING MACHINE", subtitle="C-CHANNEL C-150")

    if args.preview:
        gen.preview()

    if args.save:
        gen.save(args.save)


if __name__ == "__main__":
    main()
