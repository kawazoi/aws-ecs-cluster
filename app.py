from dotenv import load_dotenv
from os import getenv

from aws_cdk import core

from nlp_infra.ecs_cluster import EcsCluster


load_dotenv()
_env = core.Environment(
    account=getenv("AWS_ACCOUNT_ID"), region=getenv("AWS_DEFAULT_REGION")
)
app = core.App()

ENV = "Staging"
config_stg = {}
stg = EcsCluster(app, f"nlp-infra-{ENV.lower()}", ENV, config_stg, env=_env)
core.Tag.add(stg, "Project", "NlpServing")
core.Tag.add(stg, "Environment", ENV)


ENV = "Production"
config_prod = {}
prd = EcsCluster(app, f"nlp-infra-{ENV.lower()}", ENV, config_stg, env=_env)
core.Tag.add(prd, "Project", "NlpServing")
core.Tag.add(prd, "Environment", ENV)

app.synth()
