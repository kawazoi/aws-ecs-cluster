from aws_cdk import (
    aws_ec2,
    aws_ecs,
    core,
    aws_iam,
)


ENV = "Production"


class NlpInfraProduction(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        self.vpc = aws_ec2.Vpc(
            self,
            "Vpc{}".format(ENV),
            cidr="10.0.0.0/24",
        )

        # Creating ECS Cluster in the VPC created above
        self.ecs_cluster = aws_ecs.Cluster(
            self,
            "ECSCluster{}".format(ENV),
            vpc=self.vpc,
            cluster_name="ECSCluster{}".format(ENV),
        )

        # Adding service discovery namespace to cluster
        self.ecs_cluster.add_default_cloud_map_namespace(
            name="service{}".format(ENV),
        )

        ###### CAPACITY PROVIDERS SECTION #####
        # Adding EC2 capacity to the ECS Cluster
        # self.asg = self.ecs_cluster.add_capacity(
        #    "ECSEC2Capacity",
        #    instance_type=aws_ec2.InstanceType(instance_type_identifier='t3.small'),
        #    min_capacity=0,
        #    max_capacity=10
        # )

        # core.CfnOutput(self, "EC2AutoScalingGroupName", value=self.asg.auto_scaling_group_name, export_name="EC2ASGName")
        ##### END CAPACITY PROVIDER SECTION #####

        # asg = autoscaling.AutoScalingGroup(
        #     self,
        #     "NlpFleetStg",
        #     instance_type=ec2.InstanceType("t3.micro"),
        #     machine_image=ecs.EcsOptimizedAmi(),
        #     associate_public_ip_address=True,
        #     update_type=autoscaling.UpdateType.REPLACING_UPDATE,
        #     desired_capacity=1,
        #     vpc=vpc,
        #     vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
        # )
        # cluster.add_auto_scaling_group(asg)

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
        core.CfnOutput(self, "NSArn{}".format(ENV), value=self.namespace_outputs['ARN'], export_name="NSARN{}".format(ENV))
        core.CfnOutput(self, "NSName{}".format(ENV), value=self.namespace_outputs['NAME'], export_name="NSNAME{}".format(ENV))
        core.CfnOutput(self, "NSId{}".format(ENV), value=self.namespace_outputs['ID'], export_name="NSID{}".format(ENV))
        core.CfnOutput(self, "ECSClusterName{}".format(ENV), value=self.cluster_outputs['NAME'], export_name="ECSClusterName{}".format(ENV))
        core.CfnOutput(self, "ECSClusterSecGrp{}".format(ENV), value=self.cluster_outputs['SECGRPS'], export_name="ECSSecGrpList{}".format(ENV))
        # core.CfnOutput(self, "FE2BESecGrp", value=self.services_3000_sec_group.security_group_id, export_name="SecGrpId")
        # core.CfnOutput(self, "ServicesSecGrp", value=self.services_3000_sec_group.security_group_id, export_name="ServicesSecGrp")
        # core.CfnOutput(self, "StressToolEc2Id",value=self.instance.instance_id)
        # core.CfnOutput(self, "StressToolEc2Ip",value=self.instance.instance_private_ip)
