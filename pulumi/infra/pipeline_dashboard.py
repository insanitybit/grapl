"""
This is an overall hacky port of what CDK produced.
Feel free to replace the SQS metrics with Kafka queue metrics asap.
Feel free to replace all of this with a Grafana dashboard asap.
"""

import json
from typing import Any, Dict, List, Union

import pulumi_aws as aws
from infra.config import DEPLOYMENT_NAME
from infra.service import ServiceLike
from infra.service_queue import ServiceQueueNames
from pulumi.output import Output

import pulumi

CWMetric = List[Union[str, Dict[str, Any]]]


def service_queue_widgets(names: ServiceQueueNames) -> List[Dict[str, Any]]:
    all_queues = {
        names.queue: {
            "id": "default",
            "color": "#2ca02c",
        },
        names.retry_queue: {
            "id": "retry",
            "color": "#ff7f0e",
        },
        names.dead_letter_queue: {
            "id": "dlq",
            "color": "#d62728",
        },
    }

    def messages_processed() -> List[CWMetric]:
        messages_deleted: List[CWMetric] = [
            [
                "AWS/SQS",
                "NumberOfMessagesDeleted",
                "QueueName",
                q,
                {"stat": "Sum", "label": props["id"], "color": props["color"]},
            ]
            for q, props in all_queues.items()
        ]
        return messages_deleted

    def messages_in_flight_or_queued() -> List[CWMetric]:
        # Sum "Messages Visible" (in the queue) with "Messages Not Visible" (sent to service, but processing)
        # but hide the two separate metrics
        messages_visible: List[CWMetric] = [
            [
                "AWS/SQS",
                "ApproximateNumberOfMessagesVisible",
                "QueueName",
                q,
                {"stat": "Sum", "visible": False, "id": props["id"]},
            ]
            for q, props in all_queues.items()
        ]

        messages_in_flight: List[CWMetric] = [
            [
                "AWS/SQS",
                "ApproximateNumberOfMessagesNotVisible",
                "QueueName",
                q,
                {"stat": "Sum", "visible": False, "id": props["id"]},
            ]
            for q, props in all_queues.items()
        ]

        summed: List[CWMetric] = [
            [
                {
                    # We filter the above metrics by their id field
                    "expression": f'SUM(METRICS("{props["id"]}"))',
                    "label": props["id"],
                    "color": props["color"],
                }
            ]
            for q, props in all_queues.items()
        ]

        return [
            *messages_visible,
            *messages_in_flight,
            *summed,
        ]

    messages_in_flight_or_queued_props = {
        "view": "timeSeries",
        "title": f"{names.service_name} queue: messages in flight, or queued",
        "region": "us-east-1",
        "metrics": messages_in_flight_or_queued(),
        "yAxis": {},
        "liveData": True,
    }

    messages_in_flight_or_queued_widget = {
        "type": "metric",
        "width": 12,
        "height": 3,
        "properties": messages_in_flight_or_queued_props,
    }

    messages_processed_props = {
        "view": "timeSeries",
        "title": f"{names.service_name} queue: msgs processed",
        "region": "us-east-1",
        "metrics": messages_processed(),
        "yAxis": {},
        "liveData": True,
    }

    messages_processed_widget = {
        "type": "metric",
        "width": 12,
        "height": 3,
        "properties": messages_processed_props,
    }

    return [messages_in_flight_or_queued_widget, messages_processed_widget]


class PipelineDashboard(pulumi.ComponentResource):
    def __init__(
        self,
        services: List[ServiceLike],
    ) -> None:
        def create_dashboard_json(args: Dict[str, Any]) -> str:
            service_queue_names: List[ServiceQueueNames] = args["service_queue_names"]
            widgets: List[Dict[str, Any]] = sum(
                [service_queue_widgets(sqn) for sqn in service_queue_names], []
            )
            return json.dumps({"widgets": widgets})

        dashboard_body = Output.all(
            service_queue_names=[service.queue.queue_names for service in services],
        ).apply(create_dashboard_json)

        aws.cloudwatch.Dashboard(
            "pipeline-dashboard",
            dashboard_body=dashboard_body,
            dashboard_name=f"{DEPLOYMENT_NAME}-pipeline-dashboard",
            opts=pulumi.ResourceOptions(),
        )
