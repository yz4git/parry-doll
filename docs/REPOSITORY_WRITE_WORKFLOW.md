# Repository write workflow memory

This file records the working repository-edit workflow used from ChatGPT so future sessions do not fall back to saying that repository writes are unavailable when the connected GitHub API can perform them.

## Connected GitHub write path

1. Discover/load the connected `GitHub` resource when needed.
2. Read the latest target file/ref before replacing an existing file so the current blob SHA is used.
3. Use the connected GitHub API directly for `create_file` / `update_file` on `main` when repository rules allow it. A local checkout or local `gh` CLI is not required for these edits.
4. If `main` rejects a direct write because of protection/rules, create an `agent/<task>` branch from the latest main commit, make the same connector writes on that branch, and open a pull request.
5. Do not declare repository writing unavailable before checking the connected GitHub resource and attempting the appropriate API path.

## Generated binary/model workflow

Large binary assets such as Blender GLBs are not hand-written through the text contents API. The source/config/workflow/trigger files are committed through the connector, then GitHub Actions performs the Blender build and commits the generated binary with `contents: write` permission.

For PARRY DOLL model changes the normal sequence is:

1. Commit Blender source/config changes through the GitHub connector.
2. Update/create the build trigger so GitHub Actions runs.
3. The Action builds the model, validates it, commits the generated `dist/assets/models/heroine-blender.glb`, rebases on the current main if needed, and pushes it.
4. Update `.github/blender-model-audit.trigger` to run WebGL/high-resolution face audits on the generated model.
5. Review front / 3-quarter / exact-profile audit frames and iterate if necessary.
6. After the visual audit passes, update `dist/.pages-redeploy` so the existing GitHub Pages deployment publishes the new game asset.

## PARRY DOLL face-model invariant

The current face pipeline must remain a **fresh Blender build**, not an edit of the previous shipping GLB.

- Start from an empty Blender scene via the repository generator.
- Build body, costume, hair, weapon and runtime hierarchy from source.
- Use the pinned David Onizaki CC-BY anime female head as the head topology/modeling donor.
- Modify/fix that donor in Blender toward the supplied front and exact-right-profile references.
- Do **not** import the previous `heroine-blender.glb` as geometry or a fitting source.
- Re-importing the newly generated GLB is allowed only for post-export validation.
- Preserve game runtime node names and the existing shipping GLB path.

This workflow is the default for subsequent face iterations unless the user explicitly changes it.
