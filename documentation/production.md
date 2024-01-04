# Creating a Production Environment

The following has been developed on a Linux distro such as Ubuntu (Recommended). Guides on deploying to ECS, Kubernetes and other AWS services will be added in the future.

This docker compose file is for deploying a production environment for a single bench instance, with SSL certificates and a reverse proxy. 

## Prerequisites
- DNS record for your domain pointing to your server's Public IP address.

- All .env variables must be set. See the .env.example file for more information.

- Ports 80 and 443 must be open on your server. This will allow your server to receive a certificate from LetsEncrypt and allow traffic to your bench instance on HTTPS for security.

- Docker and Docker Compose must be installed on your server. See the [Docker documentation](https://docs.docker.com/engine/install/) for more information.

## Deploying

1. Pull the repo to your local machine: `git clone https://github.com/Henry-Do-Su/frappe_deployer.git`
2. `cd production`
3. Edit the .env file to include your domain name, email address and other variables. View the .env.example file for more information.
4. Create the network: `docker network create traefik-public`
5. You need to manually include the apps you want to install in your production environment. You will see it on line 90 of the production.yml file.
These will be the apps that you included in apps.json if you built a custom image.

![img_2.png](img_2.png)

