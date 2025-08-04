import serial
import serial.tools.list_ports
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import webbrowser


ser = None
led_on = False
log_file = None

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def log_data(direction, message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    formatted = f"{timestamp} {direction}: {message}"
    log_textbox.insert(tk.END, formatted + "\n")
    log_textbox.see(tk.END)

    if log_file:
        log_file.write(formatted + "\n")

def connect():
    global ser, log_file
    port = port_combo.get()
    baud = int(baud_combo.get())
    try:
        ser = serial.Serial(port, baud, timeout=1)
        connect_btn.config(text="Connected", state="disabled")
        toggle_btn.config(state="normal")
        adc_label.config(text="ADC: ---")

        # Open log file
        filename = f"serial_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file = open(filename, "a")

        read_serial_thread()
        read_adc_thread()

        log_data("INFO", f"Connected to {port} at {baud} baud.")
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))

def toggle_led():
    global led_on
    if ser and ser.is_open:
        command = "LED_ON\n" if not led_on else "LED_OFF\n"
        ser.write(command.encode())
        log_data("TX", command.strip())
        led_on = not led_on
        toggle_btn.config(text="Turn LED OFF" if led_on else "Turn LED ON")

def read_adc():
    if ser and ser.is_open:
        try:
            ser.write("READ_ADC\n".encode())
            log_data("TX", "READ_ADC")
            time.sleep(0.2)
        except:
            pass

def read_serial_thread():
    def loop():
        while ser and ser.is_open:
            try:
                if ser.in_waiting:
                    data = ser.readline().decode(errors='ignore').strip()
                    if data:
                        log_data("RX", data)
                        if data.isdigit():
                            adc_label.config(text=f"ADC: {data}")
            except Exception as e:
                log_data("ERROR", str(e))
                break
    threading.Thread(target=loop, daemon=True).start()

def read_adc_thread():
    def loop():
        while ser and ser.is_open:
            read_adc()
            time.sleep(1)
    threading.Thread(target=loop, daemon=True).start()

def on_close():
    if ser and ser.is_open:
        ser.close()
    if log_file:
        log_file.close()
    root.destroy()

# GUI
root = tk.Tk()
root.title("ESP8266 Serial Controller v3")
root.protocol("WM_DELETE_WINDOW", on_close)

frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Port:").grid(row=0, column=0, sticky="e")
port_combo = ttk.Combobox(frame, values=list_serial_ports(), width=15)
port_combo.grid(row=0, column=1)
port_combo.set("Select")

ttk.Label(frame, text="Baud:").grid(row=1, column=0, sticky="e")
baud_combo = ttk.Combobox(frame, values=["9600", "115200"], width=15)
baud_combo.grid(row=1, column=1)
baud_combo.set("9600")

connect_btn = ttk.Button(frame, text="Connect", command=connect)
connect_btn.grid(row=2, column=0, columnspan=2, pady=10)

toggle_btn = ttk.Button(frame, text="Turn LED ON", command=toggle_led, state="disabled")
toggle_btn.grid(row=3, column=0, columnspan=2, pady=5)

adc_label = ttk.Label(frame, text="ADC: ---", font=("Arial", 12))
adc_label.grid(row=4, column=0, columnspan=2, pady=5)

ttk.Label(frame, text="Log:").grid(row=5, column=0, sticky="nw", pady=5)
log_textbox = scrolledtext.ScrolledText(frame, width=50, height=15, font=("Courier", 10))
log_textbox.grid(row=6, column=0, columnspan=2, pady=5)

def open_linkedin(event):
    webbrowser.open_new("https://www.linkedin.com/in/reponsheikh/")

link_label = tk.Label(frame, text="Visit my LinkedIn: reponsheikh", fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
link_label.grid(row=7, column=0, columnspan=2, pady=10)
link_label.bind("<Button-1>", open_linkedin)


root.mainloop()
