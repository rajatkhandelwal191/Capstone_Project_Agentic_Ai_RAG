from pathlib import Path

from app.graph.graph import build_graph


def export_mermaid(output_path: str = "docs/graph_flow.mmd") -> Path:
    compiled_graph = build_graph()
    mermaid = compiled_graph.get_graph().draw_mermaid()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(mermaid, encoding="utf-8")
    return path


if __name__ == "__main__":
    out = export_mermaid()
    print(f"Mermaid graph written to: {out}")
