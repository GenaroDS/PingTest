# Set flags for ping_test

from os import path
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from subprocess import run, PIPE, CREATE_NO_WINDOW
from time import sleep
from threading import Thread
import chardet
from configparser import ConfigParser
from pystray import Menu, MenuItem, Icon
from PIL.Image import open as open_image
import re
import json
import winreg as reg
from os import path, getcwd 


settings_changed = True          
stop_ping_test = False

def open_settings_window():
    
    def set_value_in_file(key, value):
        config_file = "settings.json"
        config = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                try:
                    config = json.load(file)
                except json.JSONDecodeError:
                    pass  # If there's an error, just overwrite with new settings

        config[key] = value

        with open(config_file, "w") as file:
            json.dump(config, file)
    
    def create_or_open_key():
        path = r'Software\PingTester'  # Ruta fija para la clave del registro
        try:
            # Intenta abrir la clave si ya existe
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, path, 0, reg.KEY_WRITE)
        except FileNotFoundError:
            # Si la clave no existe, la crea
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, path)
        return registry_key

    # Función para obtener la configuración del Registro o usar el valor por defecto
    def get_reg_value(key, default):
        registry_path = r'Software\PingTester'  # Use a more unique path to avoid conflicts
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_READ) as registry_key:
                value, _ = reg.QueryValueEx(registry_key, key)
                return value
        except OSError as e:
            print(f"OSError while reading from registry: {e}")
            # Fallback to a local file if registry access fails
            return get_value_from_file(key, default)
        
    def get_value_from_file(key, default):
        config_file = "settings.json"  # Local configuration file
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                try:
                    config = json.load(file)
                    return config.get(key, default)
                except json.JSONDecodeError as e:
                    print(f"Error reading from config file: {e}")
        return default

    # Función para escribir la configuración en el Registro
    def set_reg_value(key, value):
        try:
            with create_or_open_key() as registry_key:
                reg.SetValueEx(registry_key, key, 0, reg.REG_SZ, json.dumps(value))
        except WindowsError:
            pass
    

    # Función que se llama cuando se presiona el botón de aplicar cambios
    def apply_changes():
        config_to_save = {}
        for key in entries:
            config_to_save[key] = entries[key].get()

        # Attempt to save to the registry, fallback to file if there's an error
        try:
            set_reg_value('Settings', config_to_save)
            print("Changes applied to registry")
        except OSError as e:
            print(f"Failed to write to registry: {e}, saving to file instead.")
            for key, value in config_to_save.items():
                set_value_in_file(key, value)
            print("Changes applied to file")

    # Inicializa CustomTkinter
    ctk.set_appearance_mode("Dark")
    
    # Crea la ventana principal
    root = ctk.CTk()
    root.title("Settings")

    entries = {}  # Diccionario para almacenar los widgets Entry
    default_config = {
        "ping_count": 10,
        "seconds_between_pings": 0.33,
        "max_response_time": 150,
        "server_to_ping": "google.com",
        "perfect_threshold": 9,
        "good_threshold": 18,
        "medium_threshold": 28
    }

    # Intenta obtener la configuración almacenada en el Registro, si no, usa la configuración por defecto
    try:
        stored_config_str = get_reg_value('Settings', '{}')
        stored_config = json.loads(stored_config_str) if stored_config_str else default_config
    except json.JSONDecodeError as e:
        print(f"Error al cargar la configuración del registro: {e}")
        stored_config = default_config


    # Crea y coloca los widgets Entry, inicializándolos con los valores del Registro o por defecto
    for i, (key, default) in enumerate(default_config.items()):
        label = ctk.CTkLabel(root, text=key.replace('_', ' ').capitalize() + ":")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        value = stored_config.get(key, default)
        entry = ctk.CTkEntry(root, textvariable=ctk.StringVar(value=str(value)))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[key] = entry

    # Añade el botón de aplicar cambios
    apply_button = ctk.CTkButton(root, text="Apply Changes", command=apply_changes)
    apply_button.grid(row=len(default_config), column=0, columnspan=2, pady=(7, 14))

    # Inicia el bucle de eventos de Tkinter
    root.resizable(False, False)
    root.mainloop()
    

if __name__ == "__main__":
    # Start the ping Thread
    open_settings_window()

    