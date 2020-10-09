"""
Creates all resources necessary for the initial setup of a AWS ECS service with ALB.
After the initial setup, the service should only be updated by the ci/cd pipeline of the service.
"""

from aws_cdk import (
    aws_ec2,
    aws_ecs,
    aws_ecs_patterns,
    aws_servicediscovery,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam,
    aws_sqs,
    aws_ecr,
    core,
)


class ServiceStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, stage: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.base_platform = BasePlatform(self, self.stack_name, stage)

        self.ecr_repo = aws_ecr.Repository(
            self,
            "{}-ecr".format(self.stack_name),
            repository_name=config.ecr["REPO"],
            image_scan_on_push=True,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        # Create Task Definition
        task_definition = aws_ecs.Ec2TaskDefinition(self, "TaskDef")
        container = task_definition.add_container(
            self.stack_name,
            image=aws_ecs.ContainerImage.from_ecr_repository(
                self.ecr_repo, tag=config.ecr["REPO_TAG"]
            ),
            memory_limit_mib=256,
        )
        port_mapping = aws_ecs.PortMapping(
            container_port=80, host_port=8080, protocol=aws_ecs.Protocol.TCP
        )
        container.add_port_mappings(port_mapping)

        # Create Service
        service = aws_ecs.Ec2Service(
            self,
            "Service",
            cluster=self.base_platform.ecs_cluster,
            task_definition=task_definition,
        )

        # Create ALB
        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LB",
            vpc=self.base_platform.vpc,
            internet_facing=True,
            vpc_subnets=aws_ec2.SubnetSelection(
                one_per_az=True,
                subnets=self.base_platform.vpc.private_subnets
                + self.base_platform.vpc.public_subnets,
            ),
        )
        listener = lb.add_listener("PublicListener", port=80, open=True)

        health_check = elbv2.HealthCheck(
            interval=core.Duration.seconds(60),
            path="/healthcheck",
            timeout=core.Duration.seconds(5),
        )

        # Attach ALB to ECS Service
        listener.add_targets(
            "ECS",
            port=80,
            targets=[service],
            health_check=health_check,
        )

        core.CfnOutput(self, "LoadBalancerDNS", value=lb.load_balancer_dns_name)
