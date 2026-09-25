"""Authoritative device schema.

Edit CHANNEL_PINS for channel wiring and DEVICE_METADATA_PINS for controller
metadata. CHANNELS is a generated view for runtime consumers, never a
second source of pin settings. Write contracts and observations share this schema.
"""
from homeassistant.components.climate.const import HVACMode

DOMAIN = "microclimate_integration"
CONF_LOG_RAW_RESPONSE = "log_raw_response"
DEFAULT_MODEL = "Evo Connect"

# Probe profiles control entity registration; observed modes come from control pins.
MODEL_CHANNEL_OPTIONS = {'Evo Connect': {'Yellow': {'hasTemperatureProbe': True},
                 'Blue': {'hasTemperatureProbe': False}},
 'Evo Connect 2': {'Yellow': {  'hasTemperatureProbe': True},
                   'Blue': {'hasTemperatureProbe': True}},
 'Evo Connect 3': {'Yellow': {  'hasTemperatureProbe': True},
                   'Red': {'hasTemperatureProbe': True},
                   'Blue': {'hasTemperatureProbe': True}}}

CONTROL_TYPE_MAPPING = {'0': 'fixed', '1': 'heating', '2': 'cooling'}

# Timing codes differ by channel family; consumers use timing_type_mapping.
BLUE_TIMING_TYPE_MAPPING = {'0': 'Constant', '1': 'Day Night', '2': 'Multi', '3': 'Periodic', '4': 'Seasonal'}
THERMAL_TIMING_TYPE_MAPPING = {'0': 'Constant', '1': 'Day Night', '2': 'Multi', '3': 'Seasonal'}
CHANNEL_CAPABILITIES = {
    'Yellow': {'ramp': True, 'variable_output': True, 'periodic': False},
    'Red': {'ramp': True, 'variable_output': True, 'periodic': False},
    'Blue': {'ramp': False, 'variable_output': False, 'periodic': True},
}


def timing_type_mapping(channel):
    """Validated channel families, shared across their supported model profiles."""
    if channel not in CHANNEL_CAPABILITIES:
        return {}
    return BLUE_TIMING_TYPE_MAPPING if CHANNEL_CAPABILITIES[channel]['periodic'] else THERMAL_TIMING_TYPE_MAPPING


OUTPUT_TYPE_MAPPING = {'0': 'pulse', '1': 'dimming'}

COMMON_ATTRIBUTES = {'temp_pin': {'description': 'Current Temp', 'transformation': 'temperature'},
 'setpoint_pin': {'description': 'Current Set Point', 'transformation': 'setpoint'},
 'control_pin': {'description': 'Control Type', 'transformation': 'control_type'},
 'ramp_time_pin': {'description': 'Ramp Time', 'transformation': 'duration_minutes'},
 'lower_alarm_pin': {'description': 'Lower Alarm Point', 'transformation': 'temperature'},
 'upper_alarm_pin': {'description': 'Upper Alarm Point', 'transformation': 'temperature'},
 'timing_type_pin': {'description': 'Timing Type', 'transformation': 'timing_type'},
 'output_type_pin': {'description': 'Output Type', 'transformation': 'output_type'},
 'channel_name_pin': {'description': 'Channel Name', 'transformation': 'none'},
 'current_power_pin': {'description': 'Power', 'transformation': 'none'},
 'schedule_start_time_pin': {'description': 'Start time', 'transformation': 'time'},
 'schedule_set_point_pin': {'description': 'Set point', 'transformation': 'setpoint'},
 'periodic_interval_pin': {'description': 'Periodic interval', 'transformation': 'time'},
 'periodic_duration_pin': {'description': 'Periodic duration', 'transformation': 'time'}}

