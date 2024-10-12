bl_info = {
    "name": "Point Slipper",
    "author": "Pankaj_B.",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Tool",
    "description": ("It works on 2D Bezier Curve/Spline"
                    "Reduce size depend on Distance instead of Size of Original Object"
                    "It reduce/increase the size of Looped Spline"),
    "warning": "",
    "wiki_url": "",
    "category": "Tool",
}
import bpy
import math
from math import atan2, radians, cos, sin, sqrt
class OBJECT_OT_BlackWhite(bpy.types.Operator):
    bl_idname = "object.black_white"
    bl_label = "Print The Line"
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'CURVE' and obj.data.splines:
            if obj.data.splines[0].type == 'BEZIER':
                bpy.ops.object.mode_set(mode='EDIT')
                usp1= []
                for spline_index, spline in enumerate(obj.data.splines):
                    for point_index, point in enumerate(spline.bezier_points):
                        if point.select_control_point:
                            usp1.append((spline_index, point))
                spline_indices = {spline_index for spline_index, _ in usp1}
                for spline_index in spline_indices:
                    spline = obj.data.splines[spline_index]
                    if not spline.use_cyclic_u:
                        self.report({'ERROR'}, "Make the Loop.")
                        return {'CANCELLED'}
                usp2 = []
                for spline_index, spline in enumerate(obj.data.splines):
                    for point_index, point in enumerate(spline.bezier_points):
                        if point.select_control_point:
                            usp2.append({
                                'SplineIndex': spline_index,
                                'PointIndex': point_index,
                                'PointLoc': tuple(round(coord, 7) for coord in point.co),
                            })
                bpy.ops.curve.select_all(action='DESELECT')
                fsi = min(spline_indices)
                fs = obj.data.splines[fsi]
                ntd = []
                tam1 = context.scene.bla_whi.bwtn
                dfrn= tam1/10                         
                for point_index, point in enumerate(fs.bezier_points):
                    fpt = point
                    spt = fs.bezier_points[(point_index + 1) % len(fs.bezier_points)]
                    tpt = fs.bezier_points[(point_index + 2) % len(fs.bezier_points)]
                    flm1 = (fpt.co.x + spt.co.x) / 2
                    flm2 = (fpt.co.y + spt.co.y) / 2
                    slm1 = (spt.co.x + tpt.co.x) / 2
                    slm2 = (spt.co.y + tpt.co.y) / 2
                    fla = atan2(spt.co.y - fpt.co.y, spt.co.x - fpt.co.x)
                    sla = atan2(tpt.co.y - spt.co.y, tpt.co.x - spt.co.x)
                    flpa = fla + radians(90)
                    slpa = sla + radians(90)
                    fpe1 = flm1 - dfrn* cos(flpa)
                    fpe2 = flm2 - dfrn* sin(flpa)
                    sle1 = slm1 - dfrn* cos(slpa)
                    sle2 = slm2 - dfrn* sin(slpa)
                    fll = sqrt((spt.co.x - fpt.co.x)**2 + (spt.co.y - fpt.co.y)**2)
                    sll = sqrt((tpt.co.x - spt.co.x)**2 + (tpt.co.y - spt.co.y)**2)
                    fpsp1 = fpe1 - (fll / 2) * cos(fla + radians(180))
                    fpsp2 = fpe2 - (fll / 2) * sin(fla + radians(180))
                    fpep1 = fpe1 + (fll / 2) * cos(fla + radians(180))
                    fpep2 = fpe2 + (fll / 2) * sin(fla + radians(180))
                    spsp1 = sle1 - (sll / 2) * cos(sla + radians(180))
                    spsp2 = sle2 - (sll / 2) * sin(sla + radians(180))
                    spep1 = sle1 + (sll / 2) * cos(sla + radians(180))
                    spep2 = sle2 + (sll / 2) * sin(sla + radians(180))
                    a1 = fpep2 - fpsp2
                    b1 = fpsp1 - fpep1
                    c1 = a1 * fpsp1 + b1 * fpsp2
                    a2 = spep2 - spsp2
                    b2 = spsp1 - spep1
                    c2 = a2 * spsp1 + b2 * spsp2
                    dtnt1 = a1 * b2 - a2 * b1
                    if(dtnt1==0):
                        itst1 = (b2 * c1 - b1 * c2) / 1    
                        itst2 = (a1 * c2 - a2 * c1) / 1
                    else:
                        itst1 = (b2 * c1 - b1 * c2) / dtnt1
                        itst2 = (a1 * c2 - a2 * c1) / dtnt1
                    ntd.append([
                        (round(itst1, 7), round(itst2, 7), 0.0),
                    ])
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                new_spline = obj.data.splines.new('BEZIER')
                new_spline.bezier_points.add(len(ntd) - 1)
                for i, row in enumerate(ntd):
                    point = new_spline.bezier_points[i]
                    point.co = row[0]
                    point.handle_right = row[0]
                    point.handle_left = row[0]
                    point.handle_right_type = 'FREE'
                    point.handle_left_type = 'FREE'
                new_spline.use_cyclic_u = True
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                self.report({'WARNING'}, "Active object is not a Bezier curve")
        else:
            self.report({'WARNING'}, "No active object or not a curve")
        return {'FINISHED'}
class OBJECT_PT_BwPan(bpy.types.Panel):
    bl_label = "Points Slipper"
    bl_idname = "OBJECT_PT_bw_pan"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bwt1 = scene.bla_whi        
        layout.prop(bwt1, "bwtn")
        layout.operator("object.black_white")
class BlaWhi(bpy.types.PropertyGroup):
    bwtn: bpy.props.FloatProperty(
        name = "ReSiZinG",
        description = "Maths Depend on Distance",
        default = 0.1,
        min = 0.001,
    )
def register():
    bpy.utils.register_class(OBJECT_OT_BlackWhite)
    bpy.utils.register_class(OBJECT_PT_BwPan)
    bpy.utils.register_class(BlaWhi)
    bpy.types.Scene.bla_whi = bpy.props.PointerProperty(type=BlaWhi)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_BlackWhite)
    bpy.utils.unregister_class(OBJECT_PT_BwPan)
    bpy.utils.unregister_class(BlaWhi)
    del bpy.types.Scene.bla_whi
        
if __name__ == "__main__":
    register()