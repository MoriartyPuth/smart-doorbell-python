# IR sensor (the doorbell "button") and PIR motion sensor.

import select
import sys

from machine import Pin

import pins

_ir_flag = False   # set by an interrupt so a quick wave is never missed while the board is busy
_ir = None
_pir = None
_keyboard = None


def _on_ir(pin):
    global _ir_flag
    _ir_flag = True


def begin():
    global _ir, _pir, _keyboard, _ir_flag
    pull = Pin.PULL_UP if pins.IR_ACTIVE_LOW else Pin.PULL_DOWN
    edge = Pin.IRQ_FALLING if pins.IR_ACTIVE_LOW else Pin.IRQ_RISING
    _ir = Pin(pins.PIN_IR, Pin.IN, pull)
    _ir.irq(trigger=edge, handler=_on_ir)
    if pins.PIN_PIR is not None:
        _pir = Pin(pins.PIN_PIR, Pin.IN, Pin.PULL_DOWN)

    # Testing aid: typing r + Enter in Thonny's Shell simulates a visitor.
    _keyboard = select.poll()
    _keyboard.register(sys.stdin, select.POLLIN)
    _ir_flag = False


def bell_triggered():
    """True once per wave at the IR sensor (or when r is typed in the Shell)."""
    global _ir_flag
    if _keyboard and _keyboard.poll(0) and sys.stdin.read(1) == "r":
        _ir_flag = True
    if not _ir_flag:
        return False
    _ir_flag = False
    print("[SENSOR] bell triggered")
    return True


def motion_detected():
    """True while the PIR sensor sees movement. Always False if no PIR is fitted."""
    return _pir is not None and _pir.value() == 1
