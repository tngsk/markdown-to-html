import json
import subprocess
from pathlib import Path

def test_mono_flow_geometry_pure_calculation():
    """Test MonoFlowGeometry pure function produces deterministic bezier curves and label positions"""
    script_path = Path("src/components/mono-flow/script.js").resolve()
    assert script_path.exists(), "mono-flow script.js not found"

    # Node.js から純粋関数モジュールとしてロードし計算結果を取得
    node_code = f"""
    const geom = require({json.dumps(str(script_path))});

    const wrapper = {{ left: 0, top: 0, width: 800, height: 600 }};
    const nodeA = {{ left: 100, top: 100, width: 100, height: 60 }};
    const nodeB = {{ left: 300, top: 100, width: 100, height: 60 }};

    const resLR = geom.calculateFlowCurve(nodeA, nodeB, wrapper, 'LR');
    const resTB = geom.calculateFlowCurve(nodeA, nodeB, wrapper, 'TB');

    console.log(JSON.stringify({{ lr: resLR, tb: resTB }}));
    """

    res = subprocess.run(["node", "-e", node_code], capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)

    # LR (水平フロー) の検証
    lr = data["lr"]
    assert lr["startX"] == 200  # nodeA.left(100) + nodeA.width(100)
    assert lr["startY"] == 130  # nodeA.top(100) + nodeA.height/2(30)
    assert lr["endX"] == 300    # nodeB.left(300)
    assert lr["endY"] == 130    # nodeB.top(100) + nodeB.height/2(30)
    assert "M 200 130 C 250 130, 250 130, 300 130" == lr["d"]
    assert lr["midX"] == 250
    assert lr["midY"] == 130

    # TB (垂直フロー) の検証
    tb = data["tb"]
    assert tb["startX"] == 150  # nodeA.left(100) + nodeA.width/2(50)
    assert tb["startY"] == 160  # nodeA.top(100) + nodeA.height(60)
    assert tb["endX"] == 350    # nodeB.left(300) + nodeB.width/2(50)
    assert tb["endY"] == 100    # nodeB.top(100)
    assert tb["d"].startswith("M 150 160 C 150")
    assert tb["midX"] == 250
    assert tb["midY"] == 130
