import structlog
structlog.configure(
    processors=
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ,
    wrapper_class=structlog.make_filtering_bound_logger(30),
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()
