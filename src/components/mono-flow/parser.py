import re
import html
import json
from src.processors.base_parser import BaseComponentParser
from collections import defaultdict, deque

class Parser(BaseComponentParser):
    START_PATTERN = r"@\[flow(?:\:\s*([^\]]*))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[/flow\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-flow"]

    def process(self, markdown_content: str) -> str:
        # Match from @[flow] to @[/flow] using a non-greedy wildcard.
        # We need to capture the opening tag, the content, and the closing tag.
        pattern = re.compile(f"({self.START_PATTERN})(.*?)({self.END_PATTERN})", re.DOTALL)

        def replacer(match: re.Match) -> str:
            start_tag = match.group(1)
            title = match.group(2)
            args_str = match.group(3)
            content = match.group(4)
            end_tag = match.group(5)

            args = self.parse_key_value_args(args_str)
            direction = args.get("direction", "LR").strip("'\"").upper()

            nodes = set()
            edges = []

            # Parse the content line by line
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Parse: Node A -> Node B : Label
                parts = line.split('->')
                if len(parts) == 1:
                    # Just a single node
                    node = parts[0].strip()
                    if node:
                        nodes.add(node)
                elif len(parts) == 2:
                    node_a = parts[0].strip()
                    rest = parts[1]
                    label = ""
                    if ':' in rest:
                        node_b_part, label_part = rest.split(':', 1)
                        node_b = node_b_part.strip()
                        label = label_part.strip()
                    else:
                        node_b = rest.strip()

                    if node_a:
                        nodes.add(node_a)
                    if node_b:
                        nodes.add(node_b)
                    if node_a and node_b:
                        edges.append({
                            "from": node_a,
                            "to": node_b,
                            "label": label
                        })

            # Calculate layers
            layers = self._calculate_layers(nodes, edges)

            # Build HTML
            attrs = []
            if title and title.strip():
                 attrs.append(f'title="{html.escape(title.strip())}"')
            attrs.append(f'direction="{html.escape(direction)}"')
            attrs_str = " ".join(attrs)

            result = f'<mono-flow {attrs_str}>\n'
            result += '<div class="flow-container">\n'

            # Calculate max layer
            max_layer = max(layers.values()) if layers else 0

            # Group nodes by layer
            layer_to_nodes = defaultdict(list)
            for node, layer in layers.items():
                layer_to_nodes[layer].append(node)

            for layer_idx in range(max_layer + 1):
                if layer_idx in layer_to_nodes:
                    result += f'<div class="flow-layer" data-layer="{layer_idx}">\n'
                    for node in sorted(layer_to_nodes[layer_idx]): # Sort to maintain consistent order
                        safe_node = html.escape(node)
                        # We use data-id to identify the node for SVG path generation
                        result += f'<div class="flow-node" data-id="{safe_node}">{safe_node}</div>\n'
                    result += '</div>\n'

            result += '</div>\n'

            # Embed connections as JSON
            safe_edges = json.dumps(edges).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            result += f"<script type=\"application/json\" class=\"flow-connections\">{safe_edges}</script>\n"

            result += '</mono-flow>'
            return result

        return pattern.sub(replacer, markdown_content)

    def _calculate_layers(self, nodes: set[str], edges: list[dict]) -> dict[str, int]:
        """
        Calculate the visual layer (depth) of each node using a topological sort / longest path approach.
        Handles cycles by tracking visited nodes in the current path.
        """
        if not nodes:
            return {}

        # Build adjacency list
        adj = defaultdict(list)
        in_degree = {node: 0 for node in nodes}
        for edge in edges:
            u, v = edge['from'], edge['to']
            adj[u].append(v)
            in_degree[v] = in_degree.get(v, 0) + 1

        # Find starting nodes (in-degree 0)
        start_nodes = [node for node in nodes if in_degree[node] == 0]
        if not start_nodes and nodes:
            # Graph might be a single cycle, pick an arbitrary node
            start_nodes = [next(iter(nodes))]

        layers = {node: 0 for node in nodes}

        # Use BFS to find longest path to each node
        queue = deque([(node, 0) for node in start_nodes])
        while queue:
            curr_node, curr_layer = queue.popleft()

            # If we found a longer path, update layer
            if curr_layer > layers[curr_node]:
                layers[curr_node] = curr_layer

            for neighbor in adj[curr_node]:
                # Simple cycle prevention: limit max layer
                # Or just update if we found a strictly longer path and it's less than num_nodes
                if curr_layer + 1 > layers[neighbor] and curr_layer + 1 <= len(nodes):
                    layers[neighbor] = curr_layer + 1
                    queue.append((neighbor, curr_layer + 1))

        # Pull unconnected nodes to layer 0
        for node in nodes:
            if in_degree[node] == 0 and not adj[node]:
                layers[node] = 0

        return layers
