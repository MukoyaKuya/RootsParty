
import os
import re
import glob

def extract_trans_strings(template_dir):
    trans_strings = set()
    trans_pattern = re.compile(r'{%\s*trans\s+"(.*?)"\s*%}')
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = trans_pattern.findall(content)
                        for match in matches:
                            trans_strings.add(match)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return trans_strings

def update_po_file(po_file_path, new_strings):
    if not os.path.exists(po_file_path):
        print(f"PO file not found: {po_file_path}")
        return

    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading PO file: {e}")
        return

    existing_msgids = set(re.findall(r'msgid "(.*?)"', content))
    
    with open(po_file_path, 'a', encoding='utf-8') as f:
        for s in new_strings:
            if s not in existing_msgids:
                print(f"Adding new string: {s}")
                f.write(f'\nmsgid "{s}"\n')
                f.write('msgstr ""\n')

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    po_file = os.path.join(base_dir, 'locale', 'sw', 'LC_MESSAGES', 'django.po')
    
    print("Extracting strings...")
    strings = extract_trans_strings(templates_dir)
    print(f"Found {len(strings)} unique translatable strings.")
    
    print("Updating PO file...")
    update_po_file(po_file, strings)
    print("Done.")
