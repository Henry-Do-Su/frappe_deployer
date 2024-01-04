# Key Features

1. **Frappe-Focused Development Environment:** Designed specifically for Frappe development, this repository offers a pre-configured environment to work on Frappe and its custom applications. Ideal for developers aiming to build, test, and refine Frappe-based projects on their local machines.

2. **Production-Ready with SSL Encryption:** Includes configurations for deploying Frappe applications in a production environment, complete with SSL encryption for secure HTTP communication.

3. **IDE Compatibility:** Supports `devcontainer` configurations for both Visual Studio Code and JetBrains, allowing Frappe developers to work in their preferred coding environment.

4. **Ease of Setup and Use:** Aimed at enhancing developer productivity, the repository includes detailed instructions and annotated configuration files for easy setup and customization.

5. **Scalable and Customizable:** Whether building a simple Frappe application or a complex system with custom integrations, this repository scales to meet diverse project requirements and offers flexibility for development and production needs.

# Contents

### .devcontainer

- `devcontainer.json`: Configuration for VS Code development container. Sets up the development environment with port forwarding, user settings, and extensions.
- `docker-compose.yml`: Docker Compose configuration for the development environment, defining services, volumes, and network settings.
- `jetbrains/devcontainer.json`: JetBrains-specific configuration for development container, tailored for JetBrains IDEs.

### Development

- `.vscode/launch.json`: Configuration for launching and debugging applications within Visual Studio Code.
- `apps.json`: Lists the Frappe apps included in the development environment.
- `installer.py`: Python script for automating the setup of the development environment.

### Production

- `.env`: Environment variables for the production setup, containing key-value pairs for database credentials and other settings.
- `apps.json`: Lists the Frappe apps used in the production environment.
- `Containerfile`: Dockerfile for building the production container image.
- `nginx-entrypoint.sh`: Entry point script for Nginx service in the production environment.
- `nginx-template.conf`: Template configuration for Nginx, used for setting up the Nginx server.
- `production.yml`: Docker Compose file for orchestrating and managing production services.

## Documentation

For more detailed information, see the following guides:

- [Setting Up Development Environment](./documentation/development.md)
- [Building a custom Image](./documentation/image_build.md)
- [Setting Up Production Environment](./documentation/production.md)

## Acknowledgments

This project builds upon [Frappe Docker](https://github.com/frappe/frappe_docker/tree/main) by Frappe Technologies Pvt. Ltd., which is licensed under the MIT License. Special thanks to the contributors of Frappe Docker for their valuable work.
