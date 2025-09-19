import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

csv_file = "appliances.csv"
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Appliance", "Wattage", "Hours", "Source"])
    df.to_csv(csv_file, index=False)

# ------------ Functions -----------------
def switch_frame(frame):
    for f in [home_frame, add_frame, vis_frame, sum_frame]:
        f.pack_forget()
    frame.pack(fill="both", expand=True)
    if frame == vis_frame:   # auto draw graphs on open
        draw_graphs()

def add_appliance():
    name = entry_name.get()
    wattage = entry_wattage.get()
    hours = entry_hours.get()
    source = source_var.get()

    if not (name and wattage and hours and source):
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    try:
        wattage = float(wattage)
        hours = float(hours)
    except ValueError:
        messagebox.showwarning("Input Error", "Wattage and Hours must be numbers.")
        return

    new_row = pd.DataFrame([[name, wattage, hours, source]],
                           columns=["Appliance", "Wattage", "Hours", "Source"])
    global df
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)

    entry_name.delete(0, tk.END)
    entry_wattage.delete(0, tk.END)
    entry_hours.delete(0, tk.END)
    source_var.set('')
    lbl_calc.config(text="")
    messagebox.showinfo("Success", f"{name} added!")
    update_summary_tab()
    draw_graphs()  # refresh graphs immediately

def update_calc_label(event=None):
    try:
        wattage = float(entry_wattage.get())
        hours = float(entry_hours.get())
        monthly_kwh = (wattage * hours * 30) / 1000
        lbl_calc.config(text=f"Monthly Consumption: {monthly_kwh:.2f} kWh/month")
    except:
        lbl_calc.config(text="")

def draw_graphs():
    # Clear frame_plot
    for widget in frame_plot.winfo_children():
        widget.destroy()
    if df.empty:
        tk.Label(frame_plot, text="No data yet. Add appliances to see graphs.",
                 bg="#E8F5E9").pack(pady=20)
        return

    df_grouped = df.copy()
    df_grouped["Monthly_kWh"] = (df_grouped["Wattage"] * df_grouped["Hours"] * 30) / 1000
    summary = df_grouped.groupby("Source")["Monthly_kWh"].sum()

    fig = plt.Figure(figsize=(8,4))
    ax = fig.add_subplot(111)

    gtype = graph_type_var.get()

    if gtype == "Bar":
        summary.plot(kind="bar", color=["#4CAF50", "#F44336"], ax=ax)
        ax.set_ylabel("kWh/month")
        ax.set_title("Energy by Source")
    elif gtype == "Line":
        summary.plot(kind="line", marker='o', color=["#4CAF50", "#F44336"], ax=ax)
        ax.set_ylabel("kWh/month")
        ax.set_title("Energy Trend by Source")
    elif gtype == "Pie":
        summary.plot(kind="pie", autopct="%1.1f%%", colors=["#4CAF50", "#F44336"], ax=ax)
        ax.set_ylabel("")
        ax.set_title("Energy Share")
    elif gtype == "Scatter":
        ax.scatter(df_grouped["Wattage"], df_grouped["Monthly_kWh"], color="#4CAF50")
        ax.set_xlabel("Wattage")
        ax.set_ylabel("Monthly kWh")
        ax.set_title("Scatter: Wattage vs Energy")

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def update_summary_tab():
    global df
    if df.empty:
        lbl_total.config(text="No data yet.")
        return
    df_grouped = df.copy()
    df_grouped["Monthly_kWh"] = (df_grouped["Wattage"] * df_grouped["Hours"] * 30) / 1000
    renewable = df_grouped[df_grouped["Source"] == "Renewable"]["Monthly_kWh"].sum()
    nonrenew = df_grouped[df_grouped["Source"] == "Non-Renewable"]["Monthly_kWh"].sum()
    total = df_grouped["Monthly_kWh"].sum()
    co2_est = nonrenew * 0.82
    summary_text = (
        f"🌱 Total Renewable: {renewable:.2f} kWh/month\n"
        f"🔥 Total Non-Renewable: {nonrenew:.2f} kWh/month\n"
        f"⚡ Grand Total: {total:.2f} kWh/month\n"
        f"🌍 Estimated CO₂: {co2_est:.2f} kg/month"
    )
    lbl_total.config(text=summary_text)

# ------------ GUI -----------------
root = tk.Tk()
root.title("EcoEnergy App")
root.geometry("1100x700")
root.configure(bg="#E8F5E9")  # light green background

# Top Navigation Bar
nav_bar = tk.Frame(root, bg="#A5D6A7", height=70)
nav_bar.pack(fill="x")

