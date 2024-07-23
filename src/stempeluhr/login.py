import toga
from toga.style import Pack
from toga.style.pack import COLUMN

def login_screen(app):
    login_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
    username_input = toga.TextInput(placeholder='Username', style=Pack(padding=10))
    password_input = toga.PasswordInput(placeholder='Password', style=Pack(padding=10))
    login_button = toga.Button('Login', on_press=lambda widget: handle_login(widget, app, username_input, password_input), style=Pack(padding=10))
    message_label = toga.Label('If you are a user, your login-password: user-user\nIf you are an admin, your login-password: admin-admin', style=Pack(padding=10))

    login_box.add(username_input)
    login_box.add(password_input)
    login_box.add(login_button)
    login_box.add(message_label)

    return login_box

def handle_login(widget, app, username_input, password_input):
    username = username_input.value
    password = password_input.value

    if (username == 'user' and password == 'user') or (username == 'admin' and password == 'admin'):
        app.current_user = username
        if username == 'admin':
            app.show_admin_dashboard()
        else:
            app.show_user_dashboard()
    else:
        message_label = widget.parent.children[-1]
        message_label.text = 'Invalid login credentials. Please try again.'
