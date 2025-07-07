# Gitea Workflow Configuration

This directory contains the Gitea Actions workflow for automated deployment to Portainer.

## Workflow: deploy.yml

The deployment workflow triggers on every push to the `main` branch and:

1. Checks out the code
2. Sets up Python environment
3. Deploys the stack to Portainer using the Portainer API

## Required Secrets

Configure these secrets in your Gitea repository settings:

- `PORTAINER_URL`: Your Portainer instance URL (e.g., `https://portainer.example.com`)
- `PORTAINER_TOKEN`: API token from Portainer (Settings → Users → Your User → Access Tokens)
- `PORTAINER_ENDPOINT_ID`: The endpoint ID where you want to deploy (usually `1` for local)

## Deployment Configuration

The workflow:
- Creates/updates a stack named `prd-maker`
- Uses the repository URL configured in the workflow
- Deploys using `docker-compose.yml` from the repository
- Supports both Git-based and file-based stack updates

## Local Development

To test the deployment locally:

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Portainer Stack URL

After deployment, the application will be available at:
- http://192.168.50.205:8501 (adjust based on your server configuration)