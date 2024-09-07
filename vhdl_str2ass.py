import re
import sys
from collections import defaultdict

class VHDLParser:
    def __init__(self, top_level_file):
        self.top_level_file = top_level_file
        self.entity_name = ""
        self.top_ports = {}
        self.instances = {}
        self.net_connections = defaultdict(list)

    def parse_entity_ports(self, lines):
        in_entity = False
        for line in lines:
            line = line.strip()
            if line.startswith("--") or not line:
                continue

            if "entity" in line:
                in_entity = True
                self.entity_name = re.search(r'entity\s+(\w+)\s+is', line).group(1)

            if in_entity and ("port" in line):
                port_lines = []
                while ";" not in line:
                    port_lines.append(line)
                    line = next(lines).strip()

                ports_str = " ".join(port_lines)
                ports = re.findall(r'(\w+)\s*:\s*(in|out|inout)\s*', ports_str)
                for port, direction in ports:
                    self.top_ports[port] = direction

            if "end" in line and in_entity:
                in_entity = False
                break

    def parse_instance(self, lines):
        for line in lines:
            line = line.strip()
            if line.startswith("--") or not line:
                continue

            match = re.search(r'(\w+)\s*:\s*(?:entity|component)\s+([\w\.]+)\s*port\s*map\s*\(([^;]+)\);', line)
            if match:
                instance_name, component_name, ports_str = match.groups()
                ports = [p.strip() for p in ports_str.split(',')]
                port_mapping = {}
                for port in ports:
                    port_name, net_name = [p.strip() for p in port.split("=>")]
                    port_mapping[port_name] = net_name

                self.instances[instance_name] = {
                    'component': component_name,
                    'ports': port_mapping,
                    'port_directions': self.parse_component_ports(component_name)
                }

    def parse_component_ports(self, component_name):
        component_file = f"{component_name}-e.vhd"
        try:
            with open(component_file, 'r') as file:
                lines = iter(file.readlines())
                port_directions = {}
                in_entity = False
                for line in lines:
                    line = line.strip()
                    if line.startswith("--") or not line:
                        continue

                    if "entity" in line:
                        in_entity = True

                    if in_entity and ("port" in line):
                        port_lines = []
                        while ";" not in line:
                            port_lines.append(line)
                            line = next(lines).strip()

                        ports_str = " ".join(port_lines)
                        ports = re.findall(r'(\w+)\s*:\s*(in|out|inout)\s*', ports_str)
                        for port, direction in ports:
                            port_directions[port] = direction

                    if "end" in line and in_entity:
                        break
                return port_directions
        except FileNotFoundError:
            sys.stderr.write(f"Error: Component VHDL file {component_file} not found.\n")
            return {}

    def collect_connections(self):
        for instance_name, instance_info in self.instances.items():
            for port, net in instance_info['ports'].items():
                direction = instance_info['port_directions'].get(port)
                if direction:
                    self.net_connections[net].append(f"{instance_name}.{port}:{direction}")

        for top_port, direction in self.top_ports.items():
            if top_port in self.net_connections:
                self.net_connections[top_port].insert(0, f"{top_port}:{direction}")
            else:
                self.net_connections[top_port] = [f"{top_port}:{direction}"]

    def output_to_file(self, output_file):
        try:
            with open(output_file, 'w') as file:
                for net, connections in self.net_connections.items():
                    file.write(f"{net},{', '.join(connections)}\n")
            print(f"Output written to {output_file}")
        except Exception as e:
            sys.stderr.write(f"Error: Failed to write to output file {output_file}. {str(e)}\n")

    def parse(self):
        try:
            with open(self.top_level_file, 'r') as file:
                lines = iter(file.readlines())
                self.parse_entity_ports(lines)
                self.parse_instance(lines)
                self.collect_connections()
        except FileNotFoundError:
            sys.stderr.write(f"Error: VHDL file {self.top_level_file} not found.\n")
        except Exception as e:
            sys.stderr.write(f"Error: An error occurred while parsing {self.top_level_file}. {str(e)}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_vhdl_file> <output_text_file>")
        sys.exit(1)

    input_vhdl_file = sys.argv[1]
    output_text_file = sys.argv[2]

    parser = VHDLParser(input_vhdl_file)
    parser.parse()
    parser.output_to_file(output_text_file)

if __name__ == "__main__":
    main()
