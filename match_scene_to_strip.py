bl_info = {
    "name": "Match Scene to VSE Strip",
    "author": "Patrick Hill + ChatGPT",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "Sequencer > Strip menu",
    "description": "Set scene FPS, frame range, resolution, and reset strip scale from active VSE strip",
    "category": "Sequencer",
}

import bpy


def match_scene_to_strip(context):
    scene = context.scene
    seq_editor = scene.sequence_editor

    if seq_editor is None:
        raise RuntimeError("No Sequence Editor found in this scene.")

    strip = getattr(seq_editor, "active_strip", None)

    if strip is None:
        selected = getattr(context, "selected_sequences", [])
        if len(selected) == 1:
            strip = selected[0]

    if strip is None:
        raise RuntimeError("No active strip found. Select a strip in the VSE first.")

    # --- Frame rate ---
    fps = getattr(strip, "fps", None)
    if fps:
        scene.render.fps = round(fps)
        scene.render.fps_base = 1.0

    # --- Frame range ---
    start = strip.frame_final_start
    end = strip.frame_final_end - 1
    scene.frame_start = start
    scene.frame_end = end

    # --- Resolution ---
    width = height = None
    if hasattr(strip, "elements") and strip.elements:
        el = strip.elements[0]
        width = getattr(el, "orig_width", None)
        height = getattr(el, "orig_height", None)

    if width and height:
        scene.render.resolution_x = width
        scene.render.resolution_y = height

    # --- Strip scale (Transform) ---
    if hasattr(strip, "transform") and strip.transform:
        strip.transform.scale_x = 1.0
        strip.transform.scale_y = 1.0
    else:
        # Not all strip types expose transform scaling
        pass


class SEQUENCER_OT_match_scene_to_strip(bpy.types.Operator):
    bl_idname = "sequencer.match_scene_to_strip"
    bl_label = "Match Scene to Active Strip"
    bl_description = "Set scene FPS, frame range, resolution, and reset strip scale from the active VSE strip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene and scene.sequence_editor is not None

    def execute(self, context):
        try:
            match_scene_to_strip(context)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SEQUENCER_OT_match_scene_to_strip.bl_idname)


def register():
    bpy.utils.register_class(SEQUENCER_OT_match_scene_to_strip)
    bpy.types.SEQUENCER_MT_strip.append(menu_func)


def unregister():
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)
    bpy.utils.unregister_class(SEQUENCER_OT_match_scene_to_strip)


if __name__ == "__main__":
    register()
