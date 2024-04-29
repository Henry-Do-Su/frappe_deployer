# Build your custom Frappe Image

Building a custom image, allows you to include all the apps you wish to pre-install in your Frappe environment.
This image will be used in the main docker-compose file, located in the Production directory, named `production.yml` 

## Prerequisites
A location to store your custom image. This can be a private or public repository.
You can host your images on Docker Hub, GitHub Container Registry, or any other container registry.

 For this example, we will be using a private repository, and storing the image on GitHub Container Registry.
 
## Steps
1. Pull the repo to your local machine: `git clone https://github.com/Henry-Do-Su/frappe_deployer`

2. Navigate to the `production` directory: `cd production`

3. Edit the `apps.json` file to include the apps you want to pre-install in your custom image.

4. Encode the apps.json file to base64. On Linux, use `export APPS_JSON_BASE64=$(base64 -w 0 apps.json)`

5. Edit the Containerfile if you wish to change python, node, or frappe versions. Leave as default if you wish to use the latest versions.

6. If your repository is private, you will need to create a PAT key. Follow this guide: https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token

7. Run the following command to build your image, remember to use your PAT key if your repository is private (This applies to Docker Hub and any other container registry): 

Make sure to replace the tag value with your own tag value. For example: `--tag=ghcr.io/<GITHUBUSERNAME>/<IMAGENAME>:<TAGVALUE>`

```
   docker build \
    --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
    --build-arg=FRAPPE_BRANCH=version-15 \
    --build-arg=PYTHON_VERSION=3.11.4 \
    --build-arg=NODE_VERSION=18.17.1 \
    --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
    --tag=ghcr.io/henry-do-su/frappedemo:1.0.0 \
    --file=Containerfile .
```
8. Wait for the image to build. Once complete, you can push the image to your repository. 

For example: `docker push ghcr.io/Henry-Do-Su/frappedemo:1.0.0`

9. Once the image is pushed, you can use it in the production.yml file.

To view the production setup guide, click [here](../documentation/production.md)
