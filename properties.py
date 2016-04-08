from .update import Update_EnableExport, Update_SceneOrigin, Update_LocationDefault, Update_ExportDefault, Update_Normals, Update_ObjectItemName, Update_ObjectItemExport, Update_GroupItemName, Update_ActionItemName, Focus_Object, Focus_Group, Select_Object, Select_Group, Update_GroupExport, Update_GroupRootObject, Update_GroupExportDefault, Update_GroupLocationDefault, Update_GroupNormals

import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent

class ObjectItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=Update_ObjectItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

    enable_export = BoolProperty(
        name="",
        description="",
        default=False,
        update=Update_ObjectItemExport
    )

    sel = BoolProperty(
        name = "Select",
        description = "Selects the object in the scene",
        default = True,
        update = Select_Object)

    focus = BoolProperty(
        name = "Focus",
        description = "Focuses the camera to the object",
        default = True,
        update = Focus_Object)

class GroupItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the group.",
        update=Update_GroupItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

    sel = BoolProperty(
        name = "Select",
        description = "Selects the group in the scene",
        default = True,
        update = Select_Group)

    focus = BoolProperty(
        name = "Focus Export",
        description = "Focuses the camera to the entire group.",
        default = True,
        update = Focus_Group)

class ActionItem(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the action.",
        update=Update_ActionItemName
    )

    prev_name = StringProperty(
        name="",
        description="Internal only, used for tracking name updates."
    )

    anim_type = EnumProperty(
        name = "Animation Data Type",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Action Object', ''),
        ('2', 'NLA Object', ''),
        ('3', 'Action Armature', ''),
        ('4', 'NLA Armature', ''),
        ),)

