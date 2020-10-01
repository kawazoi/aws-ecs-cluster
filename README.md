![](https://github.com/kawazoi/aws-ecs-cluster/workflows/DeployStaging/badge.svg?branch=staging&event=push) ![](https://github.com/kawazoi/aws-ecs-cluster/workflows/DeployProduction/badge.svg?branch=master&event=push)

# ECS Cluster

This repository is the first one in our [series](../README.md).

Attention: Remember to clear all resources to avoid unnecessary costs.


## Requirements

- Python 3,7
- virtualenv
- AWS CDK
- Github Actions


## Initial deploy

1. Create virtualenv `venv`
2. Create and edit `.env` file
3. Deploy stack staging
    - Deploy using cdk
    - "Manually" enable [EC2 capacity](https://ecsworkshop.com/capacity_providers/ec2/) on the cluster
4. Deploy stack production
    - Deploy using cdk
    - "Manually" enable [EC2 capacity](https://ecsworkshop.com/capacity_providers/ec2/) on the cluster

- How to Enable Capacity Provider

    - Create a capacity provider:

        ```bash
        export ENV=Staging
        export AWS_REGION=us-west-2
        # Get the required cluster values needed when creating the capacity provider
        export asg_name=$(aws cloudformation describe-stacks --stack-name nlp-infra-${ENV} | jq -r '.Stacks[].Outputs[] | select(.ExportName != null) | select(.ExportName | contains("EC2ASGName"))| .OutputValue')
        export asg_arn=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names $asg_name | jq .AutoScalingGroups[].AutoScalingGroupARN)
        export capacity_provider_name=$(echo "EC2$(date +'%s')")
        # Creating capacity provider
        aws ecs create-capacity-provider \
            --name $capacity_provider_name \
            --auto-scaling-group-provider autoScalingGroupArn="$asg_arn",managedScaling=\{status="ENABLED",targetCapacity=80\},managedTerminationProtection="DISABLED" \
            --region $AWS_REGION
        ```

    - Associate it with the ECS Cluster:

        ```bash
        aws ecs put-cluster-capacity-providers \
            --cluster container-demo \
            --capacity-providers $capacity_provider_name \
            --default-capacity-provider-strategy capacityProvider=$capacity_provider_name,weight=1,base=1
        ```


## CI / CD Flow

1. Create and push `new_branch`: `Lint` and `CDK Diff Staging and Production`

2. Pull request to `staging` and `master`: `Lint` and `CDK Diff Staging and Production`

3. Push to `staging`: `DeployStaging`

4. Push to `master`: `DeployProduction`


## Deploy Stack locally

1. Follow the steps below

# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```bash
python3 -m venv venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
source venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```bash
cdk synth
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
