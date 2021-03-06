import logging
from datetime import timedelta
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
)

import custom_components.sector as sector

DEPENDENCIES = ["sector"]

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    sector_hub = hass.data[sector.DATA_SA]
    code = discovery_info[sector.CONF_CODE]
    code_format = discovery_info[sector.CONF_CODE_FORMAT]

    async_add_entities([
        SectorAlarmPanel(sector_hub, code, code_format)
        ])


class SectorAlarmPanel(AlarmControlPanelEntity):

    def __init__(self, hub, code, code_format):
        self._hub = hub
        self._code = code if code != "" else None
        self._code_format = code_format
        self._state = STATE_ALARM_PENDING
        self._changed_by = None

    @property
    def name(self):
        return "Sector Alarm {}".format(self._hub.alarm_id)

    @property
    def changed_by(self):
        return self._changed_by

    @property
    def supported_features(self) -> int:
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY

    @property
    def  code_arm_required(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def code_format(self):
        return self._code_format if self._code_format != "" else None

    def _validate_code(self, code):
        check = self._code is None or code == self._code
        if not check:
            _LOGGER.warning("Invalid code given")
        return check

    async def async_alarm_arm_home(self, code=None):
        command = "partial"
        if not self._validate_code(code):
            return

        _LOGGER.debug("Trying to arm home Sector Alarm")
        result = await self._hub.triggeralarm(command, code=code)
        if result:
            _LOGGER.debug("Armed home Sector Alarm")
            self._state = STATE_ALARM_ARMED_HOME
            return True
        return False

    async def async_alarm_disarm(self, code=None):
        command = "disarm"
        if not self._validate_code(code):
            return

        _LOGGER.debug("Trying to disarm Sector Alarm")
        result = await self._hub.triggeralarm(command, code=code)
        if result:
            _LOGGER.debug("Disarmed Sector Alarm")
            self._state = STATE_ALARM_DISARMED
            return True
        return False

    async def async_alarm_arm_away(self, code=None):
        command = "full"
        if not self._validate_code(code):
            return

        _LOGGER.debug("Trying to arm away Sector Alarm")
        result = await self._hub.triggeralarm(command, code=code)
        if result:
            _LOGGER.debug("Armed away Sector Alarm")
            self._state = STATE_ALARM_ARMED_AWAY
            return True
        return False

    async def async_update(self):
        update = await self._hub.async_update()
        if self._hub.alarm_state == 3:
            self._state = STATE_ALARM_ARMED_AWAY
        elif self._hub.alarm_state == 2:
            self._state = STATE_ALARM_ARMED_HOME
        elif self._hub.alarm_state == 1:
            self._state = STATE_ALARM_DISARMED
        else:
            self._state = STATE_ALARM_PENDING

        self._changed_by = self._hub.alarm_changed_by

        return True
