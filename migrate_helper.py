import ast
import subprocess

def parse_env_vars(filepath):
    with open(filepath, 'r') as f:
        content = f.read().strip()
    
    # Split by semicolon if present, otherwise treat as single dict or list
    if ';' in content:
        parts = content.split(';')
    else:
        parts = [content]
    
    env_vars = {}
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            # Safely evaluate the string as a python dictionary
            d = ast.literal_eval(part)
            if isinstance(d, dict) and 'name' in d and 'value' in d:
                env_vars[d['name']] = d['value']
        except Exception as e:
            print(f"Error parsing part: {part[:20]}... {e}")
            continue
            
    return env_vars

def main():
    env_vars = parse_env_vars('env_vars.txt')
    if not env_vars:
        print("No environment variables found.")
        return

    # Construct --set-env-vars string with escaped commas
    # gcloud requires commas in values to be escaped with backslash
    pairs = []
    for k, v in env_vars.items():
        # Escape commas in the value
        escaped_v = str(v).replace(',', r'\,')
        # Also escape equals if needed? Docs say format is KEY=VALUE. 
        # Usually equals in value is fine, but let's be safe on commas.
        pairs.append(f"{k}={escaped_v}")
        
    env_str = ",".join(pairs)
    
    # Command to update the job with env vars
    # Job configuration
    job_name = "migrate-db-roots-minimal"
    region = "europe-north1"
    image = "gcr.io/gen-lang-client-0549116861/roots-party" # Hardcoded from previous context
    
    # Filter only essential env vars for migration
    essential_keys = ['DATABASE_URL', 'SECRET_KEY']
    env_vars = {k: v for k, v in env_vars.items() if k in essential_keys}
    
    # Reconstruct --set-env-vars string with escaped commas
    pairs = []
    for k, v in env_vars.items():
        escaped_v = str(v).replace(',', r'\,')
        pairs.append(f"{k}={escaped_v}")
    env_str = ",".join(pairs)
    
    # 2. Create new job with env vars
    print(f"Creating job {job_name} with minimal env vars...")
    cmd_create = [
        "gcloud", "run", "jobs", "create", job_name,
        "--image", image,
        "--set-env-vars", f'"{env_str}"', # env_str will be recomputed below loop
        "--region", region,
        "--command", "python", # Keeping as one arg if possible or split? gcloud command flag usually takes a string
        "--args", "manage.py,migrate",
        "--quiet"
    ]
    create_cmd_str = " ".join(cmd_create)
    print("COMMAND TO RUN:")
    print(create_cmd_str)
    # subprocess.run(create_cmd_str, check=True, shell=True)
    
    # 3. Execute the job
    # print("Executing migration job...")
    # cmd_execute = f"gcloud run jobs execute {job_name} --region {region} --wait --quiet"
    # subprocess.run(cmd_execute, check=True, shell=True)

if __name__ == "__main__":
    main()