def GetSelectedGroups(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    scn = context.scene.CAPScn
    scn.group_selected_list.clear()
    groups_found = []

    for item in context.selected_objects:
        for group in item.users_group:
            groupAdded = False

            for found_group in groups_found:
                if found_group.name == group.name:
                    groupAdded = True

            if groupAdded == False:
                groups_found.append(group)

    u = 1

    for i,x in enumerate(groups_found):

        items.append((str(i+1), x.name, x.name, i+1))
        newGroup = scn.group_selected_list.add()
        newGroup.name = x.name

    return items

class CAP_Scene_Preferences(PropertyGroup):

    engine_select = EnumProperty(
        name="Set Game Engine",
        items=(
        ('1', 'Unreal Engine 4', 'Configures export and export options for Unreal Engine 4'),
        ('2', 'Unity 5', 'Configures export and export options for Unity'),
        ),)

    correct_rotation = BoolProperty(
        name="Correct Rotation",
        description="Rotates all assets 180º on the Z axis before exporting, to appear in the same orientation in Unity as it does currently.",
        default=False)


    group_list = CollectionProperty(type=GroupItem)
    group_list_index = IntProperty()

    group_selected_list = CollectionProperty(type=GroupItem)
    group_selected_list_enum = EnumProperty(items=GetSelectedGroups)
    group_selected_list_index = IntProperty()

    object_list = CollectionProperty(type=ObjectItem)
    object_list_index = IntProperty()

    object_switch = EnumProperty(
        name = "Object Type Switch",
        description = "Switches the selection editing mode between individual, selected objects, and groups that can be browsed and edited through a list.",
        items=(
        ('1', 'Objects', 'Switches to the Object menu, for editing the exports of single objects and any tags associated with them.'),
        ('2', 'Groups', 'Switches to the Group menu, for editing the exports of groups.')
        ),)

def GetLocationDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.location_defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetExportDefaults(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

    u = 1

    for i,x in enumerate(exp.export_defaults):

        items.append((str(i+1), x.name, x.name, i+1))

    return items

class CAP_Object_Preferences(PropertyGroup):
    enable_export = BoolProperty(
        name = "Enable Export",
        description = "Enables the object and any matching, tagged objects to be exported as a single FBX file through GEX.",
        default = False,
        update = Update_EnableExport)

    use_scene_origin = BoolProperty(
        name = "Use Scene Origin",
        description = "Uses the scene's centre as an origin point for the object export, rather than the object's own origin point.",
        default = False,
        update = Update_SceneOrigin)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected objects will be exported to.",
        items=GetLocationDefaults,
        update=Update_LocationDefault)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
        update=Update_ExportDefault)

    normals = EnumProperty(
        name = "Normal Export Type",
        description = "Defines how the mesh normals are exported.",
        items=(
        ('1', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
        ('2', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
        ('3', 'Normals Only', 'Exports the current custom normals of the model.')
        ),
        update=Update_Normals)

class CAP_Group_Preferences(PropertyGroup):
    export_group = BoolProperty(
        name = "Export Group",
        description = "Enables all objects within the group to be exported as a single FBX file through GEX.",
        default = False,
        update=Update_GroupExport)

    root_object = StringProperty(
        name = "Origin Object",
        description = "Defines the exported origin point of the group object.  If not defined, the origin will be the world center.",
        default = "",
        update=Update_GroupRootObject)

    location_default = EnumProperty(
        name="Select Location Default",
        description="The filepath default the selected group will be exported to.",
        items=GetLocationDefaults,
        update=Update_GroupLocationDefault)

    export_default = EnumProperty(
        name = "Select Export Default",
        description = "Defines the export setting sets used on this object.",
        items=GetExportDefaults,
        update=Update_GroupExportDefault)

    normals = EnumProperty(
        name = "Normal Export Type",
        description = "Defines how the mesh normals are exported.",
        items=(
        ('1', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
        ('2', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
        ('3', 'Normals Only', 'Exports the current custom normals of the model.')
        ),
        update=Update_GroupNormals)

def GetExportPresets(scene, context):

    items = []
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["Blinkey"].preferences

    u = 1

    for i,x in enumerate(addon_prefs.presets):

        items.append((str(i), x.name, x.name, i))

    return items

class CAP_UI_Preferences(PropertyGroup):
    export_presets = EnumProperty(
        name = "Export Presets",
        description = "List of available visibility presets.",
        items = GetExportPresets
    )

    action_list = CollectionProperty(type=ActionItem)
    action_list_index = IntProperty()

    enable_export_loop = BoolProperty(default = False)

class CAP_Object_StateMachine(PropertyGroup):

    has_triangulate = BoolProperty(
        name = "Has Triangulation Modifier",
        description = "Internal variable used to monitor whether or not the object has a Triangulation modifier, when triangulating the mesh ",
        default = False)

class CAP_Action_Preferences(PropertyGroup):
    export = BoolProperty(
        name = "Export",
        description = "Determines whether the action can be exported or not.",
        default = True)


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
classes = (ObjectItem, GroupItem, ActionItem, CAP_Scene_Preferences, CAP_Object_Preferences, CAP_Group_Preferences, CAP_UI_Preferences, CAP_Object_StateMachine, CAP_Action_Preferences)

def register():
    print("Registering Properties")
    for item in classes:
        bpy.utils.register_class(item)

    bpy.types.Scene.CAPScn = PointerProperty(type=CAP_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(type=CAP_Object_Preferences)
    bpy.types.Group.CAPGrp = PointerProperty(type=CAP_Group_Preferences)
    bpy.types.Action.CAPAcn = PointerProperty(type=CAP_Action_Preferences)
    bpy.types.Scene.CAPUI = PointerProperty(type=CAP_UI_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(type=CAP_Object_StateMachine)

def unregister():
    print("Un-registering Properties")
    del bpy.types.Scene.CAPScn
    del bpy.types.Object.CAPObj
    del bpy.types.Group.CAPGrp
    del bpy.types.Action.CAPAcn
    del bpy.types.Scene.CAPUI
    del bpy.types.Object.CAPStm

    i = len(classes) - 1
    while i != -1:
        bpy.utils.unregister_class(classes[i])

@persistent
def CreateDefaultData(scene):

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    # Figure out if an object already exists, if yes do nothing
    for object in bpy.data.objects:
        print(object)
        if object.name == addon_prefs.default_datablock:
            return

    # Otherwise create the object using the addon preference data
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES')

    defaultDatablock = bpy.context.scene.objects.active
    defaultDatablock.name = addon_prefs.default_datablock
    defaultDatablock.hide = True
    defaultDatablock.hide_render = True
    defaultDatablock.hide_select = True
    defaultDatablock.CAPExp.is_storage_object = True

bpy.app.handlers.load_post.append(CreateDefaultData)
