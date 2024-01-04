#!/usr/bin/env python3
import argparse
import os
import subprocess


RED_COLOR = "\033[31m"
GREEN_COLOR = "\33[92m"
YELLOW_COLOR = "\33[93m"
COLOR_RESET = "\033[0m"


def cprint(*args, level: int = 1):
    """
    Prints the given arguments with color formatting based on the specified level.

    :param args: Variable number of arguments to be printed.
    :param level: Integer representing the color level. Defaults to 1.
    :return: None
    """
    message = " ".join(map(str, args))
    if level == 1:
        print(RED_COLOR, message, COLOR_RESET)
    if level == 2:
        print(GREEN_COLOR, message, COLOR_RESET)
    if level == 3:
        print(YELLOW_COLOR, message, COLOR_RESET)


def main():
    """
    Main method for the application.

    This method performs the following steps:
    1. Parse command line arguments using `get_args_parser`.
    2. Initialize the bench if it doesn't already exist, using `init_bench_if_not_exist`.
    3. Create a site in the bench, using `create_site_in_bench`.

    :return: None
    """
    parser = get_args_parser()
    args = parser.parse_args()
    init_bench_if_not_exist(args)
    create_site_in_bench(args)


def get_args_parser():
    """
    :return: An ArgumentParser object with the following command line arguments:
        - "-j", "--apps-json": Path to apps.json, default: "apps-example.json"
        - "-b", "--bench-name": Bench directory name, default: "frappe-bench"
        - "-s", "--site-name": Site name, should end with .localhost, default: "development.localhost"
        - "-r", "--frappe-repo": Frappe repo to use, default: "https://github.com/frappe/frappe"
        - "-t", "--frappe-branch": Frappe repo branch to use, default: "version-15"
        - "-p", "--py-version": Python version, default: "Not Set"
        - "-n", "--node-version": Node version, default: "Not Set"
        - "-v", "--verbose": Enable verbose output
        - "-a", "--admin-password": Admin password for site, default: "admin"
        - "-d", "--db-type": Database type to use (e.g., mariadb or postgres), default: "mariadb"
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-j",
        "--apps-json",
        action="store",
        type=str,
        help="Path to apps.json, default: apps.json",
        default="apps.json",
    )  # noqa: E501
    parser.add_argument(
        "-b",
        "--bench-name",
        action="store",
        type=str,
        help="Bench directory name, default: frappe-bench",
        default="frappe-bench",
    )  # noqa: E501
    parser.add_argument(
        "-s",
        "--site-name",
        action="store",
        type=str,
        help="Site name, should end with .localhost, default: development.localhost",
        default="development.localhost",
    )
    parser.add_argument(
        "-r",
        "--frappe-repo",
        action="store",
        type=str,
        help="frappe repo to use, default: https://github.com/frappe/frappe",
        default="https://github.com/frappe/frappe",
    )
    parser.add_argument(
        "-t",
        "--frappe-branch",
        action="store",
        type=str,
        help="frappe repo to use, default: version-15",
        default="version-15",
    )
    parser.add_argument(
        "-p",
        "--py-version",
        action="store",
        type=str,
        help="python version, default: Not Set",
        default=3.11,
    )
    parser.add_argument(
        "-n",
        "--node-version",
        action="store",
        type=str,
        help="node version, default: Not Set",
        default=18.18,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose output",
    )
    parser.add_argument(
        "-a",
        "--admin-password",
        action="store",
        type=str,
        help="admin password for site, default: admin",
        default="admin",
    )
    parser.add_argument(
        "-d",
        "--db-type",
        action="store",
        type=str,
        help="Database type to use (e.g., mariadb or postgres)",
        default="mariadb",
    )
    return parser

def set_config(cwd, key, value):
    """
    Set a configuration value for a specific key.

    :param cwd: The current working directory where the command will be executed.
    :type cwd: str
    :param key: The configuration key to set.
    :type key: str
    :param value: The value to set for the configuration key.
    :type value: str
    :return: None
    """
    subprocess.call(
        ["bench", "set-config", "-g", key, value],
        cwd=cwd,
    )

def init_bench_if_not_exist(args):
    """
    :param args: Command line arguments passed to the method
    :return: None

    This method initializes a bench if it does not already exist. The method performs the following steps:

    1. Checks if the bench directory already exists. If it does, the method prints a message indicating that the bench already exists and returns without performing any further actions.

    2. If the bench directory does not exist, the method proceeds to initialize the bench by executing the necessary command-line commands.

    3. Copies the current environment and sets the "PYENV_VERSION" environment variable if the "py_version" argument is provided.

    4. Constructs the initialization command for the bench based on the provided arguments. The command includes options such as skipping redis configuration generation and verbose mode
    *. The frappe repository path, branch, and apps path are also included in the command.

    5. Executes the initialization command using the subprocess module. The command is executed in a new shell process with the necessary environment variables and current working directory
    *.

    6. Prints a message indicating that the bench is being configured.

    7. Sets the "db_type" configuration option to the provided value if the "db_type" argument is provided.

    8. Sets other configuration options related to redis cache, queue, and socketio if the "db_type" argument is provided.

    9. Sets the "developer_mode" configuration option to "1" regardless of the "db_type" argument.

    10. Handles any subprocess errors that occur during the execution of the initialization command. Prints the error output if available.

    Note: The method assumes that the necessary modules such as "os", "subprocess", and "cprint" are already imported.

    """
    if os.path.exists(args.bench_name):
        cprint("Bench already exists. Only site will be created", level=3)
        return
    try:
        env = os.environ.copy()
        if args.py_version:
            env["PYENV_VERSION"] = args.py_version
        init_command = ""
        if args.node_version:
            init_command = f"nvm use {args.node_version};"
        if args.py_version:
            init_command += f"PYENV_VERSION={args.py_version} "
        init_command += "bench init "
        init_command += "--skip-redis-config-generation "
        init_command += "--verbose " if args.verbose else " "
        init_command += f"--frappe-path={args.frappe_repo} "
        init_command += f"--frappe-branch={args.frappe_branch} "
        init_command += f"--apps_path={args.apps_json} "
        init_command += args.bench_name
        command = [
            "/bin/bash",
            "-i",
            "-c",
            init_command,
        ]
        subprocess.call(command, env=env, cwd=os.getcwd())

        cprint("Configuring Bench ...", level=2)

        cwd = os.getcwd() + "/" + args.bench_name

        if args.db_type:
            cprint(f"Setting db_type to {args.db_type}", level=3)
            set_config(cwd, "db_type", args.db_type)
            cprint("Set redis_cache to redis://redis-cache:6379", level=3)
            set_config(cwd, "redis_cache", "redis://redis-cache:6379")
            cprint("Set redis_queue to redis://redis-queue:6379", level=3)
            set_config(cwd, "redis_queue", "redis://redis-queue:6379")
            cprint("Set redis_socketio to redis://redis-queue:6379 for backward compatibility", level=3)
            set_config(cwd, "redis_socketio", "redis://redis-queue:6379")
            cprint("Set developer_mode", level=3)
            set_config(cwd, "developer_mode", "1")
    except subprocess.CalledProcessError as e:
        cprint(e.output, level=1)


def create_site_in_bench(args):
    """
    Create a new site in the bench.

    :param args: An object containing the arguments needed for site creation.
    :return: None.
    """
    if "mariadb" == args.db_type:
        cprint("Set db_host", level=3)
        subprocess.call(
            ["bench", "set-config", "-g", "db_host", "mariadb"],
            cwd=os.getcwd() + "/" + args.bench_name,
        )
        new_site_cmd = [
            "bench",
            "new-site",
            f"--db-host=mariadb",
            f"--db-type={args.db_type}",
            f"--no-mariadb-socket",
            f"--db-root-password=123",
            f"--admin-password={args.admin_password}",
        ]
    else:
        cprint("Set db_host", level=3)
        subprocess.call(
            ["bench", "set-config", "-g", "db_host", "postgresql"],
            cwd=os.getcwd() + "/" + args.bench_name,
        )
        new_site_cmd = [
            "bench",
            "new-site",
            f"--db-host=postgresql",
            f"--db-type={args.db_type}",
            f"--db-root-password=123",
            f"--admin-password={args.admin_password}",
        ]
    apps = os.listdir(f"{os.getcwd()}/{args.bench_name}/apps")
    apps.remove("frappe")
    for app in apps:
        new_site_cmd.append(f"--install-app={app}")
    new_site_cmd.append(args.site_name)
    cprint(f"Creating Site {args.site_name} ...", level=2)
    subprocess.call(
        new_site_cmd,
        cwd=os.getcwd() + "/" + args.bench_name,
    )


if __name__ == "__main__":
    main()