# Logo left
try:
    logo_img = Image.open("logo.png").resize((50, 50))
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(nav_bar, image=logo_photo, bg="#A5D6A7").pack(side="left", padx=10)
except:
    tk.Label(nav_bar, text="🌳", font=("Arial", 30), bg="#A5D6A7").pack(side="left", padx=10)

tk.Label(nav_bar, text="EcoEnergy", font=("Arial", 22, "bold"), bg="#A5D6A7", fg="white").pack(side="left")

# Nav Buttons
btn_style = {"bg": "#81C784", "activebackground": "#66BB6A",
             "font": ("Arial", 16, "bold"), "bd": 0, "width":12, "height":2}
tk.Button(nav_bar, text="Home", command=lambda: switch_frame(home_frame), **btn_style).pack(side="right", padx=5)
tk.Button(nav_bar, text="Summary", command=lambda: [switch_frame(sum_frame), update_summary_tab()], **btn_style).pack(side="right", padx=5)
tk.Button(nav_bar, text="Visualization", command=lambda: switch_frame(vis_frame), **btn_style).pack(side="right", padx=5)
tk.Button(nav_bar, text="Add Data", command=lambda: switch_frame(add_frame), **btn_style).pack(side="right", padx=5)

# -------- Frames --------
home_frame = tk.Frame(root, bg="#E8F5E9")
add_frame = tk.Frame(root, bg="#E8F5E9")
vis_frame = tk.Frame(root, bg="#E8F5E9")
sum_frame = tk.Frame(root, bg="#E8F5E9")

# Home Frame Content
tk.Label(home_frame, text="🌳🌸 Welcome to EcoEnergy App 🌸🌳",
         font=("Arial", 28, "bold"), bg="#E8F5E9", fg="#2E7D32").pack(pady=40)
tk.Label(home_frame, text="Monitor your energy usage, discover renewable potential, and reduce your carbon footprint.",
         font=("Arial", 16), bg="#E8F5E9", wraplength=800).pack()

# Add Frame Content
form_frame = tk.Frame(add_frame, bg="#E8F5E9")
form_frame.pack(pady=20)

tk.Label(form_frame, text="Appliance Name:", bg="#E8F5E9").grid(row=0, column=0, sticky="w", pady=5)
entry_name = tk.Entry(form_frame)
entry_name.grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="Wattage (W):", bg="#E8F5E9").grid(row=1, column=0, sticky="w", pady=5)
entry_wattage = tk.Entry(form_frame)
entry_wattage.grid(row=1, column=1, pady=5)
entry_wattage.bind("<KeyRelease>", update_calc_label)

tk.Label(form_frame, text="Hours per Day:", bg="#E8F5E9").grid(row=2, column=0, sticky="w", pady=5)
entry_hours = tk.Entry(form_frame)
entry_hours.grid(row=2, column=1, pady=5)
entry_hours.bind("<KeyRelease>", update_calc_label)

tk.Label(form_frame, text="Source:", bg="#E8F5E9").grid(row=3, column=0, sticky="w", pady=5)
source_var = tk.StringVar()
ttk.Combobox(form_frame, textvariable=source_var,
             values=["Renewable", "Non-Renewable"]).grid(row=3, column=1, pady=5)

lbl_calc = tk.Label(form_frame, text="", fg="blue", bg="#E8F5E9")
lbl_calc.grid(row=4, column=0, columnspan=2, pady=5)

tk.Button(form_frame, text="Add Appliance", command=add_appliance,
          bg="#4CAF50", fg="white", font=("Arial",14,"bold")).grid(row=5, column=0, columnspan=2, pady=15)

# Visualization Frame Content
vis_top = tk.Frame(vis_frame, bg="#E8F5E9")
vis_top.pack(fill="x", pady=10)

tk.Label(vis_top, text="Select Graph Type:", bg="#E8F5E9", font=("Arial",14)).pack(side="left", padx=10)
graph_type_var = tk.StringVar(value="Bar")
graph_types = ["Bar","Line","Pie","Scatter"]
graph_menu = ttk.Combobox(vis_top, textvariable=graph_type_var, values=graph_types, state="readonly")
graph_menu.pack(side="left", padx=10)
graph_menu.bind("<<ComboboxSelected>>", lambda e: draw_graphs())

frame_plot = tk.Frame(vis_frame, bg="#E8F5E9")
frame_plot.pack(fill=tk.BOTH, expand=True)

# Summary Frame Content
lbl_total = tk.Label(sum_frame, text="", justify="left", font=("Arial", 16), bg="#E8F5E9")
lbl_total.pack(pady=40)

# Show Home first
switch_frame(home_frame)

root.mainloop()
