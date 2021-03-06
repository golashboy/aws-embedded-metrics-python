# Copyright 2019 Amazon.com, Inc. or its affiliates.
# Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from aws_embedded_metrics.logger.metrics_context import MetricsContext
from aws_embedded_metrics.serializers import Serializer
from aws_embedded_metrics.constants import MAX_DIMENSIONS
import json
from typing import Any, Dict, List


class LogSerializer(Serializer):
    @staticmethod
    def serialize(context: MetricsContext) -> str:
        dimension_keys = []
        dimensions_properties: Dict[str, str] = {}

        for dimension_set in context.get_dimensions():
            keys = list(dimension_set.keys())
            dimension_keys.append(keys[0:MAX_DIMENSIONS])
            dimensions_properties = {**dimensions_properties, **dimension_set}

        metric_pointers: List[Dict[str, str]] = []

        metric_definitions = {
            "Dimensions": dimension_keys,
            "Metrics": metric_pointers,
            "Namespace": context.namespace,
        }
        cloud_watch_metrics = [metric_definitions]

        body: Dict[str, Any] = {
            **dimensions_properties,
            **context.properties,
            "_aws": {**context.meta, "CloudWatchMetrics": cloud_watch_metrics},
        }

        for metric_name, metric in context.metrics.items():

            if len(metric.values) == 1:
                body[metric_name] = metric.values[0]
            else:
                body[metric_name] = metric.values

            metric_pointers.append({"Name": metric_name, "Unit": metric.unit})

        return json.dumps(body)
