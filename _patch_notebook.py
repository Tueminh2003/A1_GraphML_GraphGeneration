import json, uuid

NB = r'C:\Users\Chloe\Documents\GitHub\A1_GraphML_GraphGeneration\A1_Chloe_FinalNoteBook.ipynb'

def cid():
    return uuid.uuid4().hex[:8]

def code(lines):
    return {"cell_type": "code", "execution_count": None, "id": cid(),
            "metadata": {}, "outputs": [], "source": lines}

def md(text):
    lines = text.split('\n')
    src = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "markdown", "id": cid(), "metadata": {}, "source": src}

with open(NB, 'r', encoding='utf-8-sig') as f:
    nb = json.load(f)

# Find the "Show Aperture" cell (last existing cell in the notebook)
target = -1
for i, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    if 'Topology.Show(Aperture' in src and '210,210,250' in src:
        target = i
if target == -1:
    target = len(nb['cells']) - 1
print(f"Inserting after cell index {target}")

new_cells = []

# ================================================================
# SECTION A: CIRCULATION GRAPH
# ================================================================
new_cells.append(md("## CIRCULATION GRAPH — Door Connections"))

new_cells.append(code([
    "from topologicpy.Cell import Cell\n",
    "\n",
    "# Collect all door faces from the apertures OBJ\n",
    "aperture_faces = []\n",
    "for obj in Aperture:\n",
    "    aperture_faces.extend(Topology.Faces(obj))\n",
    "print(f\"Total door aperture faces: {len(aperture_faces)}\")\n",
    "\n",
    "# Attach door faces as apertures onto matching shared faces of the CellComplex\n",
    "cellComplex_doors = Topology.AddApertures(\n",
    "    cellComplex, aperture_faces,\n",
    "    subTopologyType=\"face\",\n",
    "    tolerance=0.01\n",
    ")\n",
    "print(\"Apertures added to CellComplex\")"
]))

new_cells.append(code([
    "# Build circulation graph — spaces connected only through door apertures\n",
    "try:\n",
    "    circulation_graph = Graph.ByTopology(\n",
    "        cellComplex_doors,\n",
    "        direct=False,\n",
    "        viaSharedTopologies=False,\n",
    "        viaSharedApertures=True,\n",
    "        toExteriorTopologies=False,\n",
    "        toExteriorApertures=True\n",
    "    )\n",
    "    n_v = len(Graph.Vertices(circulation_graph))\n",
    "    n_e = len(Graph.Edges(circulation_graph))\n",
    "    if n_v == 0:\n",
    "        raise ValueError(\"Empty graph — apertures may not match cell faces\")\n",
    "    print(f\"Circulation graph: {n_v} nodes, {n_e} door connections\")\n",
    "except Exception as ex:\n",
    "    print(f\"Aperture-based graph failed ({ex}), falling back to direct adjacency\")\n",
    "    circulation_graph = Graph.ByTopology(cellComplex_doors, direct=True)\n",
    "    print(f\"Circulation graph (fallback): {len(Graph.Vertices(circulation_graph))} nodes, \"\n",
    "          f\"{len(Graph.Edges(circulation_graph))} connections\")"
]))

new_cells.append(code([
    "# Style: blue nodes, cyan edges (distinct from red dual graph)\n",
    "for v in Graph.Vertices(circulation_graph):\n",
    "    Topology.SetDictionary(v, Dictionary.ByKeysValues([\"size\", \"color\"], [16, \"blue\"]))\n",
    "for e in Graph.Edges(circulation_graph):\n",
    "    Topology.SetDictionary(e, Dictionary.ByKeysValues([\"width\", \"color\"], [3, \"cyan\"]))\n",
    "\n",
    "# Show circulation graph alone\n",
    "Topology.Show(circulation_graph,\n",
    "              vertexSizeKey=\"size\",\n",
    "              vertexColorKey=\"color\",\n",
    "              edgeWidthKey=\"width\",\n",
    "              edgeColorKey=\"color\",\n",
    "              backgroundColor=\"white\",\n",
    "              width=800, height=600,\n",
    "              renderer=renderer)"
]))

# ================================================================
# SECTION B: BUILDING + YELLOW APERTURES
# ================================================================
new_cells.append(md("## BUILDING WITH APERTURES (Yellow Doors)"))

