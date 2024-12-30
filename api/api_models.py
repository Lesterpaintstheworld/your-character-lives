from marshmallow import Schema, fields, validate

class MemorySchema(Schema):
    """Schema for memory data"""
    id = fields.Str(required=True)
    content = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    type = fields.Str(validate=validate.OneOf(['conversation', 'event', 'decision']))
    metadata = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)

class PerformanceSchema(Schema):
    """Schema for performance metrics"""
    cpu_usage = fields.Float(required=True)
    memory_usage = fields.Float(required=True)
    uptime = fields.Int(required=True)
    active_threads = fields.Int(required=True)
    audio_latency = fields.Float(required=True)

class ConfigSchema(Schema):
    """Schema for configuration data"""
    screenshot_interval = fields.Int(validate=validate.Range(min=1))
    audio_format = fields.Int()
    channels = fields.Int(validate=validate.Range(min=1))
    sample_rate = fields.Int(validate=validate.Range(min=1))
    record_duration = fields.Int(validate=validate.Range(min=1))
