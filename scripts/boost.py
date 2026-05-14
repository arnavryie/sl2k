import subprocess
import os
import sys

def run_command(cmd, env=None):
    # Merge current env with provided env
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=full_env)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(result.stderr)
        return False
    return True

def main():
    count = 100
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass

    override_date = os.environ.get("OVERRIDE_DATE")
    print(f"Starting boost: {count} contributions (Date: {override_date if override_date else 'Current'})...")

    for i in range(1, count + 1):
        # Run generate.py with --force
        if not run_command("py scripts/generate.py --force"):
            print("Failed at generation step.")
            break
        
        # Git add
        if not run_command("git add ."):
            print("Failed at git add.")
            break
            
        msg = f"chore: contribution boost {i}/{count}"
        
        # Git commit with date if overridden
        commit_cmd = f'git commit -m "{msg}"'
        if override_date:
            # Note: We use the same date but slightly different times could be better, 
            # but for 100 commits one day is fine.
            commit_cmd += f' --date="{override_date}T12:00:00"'
        
        if not run_command(commit_cmd):
            print("Failed at git commit.")
            break
            
        if i % 10 == 0:
            print(f"Progress: {i}/{count} commits done.")

    print("Finished generating commits.")

if __name__ == "__main__":
    main()
