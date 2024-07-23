import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from datetime import datetime, timedelta
import json
import os

from .login import login_screen

class WorkHourApp(toga.App):

    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # JSON file path
        self.data_file = 'work_hours.json'

        self.current_user = None
        self.timer_running = False
        self.total_worked_time = timedelta()

        # Load data
        self.load_data()

        # Show login screen initially
        self.main_window.content = login_screen(self)
        self.main_window.show()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f)

    def show_user_dashboard(self):
        self.user_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.start_button = toga.Button('Start', on_press=self.start_timer, style=Pack(padding=10))
        self.stop_button = toga.Button('Stop', on_press=self.stop_timer, style=Pack(padding=10))
        self.logout_button = toga.Button('Logout', on_press=self.logout, style=Pack(padding=10))

        self.start_time_label = toga.Label('Start Time: ', style=Pack(padding=10))
        self.end_time_label = toga.Label('End Time: ', style=Pack(padding=10))
        self.worked_time_label = toga.Label('Worked Time: ', style=Pack(padding=10))

        self.user_box.add(self.start_button)
        self.user_box.add(self.stop_button)
        self.user_box.add(self.logout_button)
        self.user_box.add(self.start_time_label)
        self.user_box.add(self.end_time_label)
        self.user_box.add(self.worked_time_label)

        self.main_window.content = self.user_box
        self.main_window.show()

    def show_admin_dashboard(self):
        self.admin_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.logout_button = toga.Button('Logout', on_press=self.logout, style=Pack(padding=10))

        self.admin_box.add(self.logout_button)

        self.admin_worked_time_label = toga.Label('User Worked Times:', style=Pack(padding=10))
        self.admin_box.add(self.admin_worked_time_label)

        for user, seconds in self.data.items():
            user_label = toga.Label(f'{user}: {str(timedelta(seconds=seconds))}', style=Pack(padding=10))
            self.admin_box.add(user_label)

        self.main_window.content = self.admin_box
        self.main_window.show()

    def start_timer(self, widget):
        if not self.timer_running:
            self.start_time = datetime.now()
            self.start_time_label.text = f'Start Time: {self.start_time.strftime("%H:%M:%S - %d/%m/%Y")}'
            self.timer_running = True

    def stop_timer(self, widget):
        if self.timer_running:
            end_time = datetime.now()
            worked_time = end_time - self.start_time
            self.total_worked_time += worked_time

            self.end_time_label.text = f'End Time: {end_time.strftime("%H:%M:%S - %d/%m/%Y")}'
            self.worked_time_label.text = f'Worked Time: {str(self.total_worked_time).split(".")[0]}'
            self.timer_running = False

            # Save worked time to data
            if self.current_user not in self.data:
                self.data[self.current_user] = 0
            elif isinstance(self.data[self.current_user], dict):  # if stored as dict, convert to int
                self.data[self.current_user] = int(self.data[self.current_user].get('seconds', 0))
            self.data[self.current_user] += int(worked_time.total_seconds())
            self.save_data()

    def logout(self, widget):
        self.current_user = None
        self.timer_running = False
        self.start_time = None
        self.total_worked_time = timedelta()
        self.main_window.content = login_screen(self)

def main():
    return WorkHourApp()

if __name__ == '__main__':
    main().main_loop()
