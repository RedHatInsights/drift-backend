# Deploying to Openshift

Deploying to Openshift uses Ansible to generate and modify Openshift resources.

## Requirements

 * Openshift python package
 * Ansible

To install:

    pip install -r requirements.txt

## Deployment

To deploy to Openshift, run the following playbook:

    ansible-playbook deploy.yml --ask-vault-pass
