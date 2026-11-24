import bpy, math
S = bpy.context.scene
if __import__("os").environ.get("EEVEE") == "1":
    S.render.engine = "BLENDER_EEVEE_NEXT"
    S.eevee.taa_render_samples = 8
    S.eevee.use_shadows = True
    S.eevee.use_raytracing = False
    w = bpy.data.worlds.new("w"); S.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.55, 0.7, 0.95, 1); bg.inputs[1].default_value = 0.55
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); S.collection.objects.link(sun)
    sun.data.energy = 2.0; sun.data.angle = math.radians(6); sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    S.view_settings.view_transform = "Standard"
