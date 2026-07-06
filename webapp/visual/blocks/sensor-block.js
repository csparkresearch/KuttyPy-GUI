/**
 * Unified KuttyPy sensor read block — scan, configure, read selected fields.
 * Requires window.KUTTYPY_SENSORS (injected before this script loads).
 */

(function () {
  const DEFAULT_TYPE = 'BMP280';
  const DEFAULT_ADDR = 0x76;

  function meta(typeId) {
    return window.KUTTYPY_SENSORS?.[typeId] ?? null;
  }

  function iconSrc(typeId) {
    const m = meta(typeId);
    return m?.icon || 'images/icons/undefined.jpeg';
  }

  Blockly.Blocks.kuttypy_sensor_read = {
    init() {
      this.typeId_ = DEFAULT_TYPE;
      this.address_ = DEFAULT_ADDR;
      this.configIndices_ = {};
      this.selectedFields_ = {};

      this.appendDummyInput('HEADER')
        .appendField('Read sensor')
        .appendField(new Blockly.FieldImage(
          'images/icons/i2cscan.png', 88, 26, 'Scan I2C', this.onScan_.bind(this),
        ))
        .appendField(new Blockly.FieldLabelSerializable(this.sensorLabel_()), 'SENSOR_LABEL')
        .appendField(new Blockly.FieldImage(iconSrc(this.typeId_), 56, 56), 'ICON');

      this.appendDummyInput('ADDR_ROW')
        .appendField('Address')
        .appendField(new Blockly.FieldTextInput(this.addrLabel_()), 'ADDR_LABEL');

      this.fieldRow_ = null;
      this.configInput_ = null;
      this.rebuildFieldRow_();
      this.rebuildConfigRow_();

      this.setInputsInline(false);
      this.setOutput(true, null);
      this.setColour(330);
      this.setTooltip('Read one or more sensor values. Multiple selections return an object for plotting.');
      this.setHelpUrl('');
    },

    sensorLabel_() {
      const m = meta(this.typeId_);
      return m ? m.name : this.typeId_;
    },

    addrLabel_() {
      const m = meta(this.typeId_);
      if (m && !m.addresses.length) return 'On-board ADC';
      return `0x${(this.address_ || 0).toString(16).toUpperCase().padStart(2, '0')}`;
    },

    rebuildFieldRow_() {
      if (this.fieldRow_) {
        this.removeInput('FIELD_ROW');
      }
      this.fieldRow_ = this.appendDummyInput('FIELD_ROW');
      this.fieldRow_.appendField('Readings');

      const m = meta(this.typeId_);
      if (!m?.fields?.length) {
        this.fieldRow_.appendField(new Blockly.FieldLabel('(none)'));
        return;
      }

      if (!this.selectedFields_ || !Object.keys(this.selectedFields_).length) {
        this.selectedFields_ = {};
        this.selectedFields_[m.fields[0][1]] = true;
      }

      for (const [label, key] of m.fields) {
        const on = this.selectedFields_[key] === true;
        this.fieldRow_.appendField(
          new Blockly.FieldCheckbox(on ? 'TRUE' : 'FALSE'),
          `F_${key}`,
        );
        this.fieldRow_.appendField(label);
      }
    },

    getSelectedFieldKeys_() {
      const m = meta(this.typeId_);
      if (!m?.fields?.length) return [];
      const keys = [];
      for (const [, key] of m.fields) {
        if (this.getField(`F_${key}`)?.getValue() === 'TRUE') keys.push(key);
      }
      return keys.length ? keys : [m.fields[0][1]];
    },

    snapshotSelectedFields_() {
      const m = meta(this.typeId_);
      const state = {};
      for (const [, key] of m?.fields || []) {
        state[key] = this.getField(`F_${key}`)?.getValue() === 'TRUE';
      }
      return state;
    },

    rebuildConfigRow_() {
      if (this.configInput_) {
        this.removeInput('CONFIG_ROW');
      }
      this.configInput_ = this.appendDummyInput('CONFIG_ROW');

      const m = meta(this.typeId_);
      if (!m || !m.config.length) {
        this.configInput_
          .appendField('Configure')
          .appendField(new Blockly.FieldLabel('(none)'), 'CONFIG_NONE');
        return;
      }

      const cfgOpts = m.config.map((c, i) => [c.label, String(i)]);
      this.configInput_
        .appendField('Configure')
        .appendField(new Blockly.FieldDropdown(cfgOpts, this.onConfigChange_.bind(this)), 'CONFIG')
        .appendField(new Blockly.FieldDropdown(() => this.settingOptions_(), this.onSettingChange_.bind(this)), 'SETTING');

      const first = m.config[0];
      const saved = this.configIndices_[first.key];
      const settingIdx = saved === undefined ? (first.defaultIndex ?? 0) : Number(saved);
      const settingField = this.getField('SETTING');
      if (settingField) settingField.setValue(String(settingIdx));
    },

    settingOptions_() {
      const m = meta(this.typeId_);
      if (!m || !m.config.length) return [['—', '0']];
      const cfgIdx = Number(this.getFieldValue('CONFIG') || 0);
      const cfg = m.config[cfgIdx] || m.config[0];
      return cfg.options.map((opt, i) => [opt, String(i)]);
    },

    onConfigChange_(newCfgIndex) {
      const m = meta(this.typeId_);
      if (!m) return newCfgIndex;
      const cfg = m.config[Number(newCfgIndex)] || m.config[0];
      const saved = this.configIndices_[cfg.key];
      const idx = saved === undefined ? (cfg.defaultIndex ?? 0) : Number(saved);
      const settingField = this.getField('SETTING');
      if (settingField) settingField.setValue(String(idx));
      return newCfgIndex;
    },

    onSettingChange_(newVal) {
      const m = meta(this.typeId_);
      if (!m || !m.config.length) return newVal;
      const cfgIdx = Number(this.getFieldValue('CONFIG') || 0);
      const cfg = m.config[cfgIdx] || m.config[0];
      this.configIndices_[cfg.key] = Number(newVal);
      return newVal;
    },

    applySensor_(typeId, address) {
      this.typeId_ = typeId;
      this.address_ = address;
      this.configIndices_ = {};
      this.selectedFields_ = {};
      const m = meta(typeId);
      if (m) {
        for (const c of m.config) {
          this.configIndices_[c.key] = c.defaultIndex ?? 0;
        }
        if (m.fields?.length) {
          this.selectedFields_[m.fields[0][1]] = true;
        }
      }

      this.getField('SENSOR_LABEL')?.setValue(this.sensorLabel_());
      this.getField('ADDR_LABEL')?.setValue(this.addrLabel_());
      this.getField('ICON')?.setValue(iconSrc(typeId));
      this.rebuildFieldRow_();
      this.rebuildConfigRow_();
    },

    onScan_() {
      const picker = window.kuttypyOpenSensorPicker;
      if (!picker) {
        console.warn('Sensor picker not wired');
        return;
      }
      picker(this);
    },

    mutationToDom() {
      const container = document.createElement('mutation');
      container.setAttribute('type_id', this.typeId_);
      container.setAttribute('address', String(this.address_));
      container.setAttribute('config', JSON.stringify(this.configIndices_));
      container.setAttribute('fields', JSON.stringify(this.snapshotSelectedFields_()));
      return container;
    },

    domToMutation(xmlElement) {
      this.typeId_ = xmlElement.getAttribute('type_id') || DEFAULT_TYPE;
      this.address_ = Number(xmlElement.getAttribute('address') || DEFAULT_ADDR);
      try {
        this.configIndices_ = JSON.parse(xmlElement.getAttribute('config') || '{}');
      } catch {
        this.configIndices_ = {};
      }
      try {
        this.selectedFields_ = JSON.parse(xmlElement.getAttribute('fields') || '{}');
      } catch {
        this.selectedFields_ = {};
      }
      this.getField('SENSOR_LABEL')?.setValue(this.sensorLabel_());
      this.getField('ADDR_LABEL')?.setValue(this.addrLabel_());
      this.getField('ICON')?.setValue(iconSrc(this.typeId_));
      this.rebuildFieldRow_();
      this.rebuildConfigRow_();
    },

    saveExtraState() {
      return {
        typeId: this.typeId_,
        address: this.address_,
        configIndices: this.configIndices_,
        selectedFields: this.snapshotSelectedFields_(),
      };
    },

    loadExtraState(state) {
      this.typeId_ = state.typeId || DEFAULT_TYPE;
      this.address_ = state.address ?? DEFAULT_ADDR;
      this.configIndices_ = state.configIndices || {};
      this.selectedFields_ = state.selectedFields || {};
      this.getField('SENSOR_LABEL')?.setValue(this.sensorLabel_());
      this.getField('ADDR_LABEL')?.setValue(this.addrLabel_());
      this.getField('ICON')?.setValue(iconSrc(this.typeId_));
      this.rebuildFieldRow_();
      this.rebuildConfigRow_();
    },
  };

  function sensorInstanceLabel(block) {
    const m = meta(block.typeId_);
    const name = (m?.name || block.typeId_).replace(/\s+/g, '_');
    if (m && !m.addresses.length) {
      const ch = block.configIndices_?.channel ?? 0;
      return `${name}_A${ch}`;
    }
    const hex = (block.address_ || 0).toString(16).toUpperCase().padStart(2, '0');
    return `${block.typeId_}_0x${hex}`;
  }

  Blockly.JavaScript.kuttypy_sensor_read = function (block) {
    const typeId = block.typeId_;
    const address = block.address_;
    const fields = block.getSelectedFieldKeys_();
    const cfg = JSON.stringify(block.configIndices_ || {});
    const label = sensorInstanceLabel(block);
    const code = `readKuttyPySensor('${label}','${typeId}',${address},${JSON.stringify(fields)},${JSON.stringify(cfg)})`;
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
  };

  Blockly.Python.kuttypy_sensor_read = function (block) {
    const typeId = block.typeId_;
    const fields = block.getSelectedFieldKeys_();
    return [`p.get_sensor('${typeId}',${JSON.stringify(fields)})`, Blockly.Python.ORDER_FUNCTION_CALL];
  };
})();
