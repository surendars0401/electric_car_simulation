from pynput import keyboard
import time
import sys


class ElectricCar:
    def __init__(self, battery_capacity_kWh=1, max_speed=500, acceleration_rate=20, deceleration_rate=5,
                 braking_force=20, sudden_brake_force=100):
        self.battery_capacity_kWh = battery_capacity_kWh
        self.battery_remaining_kWh = battery_capacity_kWh
        self.max_speed = max_speed
        self.acceleration_rate = acceleration_rate
        self.deceleration_rate = deceleration_rate
        self.braking_force = braking_force
        self.sudden_brake_force = sudden_brake_force
        self.speed = 0
        self.last_speed = 0
        self.accelerating = False
        self.braking = False
        self.sudden_braking = False
        self.last_update_time = time.time()

    def update_status(self):
        if self.battery_remaining_kWh <= 0:
            self.speed = 0
            self.accelerating = False
            self.braking = False
            self.sudden_braking = False
            print("\rBattery drained. Car stopped.")
            return

        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        speed_before_update = self.speed
        self.last_update_time = current_time

        self.apply_movement(elapsed_time)
        self.consume_battery(elapsed_time)
        acceleration = (self.speed - speed_before_update) / elapsed_time
        self.display_status(acceleration)

    def apply_movement(self, elapsed_time):
        if self.sudden_braking:
            self.speed = max(self.speed - self.sudden_brake_force * elapsed_time, 0)
            if self.speed == 0:
                self.sudden_braking = False
        elif self.braking:
            self.speed = max(self.speed - self.braking_force * elapsed_time, 0)
        elif self.accelerating and self.battery_remaining_kWh > 0:
            self.speed = min(self.speed + self.acceleration_rate * elapsed_time, self.max_speed)
        else:
            self.speed = max(self.speed - self.deceleration_rate * elapsed_time, 0)

    def consume_battery(self, elapsed_time):
        consumption_rate = 0.2 * self.speed
        self.battery_remaining_kWh -= consumption_rate * (elapsed_time / 3600)
        self.battery_remaining_kWh = max(self.battery_remaining_kWh, 0)

    def display_status(self, acceleration):
        battery_bar = self.get_battery_bar()
        acceleration_bar = self.get_acceleration_bar(acceleration)
        sys.stdout.write(
            f"\r{battery_bar} Battery: {self.battery_remaining_kWh:.2f} kWh | {acceleration_bar} Acceleration: {acceleration:.2f} m/s² | Speed: {self.speed:.2f} km/h")
        sys.stdout.flush()

    def get_battery_bar(self):
        battery_percentage = self.battery_remaining_kWh / self.battery_capacity_kWh * 100
        bar_length = 10
        filled_length = int(bar_length * battery_percentage / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        color = '\033[92m' if battery_percentage >= 50 else '\033[93m' if battery_percentage >= 25 else '\033[91m'
        return color + bar + '\033[0m'

    def get_acceleration_bar(self, acceleration):
        bar_length = 10
        max_acceleration = max(self.acceleration_rate, self.braking_force, self.sudden_brake_force)
        normalized_acceleration = min(abs(acceleration) / max_acceleration, 1)
        filled_length = int(bar_length * normalized_acceleration)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        color = '\033[94m' if acceleration >= 0 else '\033[95m'
        return color + bar + '\033[0m'

    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False
        if key == keyboard.KeyCode.from_char('w'):
            self.accelerating = True
            self.braking = False
            self.sudden_braking = False
        if key == keyboard.KeyCode.from_char('s'):
            self.braking = True
            self.sudden_braking = False
        if key == keyboard.Key.space:
            self.sudden_braking = True
            self.accelerating = False
            self.braking = False

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('w'):
            self.accelerating = False
        if key == keyboard.KeyCode.from_char('s'):
            self.braking = False


def main():
    car = ElectricCar()

    listener = keyboard.Listener(
        on_press=car.on_press,
        on_release=car.on_release)
    listener.start()

    try:
        while listener.running:
            car.update_status()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        pass


if __name__ == "__main__":
    main()
