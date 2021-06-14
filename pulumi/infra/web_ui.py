from infra.cache import Cache
from infra.config import configurable_envvars
from infra.fargate_service import GraplDockerBuild
from infra.metric_forwarder import MetricForwarder
from infra.network import Network
from infra.web_ui_fargate_service import WebUiFargateService


class WebUi(WebUiFargateService):
    def __init__(
        self,
        network: Network,
        cache: Cache,
        forwarder: MetricForwarder,
    ) -> None:

        super().__init__(
            "web-ui",
            image=GraplDockerBuild(
                dockerfile="../src/rust/Dockerfile",
                target="web-ui-deploy",  # check this
                context="../src",
            ),
            command="/web-ui",
            env={
                **configurable_envvars("web_ui", ["RUST_LOG", "RUST_BACKTRACE"]),
            },

            forwarder=forwarder,
            network=network,
        )
