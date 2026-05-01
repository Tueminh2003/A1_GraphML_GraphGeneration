import json, uuid

path = r'C:\Users\Chloe\Documents\GitHub\A1_GraphML_GraphGeneration\A1_Chloe_FinalNoteBook.ipynb'

with open(path, encoding='utf-8-sig') as f:
    nb = json.load(f)

print(f"Current cells: {len(nb['cells'])}")

# Only add if the last cell doesn't already have the graph-only viz
last_src = ''.join(nb['cells'][-1]['source'])
if 'GRAPHS ONLY' in last_src:
    print("Graph-only cell already exists, nothing to do.")
else:
    new_cell_src = (
        "# === GRAPHS ONLY: Dual (red nodes, darkred edges) + Circulation (blue nodes, cyan edges) ===\n"
        "\n"
        "# Re-style dual graph: red nodes, dark red edges\n"
        "for v in Graph.Vertices(dual_graph):\n"
        "    Topology.SetDictionary(v, Dictionary.ByKeysValues([\"size\", \"color\"], [12, \"red\"]))\n"
        "for e in Graph.Edges(dual_graph):\n"
        "    Topology.SetDictionary(e, Dictionary.ByKeysValues([\"width\", \"color\"], [2, \"darkred\"]))\n"
        "\n"
        "# Re-style circulation graph: blue nodes, cyan edges\n"
        "for v in Graph.Vertices(circulation_graph):\n"
        "    Topology.SetDictionary(v, Dictionary.ByKeysValues([\"size\", \"color\"], [16, \"blue\"]))\n"
        "for e in Graph.Edges(circulation_graph):\n"
        "    Topology.SetDictionary(e, Dictionary.ByKeysValues([\"width\", \"color\"], [3, \"cyan\"]))\n"
        "\n"
        "Topology.Show(dual_graph, circulation_graph,\n"
        "              vertexSizeKey=\"size\",\n"
        "              vertexColorKey=\"color\",\n"
        "              edgeWidthKey=\"width\",\n"
        "              edgeColorKey=\"color\",\n"
        "              backgroundColor=\"white\",\n"
        "              width=900,\n"
        "              height=700,\n"
        "              renderer=renderer)\n"
    )

    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "source": new_cell_src.splitlines(keepends=True)
    }

    nb['cells'].append(new_cell)
    print(f"New cell ID: {new_cell['id']}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"Done. Total cells: {len(nb['cells'])}")
