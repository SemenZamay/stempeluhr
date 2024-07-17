import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime, timedelta
import json
import os
import threading

class StempelUhr(toga.App):
    def startup(self):

        self.current_user = None
        self.start_time = None
        self.total_time = timedelta()

        self.work_hours = self.load_work_hours()
        self.timer_running = False

        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.username_input = toga.TextInput(placeholder="Username", style=Pack(flex=1, padding=(0, 5)))
        self.password_input = toga.PasswordInput(placeholder="Password", style=Pack(flex=1, padding=(0, 5)))
        self.login_button = toga.Button("Login", on_press=self.handle_login, style=Pack(padding=5))

        login_box = toga.Box(style=Pack(direction=ROW, padding=10))
        login_box.add(self.username_input)
        login_box.add(self.password_input)
        login_box.add(self.login_button)

        self.main_box.add(login_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()



    def handle_login(self, widget):
        username = self.username_input.value
        password = self.password_input.value

        if username == "admin" and password == "admin123":
            self.current_user = "admin"
            self.show_admin_dashboard()
        elif username == "user" and password == "user123":
            self.current_user = username
            self.show_user_dashboard()
        else:
            self.main_window.info_dialog("Login Failed", "Invalid username or password")

    def show_admin_dashboard(self):
        self.main_box.clear()

        admin_label = toga.Label("Welcome, Admin", style=Pack(padding=10))
        self.main_box.add(admin_label)

        work_hours_label = toga.Label("Users' Work Hours This Week:", style=Pack(padding=10))
        self.main_box.add(work_hours_label)

        self.work_hours_display = toga.Box(style=Pack(direction=COLUMN))
        self.main_box.add(self.work_hours_display)

        self.logout_button = toga.Button("Log out", on_press=self.handle_logout, style=Pack(padding=10))
        self.main_box.add(self.logout_button)

        self.update_work_hours_display()

    def show_user_dashboard(self):
        self.main_box.clear()

        user_label = toga.Label(f"Welcome, {self.current_user}", style=Pack(padding=10))
        self.main_box.add(user_label)

        self.start_time_display = toga.Label("Start time: Not started", style=Pack(padding=10))
        self.main_box.add(self.start_time_display)

        self.timer_button = toga.Button("Start/Stop Timer", on_press=self.toggle_timer, style=Pack(padding=10))
        self.main_box.add(self.timer_button)

        self.timer_display = toga.Label("Total time: 00:00", style=Pack(padding=10))
        self.main_box.add(self.timer_display)

        self.logout_button = toga.Button("Log out", on_press=self.handle_logout, style=Pack(padding=10))
        self.main_box.add(self.logout_button)

    def handle_logout(self, widget):
        self.current_user = None
        self.main_box.clear()
        self.startup()

    def toggle_timer(self, widget):
        if not self.timer_running:
            self.start_time = datetime.now()
            self.start_time_display.text = f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            self.timer_button.label = "Stop Timer"
            self.timer_running = True
            self.update_timer_display()  # Start the timer update loop
        else:
            end_time = datetime.now()
            elapsed_time = end_time - self.start_time
            self.split_and_save_work_hours(elapsed_time)
            self.total_time += elapsed_time  # Add elapsed time to total time
            self.start_time = None
            self.timer_button.label = "Start Timer"
            self.timer_display.text = f"Total time: {self.format_timedelta(self.total_time)}"
            self.timer_running = False

    def update_timer_display(self):
        if self.timer_running:
            elapsed_time = datetime.now() - self.start_time
            self.timer_display.text = f"Total time: {self.format_timedelta(self.total_time + elapsed_time)}"
            threading.Timer(1, self.update_timer_display).start()  # Use threading.Timer for periodic updates

    def format_timedelta(self, td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"

    def split_and_save_work_hours(self, elapsed_time):
        all_work_hours = self.work_hours
        start_date = self.start_time.date()
        end_date = datetime.now().date()

        if start_date == end_date:
            self.update_user_hours(all_work_hours, self.current_user, start_date, elapsed_time.total_seconds() / 3600)
        else:
            midnight = datetime.combine(start_date + timedelta(days=1), datetime.min.time())
            first_part = midnight - self.start_time
            second_part = elapsed_time - first_part

            self.update_user_hours(all_work_hours, self.current_user, start_date, first_part.total_seconds() / 3600)
            self.update_user_hours(all_work_hours, self.current_user, end_date, second_part.total_seconds() / 3600)

        with open('work_hours.json', 'w') as f:
            json.dump(self.serialize_work_hours(all_work_hours), f)

    def serialize_work_hours(self, work_hours):
        serialized = {}
        for user, hours in work_hours.items():
            serialized[user] = {str(date): hour for date, hour in hours.items()}
        return serialized

    def update_user_hours(self, all_work_hours, user, date, hours):
        user_hours = all_work_hours.get(user, {})
        if not isinstance(user_hours, dict):
            user_hours = {}

        date_str = date.strftime('%Y-%m-%d')
        if date_str in user_hours:
            user_hours[date_str] += hours
        else:
            user_hours[date_str] = hours

        all_work_hours[user] = user_hours

    def load_work_hours(self):
        try:
            with open('work_hours.json', 'r') as f:
                all_work_hours = json.load(f)
            for user, hours in all_work_hours.items():
                all_work_hours[user] = {datetime.strptime(date, '%Y-%m-%d').date(): hour for date, hour in hours.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            all_work_hours = {}

        if self.current_user and self.current_user in all_work_hours:
            user_hours = all_work_hours.get(self.current_user, {})
            if isinstance(user_hours, dict):
                self.total_time = timedelta(hours=sum(user_hours.values()))
            else:
                self.total_time = timedelta()
        return all_work_hours

    def get_weekly_hours(self, user_hours):
        if isinstance(user_hours, dict):
            total_hours = sum(user_hours.values())
        else:
            total_hours = user_hours
        return total_hours

    def update_work_hours_display(self):
        all_work_hours = self.work_hours
        self.work_hours_display.clear()

        for user, hours in all_work_hours.items():
            user_hours_label = toga.Label(f"{user}: {self.get_weekly_hours(hours):.2f} hours", style=Pack(padding=10))
            self.work_hours_display.add(user_hours_label)

def main():
    return StempelUhr()

if __name__ == '__main__':
    main().main_loop()
