import logging
import os

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_otel(app, service_name: str, environment: str, version: str) -> None:
    resource = Resource.create(
        {
            "service.name": service_name,
            "deployment.environment": environment,
            "service.version": version,
        }
    )

    # ---------- traces ----------
    traces_endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT"
    )

    if traces_endpoint:
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        trace_exporter = OTLPSpanExporter(endpoint=traces_endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

    # ---------- logs ----------
    logs_endpoint = os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT") or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT"
    )

    if logs_endpoint:
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        log_exporter = OTLPLogExporter(endpoint=logs_endpoint)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

        # Attach OTel log handler to root logger in addition to existing stdout handler
        app_logger = logging.getLogger(service_name)
        app_logger.addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider))
