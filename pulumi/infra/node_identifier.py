from infra import dynamodb
from infra.cache import Cache
from infra.config import configurable_envvars
from infra.dynamodb import DynamoDB
from infra.emitter import EventEmitter
from infra.fargate_service import FargateService, GraplDockerBuild
from infra.metric_forwarder import MetricForwarder
from infra.network import Network


class NodeIdentifier(FargateService):
    def __init__(
        self,
        input_emitter: EventEmitter,
        output_emitter: EventEmitter,
        db: DynamoDB,
        network: Network,
        cache: Cache,
        forwarder: MetricForwarder,
    ) -> None:

        super().__init__(
            "node-identifier",
            image=GraplDockerBuild(
                dockerfile="../src/rust/Dockerfile",
                target="node-identifier-deploy",
                context="../src",
            ),
            retry_image=GraplDockerBuild(
                dockerfile="../src/rust/Dockerfile",
                target="node-identifier-retry-handler-deploy",
                context="../src",
            ),
            command="/node-identifier",
            retry_command="/node-identifier-retry-handler",
            env={
                **configurable_envvars(
                    "node-identifier", ["RUST_LOG", "RUST_BACKTRACE"]
                ),
                "REDIS_ENDPOINT": cache.endpoint,
                # TODO: If the retry handler doesn't get permission to
                # interact with these tables, then it probably
                # shouldn't get these environment variables.
                "DYNAMIC_SESSION_TABLE": db.dynamic_session_table.name,
            },
            input_emitter=input_emitter,
            output_emitter=output_emitter,
            forwarder=forwarder,
            network=network,
        )

        # Note that these permissions are only granted to the
        # default service's task role, *not* the retry service.
        # (This is probably a mistake).
        #
        # Also, these are the same tables that were passed to the
        # service via environment variables above.
        dynamodb.grant_read_write_on_tables(
            self.default_service.task_role,
            [
                db.dynamic_session_table,
            ],
        )

        self.allow_egress_to_cache(cache)
