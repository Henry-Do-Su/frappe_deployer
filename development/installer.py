#!/usr/bin/env python3
import argparse
import os
import subprocess
import json
import sys

RED_COLOR = "\033[31m"
GREEN_COLOR = "\33[92m"
YELLOW_COLOR = "\33[93m"
COLOR_RESET = "\033[0m"

def cprint(*args, level: int = 1):
    message = " ".join(map(str, args))
    color = COLOR_RESET
    if level == 1: color = RED_COLOR
    elif level == 2: color = GREEN_COLOR
    elif level == 3: color = YELLOW_COLOR
    print(color, message, COLOR_RESET, file=sys.stderr if level == 1 else sys.stdout)

def run_command(command, cwd=None, env=None, check=True):
    print(f"{YELLOW_COLOR}Running: {' '.join(command)}{COLOR_RESET} {f'(in {cwd})' if cwd else ''}")
    try:
        process = subprocess.run(command, cwd=cwd, env=env, check=check, capture_output=True, text=True)
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)
        return process
    except subprocess.CalledProcessError as e:
        cprint(f"Error running command: {' '.join(command)}", level=1)
        cprint(f"Return Code: {e.returncode}", level=1)
        if e.stdout:
            cprint("--- STDOUT ---", level=1)
            cprint(e.stdout, level=1)
        if e.stderr:
            cprint("--- STDERR ---", level=1)
            cprint(e.stderr, level=1)
        raise

def main():
    parser = get_args_parser()
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    bench_path = os.path.join(workspace_root, args.bench_name)

    env = os.environ.copy()

    init_bench_if_not_exist(args, bench_path, env)
    create_site_if_not_exist(args, bench_path, env)
    install_apps(args, bench_path, env)
    configure_bench(args, bench_path, env)

def get_args_parser():
    parser = argparse.ArgumentParser(description="Frappe Bench Setup Script for Dev Containers")
    parser.add_argument("-j", "--apps-json", type=str, default="apps.json", help="Path to apps.json (relative to script dir)")
    parser.add_argument("-b", "--bench-name", type=str, default="frappe-bench", help="Bench directory name (created in repo root)")
    parser.add_argument("-s", "--site-name", type=str, default="development.localhost", help="Site name")
    parser.add_argument("-r", "--frappe-repo", type=str, default="https://github.com/frappe/frappe", help="Frappe repo URL")
    parser.add_argument("-t", "--frappe-branch", type=str, default="version-15", help="Frappe repo branch")
    parser.add_argument("-a", "--admin-password", type=str, default="admin", help="Admin password for site")
    parser.add_argument("-d", "--db-type", type=str, default="mariadb", choices=["mariadb", "postgres"], help="Database type")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output (bench commands already show output)")
    parser.add_argument("--force-site-creation", action="store_true", help="Force site creation even if it exists")
    return parser

def set_config(bench_path, key, value):
    run_command(["bench", "set-config", "-g", key, value], cwd=bench_path)

def init_bench_if_not_exist(args, bench_path, env):
    if os.path.exists(bench_path):
        cprint(f"Bench directory '{bench_path}' already exists. Skipping init.", level=3)
        return

    cprint(f"Initializing Frappe bench in '{bench_path}'...", level=2)
    init_command = [
        "bench", "init",
        "--skip-redis-config-generation",
        f"--frappe-path={args.frappe_repo}",
        f"--frappe-branch={args.frappe_branch}",
        bench_path
    ]

    run_command(init_command, cwd=os.path.dirname(bench_path), env=env)
    cprint("Bench initialized.", level=2)

def configure_bench(args, bench_path, env):
    cprint("Configuring Bench...", level=2)
    set_config(bench_path, "developer_mode", "1")
    cprint("Set developer_mode=1", level=3)

    if args.db_type == "mariadb":
        db_host = "mariadb"
    elif args.db_type == "postgres":
        db_host = "postgresql"
    else:
        cprint(f"Unsupported db_type: {args.db_type}", level=1)
        sys.exit(1)

    set_config(bench_path, "db_host", db_host)
    cprint(f"Set db_host to {db_host}", level=3)
    set_config(bench_path, "redis_cache", "redis://redis-cache:6379")
    cprint("Set redis_cache to redis://redis-cache:6379", level=3)
    set_config(bench_path, "redis_queue", "redis://redis-queue:6379")
    cprint("Set redis_queue to redis://redis-queue:6379", level=3)
    set_config(bench_path, "redis_socketio", "redis://redis-queue:6379")
    cprint("Set redis_socketio to redis://redis-queue:6379", level=3)

