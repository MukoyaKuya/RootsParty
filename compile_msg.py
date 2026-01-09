import struct
import os

def msgfmt(input_file, output_file):
    messages = {}
    current_msgid = None
    current_msgstr = None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('msgid '):
            if current_msgid is not None and current_msgstr is not None:
                messages[current_msgid] = current_msgstr
            current_msgid = line[6:].strip('"')
            current_msgstr = ""
        elif line.startswith('msgstr '):
            current_msgstr = line[7:].strip('"')
        elif line.startswith('"'):
            # Multiline
            if current_msgstr is not None:
                current_msgstr += line.strip('"')
            elif current_msgid is not None:
                current_msgid += line.strip('"')

    if current_msgid is not None and current_msgstr is not None:
        messages[current_msgid] = current_msgstr

    keys = sorted(messages.keys())
    count = len(keys)
    
    string_buffer = bytearray()
    key_descriptors = []
    val_descriptors = []
    
    # Calculate start of data segment
    # Header: 28 bytes
    # Key descriptors: count * 8
    # Val descriptors: count * 8
    datastart = 28 + (2 * count * 8)
    
    for k in keys:
        v = messages[k]
        
        # Key
        k_bytes = k.encode('utf-8') + b'\0'
        k_len = len(k_bytes) - 1 # Length without null
        k_off = datastart + len(string_buffer)
        string_buffer.extend(k_bytes)
        key_descriptors.append((k_len, k_off))
        
        # Value
        v_bytes = v.encode('utf-8') + b'\0'
        v_len = len(v_bytes) - 1
        v_off = datastart + len(string_buffer)
        string_buffer.extend(v_bytes)
        val_descriptors.append((v_len, v_off))
        
    with open(output_file, 'wb') as f:
        # Magic
        f.write(struct.pack('<I', 0x950412de))
        # Version
        f.write(struct.pack('<I', 0))
        # N
        f.write(struct.pack('<I', count))
        # Offset originals
        f.write(struct.pack('<I', 28))
        # Offset translations
        f.write(struct.pack('<I', 28 + count * 8))
        # Hash size (0)
        f.write(struct.pack('<I', 0))
        # Hash offset (0)
        f.write(struct.pack('<I', 0))
        
        # Key descriptors
        for l, o in key_descriptors:
            f.write(struct.pack('<II', l, o))
            
        # Value descriptors
        for l, o in val_descriptors:
            f.write(struct.pack('<II', l, o))
            
        # Data
        f.write(string_buffer)
    print(f"Compiled {count} messages to {output_file}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Little Human\Desktop\RootsParty"
    po_file = os.path.join(base_dir, "locale", "sw", "LC_MESSAGES", "django.po")
    mo_file = os.path.join(base_dir, "locale", "sw", "LC_MESSAGES", "django.mo")
    
    if os.path.exists(po_file):
        msgfmt(po_file, mo_file)
    else:
        print(f"File not found: {po_file}")
