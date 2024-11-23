import flet as ft
import json
import os
import ipaddress
from pythonosc import udp_client

FILE_PATH = "data.json"

def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"IP": "", "PORT": ""}
    return {"IP": "", "PORT": ""}

def save_data(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

class InvalidPortError(Exception):
    pass

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError("Invalid IP address.")

def validate_port(port):
    try:
        port = int(port)
        if not (1 <= port <= 65535):
            raise InvalidPortError("Port must be between 1 and 65535.")
    except ValueError:
        raise InvalidPortError("Port must be a valid number.")

def main(page: ft.Page):
    page.title = "EOS GO"
    page.window.width = 300
    page.window.height = 440
    page.window.resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    config = load_data()
    IP = config.get("IP", "127.0.0.1")
    PORT = int(config.get("PORT", 8000))

    osc_client = udp_client.SimpleUDPClient(IP, PORT)

    def show_snack_bar(message, color):
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=3000,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def send_osc_message(e):
        osc_message = "/eos/key/go_0"
        osc_client.send_message(osc_message, [])

    def update_configuration(e):
        nonlocal osc_client
        new_ip = ip_field.value.strip()
        new_port = port_field.value.strip()

        try:
            validate_ip(new_ip)
            validate_port(new_port)
            osc_client = udp_client.SimpleUDPClient(new_ip, int(new_port))
            save_data({"IP": new_ip, "PORT": int(new_port)})
            #show_snack_bar("Configuration updated successfully.", ft.colors.GREEN)
            page.update()
        except ValueError as ve:
            show_snack_bar(str(ve), ft.colors.RED)
        except InvalidPortError as pe:
            show_snack_bar(str(pe), ft.colors.RED)

    base_color = ft.colors.BLUE
    label_style_definition = ft.TextStyle(color=base_color)

    ip_field = ft.TextField(
        label="IP",
        value=IP,
        width=200,
        border_color=base_color,
        label_style=label_style_definition,
        on_submit=update_configuration,
    )

    port_field = ft.TextField(
        label="Port",
        value=str(PORT),
        width=200,
        border_color=base_color,
        label_style=label_style_definition,
        on_submit=update_configuration,
    )

    go_button = ft.ElevatedButton(
        text="GO",
        on_click=send_osc_message,
        style=ft.ButtonStyle(
            bgcolor=base_color,
            color=ft.colors.WHITE,
            padding=20,
            text_style=ft.TextStyle(size=86),
            shape=ft.RoundedRectangleBorder(radius=20),
        ),
        width=200,
        height=200,
    )

    page.add(
        ft.Column(
            controls=[
                ip_field,
                port_field,
                go_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)