import argparse
import re
import sys
from pathlib import Path

def parse_arguments():
    """Handles Command Line Arguments"""
    parser = argparse.ArgumentParser(
        description="etxDIR: Generate directory structures from PlantUML files."
    )
    parser.add_argument(
        "source_file", 
        type=Path, 
        help="Path to the source .puml or .txt file"
    )
    parser.add_argument(
        "target_directory", 
        type=Path, 
        help="Root path where the structure will be generated"
    )
    return parser.parse_args()

def clean_name(name_str):
    """
    Removes quotes, extra whitespace, and tree symbols.
    """
    if not name_str:
        return ""
    # Remove Salt tree markers like "++ " or "+ "
    cleaned = re.sub(r'^\s*\++\s*', '', name_str)
    return cleaned.strip().strip('"').strip("'")

def is_salt_file(lines):
    """Detects if the file uses Salt (Tree) syntax (lines start with +)."""
    for line in lines:
        if line.strip().startswith("{T"):
            return True
        if re.match(r'^\s*\+', line):
            return True
    return False

def parse_salt_tree(lines, target_root):
    """
    Parses PlantUML Salt (Tree) syntax:
    + folder
    ++ subfolder
    ++ file.txt
    """
    print("-> Detected Salt/Tree Syntax.")
    
    # Pre-process: Extract (depth, name) tuples
    items = []
    for line in lines:
        line = line.strip()
        # Skip control characters and comments
        if not line or line.startswith("'") or line == "}" or line == "{" or line == "{T" or line.startswith("@"):
            continue
        
        # Regex to capture the plus signs (depth) and the name
        # ^(\++) matches one or more plus signs at the start
        match = re.match(r'^(\++)\s*(.*)', line)
        if match:
            pluses = match.group(1)
            name_part = match.group(2)
            depth = len(pluses)
            clean = clean_name(name_part)
            if clean:
                items.append({'depth': depth, 'name': clean})

    if not items:
        print("Warning: No items found in Salt structure.")
        return

    # Dictionary to track the active directory at each depth level
    # Level 0 is the target root.
    dir_stack = {0: target_root}

    for i, item in enumerate(items):
        depth = item['depth']
        name = item['name']
        
        # Look ahead to see if this item has children (is it a folder?)
        is_directory = False
        if i + 1 < len(items):
            next_depth = items[i+1]['depth']
            if next_depth > depth:
                is_directory = True
        
        # The parent is the directory at the previous depth level (depth - 1)
        # If the structure skips levels (bad practice but possible), fall back to closest parent
        parent_depth = depth - 1
        while parent_depth > 0 and parent_depth not in dir_stack:
            parent_depth -= 1
        
        parent_dir = dir_stack.get(parent_depth, target_root)
        current_path = parent_dir / name

        if is_directory:
            try:
                current_path.mkdir(parents=True, exist_ok=True)
                print(f"[DIR]  {current_path}")
                # Register this path as the parent for the next level
                dir_stack[depth] = current_path 
            except OSError as e:
                print(f"Error creating dir {name}: {e}")
        else:
            # It's a file
            try:
                # Ensure parent exists
                parent_dir.mkdir(parents=True, exist_ok=True)
                # Create empty file
                with open(current_path, 'w', encoding='utf-8') as f:
                    pass
                print(f"[FILE] {current_path}")
            except OSError as e:
                print(f"Error creating file {name}: {e}")

def parse_classic_uml(lines, target_root):
    """
    Parses standard PlantUML Package/Class syntax.
    """
    print("-> Detected Standard Class/Package Syntax.")
    
    definition_pattern = re.compile(
        r'^\s*(package|folder|namespace|node|component|class|interface|file|artifact|object)\s+(?:"([^"]+)"|([^\s{]+))', 
        re.IGNORECASE
    )

    current_path = target_root
    path_stack = [current_path]

    for line in lines:
        line = line.strip()
        if not line or line.startswith("'") or line.startswith("@"): continue

        if line.startswith('}'):
            if len(path_stack) > 1:
                path_stack.pop()
            continue

        match = definition_pattern.search(line)
        if match:
            obj_type = match.group(1).lower()
            raw_name = match.group(2) if match.group(2) else match.group(3)
            obj_name = clean_name(raw_name)

            if obj_type in ['package', 'folder', 'namespace', 'node', 'component']:
                new_dir = path_stack[-1] / obj_name
                new_dir.mkdir(exist_ok=True)
                print(f"[DIR]  {new_dir}")
                path_stack.append(new_dir)
            
            elif obj_type in ['class', 'interface', 'file', 'artifact', 'object']:
                new_file = path_stack[-1] / obj_name
                with open(new_file, 'w', encoding='utf-8') as f: pass
                print(f"[FILE] {new_file}")

def main():
    args = parse_arguments()
    
    target_root = args.target_directory.resolve()
    try:
        target_root.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating root: {e}")
        sys.exit(1)

    print(f"--- etxDIR Processing: {args.source_file.name} ---")

    try:
        with open(args.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{args.source_file}' not found.")
        sys.exit(1)

    # Route to correct parser
    if is_salt_file(lines):
        parse_salt_tree(lines, target_root)
    else:
        parse_classic_uml(lines, target_root)

    print("\nProcessing Complete.")

if __name__ == "__main__":
    main()