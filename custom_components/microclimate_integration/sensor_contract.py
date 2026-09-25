"""Typed measurements may be registered only after pin/unit evidence review.

Mappings are maintainer-confirmed against the controller display. Synthetic
fixtures are regression examples, not independent hardware captures.
"""
from dataclasses import dataclass, field
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfTime, PERCENTAGE


@dataclass(frozen=True, kw_only=True)
class MeasurementDefinition:
    key: str
    name: str
    channel: str
    pin: str
    kind: str
    evidence: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    alarm_codes: dict[int, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.evidence.strip():
            raise ValueError("Documented pin/unit evidence is required")
        if self.kind not in ("temperature", "setpoint", "number", "percentage", "alarm", "duration"):
            raise ValueError("Unknown measurement kind")
        if self.kind in ("temperature", "setpoint") and (self.unit != UnitOfTemperature.CELSIUS or self.device_class != SensorDeviceClass.TEMPERATURE):
            raise ValueError("Microclimate native temperatures are Celsius")
        if self.kind == "alarm" and (not self.alarm_codes or self.unit is not None or self.device_class != SensorDeviceClass.ENUM):
            raise ValueError("Alarm meanings require explicit code definitions and no units")


VERIFIED_MEASUREMENTS: dict[str, tuple[MeasurementDefinition, ...]] = {}

# Maintainer confirmation in this task: the defined mappings were checked
# against the controller display. Firmware and original captures were not supplied.
from .const import CHANNELS, MODEL_CHANNEL_OPTIONS, CHANNEL_CAPABILITIES

EVIDENCE = "Maintainer display verification, 2026-09-22; firmware unspecified"

for model, channels in MODEL_CHANNEL_OPTIONS.items():
    definitions = []
    for channel, capabilities in channels.items():
        pins = CHANNELS[channel]
        if capabilities.get("hasTemperatureProbe"):
            for key, name, pin_key, kind in (
                ("temperature", "Temperature", "temp_pin", "temperature"),
                ("setpoint", "Observed setpoint", "setpoint_pin", "setpoint"),
                ("lower_alarm", "Lower alarm threshold", "lower_alarm", "temperature"),
                ("upper_alarm", "Upper alarm threshold", "upper_alarm", "temperature"),
            ):
                if pin_key in pins:
                    definitions.append(MeasurementDefinition(
                        key=key, name=name, channel=channel, pin=pins[pin_key],
                        kind=kind, evidence=EVIDENCE, unit=UnitOfTemperature.CELSIUS,
                        device_class=SensorDeviceClass.TEMPERATURE,
                        state_class=SensorStateClass.MEASUREMENT if key=="temperature" else None,
                    ))
        if CHANNEL_CAPABILITIES[channel]["ramp"]:
            definitions.append(MeasurementDefinition(
                key="ramp_time", name="Ramp time", channel=channel, pin=pins["ramp_time"],
                kind="duration", evidence=EVIDENCE, unit=UnitOfTime.MINUTES,
                device_class=SensorDeviceClass.DURATION,
            ))
        if "current_power" in pins:
            definitions.append(MeasurementDefinition(
                key="output", name="Output percentage", channel=channel,
                pin=pins["current_power"], kind="percentage", evidence=EVIDENCE,
                unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT,
            ))
    VERIFIED_MEASUREMENTS[model] = tuple(definitions)