def site_exists(bench_path, site_name):
    """Checks if a site exists in the bench."""
    sites_dir = os.path.join(bench_path, "sites")
    return os.path.exists(os.path.join(sites_dir, site_name))

def create_site_if_not_exist(args, bench_path, env):
    """Creates a new site if it doesn't already exist."""
    if site_exists(bench_path, args.site_name) and not args.force_site_creation:
        cprint(f"Site '{args.site_name}' already exists. Skipping creation.", level=3)
        cprint("Use --force-site-creation flag in installer.py if you want to recreate it (data will be lost!).", level=3)
        run_command(["bench", "use", args.site_name], cwd=bench_path)
        run_command(["bench", "set-config", "db_host", os.environ.get('DB_HOST', 'mariadb' if args.db_type == 'mariadb' else 'postgresql')], cwd=bench_path)
        run_command(["bench", "set-config", "developer_mode", "1"], cwd=bench_path) # Ensure dev mode is on
        return

    if args.force_site_creation and site_exists(bench_path, args.site_name):
         cprint(f"Recreating site '{args.site_name}' due to --force-site-creation flag...", level=3)
         run_command(["bench", "drop-site", args.site_name, "--force"], cwd=bench_path)

    cprint(f"Creating Site {args.site_name}...", level=2)
    db_host = "mariadb" if args.db_type == "mariadb" else "postgresql"
    db_root_password = "superpassword"

    new_site_cmd = [
        "bench", "new-site", args.site_name,
        f"--db-type={args.db_type}",
        f"--db-host={db_host}",
        f"--db-root-password={db_root_password}",
        f"--admin-password={args.admin_password}",
        "--install-app", "frappe",
        "--set-default"
    ]


    run_command(new_site_cmd, cwd=bench_path, env=env)
    cprint(f"Site {args.site_name} created successfully.", level=2)


def install_apps(args, bench_path, env):
    """Installs apps listed in apps.json onto the site."""
    apps_json_path = os.path.join(os.path.dirname(__file__), args.apps_json)
    if not os.path.exists(apps_json_path):
        cprint(f"apps.json not found at {apps_json_path}. Skipping app installation.", level=3)
        return

    cprint(f"Processing apps from {args.apps_json}...", level=2)
    try:
        with open(apps_json_path, 'r') as f:
            apps_to_install = json.load(f)
    except json.JSONDecodeError:
        cprint(f"Error reading or parsing {apps_json_path}", level=1)
        return
    except FileNotFoundError:
        cprint(f"Could not find {apps_json_path}", level=1)
        return

    if not apps_to_install:
         cprint("No apps listed in apps.json to install.", level=3)
         return

    # Ensure the correct site context is set
    run_command(["bench", "use", args.site_name], cwd=bench_path)

    for app_info in apps_to_install:
        app_name = app_info['url'].split('/')[-1].replace('.git', '')
        app_url = app_info['url']
        app_branch = app_info.get('branch')

        cprint(f"Getting app '{app_name}' from {app_url}" + (f" (branch: {app_branch})" if app_branch else ""), level=2)
        get_app_cmd = ["bench", "get-app", app_url]
        if app_branch:
            get_app_cmd.extend(["--branch", app_branch])

        try:
            run_command(get_app_cmd, cwd=bench_path, env=env)
            cprint(f"Installing app '{app_name}' on site '{args.site_name}'...", level=2)
            # Check if app is already installed before trying to install
            installed_apps_process = run_command(["bench", "list-apps"], cwd=bench_path, check=False)
            if app_name not in installed_apps_process.stdout.splitlines():
                 run_command(["bench", "install-app", app_name], cwd=bench_path, env=env)
                 cprint(f"App '{app_name}' installed successfully.", level=2)
            else:
                 cprint(f"App '{app_name}' already installed on site. Skipping install command.", level=3)
        except subprocess.CalledProcessError:
            cprint(f"Failed to get or install app '{app_name}'. Please check logs.", level=1)



if __name__ == "__main__":
    try:
        main()
        cprint("\nDevelopment environment setup complete!", level=2)
        cprint(f"Run 'bench start' or 'bench watch' in '{os.path.join(os.path.dirname(__file__), '../frappe-bench')}' to start the server.", level=2) # Adjust path if bench name changes
        cprint(f"Access the site at http://{os.environ.get('CODESPACE_NAME', 'localhost')}:{os.environ.get('FRONTEND_PORT', '8000')}", level=2) # Use env vars for dynamic URLs if in Codespaces/Gitpod
    except Exception as e:
        cprint(f"\nSetup failed: {e}", level=1)
        sys.exit(1)