import logging

from aws_cdk import (
    aws_ec2,
    aws_ecs,
    core,
    aws_iam,
)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class EcsCluster(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, environment: str, config: dict, **kwargs
    ):
        super().__init__(scope, id, **kwargs)
        MSG = "- Environment: {}\n- Config: {}".format(environment, config)
        logging.info(MSG)

        self.vpc = aws_ec2.Vpc.from_lookup(
            self, "VPC{}".format(environment), vpc_name=environment.lower()
        )

        # Creating ECS Cluster in the VPC created above
        self.ecs_cluster = aws_ecs.Cluster(
            self,
            "ECSCluster{}".format(environment),
            vpc=self.vpc,
            cluster_name="ECSCluster{}".format(environment),
        )

        # Adding service discovery namespace to cluster
        self.ecs_cluster.add_default_cloud_map_namespace(
            name="service{}".format(environment),
        )

        ###### CAPACITY PROVIDERS SECTION #####
        # Adding EC2 capacity to the ECS Cluster
        self.asg = self.ecs_cluster.add_capacity(
            "ECSEC2Capacity",
            instance_type=aws_ec2.InstanceType(instance_type_identifier="t3.small"),
            min_capacity=0,
            max_capacity=10,
        )

        core.CfnOutput(
            self,
            "EC2AutoScalingGroupName{}".format(environment),
            value=self.asg.auto_scaling_group_name,
            export_name="EC2ASGName{}".format(environment),
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
            "NSArn{}".format(environment),
            value=self.namespace_outputs["ARN"],
            export_name="NSARN{}".format(environment),
        )
        core.CfnOutput(
            self,
            "NSName{}".format(environment),
            value=self.namespace_outputs["NAME"],
            export_name="NSNAME{}".format(environment),
        )
        core.CfnOutput(
            self,
            "NSId{}".format(environment),
            value=self.namespace_outputs["ID"],
            export_name="NSID{}".format(environment),
        )
        core.CfnOutput(
            self,
            "ECSClusterName{}".format(environment),
            value=self.cluster_outputs["NAME"],
            export_name="ECSClusterName{}".format(environment),
        )
        core.CfnOutput(
            self,
            "ECSClusterSecGrp{}".format(environment),
            value=self.cluster_outputs["SECGRPS"],
            export_name="ECSSecGrpList{}".format(environment),
        )
        # core.CfnOutput(self, "FE2BESecGrp", value=self.services_3000_sec_group.security_group_id, export_name="SecGrpId")
        # core.CfnOutput(self, "ServicesSecGrp", value=self.services_3000_sec_group.security_group_id, export_name="ServicesSecGrp")
        # core.CfnOutput(self, "StressToolEc2Id",value=self.instance.instance_id)
        # core.CfnOutput(self, "StressToolEc2Ip",value=self.instance.instance_private_ip)
