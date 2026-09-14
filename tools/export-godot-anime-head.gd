extends SceneTree

# Extracts the CC-BY anime head ArrayMesh from the pinned Godot donor scene as OBJ.
# The donor repository and attribution are documented in docs/THIRD_PARTY_FACE_V160.md.

func _write_surface(file, mesh, surface_index, vertex_offset):
    var arrays = mesh.surface_get_arrays(surface_index)
    var vertices = arrays[Mesh.ARRAY_VERTEX]
    var normals = arrays[Mesh.ARRAY_NORMAL]
    var uvs = arrays[Mesh.ARRAY_TEX_UV]
    var indices = arrays[Mesh.ARRAY_INDEX]

    file.store_line("o AnimeHeadSurface%d" % surface_index)
    for v in vertices:
        file.store_line("v %.9f %.9f %.9f" % [v.x, v.y, v.z])
    if uvs.size() == vertices.size():
        for uv in uvs:
            # OBJ's V axis is opposite Godot's image convention.
            file.store_line("vt %.9f %.9f" % [uv.x, 1.0 - uv.y])
    if normals.size() == vertices.size():
        for n in normals:
            file.store_line("vn %.9f %.9f %.9f" % [n.x, n.y, n.z])

    var has_uv = uvs.size() == vertices.size()
    var has_normal = normals.size() == vertices.size()
    var tri_count = int(indices.size() / 3)
    for t in range(tri_count):
        var parts = []
        for k in range(3):
            var local_i = int(indices[t * 3 + k])
            var i = vertex_offset + local_i
            if has_uv and has_normal:
                parts.append("%d/%d/%d" % [i, i, i])
            elif has_uv:
                parts.append("%d/%d" % [i, i])
            elif has_normal:
                parts.append("%d//%d" % [i, i])
            else:
                parts.append(str(i))
        file.store_line("f %s %s %s" % [parts[0], parts[1], parts[2]])

    return vertex_offset + vertices.size()

func _init():
    var output_path = OS.get_environment("HEAD_OBJ_OUTPUT")
    if output_path == "":
        output_path = "/tmp/anime-head.obj"
    var include_brows = OS.get_environment("HEAD_INCLUDE_BROWS") == "1"

    var packed = load("res://addons/rigidRagdoll/Characters/GeneralRagdoll_Simple.tscn")
    if packed == null:
        push_error("Could not load donor scene")
        quit(2)
        return
    var root = packed.instance()
    var node = root.get_node("SkeletonRagdoll/HeadMesh")
    if node == null or node.mesh == null:
        push_error("HeadMesh ArrayMesh was not found")
        quit(3)
        return

    var mesh = node.mesh
    print("DONOR_HEAD surfaces=", mesh.get_surface_count(), " blend_shapes=", mesh.get_blend_shape_count())
    for i in range(mesh.get_blend_shape_count()):
        print("DONOR_BLEND_SHAPE ", i, " ", mesh.get_blend_shape_name(i))

    var file = File.new()
    if file.open(output_path, File.WRITE) != OK:
        push_error("Could not open OBJ output: " + output_path)
        quit(4)
        return
    file.store_line("# David Onizaki CC-BY anime head; extracted from pinned Godot donor scene")
    file.store_line("# Source: https://sketchfab.com/3d-models/genshin-style-anime-female-base-mesh-for-blender-c2d6727e8c9742feb9a4a3bccac6e0e0")
    var offset = 1
    offset = _write_surface(file, mesh, 0, offset)
    if include_brows and mesh.get_surface_count() > 1:
        offset = _write_surface(file, mesh, 1, offset)
    file.close()

    var arrays = mesh.surface_get_arrays(0)
    print("DONOR_HEAD_EXPORTED path=", output_path,
        " vertices=", arrays[Mesh.ARRAY_VERTEX].size(),
        " indices=", arrays[Mesh.ARRAY_INDEX].size(),
        " final_obj_index=", offset - 1)
    root.queue_free()
    quit(0)