new_cells.append(code([
    "# Tag building faces light blue, door aperture faces yellow\n",
    "for obj in objects:\n",
    "    for face in Topology.Faces(obj):\n",
    "        Topology.SetDictionary(face, Dictionary.ByKeysValues([\"face_color\"], [[210, 210, 250]]))\n",
    "\n",
    "for obj in Aperture:\n",
    "    for face in Topology.Faces(obj):\n",
    "        Topology.SetDictionary(face, Dictionary.ByKeysValues([\"face_color\"], [[255, 215, 0]]))\n",
    "\n",
    "# Show building + yellow door apertures\n",
    "Topology.Show(objects, Aperture,\n",
    "              faceColorKey=\"face_color\",\n",
    "              faceOpacity=0.4,\n",
    "              edgeColor=[180, 180, 180],\n",
    "              edgeWidth=1,\n",
    "              showVertices=False,\n",
    "              backgroundColor=\"white\",\n",
    "              width=800, height=600,\n",
    "              renderer=renderer)"
]))

# ================================================================
# SECTION C: COLOR-CODED ROOMS
# ================================================================
new_cells.append(md("## COLOR-CODED SPACES BY ROOM TYPE"))

new_cells.append(code([
    "# Room-type colour palette\n",
    "# Layout: 3 floors x 10 apartments (2 bedrooms, 2 bathrooms, 1 kitchen, 1 living room)\n",
    "# + 6 elevators/floor + 4 stairs/floor + corridors  =>  ~236 cells total\n",
    "room_palette = {\n",
    "    \"bathroom\":    [102, 205, 170],   # aquamarine\n",
    "    \"kitchen\":     [255, 127,  80],   # coral\n",
    "    \"bedroom\":     [100, 149, 237],   # cornflower blue\n",
    "    \"living_room\": [255, 215,   0],   # gold\n",
    "    \"elevator\":    [147, 112, 219],   # medium purple\n",
    "    \"stairs\":      [160,  82,  45],   # sienna\n",
    "    \"corridor\":    [192, 192, 192],   # silver\n",
    "}\n",
    "\n",
    "# Compute volume per cell\n",
    "cells_list = Topology.Cells(cellComplex)\n",
    "cell_volumes = []\n",
    "for c in cells_list:\n",
    "    try:\n",
    "        vol = Cell.Volume(c)\n",
    "        cell_volumes.append(float(vol) if (vol and vol > 0) else 0.0)\n",
    "    except:\n",
    "        cell_volumes.append(0.0)\n",
    "\n",
    "# Sort ascending; exclude zero-volume (degenerate) cells from percentile calc\n",
    "indexed = sorted(enumerate(cell_volumes), key=lambda x: x[1])\n",
    "valid   = [(idx, vol) for idx, vol in indexed if vol > 0]\n",
    "n_valid = len(valid)\n",
    "\n",
    "# Percentile thresholds — based on expected room counts for your building.\n",
    "# Adjust these fractions if the classification doesn't look right.\n",
    "thresholds = [\n",
    "    (0.25, \"bathroom\"),    # smallest ~25% => 60 bathrooms\n",
    "    (0.38, \"kitchen\"),     # next ~13%    => 30 kitchens\n",
    "    (0.64, \"bedroom\"),     # next ~26%    => 60 bedrooms\n",
    "    (0.77, \"living_room\"), # next ~13%    => 30 living rooms\n",
    "    (0.85, \"elevator\"),    # next ~8%     => 18 elevators\n",
    "    (0.90, \"stairs\"),      # next ~5%     => 12 stairs\n",
    "    (1.01, \"corridor\"),    # remainder    => corridors\n",
    "]\n",
    "\n",
    "cell_types = [\"corridor\"] * len(cell_volumes)\n",
    "for rank, (orig_idx, vol) in enumerate(valid):\n",
    "    pct = rank / n_valid\n",
    "    for threshold, rtype in thresholds:\n",
    "        if pct < threshold:\n",
    "            cell_types[orig_idx] = rtype\n",
    "            break\n",
    "\n",
    "from collections import Counter\n",
    "print(\"Room classification (adjust thresholds above to match your building):\")\n",
    "for rtype, cnt in sorted(Counter(cell_types).items()):\n",
    "    print(f\"  {rtype:12s}: {cnt:3d} cells\")"
]))

