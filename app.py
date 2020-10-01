from aws_cdk import core

from nlp_infra.nlp_infra_stg import NlpInfraStaging
from nlp_infra.nlp_infra_prod import NlpInfraProduction


app = core.App()

stg = NlpInfraStaging(app, "nlp-infra-staging")
core.Tag.add(stg, "Project", "NlpServing")
core.Tag.add(stg, "Environment", "Staging")

prd = NlpInfraProduction(app, "nlp-infra-production")
core.Tag.add(prd, "Project", "NlpServing")
core.Tag.add(prd, "Environment", "Production")

app.synth()
