import logging

from aws_cdk import (
    aws_ec2,
    aws_ecs,
    core,
)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class EcsCluster(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, stage: str, config: dict, **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        MSG = "- Environment: {}\n- Config: {}".format(stage, config)
        logging.info(MSG)

        self.vpc = aws_ec2.Vpc.from_lookup(
            self, "VPC{}".format(stage), vpc_name=stage.lower()
        )

        # Creating ECS Cluster in the VPC created above
        self.ecs_cluster = aws_ecs.Cluster(
            self,
            "ECSCluster{}".format(stage),
            vpc=self.vpc,
            cluster_name="ECSCluster{}".format(stage),
        )

        # Adding service discovery namespace to cluster
        self.ecs_cluster.add_default_cloud_map_namespace(
            name="service{}".format(stage),
        )

        ###### CAPACITY PROVIDERS SECTION #####
        # Adding EC2 capacity to the ECS Cluster
        self.asg = self.ecs_cluster.add_capacity(
            "ECSEC2Capacity",
            instance_type=aws_ec2.InstanceType(instance_type_identifier="t3.small"),
            min_capacity=1,
            max_capacity=10,
        )

        core.CfnOutput(
            self,
            "EC2AutoScalingGroupName{}".format(stage),
            value=self.asg.auto_scaling_group_name,
            export_name="EC2ASGName{}".format(stage),
        )

        # Namespace details as CFN output
        self.namespace_outputs = {
            "ARN": self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_arn,
            "NAME": self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_name,
            "ID": self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_id,
        }

        # Cluster Attributes
        self.cluster_outputs = {
            "NAME": self.ecs_cluster.cluster_name,
            "SECGRPS": str(self.ecs_cluster.connections.security_groups),
        }

        # When enabling EC2, we need the security groups "registered" to the cluster for imports in other service stacks
        if self.ecs_cluster.connections.security_groups:
            self.cluster_outputs["SECGRPS"] = str(
                [
                    x.security_group_id
                    for x in self.ecs_cluster.connections.security_groups
                ][0]
            )

        # All Outputs required for other stacks to build
        core.CfnOutput(
            self,
            "NSArn{}".format(stage),
            value=self.namespace_outputs["ARN"],
            export_name="NSARN{}".format(stage),
        )
        core.CfnOutput(
            self,
            "NSName{}".format(stage),
            value=self.namespace_outputs["NAME"],
            export_name="NSNAME{}".format(stage),
        )
        core.CfnOutput(
            self,
            "NSId{}".format(stage),
            value=self.namespace_outputs["ID"],
            export_name="NSID{}".format(stage),
        )
        core.CfnOutput(
            self,
            "ECSClusterName{}".format(stage),
            value=self.cluster_outputs["NAME"],
            export_name="ECSClusterName{}".format(stage),
        )
        core.CfnOutput(
            self,
            "ECSClusterSecGrp{}".format(stage),
            value=self.cluster_outputs["SECGRPS"],
            export_name="ECSSecGrpList{}".format(stage),
        )