new_cells.append(code([
    "# Apply type_color to each cell's faces via dictionary\n",
    "for i, cell in enumerate(cells_list):\n",
    "    color = room_palette[cell_types[i]]\n",
    "    for face in Topology.Faces(cell):\n",
    "        Topology.SetDictionary(face, Dictionary.ByKeysValues(\n",
    "            [\"type_color\", \"room_type\"], [color, cell_types[i]]))\n",
    "\n",
    "# Show colour-coded building\n",
    "Topology.Show(cellComplex,\n",
    "              faceColorKey=\"type_color\",\n",
    "              faceOpacity=0.5,\n",
    "              edgeColor=[100, 100, 100],\n",
    "              edgeWidth=1,\n",
    "              showVertices=False,\n",
    "              backgroundColor=\"white\",\n",
    "              width=800, height=600,\n",
    "              renderer=renderer)"
]))

# ================================================================
# LEGEND
# ================================================================
new_cells.append(md(
    "## COLOUR LEGEND\n\n"
    "| Space Type | Colour |\n"
    "|---|---|\n"
    "| Bathroom | Aquamarine |\n"
    "| Kitchen | Coral |\n"
    "| Bedroom | Cornflower Blue |\n"
    "| Living Room | Gold |\n"
    "| Elevator | Medium Purple |\n"
    "| Stairs | Sienna |\n"
    "| Corridor | Silver |\n"
    "| Apertures (Doors) | Yellow |\n"
    "| Dual Graph | Red nodes + Dark Red edges |\n"
    "| Circulation Graph | Blue nodes + Cyan edges |"
))

# ================================================================
# SECTION D: FINAL COMBINED VISUALIZATION
# ================================================================
new_cells.append(md(
    "## FINAL COMBINED VISUALIZATION\n\n"
    "Colour-coded building + yellow doors + dual graph (red) + circulation graph (blue/cyan)"
))

new_cells.append(code([
    "# Re-style dual graph: red nodes, dark red edges\n",
    "for v in Graph.Vertices(dual_graph):\n",
    "    Topology.SetDictionary(v, Dictionary.ByKeysValues([\"size\", \"color\"], [12, \"red\"]))\n",
    "for e in Graph.Edges(dual_graph):\n",
    "    Topology.SetDictionary(e, Dictionary.ByKeysValues([\"width\", \"color\"], [2, \"darkred\"]))\n",
    "\n",
    "# Re-style circulation graph: blue nodes, cyan edges\n",
    "for v in Graph.Vertices(circulation_graph):\n",
    "    Topology.SetDictionary(v, Dictionary.ByKeysValues([\"size\", \"color\"], [16, \"blue\"]))\n",
    "for e in Graph.Edges(circulation_graph):\n",
    "    Topology.SetDictionary(e, Dictionary.ByKeysValues([\"width\", \"color\"], [3, \"cyan\"]))\n",
    "\n",
    "# Ensure aperture faces are tagged yellow (override any room-type colour)\n",
    "for obj in Aperture:\n",
    "    for face in Topology.Faces(obj):\n",
    "        Topology.SetDictionary(face, Dictionary.ByKeysValues([\"type_color\"], [[255, 215, 0]]))\n",
    "\n",
    "# FINAL: colour-coded building + yellow doors + dual graph (red) + circulation (blue)\n",
    "Topology.Show(\n",
    "    cellComplex, Aperture,\n",
    "    dual_graph,\n",
    "    circulation_graph,\n",
    "    faceColorKey=\"type_color\",\n",
    "    faceOpacity=0.2,\n",
    "    vertexSizeKey=\"size\",\n",
    "    vertexColorKey=\"color\",\n",
    "    edgeWidthKey=\"width\",\n",
    "    edgeColorKey=\"color\",\n",
    "    showVertices=True,\n",
    "    backgroundColor=\"white\",\n",
    "    width=1000, height=700,\n",
    "    renderer=renderer\n",
    ")"
]))

# Insert all new cells after the target cell
nb['cells'] = nb['cells'][:target+1] + new_cells + nb['cells'][target+1:]
print(f"Added {len(new_cells)} cells. Total cells: {len(nb['cells'])}")

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Saved!")
