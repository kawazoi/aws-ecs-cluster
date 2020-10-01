from dotenv import load_dotenv
from os import getenv

from aws_cdk import core

from nlp_infra.nlp_infra_stg import NlpInfraStaging
from nlp_infra.nlp_infra_prod import NlpInfraProduction


load_dotenv()
_env = core.Environment(account=getenv('AWS_ACCOUNT_ID'), region=getenv('AWS_DEFAULT_REGION'))
app = core.App()

stg = NlpInfraStaging(app, "nlp-infra-staging", env=_env)
core.Tag.add(stg, "Project", "NlpServing")
core.Tag.add(stg, "Environment", "Staging")

prd = NlpInfraProduction(app, "nlp-infra-production", env=_env)
core.Tag.add(prd, "Project", "NlpServing")
core.Tag.add(prd, "Environment", "Production")

app.synth()
