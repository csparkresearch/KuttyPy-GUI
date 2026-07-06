/** ATMEGA32 register map — mirrors utilities/REGISTERS.py */

export const ATMEGA32_REGISTERS = {
  TWBR: 0x20,
  TWSR: 0x21,
  TWAR: 0x22,
  TWDR: 0x23,
  ADCL: 0x24,
  ADCH: 0x25,
  ADCSRA: 0x26,
  ADMUX: 0x27,
  ACSR: 0x28,
  UBRRL: 0x29,
  UCSRB: 0x2a,
  UCSRA: 0x2b,
  UDR: 0x2c,
  SPCR: 0x2d,
  SPSR: 0x2e,
  SPDR: 0x2f,
  PIND: 0x30,
  DDRD: 0x31,
  PORTD: 0x32,
  PINC: 0x33,
  DDRC: 0x34,
  PORTC: 0x35,
  PINB: 0x36,
  DDRB: 0x37,
  PORTB: 0x38,
  PINA: 0x39,
  DDRA: 0x3a,
  PORTA: 0x3b,
  EECR: 0x3c,
  EEDR: 0x3d,
  EEARL: 0x3e,
  EEARH: 0x3f,
  OCR2: 0x43,
  TCNT2: 0x44,
  TCCR2: 0x45,
  ICR1L: 0x46,
  ICR1H: 0x47,
  OCR1BL: 0x48,
  OCR1BH: 0x49,
  OCR1AL: 0x4a,
  OCR1AH: 0x4b,
  TCNT1L: 0x4c,
  TCNT1H: 0x4d,
  TCCR1B: 0x4e,
  TCCR1A: 0x4f,
  SFIOR: 0x50,
  TCNT0: 0x52,
  TCCR0: 0x53,
  MCUCSR: 0x54,
  MCUCR: 0x55,
  TWCR: 0x56,
  SPMCR: 0x57,
  TIFR: 0x58,
  TIMSK: 0x59,
  GIFR: 0x5a,
  GICR: 0x5b,
  OCR0: 0x5c,
  SPL: 0x5d,
  SPH: 0x5e,
  SREG: 0x5f,
};

export const REGISTER_NAMES = Object.keys(ATMEGA32_REGISTERS).sort();

/** UART — can break serial comms if misconfigured */
export const UART_REGISTERS = new Set(['UBRRL', 'UCSRA', 'UCSRB', 'UDR']);

/** MCU core / system — can crash or reset the chip */
export const MCU_REGISTERS = new Set(['SPL', 'SPH', 'SREG', 'MCUCR', 'MCUCSR', 'SPMCR', 'GICR', 'GIFR']);

export const RESTRICTED_REGISTERS = new Set(['UBRRL']);

export function isCriticalRegister(name) {
  return UART_REGISTERS.has(name) || MCU_REGISTERS.has(name);
}

export function criticalHint(name) {
  if (RESTRICTED_REGISTERS.has(name)) {
    return 'Restricted: writing UBRRL can change baud rate and disconnect the link.';
  }
  if (UART_REGISTERS.has(name)) {
    return 'UART register — incorrect values may break USB serial communication.';
  }
  if (MCU_REGISTERS.has(name)) {
    return 'MCU system register — incorrect values may reset or crash the firmware.';
  }
  return '';
}

export function resolveRegister(name) {
  const key = String(name || '').trim().toUpperCase();
  if (!key || !(key in ATMEGA32_REGISTERS)) return null;
  return { name: key, addr: ATMEGA32_REGISTERS[key] };
}

export function clampByte(n) {
  return (Number(n) | 0) & 0xff;
}

const DDR_TO_PORT = { DDRA: 'A', DDRB: 'B', DDRC: 'C', DDRD: 'D' };

/** Map a port panel register name to port letter and kind (ddr/port/pin). */
export function portPanelFromRegister(name) {
  const key = String(name || '').trim().toUpperCase();
  if (key in DDR_TO_PORT) return { port: DDR_TO_PORT[key], kind: 'ddr' };
  if (key.length === 5 && key.startsWith('PORT')) return { port: key[4], kind: 'port' };
  if (key.length === 4 && key.startsWith('PIN')) return { port: key[3], kind: 'pin' };
  return null;
}
