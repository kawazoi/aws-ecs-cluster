from aws_cdk import core

from nlp_ecs_infra.ecs_cluster_stg import ECSClusterStg
from nlp_ecs_infra.ecs_cluster_prod import ECSClusterProd


app = core.App()

ecs_cluster_stg_stack = ECSClusterStg(app, "nlp-ecs-cluster-stg")
core.Tag.add(ecs_cluster_stg_stack, "Project", "NlpServing")
core.Tag.add(ecs_cluster_stg_stack, "Environment", "Staging")

ecs_cluster_prod_stack = ECSClusterProd(app, "nlp-ecs-cluster-prod")
core.Tag.add(ecs_cluster_prod_stack, "Project", "NlpServing")
core.Tag.add(ecs_cluster_prod_stack, "Environment", "Production")

app.synth()
