import json

# Read the notebook
with open(r"C:\Users\Chloe\Documents\GitHub\A1_GraphML_GraphGeneration\A1_Chloe_FinalNoteBook.ipynb", 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find the cell with the error (the one that starts with "from topologicpy.Cell import Cell")
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        # Check if this is the cell that uses Aperture without defining it
        source = ''.join(cell['source'])
        if 'from topologicpy.Cell import Cell' in source and 'for obj in Aperture:' in source and 'Load door apertures' not in source:
            # Add the code to load Aperture at the beginning
            new_source = [
                "from topologicpy.Cell import Cell\n",
                "\n",
                "# Load door apertures from OBJ file\n",
                'Aperture = Topology.ByOBJPath(r"C:\\Users\\Chloe\\Documents\\GitHub\\A1_GraphML_GraphGeneration\\OBJ_Files\\DoorsApertures.obj")\n',
                'print(f"Loaded {len(Aperture)} door aperture objects")\n',
                "\n",
                "# Collect all door faces from the apertures OBJ\n",
                "aperture_faces = []\n",
                "for obj in Aperture:\n",
                "    aperture_faces.extend(Topology.Faces(obj))\n",
                'print(f"Total door aperture faces: {len(aperture_faces)}")\n',
                "\n",
                "# Attach door faces as apertures onto matching shared faces of the CellComplex\n",
                "cellComplex_doors = Topology.AddApertures(\n",
                "    cellComplex, aperture_faces,\n",
                '    subTopologyType="face",\n',
                "    tolerance=0.01\n",
                ")\n",
                '"Apertures added to CellComplex")\n'
            ]
            cell['source'] = new_source
            print(f"Fixed cell {i}")
            break

# Save the modified notebook
with open(r"C:\Users\Chloe\Documents\GitHub\A1_GraphML_GraphGeneration\A1_Chloe_FinalNoteBook.ipynb", 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print("Notebook fixed successfully!")
