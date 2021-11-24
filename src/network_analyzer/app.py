import tkinter as tk
from tkinter import filedialog
from network_analyzer.analyzer import Analyzer

# Analyzer
csv_dir_path = None
default_jsonrpc = "https://tlbc.rpc.anyblock.tools"
default_relay_api_url = "http://localhost:5000/api/v1"

# App main window
root = tk.Tk()

root.title("Trustlines Network Analyzer")
root.geometry("500x250")

canvas_window = tk.Canvas(root, width=300, height=300)
canvas_window.pack()

jsonrpc = tk.StringVar(root, default_jsonrpc)
relay = tk.StringVar(root, default_relay_api_url)

label_jsonrpc = tk.Label(root, text="JSON RPC URL").place(x=30, y=50)
text_jsonrpc = tk.Entry(root, textvariable=jsonrpc, width=30).place(x=180, y=50)

label_relay = tk.Label(root, text="Relay API Server URL").place(x=30, y=90)
text_relay = tk.Entry(root, textvariable=relay, width=30).place(x=180, y=90)
label_chosen_path = tk.Label(root, text="")


def choose_folder():
    global csv_dir_path
    csv_dir_path = filedialog.askdirectory()
    label_chosen_path.config(text=csv_dir_path)


label_folder_csv = tk.Label(root, text="Save Files to").place(x=30, y=130)
button_folder_csv = tk.Button(root, text="Browse Folders", command=choose_folder).place(x=180, y=130)
label_chosen_path.place(x=180, y=170)


def analyze():
    analyzer = Analyzer(jsonrpc=jsonrpc.get(), relay_api_url=relay.get(), output_path=csv_dir_path)
    analyzer.analyze_bridge_transfers()
    analyzer.analyze_networks()
    analyzer.analyze_dead_identities()


button_analyze = tk.Button(text='Analyze', command=analyze, bg='green', fg='white')
canvas_window.create_window(170, 210, window=button_analyze)

root.mainloop()
