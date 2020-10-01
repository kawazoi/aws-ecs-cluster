from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    core,
)


class ECSClusterProd(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        vpc = ec2.Vpc(self, "Production", max_azs=1)

        asg = autoscaling.AutoScalingGroup(
            self,
            "NlpFleetProd",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ecs.EcsOptimizedAmi(),
            associate_public_ip_address=True,
            update_type=autoscaling.UpdateType.REPLACING_UPDATE,
            desired_capacity=2,
            vpc=vpc,
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
        )

        cluster = ecs.Cluster(self, "NlpClusterProd", vpc=vpc)

        cluster.add_auto_scaling_group(asg)
