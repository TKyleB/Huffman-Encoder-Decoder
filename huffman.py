import argparse, heapq, pickle
from pathlib import Path
from collections import defaultdict

class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

def get_letter_frequency(file_path: Path) -> defaultdict:
    letter_frequency = defaultdict(int)
    
    with open(file_path, "rt", encoding="utf-8-sig") as file:
        for line in file:
            for c in line:
                letter_frequency[c] += 1
    return letter_frequency
def build_huffman_tree(letter_freq: defaultdict) -> Node:
    nodes = []
    for key, value in letter_freq.items():
        node = Node(freq=value, symbol=key)
        nodes.append(node)
    heapq.heapify(nodes)
    
    while len(nodes) > 1:
        nodes.sort()
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)
        combined_nodes = Node(left.freq + right.freq, left=left, right=right)
        heapq.heappush(nodes, combined_nodes)
   
    return nodes[0]
def generate_huffman_codes(node: Node, code="", huffman_codes={}) -> dict[str, str]:
    if node is not None:
        if node.symbol is not None:
            huffman_codes[node.symbol] = code
        generate_huffman_codes(node.left, code + '0', huffman_codes)
        generate_huffman_codes(node.right, code + '1', huffman_codes)
    
    return huffman_codes
def encode(input_file_path: Path, output_file_path: Path, huffman_tree_base_node: None, huffman_codes: dict[str, str]) -> None:
    with open(output_file_path, "wb") as output_file, open(input_file_path, "rt", encoding="utf-8-sig") as input_file:
        # Write header file containing base node. First 4 bytes specify length of header
        header_bytes = pickle.dumps(huffman_tree_base_node)
        header_lenth = len(header_bytes).to_bytes(4, byteorder="big")
        output_file.write(header_lenth)
        output_file.write(header_bytes)
        
        # Begin encoding input file to output file
        encoded_bits = ""
        for line in input_file:
            for c in line:
                encoded_bits += huffman_codes[c]
                # Convert encoded_bits to bytes and write to output_file when it's a multiple of 8
                while len(encoded_bits) >= 8:
                    byte_data = int(encoded_bits[:8], 2).to_bytes(1, byteorder="big")
                    output_file.write(byte_data)
                    encoded_bits = encoded_bits[8:]
        # Write any remaining bits padded with zeros
        if encoded_bits:
            remaining_bits = encoded_bits.ljust(8, '0')
            byte_data = int(remaining_bits, 2).to_bytes(1, byteorder="big")
            output_file.write(byte_data)        
def decode(input_file_path: Path, output_file_path: Path) -> None:
    with open(input_file_path, "rb") as input_file:
        header_length = int.from_bytes(input_file.read(4), byteorder="big")
        header_bytes = input_file.read(header_length)
        header_data = pickle.loads(header_bytes)
        huffman_codes = generate_huffman_codes(header_data)
        bitstream = ""
        byte = input_file.read(1)
        while byte:
             byte = ord(byte)
             bitstream += f"{byte:08b}"
             byte = input_file.read(1)
        
        decoded_data = ""
        current_code = ""
        for bit in bitstream:
            current_code += bit
            for char, code in huffman_codes.items():
                if current_code == code:
                    decoded_data += char
                    current_code = ""
                    break
                
    with open(output_file_path, "wt", encoding="utf-8") as output_file:
        output_file.write(decoded_data)
             

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Huffman Coding Encoder/Decoder")
    parser.add_argument("--encode", action="store_true", help="Encode input file using Huffman coding")
    parser.add_argument("--decode", action="store_true", help="Decode input file using Huffman coding")
    parser.add_argument("input_file", type=Path, help="Input file path")
    parser.add_argument("output_file", type=Path, help="Output file path")
    
    args = parser.parse_args()
    input_file = Path(args.input_file)
    output_file = Path(args.output_file)
    if args.encode:
        if input_file.exists():
            letter_freq = get_letter_frequency(input_file)
            huffman_tree_base_node = build_huffman_tree(letter_freq)
            huffman_codes = generate_huffman_codes(huffman_tree_base_node)
            encode(input_file, output_file, huffman_tree_base_node, huffman_codes)
            print(f"{input_file} encoded as {output_file}")
    if args.decode:
        if input_file.exists():
            decode(input_file, output_file)
            print(f"{input_file} decoded as {output_file}")

    
    