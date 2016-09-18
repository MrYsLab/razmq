import pigpio
import time

def play_tone(frequency, duration, pin):
    pi = pigpio.pi()

    pi.set_mode(pin, pigpio.OUTPUT)
    frequency = int((1000 / frequency) * 1000)


    tone = [pigpio.pulse(1 << pin, 0, frequency), pigpio.pulse(0, 1 << pin, frequency)]  # flash every 100 ms

    pi.wave_clear()

    pi.wave_add_generic(tone)  # 100 ms flashes
    tone_wave = pi.wave_create()  # create and save id
    pi.wave_send_repeat(tone_wave)

    if duration == 0:
        return

    sleep_time = duration * .001
    time.sleep(sleep_time)
    pi.wave_tx_stop()  # stop waveform

    pi.wave_clear()  # clear all waveforms

play_tone(1000, 1000, 10)