CHANNEL_PINS = {'Yellow': {'temperature': {'temp_pin': 'v0', 'setpoint_pin': 'v8'},
            'alarm': {'lower_alarm_pin': 'v49', 'upper_alarm_pin': 'v50'},
            'metadata': {'control_pin': 'v52',
                         'output_type_pin': 'v54',
                         'channel_name_pin': 'v16',
                         'current_power_pin': 'v4'},
            'schedule': {'ramp_time_pin': 'v48',
                         'timing_type_pin': 'v53',
                         'period_1': {'schedule_start_time_pin': 'v32',
                                      'schedule_set_point_pin': 'v33'},
                         'period_2': {'schedule_start_time_pin': 'v34',
                                      'schedule_set_point_pin': 'v35'},
                         'period_3': {'schedule_start_time_pin': 'v36',
                                      'schedule_set_point_pin': 'v37'},
                         'period_4': {'schedule_start_time_pin': 'v38',
                                      'schedule_set_point_pin': 'v39'},
                         'period_5': {'schedule_start_time_pin': 'v40',
                                      'schedule_set_point_pin': 'v41'},
                         'period_6': {'schedule_start_time_pin': 'v42',
                                      'schedule_set_point_pin': 'v43'},
                         'period_7': {'schedule_start_time_pin': 'v44',
                                      'schedule_set_point_pin': 'v45'},
                         'period_8': {'schedule_start_time_pin': 'v46',
                                      'schedule_set_point_pin': 'v47'}}},
 'Red': {'temperature': {'temp_pin': 'v1', 'setpoint_pin': 'v9'},
         'alarm': {'lower_alarm_pin': 'v79', 'upper_alarm_pin': 'v80'},
         'metadata': {'control_pin': 'v82',
                      'output_type_pin': 'v84',
                      'channel_name_pin': 'v17',
                      'current_power_pin': 'v5'},
         'schedule': {'ramp_time_pin': 'v78',
                      'timing_type_pin': 'v83',
                      'period_1': {'schedule_start_time_pin': 'v62',
                                   'schedule_set_point_pin': 'v63'},
                      'period_2': {'schedule_start_time_pin': 'v64',
                                   'schedule_set_point_pin': 'v65'},
                      'period_3': {'schedule_start_time_pin': 'v66',
                                   'schedule_set_point_pin': 'v67'},
                      'period_4': {'schedule_start_time_pin': 'v68',
                                   'schedule_set_point_pin': 'v69'},
                      'period_5': {'schedule_start_time_pin': 'v70',
                                   'schedule_set_point_pin': 'v71'},
                      'period_6': {'schedule_start_time_pin': 'v72',
                                   'schedule_set_point_pin': 'v73'},
                      'period_7': {'schedule_start_time_pin': 'v74',
                                   'schedule_set_point_pin': 'v75'},
                      'period_8': {'schedule_start_time_pin': 'v76',
                                   'schedule_set_point_pin': 'v77'},
                      'periodic_interval_pin': 'v85',
                      'periodic_duration_pin': 'v86'}},
 'Blue': {'temperature': {'temp_pin': 'v2', 'setpoint_pin': 'v10'},
          'alarm': {'lower_alarm_pin': 'v109', 'upper_alarm_pin': 'v110'},
          'metadata': {'control_pin': 'v112',
                       'output_type_pin': 'v114',
                       'channel_name_pin': 'v18',
                       'current_power_pin': 'v6'},
          'schedule': {'ramp_time_pin': 'v108',
                       'timing_type_pin': 'v113',
                       'period_1': {'schedule_start_time_pin': 'v92',
                                    'schedule_set_point_pin': 'v93'},
                       'period_2': {'schedule_start_time_pin': 'v94',
                                    'schedule_set_point_pin': 'v95'},
                       'period_3': {'schedule_start_time_pin': 'v96',
                                    'schedule_set_point_pin': 'v97'},
                       'period_4': {'schedule_start_time_pin': 'v98',
                                    'schedule_set_point_pin': 'v99'},
                       'period_5': {'schedule_start_time_pin': 'v100',
                                    'schedule_set_point_pin': 'v101'},
                       'period_6': {'schedule_start_time_pin': 'v102',
                                    'schedule_set_point_pin': 'v103'},
                       'period_7': {'schedule_start_time_pin': 'v104',
                                    'schedule_set_point_pin': 'v105'},
                       'period_8': {'schedule_start_time_pin': 'v106',
                                    'schedule_set_point_pin': 'v107'},
                       'periodic_interval_pin': 'v115',
                       'periodic_duration_pin': 'v116'}}}

DEVICE_METADATA_PINS = {'season_1_start_pin': {'pin': 'v20',
                        'description': 'Season 1 Start',
                        'channel': 'Root',
                        'transformation': 'date'},
 'season_2_start_pin': {'pin': 'v21',
                        'description': 'Season 2 Start',
                        'channel': 'Root',
                        'transformation': 'date'},
 'season_3_start_pin': {'pin': 'v22',
                        'description': 'Season 3 Start',
                        'channel': 'Root',
                        'transformation': 'date'},
 'season_4_start_pin': {'pin': 'v23',
                        'description': 'Season 4 Start',
                        'channel': 'Root',
                        'transformation': 'date'},
 'prev_24hr_power_pin': {'pin': 'v24',
                         'description': 'Prev Power 24hr',
                         'channel': 'Root',
                         'transformation': 'none'},
 'temperature_units_pin': {'pin': 'v25',
                           'description': 'Temperature Units',
                           'channel': 'Root',
                           'transformation': 'none'},
 'system_date_pin': {'pin': 'v26',
                     'description': 'System Date',
                     'channel': 'Root',
                     'transformation': 'date'},
 'system_time_pin': {'pin': 'v27',
                     'description': 'System Time',
                     'channel': 'Root',
                     'transformation': 'time'},
 'system_name_pin': {'pin': 'v29',
                     'description': 'System Name',
                     'channel': 'Root',
                     'transformation': 'none'}}

CHANNEL_FIELD_PATHS = {'temp_pin': ('temperature', 'temp_pin'),
 'setpoint_pin': ('temperature', 'setpoint_pin'),
 'control_pin': ('metadata', 'control_pin'),
 'channel_name': ('metadata', 'channel_name_pin'),
 'current_power': ('metadata', 'current_power_pin'),
 'output_type': ('metadata', 'output_type_pin'),
 'lower_alarm': ('alarm', 'lower_alarm_pin'),
 'upper_alarm': ('alarm', 'upper_alarm_pin'),
 'ramp_time': ('schedule', 'ramp_time_pin'),
 'timing_type': ('schedule', 'timing_type_pin')}

MODEL_OPTIONS = tuple(MODEL_CHANNEL_OPTIONS)
HVAC_MODE_MAPPING = {"off": HVACMode.OFF, "heating": HVACMode.HEAT, "cooling": HVACMode.COOL}

# Derived flat view used by measurements, validation and write contracts.
CHANNELS = {
    channel: {key: groups[group][role] for key, (group, role) in CHANNEL_FIELD_PATHS.items()}
    for channel, groups in CHANNEL_PINS.items()
}
# Temporary defaults for the write-validation release.
CONF_ENABLE_WRITES = 'enable_writes'
DEFAULT_ENABLE_WRITES = True
DEFAULT_ENABLE_DIAGNOSTICS = True
