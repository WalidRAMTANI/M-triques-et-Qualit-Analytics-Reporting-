import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from app.database import SessionLocal, AAVModel

def generate_aav_dependency_graph(target_aav_id):
    """
    Generates a base64 encoded image of the dependency graph for a target AAV.
    """
    db = SessionLocal()
    try:
        # Build the graph starting from target_aav_id and its prerequisites
        G = nx.DiGraph()
        
        to_process = [target_aav_id]
        processed = set()
        
        while to_process:
            curr_id = to_process.pop(0)
            if curr_id in processed:
                continue
            processed.add(curr_id)
            
            aav = db.query(AAVModel).filter(AAVModel.id_aav == curr_id).first()
            if not aav:
                continue
            
            # Add node with name
            G.add_node(curr_id, label=aav.nom)
            
            # Process prerequisites
            prereqs = aav.prerequis_ids or []
            if isinstance(prereqs, str):
                import json
                try:
                    prereqs = json.loads(prereqs)
                except:
                    prereqs = []
            
            for pr_id in prereqs:
                G.add_edge(pr_id, curr_id)
                if pr_id not in processed:
                    to_process.append(pr_id)
        
        if not G.nodes():
            return None

        # Draw the graph
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        
        labels = nx.get_node_attributes(G, 'label')
        # Combined ID + Label for better visibility
        final_labels = {k: f"{k}\n{v[:15]}..." if len(v) > 15 else f"{k}\n{v}" for k, v in labels.items()}
        
        nx.draw(G, pos, labels=final_labels, with_labels=True, 
                node_color='#BBDEFB', node_size=2000, 
                font_size=8, font_weight='bold', 
                arrows=True, edge_color='#1565C0')
        
        plt.title(f"Graphe des prérequis (AAV #{target_aav_id})")
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Encode to base64
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    finally:
        db.close()

def generate_interactive_graph(target_aav_id):
    """
    Generates an interactive dependency graph using Pyvis and returns the path to the HTML file.
    """
    db = SessionLocal()
    try:
        from pyvis.network import Network
        import tempfile
        import os
        import json
        
        G = nx.DiGraph()
        
        to_process = [target_aav_id]
        processed = set()
        
        while to_process:
            curr_id = to_process.pop(0)
            if curr_id in processed:
                continue
            processed.add(curr_id)
            
            aav = db.query(AAVModel).filter(AAVModel.id_aav == curr_id).first()
            if not aav:
                continue
            
            # Add node with title (tooltip) and label
            label_text = f"{curr_id}: {aav.nom[:20]}..." if len(aav.nom) > 20 else f"{curr_id}: {aav.nom}"
            G.add_node(curr_id, label=label_text, title=f"[{curr_id}] {aav.nom}\nType: {aav.type_aav}", color="#1565C0" if curr_id == target_aav_id else "#BBDEFB")
            
            # Process prerequisites
            prereqs = aav.prerequis_ids or []
            if isinstance(prereqs, str):
                try:
                    prereqs = json.loads(prereqs)
                except:
                    prereqs = []
            
            for pr_id in prereqs:
                G.add_edge(pr_id, curr_id, color="#9C27B0")
                if pr_id not in processed:
                    to_process.append(pr_id)
        
        if not G.nodes():
            return None

        # Create interactive network container
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
        net.from_nx(G)
        
        # Options for better visualization
        net.set_options("""
        var options = {
          "nodes": {
            "font": { "size": 14, "face": "Inter" },
            "shape": "box",
            "borderWidth": 2
          },
          "edges": {
            "arrows": { "to": { "enabled": true, "scaleFactor": 1.2 } },
            "smooth": { "type": "continuous", "forceDirection": "none" }
          },
          "physics": {
            "hierarchicalRepulsion": { "centralGravity": 0.0, "springLength": 150, "nodeDistance": 150 },
            "minVelocity": 0.75,
            "solver": "hierarchicalRepulsion"
          }
        }
        """)
        
        # Save HTML
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"graphe_aav_{target_aav_id}.html")
        net.write_html(file_path)
        
        return file_path
    finally:
        db.close()
