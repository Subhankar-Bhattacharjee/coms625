# 625 Project

This project is designed to perform program analysis and generate a Program Dependency Graph (PDG) with suspicious score mapping. Follow the steps below to set up and run the project.

## Prerequisites

Make sure you have the following installed on your system:

- Docker
- Python 3 with `pip3`
- Clang (for LLVM generation)
- Graphviz (for `.dot` file conversion)
- Make sure the Perfograph ran from the link "https://github.com/tehranixyz/perfograph" and generated AST in .jason format.

## Setup Instructions to run prototype of fault localization tool

1. **Build the Docker Image**
   ```bash
   docker build -t 625-project .

2. **Run the Docker Image**
   docker run -it -v /Local_path:/usr/src/app 625-project

3. **Install dependencies**
   pip3 install --break-system-packages networkx

4. **Generate Suspicious Score Report**
   python3 1_trace_suspecious_score_report.py

5. **Generate LLVM Intermediate Representation**
   clang -S -emit-llvm -g -o program.ll program.c

6. **Update JSON Using Intermediate Information**
   python3 2_updated_json_using_II.py

7. **Map Suspicious Scores to the Program Dependency Graph (PDG)**
   python3 3_map_suspecious_score_PDG.py

8. **Generate Highlighted PDG Visualization**
   dot -Tpng highlighted_nodes_pdg.dot -o PDG_highlighted_PNG.png

9. **Generate Updated PDG JSON**
   python3 4_generate_modified_PDG_json.py

10. **Generate Original PDG Visualization**
   dot -Tpng PDG_Dot_File.dot -o PDG_PNG_File.png

The examples directory contains, toy example file for this tool. Follow the above instruction to get the results.
