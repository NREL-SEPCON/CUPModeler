import io
import re
import csv
import time
import json
import base64
import psutil
import webbrowser
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import find_peaks, savgol_filter
from scipy.io import loadmat

# Import custom modules
from CupV6 import CupV6
from DualV2 import DualV2
from EECCC_V8 import EECCC_V8
from ECPC_V1 import ECPC_V1
from MDMV2 import MDMV2


# Custom JSON encoder for numpy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.complex):
            return {'real': float(obj.real), 'imag': float(obj.imag)}
        # Handle matplotlib colors and other objects
        if hasattr(obj, '__dict__'):
            try:
                return str(obj)  # Convert to string representation
            except:
                return None
        # Handle tuples (convert to lists for JSON)
        if isinstance(obj, tuple):
            return list(obj)
        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        try:
            return super(NumpyEncoder, self).default(obj)
        except TypeError:
            # If all else fails, convert to string
            return str(obj)

class AppV1:
    def __init__(self, root):
        """Initialize the application and create all UI elements"""
        self.root = root
        self.root.title("CUP Modeler")
        style = ttk.Style()
        style.theme_use('alt')

        # Make window larger and resizable
        self.root.geometry("1500x600")
        self.root.minsize(1400, 600)

        # Configure main grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Left panel fixed
        self.root.grid_columnconfigure(1, weight=1)  # Right panel expandable

        self.setup_validation()

        # Create sections of the interface
        self.create_menu()
        self.create_left_panel()
        self.create_right_panel()

        self.setup_inline_editing()
        self.setup_keyboard_shortcuts()

    def create_menu(self):
        """Create the menu bar"""
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.clear_all_data)
        self.file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_state)
        self.file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.load_state)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Shortcuts", command=self.show_shortcuts_help)
        self.file_menu.add_command(label="About", command=self.show_about)

    def create_left_panel(self):
        """Create the left panel with column properties and compound list"""
        # Left panel frame
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure left frame grid
        self.left_frame.grid_rowconfigure(1, weight=0)  # Column properties
        self.left_frame.grid_rowconfigure(3, weight=1)  # Compound list (expandable)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.create_column_properties()
        self.create_compound_list()

    def create_right_panel(self):
        """Create the right panel with tabs"""
        # Right panel frame
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Configure right frame grid
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Create tab control
        self.tab_control = ttk.Notebook(self.right_frame)
        self.tab_control.grid(row=0, column=0, sticky="nsew")

        self.create_tabs()

    def create_column_properties(self):
        """Create the column properties section using grid"""
        # Header
        header_label = ttk.Label(self.left_frame, text="Column Properties",
                                 font=("Arial", 18, "bold"))
        header_label.grid(row=0, column=0, pady=(10, 0))

        # Main frame
        self.column_properties_frame = ttk.LabelFrame(self.left_frame, text="", padding=10)
        self.column_properties_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Configure internal grid
        for i in range(6):
            self.column_properties_frame.grid_columnconfigure(i, weight=1)

        # Row 1 - Basic parameters
        row = 0
        ttk.Label(self.column_properties_frame, text="Flow\nRate").grid(row=row, column=0, sticky="w", padx=(0, 0))
        self.flow_rate_entry = self.create_validated_entry(self.column_properties_frame,
                                                           validation_params={'allow_zero': False, 'min_val': 0},
                                                           width=5
                                                           )
        self.flow_rate_entry.grid(row=row, column=1, sticky="w", padx=(0, 0))
        self.flow_rate_entry.insert(0, "5")
        ttk.Label(self.column_properties_frame, text="mL/min").grid(row=row, column=2, sticky="w", padx=(0, 15))

        ttk.Label(self.column_properties_frame, text="Column\nVolume").grid(row=row, column=3, sticky="w", padx=(0, 5))
        self.column_volume_entry = self.create_validated_entry(self.column_properties_frame,
                                                               validation_params={'allow_zero': False, 'min_val': 0},
                                                               width=5
                                                               )
        self.column_volume_entry.grid(row=row, column=4, sticky="w", padx=(0, 5))
        self.column_volume_entry.insert(0, "81")
        ttk.Label(self.column_properties_frame, text="mL").grid(row=row, column=5, sticky="w")

        # Row 2 - Elution and Injection
        row = 1
        self.elution_label = ttk.Label(self.column_properties_frame, text="Elution\nDuration")
        self.elution_label.grid(row=row, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        self.elution_duration_entry = self.create_validated_entry(self.column_properties_frame,
                                                                  validation_params={'allow_zero': False, 'min_val': 0},
                                                                  width=5
                                                                  )
        self.elution_duration_entry.grid(row=row, column=1, sticky="w", padx=(0, 5), pady=(10, 0))
        self.elution_duration_entry.insert(0, "60")
        self.elution_unit_label = ttk.Label(self.column_properties_frame, text="min")
        self.elution_unit_label.grid(row=row, column=2, sticky="w", padx=(0, 15), pady=(10, 0))

        ttk.Label(self.column_properties_frame, text="Injection\nVolume").grid(row=row, column=3, sticky="w", padx=(0, 5), pady=(10, 0))
        self.injection_volume_entry = self.create_validated_entry(self.column_properties_frame,
                                                                  validation_params={'allow_zero': False, 'min_val': 0},
                                                                  width=5
                                                                  )
        self.injection_volume_entry.grid(row=row, column=4, sticky="w", padx=(0, 5), pady=(10, 0))
        self.injection_volume_entry.insert(0, "1")
        ttk.Label(self.column_properties_frame, text="mL").grid(row=row, column=5, sticky="w", pady=(10, 0))

        # Row 3 - Stationary Phase and Column Efficiency (main controls)
        row = 2
        ttk.Label(self.column_properties_frame, text="Stationary\nPhase\nRetention").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        self.stationary_phase_single_entry = self.create_validated_entry(self.column_properties_frame,
                                                                         validation_params={'min_val': 0, 'max_val': 1, 'allow_zero': False},
                                                                         width=5
                                                                         )
        self.stationary_phase_single_entry.grid(row=row, column=1, sticky="w", padx=(0, 5), pady=(10, 0))
        self.stationary_phase_single_entry.insert(0, "0.75")

        self.stationary_phase_var = tk.StringVar(value="Set Sf")
        self.stationary_phase_switch = ttk.Combobox(self.column_properties_frame,
                                                    textvariable=self.stationary_phase_var,
                                                    values=["Set Sf", "Coeff."],
                                                    width=5,
                                                    state="readonly")
        self.stationary_phase_switch.grid(row=row, column=2, sticky="w", padx=(0, 15), pady=(10, 0))
        self.stationary_phase_switch.bind("<<ComboboxSelected>>", self.toggle_stationary)

        ttk.Label(self.column_properties_frame, text="Column\nEfficiency").grid(row=row, column=3, sticky="w", padx=(0, 5), pady=(10, 0))
        self.column_efficiency_single_entry = self.create_validated_entry(self.column_properties_frame,
                                                                          validation_params={'allow_zero': False, 'integer_only': True, 'min_val': 0},
                                                                          width=5
                                                                          )
        self.column_efficiency_single_entry.grid(row=row, column=4, sticky="w", padx=(0, 5), pady=(10, 0))
        self.column_efficiency_single_entry.insert(0, "400")

        self.column_efficiency_var = tk.StringVar(value="Set N")
        self.column_efficiency_switch = ttk.Combobox(self.column_properties_frame,
                                                     textvariable=self.column_efficiency_var,
                                                     values=["Set N", "Coeff."],
                                                     width=5,
                                                     state="readonly")
        self.column_efficiency_switch.grid(row=row, column=5, sticky="w", pady=(10, 0))
        self.column_efficiency_switch.bind("<<ComboboxSelected>>", self.toggle_efficiency)

        # Row 4 - Coefficients (always present, initially hidden)
        row = 3
        self.sf_coeff_frame = ttk.Frame(self.column_properties_frame)
        self.sf_coeff_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(5, 0))

        # Sf coefficient A
        self.sf_coeff_a_label = ttk.Label(self.sf_coeff_frame, text="A:")
        self.sf_coeff_a_label.pack(side="left", padx=(0, 0), expand=True)
        self.sf_coefficient_a_entry = ttk.Entry(self.sf_coeff_frame, width=5)
        self.sf_coefficient_a_entry.pack(side="left", padx=(0, 10), expand=False)
        self.sf_coefficient_a_entry.insert(0, "0.982")

        # Sf coefficient B
        self.sf_coeff_b_label = ttk.Label(self.sf_coeff_frame, text="B:")
        self.sf_coeff_b_label.pack(side="left", padx=(10, 0), expand=False)
        self.sf_coefficient_b_entry = ttk.Entry(self.sf_coeff_frame, width=5)
        self.sf_coefficient_b_entry.pack(side="left", expand=True, padx=(0, 10))
        self.sf_coefficient_b_entry.insert(0, "-0.142")

        # N Coefficients

        self.n_coeff_frame = ttk.Frame(self.column_properties_frame)
        self.n_coeff_frame.grid(row=row, column=3, columnspan=3, sticky="ew", pady=(5, 0))

        # N coefficient A
        self.n_coeff_a_label = ttk.Label(self.n_coeff_frame, text="A:")
        self.n_coeff_a_label.pack(side="left", padx=(0, 5))
        self.n_coefficient_a_entry = ttk.Entry(self.n_coeff_frame, width=4)
        self.n_coefficient_a_entry.pack(side="left", padx=(0, 5))
        self.n_coefficient_a_entry.insert(0, "371.23")

        # N coefficient B
        self.n_coeff_b_label = ttk.Label(self.n_coeff_frame, text="B:")
        self.n_coeff_b_label.pack(side="left", padx=(0, 2))
        self.n_coefficient_b_entry = ttk.Entry(self.n_coeff_frame, width=4)
        self.n_coefficient_b_entry.pack(side="left", padx=(0, 5))
        self.n_coefficient_b_entry.insert(0, "-7.204")

        # N coefficient C
        self.n_coeff_c_label = ttk.Label(self.n_coeff_frame, text="C:")
        self.n_coeff_c_label.pack(side="left", padx=(0, 2))
        self.n_coefficient_c_entry = ttk.Entry(self.n_coeff_frame, width=4)
        self.n_coefficient_c_entry.pack(side="left")
        self.n_coefficient_c_entry.insert(0, "0.1480")

        # Row 6 - Dead Volume and Options
        row = 5
        ttk.Label(self.column_properties_frame, text="Column\nDead\nVolume").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        self.dead_volume_entry = self.create_validated_entry(self.column_properties_frame,
                                                             validation_params={'allow_zero': True, 'min_val': 0},
                                                             width=5
                                                             )
        self.dead_volume_entry.grid(row=row, column=1, sticky="w", padx=(0, 0), pady=(10, 0))
        self.dead_volume_entry.insert(0, "0")
        ttk.Label(self.column_properties_frame, text="mL").grid(row=row, column=2, sticky="w", padx=(0, 15), pady=(10, 0))

        self.include_injection_var = tk.BooleanVar(value=True)
        self.include_injection_checkbox = ttk.Checkbutton(
            self.column_properties_frame,
            text="Include\nInj. Vol.?",
            variable=self.include_injection_var
        )
        self.include_injection_checkbox.grid(row=row, column=2, padx=(0, 5), pady=(10, 0), columnspan=2)

        ttk.Label(self.column_properties_frame, text="X-Axis").grid(row=row, column=4, padx=(0, 0), pady=(10, 0))
        self.volume_time_var = tk.StringVar(value="Time")
        self.volume_time_switch = ttk.Combobox(self.column_properties_frame,
                                               textvariable=self.volume_time_var,
                                               values=["Time", "Volume"],
                                               width=5,
                                               state="readonly")
        self.volume_time_switch.grid(row=row, column=5, sticky="w", padx=(0, 0), pady=(10, 0))
        self.volume_time_switch.bind("<<ComboboxSelected>>", self.toggle_volume_time)

        # Initially hide coefficient fields
        self.hide_sf_coefficients()
        self.hide_n_coefficients()

        # Connect coefficient fields to recalculating single entries
        self.bind_update_events()

    def create_compound_list(self):
        """Create the compound list section using grid"""
        # Header
        header_label = ttk.Label(self.left_frame, text="Compound List",
                                 font=("Arial", 18, "bold"))
        header_label.grid(row=2, column=0, pady=(0, 0))

        # Main frame
        self.compound_list_frame = ttk.LabelFrame(self.left_frame, text="", padding=10)
        self.compound_list_frame.grid(row=3, column=0, sticky="nsew")

        # Configure internal grid
        self.compound_list_frame.grid_rowconfigure(0, weight=1)  # Table area
        self.compound_list_frame.grid_rowconfigure(1, weight=0)  # Button area
        self.compound_list_frame.grid_columnconfigure(0, weight=1)

        # Create frame for table and scrollbar
        table_frame = ttk.Frame(self.compound_list_frame)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Add Treeview (table) for compounds
        self.compound_columns = ("Compound", "KD", "Conc", "RetTime")
        self.compound_table = ttk.Treeview(table_frame, columns=self.compound_columns,
                                           show="headings", height=8)

        # Configure columns
        self.compound_table.heading("Compound", text="Compound")
        self.compound_table.heading("KD", text="KD")
        self.compound_table.heading("Conc", text="Conc. (g/L)")
        self.compound_table.heading("RetTime", text="Ret. Time (min)")

        self.compound_table.column("Compound", width=120)
        self.compound_table.column("KD", width=60)
        self.compound_table.column("Conc", width=80)
        self.compound_table.column("RetTime", width=100)

        self.compound_table.column("Compound", anchor='center')
        self.compound_table.column("KD", anchor='center')
        self.compound_table.column("Conc", anchor='center')
        self.compound_table.column("RetTime", anchor='center')

        # Place table and scrollbar
        self.compound_table.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        compound_scroll_y = ttk.Scrollbar(table_frame, orient="vertical",
                                          command=self.compound_table.yview)
        self.compound_table.configure(yscrollcommand=compound_scroll_y.set)
        compound_scroll_y.grid(row=0, column=1, sticky="ns")

        # Add initial data
        self.compound_table.insert("", "end", values=("Compound 1", "1", "1", "0"))
        self.compound_table.insert("", "end", values=("Compound 2", "2", "1", "0"))

        # Button frame
        button_frame = ttk.Frame(self.compound_list_frame)
        button_frame.grid(row=1, column=0, sticky="ew")

        # Buttons
        ttk.Button(button_frame, text="+", width=3, command=self.add_compound).grid(row=0, column=0, padx=(0, 0))
        ttk.Button(button_frame, text="-", width=3, command=self.remove_compound).grid(row=0, column=1, padx=(0, 40))
        ttk.Button(button_frame, text="Save", width=6, command=self.save_compounds).grid(row=0, column=2, padx=(0, 0))
        ttk.Button(button_frame, text="Open", width=6, command=self.open_compounds).grid(row=0, column=3, padx=(0, 30))

        ttk.Label(button_frame, text="Mobile Phase").grid(row=0, column=4, sticky="w", padx=(0, 0))
        self.mobile_phase_var = tk.StringVar(value="Lower")
        self.mobile_phase_switch = ttk.Combobox(button_frame,
                                                textvariable=self.mobile_phase_var,
                                                values=["Lower", "Upper"],
                                                width=5,
                                                state="readonly")
        self.mobile_phase_switch.grid(row=0, column=5, sticky="w", padx=(0, 0))

        # Bind double-click to edit table cells
        self.compound_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'compound'))

    def create_tabs(self):
        """Create all tabs"""
        self.create_classic_tab()
        self.create_extrusion_tab()
        self.create_dual_tab()
        self.create_multi_tab()
        self.create_pulse_tab()
        self.create_fit_tab()

    def create_classic_tab(self):
        """Create Classic Elution Tab"""
        self.classic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.classic_tab, text="Classic Elution")

        # Configure grid
        self.classic_tab.grid_rowconfigure(0, weight=1)  # Plot area
        self.classic_tab.grid_rowconfigure(1, weight=0)  # Controls
        self.classic_tab.grid_columnconfigure(0, weight=1)

        # Create figure for plotting
        self.classic_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0')
        self.classic_ax = self.classic_fig.add_subplot(111)
        self.classic_ax.set_xlabel('Elution Time (min)')
        self.classic_ax.set_ylabel('Concentration (g/L)')
        self.classic_ax.set_facecolor('#ffffff')
        self.classic_ax.grid(True, linestyle='--', alpha=0.7)

        # Add the figure to the canvas
        self.classic_canvas = FigureCanvasTkAgg(self.classic_fig, self.classic_tab)
        self.classic_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Control frame
        control_frame = ttk.Frame(self.classic_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Controls
        self.classic_sum_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Show Sum",
                        variable=self.classic_sum_var).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(control_frame, text="Plot", width=10,
                   command=self.plot_classic).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(control_frame, text="Export", width=10,
                   command=self.export_classic).grid(row=0, column=2, padx=(0, 10))

        self.classic_peaks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Peak Labels",
                        variable=self.classic_peaks_var).grid(row=0, column=3, padx=(0, 10))

        self.classic_grid_var = tk.BooleanVar(value=True)
        self.classic_grid_checkbox = ttk.Checkbutton(control_frame,
                                                     text="Show Grid",
                                                     variable=self.classic_grid_var,
                                                     ).grid(row=0, column=4)

    def create_extrusion_tab(self):
        """Create Elution-Extrusion Tab"""
        self.extrusion_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.extrusion_tab, text="Elution-Extrusion")

        # Configure grid
        self.extrusion_tab.grid_rowconfigure(0, weight=1)
        self.extrusion_tab.grid_rowconfigure(1, weight=0)
        self.extrusion_tab.grid_columnconfigure(0, weight=1)

        # Create figure for plotting
        self.extrusion_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0')
        self.extrusion_ax = self.extrusion_fig.add_subplot(111)
        self.extrusion_ax.set_xlabel('Elution Time (min)')
        self.extrusion_ax.set_ylabel('Concentration (g/L)')
        self.extrusion_ax.set_facecolor('#ffffff')
        self.extrusion_ax.grid(True, linestyle='--', alpha=0.7)

        self.extrusion_canvas = FigureCanvasTkAgg(self.extrusion_fig, self.extrusion_tab)
        self.extrusion_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Control frame
        control_frame = ttk.Frame(self.extrusion_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Controls
        col = 0
        self.ccc_cpc_var = tk.StringVar(value="CCC")
        ttk.Combobox(control_frame, textvariable=self.ccc_cpc_var,
                     values=["CCC", "CPC"], width=4, state="readonly").grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Label(control_frame, text="Extrusion Duration:").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.extrusion_duration_entry = self.create_validated_entry(control_frame,
                                                                    validation_params={'allow_zero': False, 'min_val': 0},
                                                                    width=8
                                                                    )
        self.extrusion_duration_entry.grid(row=0, column=col, padx=(0, 5))
        self.extrusion_duration_entry.insert(0, "5")
        col += 1
        self.extrusion_unit_label = ttk.Label(control_frame, text="min")
        self.extrusion_unit_label.grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.extrusion_sum_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Show Sum",
                        variable=self.extrusion_sum_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Plot", width=8,
                   command=self.plot_extrusion).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Export", width=8,
                   command=self.export_extrusion).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.extrusion_peaks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Peak Labels",
                        variable=self.extrusion_peaks_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.extrusion_lines_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Lines?",
                        variable=self.extrusion_lines_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.extrusion_lines_labels_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Labels?",
                        variable=self.extrusion_lines_labels_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.extrusion_grid_var = tk.BooleanVar(value=True)
        self.extrusion_grid_checkbox = ttk.Checkbutton(control_frame,
                                                       text="Show Grid",
                                                       variable=self.extrusion_grid_var,
                                                       ).grid(row=0, column=col)

    def create_dual_tab(self):
        """Create Dual Mode Tab"""
        self.dual_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dual_tab, text="Dual Mode")

        # Configure grid
        self.dual_tab.grid_rowconfigure(0, weight=1)
        self.dual_tab.grid_rowconfigure(1, weight=0)
        self.dual_tab.grid_columnconfigure(0, weight=1)

        # Create figure for plotting
        self.dual_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0')
        self.dual_ax = self.dual_fig.add_subplot(111)
        self.dual_ax.set_xlabel('Elution Time (min)')
        self.dual_ax.set_ylabel('Concentration (g/L)')
        self.dual_ax.set_facecolor('#ffffff')
        self.dual_ax.grid(True, linestyle='--', alpha=0.7)

        self.dual_canvas = FigureCanvasTkAgg(self.dual_fig, self.dual_tab)
        self.dual_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Control frame
        control_frame = ttk.Frame(self.dual_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Controls
        col = 0
        ttk.Label(control_frame, text="Dual Mode Duration:").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.dual_duration_entry = self.create_validated_entry(control_frame,
                                                               validation_params={'allow_zero': False, 'min_val': 0},
                                                               width=8
                                                               )
        self.dual_duration_entry.grid(row=0, column=col, padx=(0, 5))
        self.dual_duration_entry.insert(0, "10")
        col += 1
        self.dual_unit_label = ttk.Label(control_frame, text="min")
        self.dual_unit_label.grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.dual_sum_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Show Sum",
                        variable=self.dual_sum_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Plot", width=8,
                   command=self.plot_dual).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Export", width=8,
                   command=self.export_dual).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.dual_peaks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Peak Labels?",
                        variable=self.dual_peaks_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.dual_lines_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Lines?",
                        variable=self.dual_lines_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.dual_lines_labels_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Labels?",
                        variable=self.dual_lines_labels_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.dual_grid_var = tk.BooleanVar(value=True)
        self.dual_grid_checkbox = ttk.Checkbutton(control_frame,
                                                  text="Show Grid",
                                                  variable=self.dual_grid_var,
                                                  ).grid(row=0, column=col)

    def create_multi_tab(self):
        """Create Multiple Dual Mode Tab"""
        self.multi_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.multi_tab, text="Multiple Dual Mode")

        # Configure main grid
        self.multi_tab.grid_rowconfigure(0, weight=1)  # Main content area
        self.multi_tab.grid_rowconfigure(1, weight=0)  # Controls
        self.multi_tab.grid_columnconfigure(0, weight=1)

        # Main content frame with two plots and switch table
        content_frame = ttk.Frame(self.multi_tab)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure content frame grid
        content_frame.grid_rowconfigure(0, weight=1)  # Top plot
        content_frame.grid_rowconfigure(1, weight=1)  # Bottom area
        content_frame.grid_columnconfigure(0, weight=0)  # Switch times table
        content_frame.grid_columnconfigure(1, weight=1)  # Plots

        # Switch times table (left side)
        switch_frame = ttk.LabelFrame(content_frame, text="Switch Times", padding=10)
        switch_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        switch_frame.grid_rowconfigure(1, weight=1)
        switch_frame.grid_columnconfigure(0, weight=1)

        # Switch times table
        self.switch_times_columns = ("Iteration", "min")
        self.switch_times_table = ttk.Treeview(switch_frame, columns=self.switch_times_columns,
                                               show="headings", height=8)
        self.switch_times_table.heading("Iteration", text="Iteration")
        self.switch_times_table.heading("min", text="min")
        self.switch_times_table.column("Iteration", width=80)
        self.switch_times_table.column("min", width=60)
        self.switch_times_table.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Initial data for switching times
        self.switch_times_table.insert("", "end", values=("Cycle 1", "10"))
        self.switch_times_table.insert("", "end", values=("Cycle 2", "5"))

        self.switch_times_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'switch_time'))

        # Buttons for managing switching times
        switch_button_frame = ttk.Frame(switch_frame)
        switch_button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Configure grid to center the buttons
        switch_button_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        switch_button_frame.grid_columnconfigure(1, weight=0)  # + button
        switch_button_frame.grid_columnconfigure(2, weight=0)  # - button
        switch_button_frame.grid_columnconfigure(3, weight=1)  # Right spacer

        ttk.Button(switch_button_frame, text="+", width=3,
                   command=self.add_cycle).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(switch_button_frame, text="-", width=3,
                   command=self.remove_cycle).grid(row=0, column=2)

        # Plots area (right side)
        plots_frame = ttk.Frame(content_frame)
        plots_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        plots_frame.grid_rowconfigure(0, weight=1)  # Top plot
        plots_frame.grid_rowconfigure(1, weight=1)  # Bottom plot
        plots_frame.grid_columnconfigure(0, weight=1)

        # Top plot - concentration
        self.multi_fig = plt.Figure(figsize=(8, 3.2), dpi=100, facecolor='#f0f0f0')
        self.multi_ax = self.multi_fig.add_subplot(111)
        self.multi_ax.set_xlabel('Elution Time (min)')
        self.multi_ax.set_ylabel('Concentration (g/L)')
        self.multi_ax.set_facecolor('#ffffff')
        self.multi_ax.grid(True, linestyle='--', alpha=0.7)

        # Bottom plot - position contour
        self.multi_pos_fig = plt.Figure(figsize=(8, 3.2), dpi=100, facecolor='#f0f0f0')
        self.multi_pos_ax = self.multi_pos_fig.add_subplot(111)
        self.multi_pos_ax.set_xlabel('Elution Time (min)')
        self.multi_pos_ax.set_ylabel('Column Position')
        self.multi_pos_ax.set_facecolor('#ffffff')
        self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)

        # Set consistent layout with adjusted margins for smaller figures
        layout_params = {
            'left': 0.12,
            'right': 0.97,
            'top': 0.93,
            'bottom': 0.20
        }

        self.multi_fig.subplots_adjust(**layout_params)
        self.multi_pos_fig.subplots_adjust(**layout_params)

        self.multi_canvas = FigureCanvasTkAgg(self.multi_fig, plots_frame)
        self.multi_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.multi_pos_canvas = FigureCanvasTkAgg(self.multi_pos_fig, plots_frame)
        self.multi_pos_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        # Control frame for Multiple Dual Mode
        control_frame = ttk.Frame(self.multi_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Controls
        col = 0
        self.multi_sum_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Show Sum",
                        variable=self.multi_sum_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Plot", width=8,
                   command=self.plot_multi).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Export", width=8,
                   command=self.export_multi).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.multi_peaks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Peak Labels?",
                        variable=self.multi_peaks_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.multi_lines_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Lines?",
                        variable=self.multi_lines_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.multi_lines_labels_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Labels?",
                        variable=self.multi_lines_labels_var).grid(row=0, column=col, padx=(0, 10))
        col += 1

        self.multi_grid_var = tk.BooleanVar(value=True)
        self.multi_grid_checkbox = ttk.Checkbutton(control_frame,
                                                   text="Show Grid",
                                                   variable=self.multi_grid_var,
                                                   ).grid(row=0, column=col)

    def create_pulse_tab(self):
        """Create Pulse Test Tab"""
        self.pulse_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.pulse_tab, text="Pulse Test")

        # Configure main grid
        self.pulse_tab.grid_rowconfigure(0, weight=1)  # Main content
        self.pulse_tab.grid_rowconfigure(1, weight=0)  # Controls
        self.pulse_tab.grid_columnconfigure(0, weight=1)

        # Main content frame
        content_frame = ttk.Frame(self.pulse_tab)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)  # Plot area
        content_frame.grid_columnconfigure(1, weight=0)  # Right panel

        # Plot area
        plot_frame = ttk.Frame(content_frame)
        plot_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.pulse_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.pulse_ax = self.pulse_fig.add_subplot(111)
        self.pulse_ax.set_xlabel('Elution Time')
        self.pulse_ax.set_ylabel('Concentration')
        self.pulse_ax.grid(True, linestyle='--', alpha=0.7)

        self.pulse_canvas = FigureCanvasTkAgg(self.pulse_fig, plot_frame)
        self.pulse_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Right panel for pulse test list and regressions
        right_panel = ttk.Frame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(1, weight=1)  # Table area
        right_panel.grid_columnconfigure(0, weight=1)

        # Pulse test list header
        ttk.Label(right_panel, text="Pulse Test List",
                  font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 10))

        # Pulse test table frame
        table_frame = ttk.Frame(right_panel)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Create table for N values
        self.pulse_columns = ("Flow Rate", "Sf", "N", "Del?")
        self.pulse_table = ttk.Treeview(table_frame, columns=self.pulse_columns,
                                        show="headings", height=8)

        for col in self.pulse_columns:
            self.pulse_table.heading(col, text=col)
            self.pulse_table.column(col, width=70)

        self.pulse_table.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Pulse list table save/open button frame
        pulse_button_frame = ttk.Frame(right_panel)
        pulse_button_frame.grid(row=2, column=0, sticky="s", pady=(10, 0))
        pulse_button_frame.grid_rowconfigure(0, weight=1)
        pulse_button_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(pulse_button_frame, text="Add N", width=6,
                   command=self.add_n_value).pack(side="left", padx=(10, 10))

        ttk.Button(pulse_button_frame, text="Save", width=6,
                   command=self.save_pulse_list).pack(side="right", padx=(10, 10))

        ttk.Button(pulse_button_frame, text="Open", width=6,
                   command=self.open_pulse_list).pack(side="right", padx=(10, 10))

        # Regression section
        regression_frame = ttk.LabelFrame(right_panel, text="Regressions", padding=10)
        regression_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        # N equation
        ttk.Label(regression_frame, text="N = A + BF + CF²",
                  font=("Arial", 14)).grid(row=0, column=0, columnspan=2, sticky="w")

        self.use_n_button = ttk.Button(regression_frame, text="Use Values",
                                       command=self.use_n_values, state="disabled")
        self.use_n_button.grid(row=0, column=2, padx=(10, 0))

        # N coefficients
        coeff_frame = ttk.Frame(regression_frame)
        coeff_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))

        self.label_na = ttk.Label(coeff_frame, text="A: ")
        self.label_na.grid(row=0, column=0)
        self.label_nb = ttk.Label(coeff_frame, text="B: ")
        self.label_nb.grid(row=0, column=1, padx=(10, 0))
        self.label_nc = ttk.Label(coeff_frame, text="C: ")
        self.label_nc.grid(row=0, column=2, padx=(10, 0))

        # Sf equation
        ttk.Label(regression_frame, text="Sf = A + BF",
                  font=("Arial", 14)).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.use_sf_button = ttk.Button(regression_frame, text="Use Values",
                                        command=self.use_sf_values, state="disabled")
        self.use_sf_button.grid(row=2, column=2, padx=(10, 0), pady=(10, 0))

        # Sf coefficients
        sf_coeff_frame = ttk.Frame(regression_frame)
        sf_coeff_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(5, 0))

        self.label_sf_a = ttk.Label(sf_coeff_frame, text="A: ")
        self.label_sf_a.grid(row=0, column=0)
        self.label_sf_b = ttk.Label(sf_coeff_frame, text="B: ")
        self.label_sf_b.grid(row=0, column=1, padx=(10, 0))

        # Controls
        control_frame = ttk.Frame(self.pulse_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        col = 0
        ttk.Button(control_frame, text="Import",
                   width=7,
                   command=lambda: self.import_trace('pulse')).grid(row=0, column=col, padx=(0, 60))
        col += 1

        ttk.Label(control_frame, text="Span").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.pulse_span_var = tk.IntVar(value=40)
        ttk.Entry(control_frame, textvariable=self.pulse_span_var, width=4).grid(row=0, column=col, padx=(0, 20))
        col += 1

        ttk.Label(control_frame, text="Prominence").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.pulse_prominence_var = tk.DoubleVar(value=5)
        ttk.Entry(control_frame, textvariable=self.pulse_prominence_var, width=4).grid(row=0, column=col, padx=(0, 20))
        col += 1

        ttk.Label(control_frame, text="Baseline").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.pulse_baseline_var = tk.DoubleVar(value=5)
        ttk.Entry(control_frame, textvariable=self.pulse_baseline_var, width=4).grid(row=0, column=col, padx=(0, 60))
        col += 1

        ttk.Button(control_frame, text="Find Peak",
                   command=self.find_pulse_peaks).grid(row=0, column=col, padx=(0, 10))

        # Storage for pulse data
        self.pulse_data = None

    def create_fit_tab(self):
        """Create Trace Fitting Tab"""
        self.fit_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.fit_tab, text="Trace Fitting")

        # Configure grid
        self.fit_tab.grid_rowconfigure(0, weight=1)
        self.fit_tab.grid_rowconfigure(1, weight=0)
        self.fit_tab.grid_columnconfigure(0, weight=1)

        # Create plot area
        self.fit_fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.fit_ax = self.fit_fig.add_subplot(111)
        self.fit_ax.set_xlabel('Elution Time')
        self.fit_ax.set_ylabel('Concentration')
        self.fit_ax.grid(True, linestyle='--', alpha=0.7)

        self.fit_canvas = FigureCanvasTkAgg(self.fit_fig, self.fit_tab)
        self.fit_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Controls
        control_frame = ttk.Frame(self.fit_tab)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        col = 0
        ttk.Button(control_frame, text="Import",
                   width=7,
                   command=lambda: self.import_trace('fit')).grid(row=0, column=col, padx=(0, 60))
        col += 1

        ttk.Label(control_frame, text="Span").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.fit_span_var = tk.IntVar(value=20)
        ttk.Entry(control_frame, textvariable=self.fit_span_var, width=4).grid(row=0, column=col, padx=(0, 20))
        col += 1

        ttk.Label(control_frame, text="Prominence").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.fit_prominence_var = tk.DoubleVar(value=5)
        ttk.Entry(control_frame, textvariable=self.fit_prominence_var, width=4).grid(row=0, column=col, padx=(0, 20))
        col += 1

        ttk.Label(control_frame, text="Threshold").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.fit_threshold_var = tk.DoubleVar(value=5)
        ttk.Entry(control_frame, textvariable=self.fit_threshold_var, width=4).grid(row=0, column=col, padx=(0, 60))
        col += 1

        ttk.Button(control_frame, text="Find Peaks",
                   command=self.find_fit_peaks).grid(row=0, column=col, padx=(0, 10))
        col += 1

        ttk.Button(control_frame, text="Send KDs",
                   command=self.update_compound_list_with_fits).grid(row=0, column=col, padx=(0, 40))
        col += 1

        self.overlay_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Overlay on Models?",
                        variable=self.overlay_var).grid(row=0, column=col)

        # Storage for fit data
        self.fit_data = None

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # Add this to your __init__ method

        # File operations
        self.root.bind("<Control-n>", lambda e: self.clear_all_data())           # Ctrl+N: New/Clear
        self.root.bind("<Control-s>", lambda e: self.save_state())               # Ctrl+S: Save
        self.root.bind("<Control-o>", lambda e: self.load_state())               # Ctrl+O: Open/Load

        # Simulation shortcuts
        self.root.bind("<Control-r>", lambda e: self.run_current_simulation())  # Ctrl+R: Run current simulation
        self.root.bind("<F9>", lambda e: self.refresh_all_plots())            # F9: Run all simulations

        # Tab navigation
        self.root.bind("<Control-Key-1>", lambda e: self.switch_to_tab(0) or "break")          # Ctrl+1: Classic
        self.root.bind("<Control-Key-2>", lambda e: self.switch_to_tab(1) or "break")          # Ctrl+2: Extrusion
        self.root.bind("<Control-Key-3>", lambda e: self.switch_to_tab(2) or "break")          # Ctrl+3: Dual Mode
        self.root.bind("<Control-Key-4>", lambda e: self.switch_to_tab(3) or "break")          # Ctrl+4: Multiple Dual
        self.root.bind("<Control-Key-5>", lambda e: self.switch_to_tab(4) or "break")          # Ctrl+4: Pulse Test
        self.root.bind("<Control-Key-6>", lambda e: self.switch_to_tab(5) or "break")          # Ctrl+4: Trace Fitting

        # Data entry shortcuts
        self.root.bind("<Control-plus>", lambda e: self.add_compound())         # Ctrl++: Add compound
        self.root.bind("<Control-minus>", lambda e: self.remove_compound())     # Ctrl+-: Remove compound

        self.root.bind("<Control-t>", lambda e: self.toggle_volume_time())  # Ctrl+T to toggle units

    # ===== Interface Methods =====
    def toggle_stationary(self, event=None):
        """Toggle between direct Sf setting and coefficient-based calculation"""
        if self.stationary_phase_var.get() == "Set Sf":
            self.hide_sf_coefficients()
            self.stationary_phase_single_entry.config(state="normal")
        elif self.stationary_phase_var.get() == "Coeff.":
            self.show_sf_coefficients()
            self.stationary_phase_single_entry.config(state="disabled")

    def toggle_efficiency(self, event=None):
        """Toggle between direct N setting and coefficient-based calculation"""
        if self.column_efficiency_var.get() == "Set N":
            self.hide_n_coefficients()
            self.column_efficiency_single_entry.config(state="normal")
        elif self.column_efficiency_var.get() == "Coeff.":
            self.show_n_coefficients()
            self.column_efficiency_single_entry.config(state="disabled")

    def update_sf_from_coefficients(self):
        """Calculate and update Sf value from coefficients"""
        if self.stationary_phase_var.get() != "Coeff.":
            return

        try:
            flow_rate = float(self.flow_rate_entry.get())
            a = float(self.sf_coefficient_a_entry.get())
            b = float(self.sf_coefficient_b_entry.get())

            sf = a + b * flow_rate
            sf = max(0.1, min(0.9, sf))  # Keep within reasonable bounds

            # Temporarily enable the entry to update it
            self.stationary_phase_single_entry.config(state="normal")
            self.stationary_phase_single_entry.delete(0, tk.END)
            self.stationary_phase_single_entry.insert(0, f"{sf:.4f}")
            self.stationary_phase_single_entry.config(state="disabled")

        except ValueError:
            # If there's an error, just disable the field
            self.stationary_phase_single_entry.config(state="disabled")

    def update_n_from_coefficients(self):
        """Calculate and update N value from coefficients"""
        if self.column_efficiency_var.get() != "Coeff.":
            return

        try:
            flow_rate = float(self.flow_rate_entry.get())
            a = float(self.n_coefficient_a_entry.get())
            b = float(self.n_coefficient_b_entry.get())
            c = float(self.n_coefficient_c_entry.get())

            n = a + b * flow_rate + c * flow_rate * flow_rate
            n = max(50, int(n))  # Keep reasonably high

            # Temporarily enable the entry to update it
            self.column_efficiency_single_entry.config(state="normal")
            self.column_efficiency_single_entry.delete(0, tk.END)
            self.column_efficiency_single_entry.insert(0, f"{n:.0f}")
            self.column_efficiency_single_entry.config(state="disabled")

        except ValueError:
            # If there's an error, just disable the field
            self.column_efficiency_single_entry.config(state="disabled")

    def on_flow_rate_change(self, event=None):
        """Called when flow rate changes to update calculated values"""
        # Update Sf if in coefficient mode
        if self.stationary_phase_var.get() == "Coeff.":
            self.update_sf_from_coefficients()

        # Update N if in coefficient mode
        if self.column_efficiency_var.get() == "Coeff.":
            self.update_n_from_coefficients()

    def on_sf_coefficient_change(self, event=None):
        """Called when Sf coefficients change"""
        if self.stationary_phase_var.get() == "Coeff.":
            self.update_sf_from_coefficients()

    def on_n_coefficient_change(self, event=None):
        """Called when N coefficients change"""
        if self.column_efficiency_var.get() == "Coeff.":
            self.update_n_from_coefficients()

    def bind_update_events(self):
        """Bind events to update calculated values when inputs change"""
        # Bind flow rate changes
        self.flow_rate_entry.bind('<KeyRelease>', self.on_flow_rate_change)
        self.flow_rate_entry.bind('<FocusOut>', self.on_flow_rate_change)

        # Bind Sf coefficient changes
        self.sf_coefficient_a_entry.bind('<KeyRelease>', self.on_sf_coefficient_change)
        self.sf_coefficient_a_entry.bind('<FocusOut>', self.on_sf_coefficient_change)
        self.sf_coefficient_b_entry.bind('<KeyRelease>', self.on_sf_coefficient_change)
        self.sf_coefficient_b_entry.bind('<FocusOut>', self.on_sf_coefficient_change)

        # Bind N coefficient changes
        self.n_coefficient_a_entry.bind('<KeyRelease>', self.on_n_coefficient_change)
        self.n_coefficient_a_entry.bind('<FocusOut>', self.on_n_coefficient_change)
        self.n_coefficient_b_entry.bind('<KeyRelease>', self.on_n_coefficient_change)
        self.n_coefficient_b_entry.bind('<FocusOut>', self.on_n_coefficient_change)
        self.n_coefficient_c_entry.bind('<KeyRelease>', self.on_n_coefficient_change)
        self.n_coefficient_c_entry.bind('<FocusOut>', self.on_n_coefficient_change)

    def toggle_volume_time(self, event=None):
        """Toggle between volume and time display with comprehensive auto-conversion"""

        # Get flow rate for conversions
        try:
            flow_rate = float(self.flow_rate_entry.get())
            if flow_rate <= 0:
                messagebox.showwarning("Invalid Flow Rate", "Please enter a valid flow rate before toggling units.")
                return
        except ValueError:
            messagebox.showwarning("Invalid Flow Rate", "Please enter a valid flow rate before toggling units.")
            return

        # Determine current mode from the UI label (more reliable than combobox)
        current_label = self.elution_label.cget('text')
        was_volume_mode = "Volume" in current_label

        print("=== TOGGLE DEBUG ===")
        print(f"Current label: {current_label}")
        print(f"Was volume mode: {was_volume_mode}")

        # Toggle to the opposite mode
        if was_volume_mode:
            new_mode = "Time"
            will_be_volume_mode = False
        else:
            new_mode = "Volume"
            will_be_volume_mode = True

        print(f"Toggling to: {new_mode}")
        print(f"Will be volume mode: {will_be_volume_mode}")

        # Update the combobox to reflect the new mode
        self.volume_time_switch.set(new_mode)
        self.volume_time_var.set(new_mode)

        # Now perform the conversion since we know the mode changed
        print(f"Converting from {'Volume' if was_volume_mode else 'Time'} to {'Volume' if will_be_volume_mode else 'Time'}")

        # Perform the conversion
        self.convert_all_values(was_volume_mode, will_be_volume_mode, flow_rate)

        # Update UI labels AFTER conversion
        self.update_ui_labels()

        # Update all plots
        self.refresh_all_plots()

        # Show success notification
        direction = "Volume → Time" if was_volume_mode and not will_be_volume_mode else "Time → Volume"
        self.show_notification(f"Converted all values: {direction}", duration=2000, notif_type="info")

        print("=== CONVERSION COMPLETE ===")

    def update_ui_labels(self):
        """Update UI labels based on current volume/time mode"""
        is_volume_mode = self.volume_time_var.get() == "Volume"

        # Update column properties labels
        self.elution_label.config(text="Elution\nVolume" if is_volume_mode else "Elution\nDuration")
        self.elution_unit_label.config(text="mL" if is_volume_mode else "min")

        # Update compound table header
        ret_column_name = "Ret. Volume (mL)" if is_volume_mode else "Ret. Time (min)"
        self.compound_table.heading("RetTime", text=ret_column_name)

        # Update other tabs' labels
        if hasattr(self, 'extrusion_unit_label'):
            self.extrusion_unit_label.config(text="mL" if is_volume_mode else "min")

        if hasattr(self, 'dual_unit_label'):
            self.dual_unit_label.config(text="mL" if is_volume_mode else "min")

        # Update switch times table heading
        if hasattr(self, 'switch_times_table'):
            self.switch_times_table.heading("min", text="mL" if is_volume_mode else "min")

        # Update plot axes labels
        x_label = "Elution Volume (mL)" if is_volume_mode else "Elution Time (min)"

        # Update all plot axes
        plot_axes = [
            self.classic_ax, self.extrusion_ax, self.dual_ax,
            self.multi_ax, self.multi_pos_ax
        ]

        for ax in plot_axes:
            if hasattr(ax, 'set_xlabel'):
                ax.set_xlabel(x_label)
                if hasattr(ax, 'figure') and hasattr(ax.figure, 'canvas'):
                    ax.figure.canvas.draw_idle()

    def hide_sf_coefficients(self):
        """Hide Sf coefficient fields"""
        self.sf_coeff_frame.grid_remove()

    def show_sf_coefficients(self):
        """Show Sf coefficient fields"""
        self.sf_coeff_frame.grid()

    def hide_n_coefficients(self):
        """Hide N coefficient fields"""
        self.n_coeff_frame.grid_remove()

    def show_n_coefficients(self):
        """Show N coefficient fields"""
        self.n_coeff_frame.grid()

    def convert_duration_fields(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert elution, extrusion, and dual mode durations"""

        print("=== CONVERTING DURATION FIELDS ===")
        print(f"was_volume_mode: {was_volume_mode}, is_volume_mode: {is_volume_mode}")

        # Convert elution duration
        try:
            current_elution = float(self.elution_duration_entry.get())
            print(f"Current elution: {current_elution}")

            if was_volume_mode and not is_volume_mode:  # Volume to Time
                new_elution = current_elution / flow_rate
                print(f"Volume → Time: {current_elution} mL ÷ {flow_rate} = {new_elution} min")
            else:  # Time to Volume
                new_elution = current_elution * flow_rate
                print(f"Time → Volume: {current_elution} min × {flow_rate} = {new_elution} mL")

            self.elution_duration_entry.delete(0, tk.END)
            self.elution_duration_entry.insert(0, f"{new_elution:.2f}")
            print(f"✅ Elution updated: {current_elution:.2f} → {new_elution:.2f}")

        except ValueError as e:
            print(f"❌ Failed to convert elution: {e}")

        # Convert extrusion duration (if it exists)
        if hasattr(self, 'extrusion_duration_entry'):
            try:
                current_extrusion = float(self.extrusion_duration_entry.get())
                if was_volume_mode and not is_volume_mode:  # Volume to Time
                    new_extrusion = current_extrusion / flow_rate
                else:  # Time to Volume
                    new_extrusion = current_extrusion * flow_rate

                self.extrusion_duration_entry.delete(0, tk.END)
                self.extrusion_duration_entry.insert(0, f"{new_extrusion:.2f}")
                print(f"✅ Extrusion updated: {current_extrusion:.2f} → {new_extrusion:.2f}")
            except ValueError as e:
                print(f"❌ Failed to convert extrusion: {e}")
        else:
            print("ℹ️ No extrusion_duration_entry found")

        # Convert dual mode duration (if it exists)
        if hasattr(self, 'dual_duration_entry'):
            try:
                current_dual = float(self.dual_duration_entry.get())
                if was_volume_mode and not is_volume_mode:  # Volume to Time
                    new_dual = current_dual / flow_rate
                else:  # Time to Volume
                    new_dual = current_dual * flow_rate

                self.dual_duration_entry.delete(0, tk.END)
                self.dual_duration_entry.insert(0, f"{new_dual:.2f}")
                print(f"✅ Dual mode updated: {current_dual:.2f} → {new_dual:.2f}")
            except ValueError as e:
                print(f"❌ Failed to convert dual mode: {e}")
        else:
            print("ℹ️ No dual_duration_entry found")

    def convert_all_values(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert all time/volume values in the application"""

        print("\n=== CONVERTING ALL VALUES ===")
        print(f"Direction: {'Volume → Time' if was_volume_mode else 'Time → Volume'}")
        print(f"Flow rate: {flow_rate}")

        # Convert elution duration/volume
        self.convert_field(
            self.elution_duration_entry,
            "Elution",
            was_volume_mode,
            is_volume_mode,
            flow_rate
        )

        # Convert extrusion duration/volume (if exists)
        if hasattr(self, 'extrusion_duration_entry'):
            self.convert_field(
                self.extrusion_duration_entry,
                "Extrusion",
                was_volume_mode,
                is_volume_mode,
                flow_rate
            )

        # Convert dual mode duration/volume (if exists)
        if hasattr(self, 'dual_duration_entry'):
            self.convert_field(
                self.dual_duration_entry,
                "Dual Mode",
                was_volume_mode,
                is_volume_mode,
                flow_rate
            )

        # Convert compound retention times
        self.convert_compound_retention_times(was_volume_mode, is_volume_mode, flow_rate)

        # Convert switch times
        self.convert_switch_times(was_volume_mode, is_volume_mode, flow_rate)

    def convert_field(self, entry_widget, field_name, was_volume_mode, is_volume_mode, flow_rate):
        """Convert a single entry field value"""
        try:
            current_value = float(entry_widget.get())

            if was_volume_mode and not is_volume_mode:  # Volume to Time
                new_value = current_value / flow_rate
                print(f"{field_name}: {current_value:.2f} mL ÷ {flow_rate} = {new_value:.2f} min")
            else:  # Time to Volume
                new_value = current_value * flow_rate
                print(f"{field_name}: {current_value:.2f} min × {flow_rate} = {new_value:.2f} mL")

            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f"{new_value:.2f}")
            print(f"✅ {field_name} updated: {current_value:.2f} → {new_value:.2f}")

        except ValueError as e:
            print(f"❌ Failed to convert {field_name}: {e}")

    def convert_compound_retention_times(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert retention times in the compound table"""

        print("\n--- Converting Compound Retention Times ---")
        for item in self.compound_table.get_children():
            current_values = list(self.compound_table.item(item, 'values'))
            try:
                current_retention = float(current_values[3])  # Retention time is column 3

                if was_volume_mode and not is_volume_mode:  # Volume to Time
                    new_retention = current_retention / flow_rate
                else:  # Time to Volume
                    new_retention = current_retention * flow_rate

                current_values[3] = f"{new_retention:.2f}"
                self.compound_table.item(item, values=current_values)
                print(f"✅ {current_values[0]}: {current_retention:.2f} → {new_retention:.2f}")

            except (ValueError, IndexError) as e:
                print(f"❌ Failed to convert compound {current_values[0] if current_values else 'unknown'}: {e}")

    def convert_switch_times(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert switch times in the multiple dual mode table"""

        if not hasattr(self, 'switch_times_table'):
            print("ℹ️ No switch times table found")
            return

        print("\n--- Converting Switch Times ---")
        for item in self.switch_times_table.get_children():
            current_values = list(self.switch_times_table.item(item, 'values'))
            try:
                current_value = float(current_values[1])  # Duration is column 1

                if was_volume_mode and not is_volume_mode:  # Volume to Time
                    new_value = current_value / flow_rate
                else:  # Time to Volume
                    new_value = current_value * flow_rate

                current_values[1] = f"{new_value:.2f}"
                self.switch_times_table.item(item, values=current_values)
                print(f"✅ {current_values[0]}: {current_value:.2f} → {new_value:.2f}")

            except (ValueError, IndexError) as e:
                print(f"❌ Failed to convert switch time {current_values[0] if current_values else 'unknown'}: {e}")

    def perform_conversion_after_ui_update(self, was_volume_mode, flow_rate, original_elution):
        """Perform the actual conversion after UI has updated"""
        
        # Get NEW state after UI update
        new_mode = self.volume_time_var.get()
        is_volume_mode = (new_mode == "Volume")
        
        print(f"New mode: {new_mode}")
        print(f"Is volume mode: {is_volume_mode}")
        print(f"Mode actually changed: {was_volume_mode != is_volume_mode}")
        
        # Only convert if mode actually changed
        if was_volume_mode == is_volume_mode:
            print("Mode didn't change - no conversion needed")
            return
        
        print(f"Converting from {'Volume' if was_volume_mode else 'Time'} to {'Volume' if is_volume_mode else 'Time'}")
        
        # Update UI labels first
        self.update_ui_labels()
        
        # Convert all time/volume fields
        self.convert_duration_fields(was_volume_mode, is_volume_mode, flow_rate)
        self.convert_compound_retention_times(was_volume_mode, is_volume_mode, flow_rate)
        self.convert_switch_times(was_volume_mode, is_volume_mode, flow_rate)
        
        # Update all plots that might be affected
        self.refresh_all_plots()
        
        # Show conversion notification
        direction = "Volume → Time" if was_volume_mode and not is_volume_mode else "Time → Volume"
        self.show_notification(f"Converted all values: {direction}", duration=2000, notif_type="info")
        
        print(f"=== CONVERSION COMPLETE ===")

    def validate_conversions(self):
        """Debug method to validate that conversions are working correctly"""
        try:
            flow_rate = float(self.flow_rate_entry.get())
            print(f"\n=== Conversion Validation (Flow Rate: {flow_rate} mL/min) ===")

            # Check if time * flow_rate = volume for key fields
            elution_value = float(self.elution_duration_entry.get())
            is_volume = (self.volume_time_var.get() == "Volume")

            if is_volume:
                expected_time = elution_value / flow_rate
                print(f"Elution Volume: {elution_value} mL → Expected Time: {expected_time:.2f} min")
            else:
                expected_volume = elution_value * flow_rate
                print(f"Elution Time: {elution_value} min → Expected Volume: {expected_volume:.2f} mL")

            print("=== End Validation ===\n")

        except ValueError:
            print("Cannot validate conversions - invalid flow rate")

    def switch_to_tab(self, tab_index):
        """Switch to specified tab by index"""
        print(f"🔍 switch_to_tab called with index: {tab_index}")
        
        try:
            # Get all tabs - these are the actual widget references
            tabs = self.tab_control.tabs()
            print(f"🔍 Available tabs: {len(tabs)} tabs")
            print(f"🔍 Tab widgets: {tabs}")

            if 0 <= tab_index < len(tabs):
                # Get current tab before switching
                current_tab = self.tab_control.index(self.tab_control.select())
                print(f"🔍 Currently on tab: {current_tab}")
                
                # Use the actual tab widget reference, not the index
                self.tab_control.select(tabs[tab_index])
                
                # Verify the switch worked
                new_tab = self.tab_control.index(self.tab_control.select())
                print(f"🔍 After switch, on tab: {new_tab}")

                # Updated tab names to match your actual tabs
                tab_names = [
                    "Classic Elution",           # Tab 0
                    "Elution-Extrusion",        # Tab 1
                    "Dual Mode",                 # Tab 2
                    "Multiple Dual Mode",        # Tab 3
                    "Pulse Test",                # Tab 4
                    "Trace Fitting"              # Tab 5
                ]

                if tab_index < len(tab_names):
                    self.show_notification(f"Switched to {tab_names[tab_index]}", duration=1000)
                    print(f"✅ Switched to tab {tab_index}: {tab_names[tab_index]}")
            else:
                print(f"❌ Invalid tab index: {tab_index} (available: 0-{len(tabs)-1})")

        except AttributeError as e:
            print(f"❌ Tab widget error: {e}")
            self.show_notification("Cannot switch tabs", notif_type="error")
        except Exception as e:
            print(f"❌ Tab switching error: {e}")

    def show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        help_text = """Keyboard Shortcuts:

    FILE OPERATIONS:
    Ctrl+N          Clear all data (New)
    Ctrl+S          Save data  
    Ctrl+O          Open/Load data

    SIMULATIONS:
    F5 or Ctrl+R    Run current tab simulation
    F9              Run all simulations

    NAVIGATION:
    Ctrl+1          Switch to Classic Gradient
    Ctrl+2          Switch to Extrusion
    Ctrl+3          Switch to Dual Mode
    Ctrl+4          Switch to Multiple Dual Mode
    Ctrl+5          Switch to Pulse Test
    Ctrl+6          Switch to Trace Fitting

    DATA ENTRY:
    Ctrl++          Add new compound
    Ctrl+-          Remove selected compound
    Ctrl+U          Toggle Time/Volume units

    HELP:
    F1              Show this help dialog"""

        messagebox.showinfo("Keyboard Shortcuts", help_text)

    # ===== Table Management Methods =====
    def add_compound(self):
        """Add a new compound to the table"""
        count = len(self.compound_table.get_children()) + 1
        self.compound_table.insert("", "end", values=(f"Compound {count}", "1", "1", "0"))

    def remove_compound(self):
        """Remove selected compound from the table"""
        selection = self.compound_table.selection()
        if selection:
            for item in selection:
                self.compound_table.delete(item)
        else:
            # Remove last item if nothing is selected
            items = self.compound_table.get_children()
            if items:
                self.compound_table.delete(items[-1])

    def update_retention_times_from_results(self, results):
        """Update compound retention times based on actual simulation results"""
        try:
            values = self.compute_values()
            if not values:
                return

            cout = results['cout']
            vspan = results['vspan']

            # Find peaks for each compound and update retention times
            for i, compound_item in enumerate(self.compound_table.get_children()):
                current_values = list(self.compound_table.item(compound_item, 'values'))

                if i < len(cout):
                    # Find the peak (maximum) for this compound
                    peak_index = np.argmax(cout[i])
                    peak_volume = vspan[peak_index]

                    # Add dead volume
                    peak_volume += values['dead_volume']

                    # Convert to time if needed
                    if self.volume_time_var.get() == "Time":
                        peak_time = peak_volume / values['flow_rate']
                        current_values[3] = f"{peak_time:.2f}"
                    else:
                        current_values[3] = f"{peak_volume:.2f}"

                    # Update the table
                    self.compound_table.item(compound_item, values=current_values)

        except Exception as e:
            print(f"Error updating retention times: {e}")

    def add_cycle(self):
        """Add a new cycle to the switch times table"""
        items = self.switch_times_table.get_children()
        next_cycle = len(items) + 1
        self.switch_times_table.insert("", "end", values=(f"Cycle {next_cycle}", "5.0"))

    def remove_cycle(self):
        """Remove selected cycle from the switch times table"""
        selection = self.switch_times_table.selection()
        if selection:
            for item in selection:
                self.switch_times_table.delete(item)
        else:
            # Remove last item if nothing is selected
            items = self.switch_times_table.get_children()
            if items:
                self.switch_times_table.delete(items[-1])

    def save_compounds(self):
        """Save compound list to a CSV file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Compound List"
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Compound", "KD", "Conc", "RetTime"])

                for item in self.compound_table.get_children():
                    writer.writerow(self.compound_table.item(item, 'values'))

            messagebox.showinfo("Success", "Compound list saved successfully")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving compounds: {str(e)}")

    def open_compounds(self):
        """Open compound list from a CSV file"""
        filename = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Open Compound List"
        )
        if not filename:
            return

        try:
            # Clear existing compounds
            for item in self.compound_table.get_children():
                self.compound_table.delete(item)

            # Read from CSV
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header

                for row in reader:
                    self.compound_table.insert("", "end", values=row)

            messagebox.showinfo("Success", "Compound list loaded successfully")
        except Exception as e:
            messagebox.showerror("Open Error", f"Error opening compounds: {str(e)}")

    def setup_inline_editing(self):
        """Setup inline editing for all tables"""
        # Bind double-click events for inline editing
        self.compound_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'compound'))
        self.switch_times_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'switch_time'))

        # Store reference to current editing state
        self.current_edit_entry = None
        self.current_edit_item = None
        self.current_edit_column = None
        self.current_edit_table = None

    def start_inline_edit(self, event, table_type):
        """Start inline editing for any table"""
        # Get the appropriate table widget
        table_map = {
            'compound': self.compound_table,
            'switch_time': self.switch_times_table
        }

        table = table_map.get(table_type)
        if not table:
            return

        # Get the selected item and column
        item = table.identify_row(event.y)
        column = table.identify_column(event.x)

        if not item or not column:
            return

        # Convert column identifier to index
        column_index = int(column.replace('#', '')) - 1

        # Get current value
        current_values = table.item(item, 'values')
        if column_index >= len(current_values):
            return

        current_value = current_values[column_index]

        # Get the bounding box of the cell
        bbox = table.bbox(item, column)
        if not bbox:
            return

        # Destroy any existing edit entry
        self.finish_inline_edit()

        # Create entry widget for editing
        entry = self.create_inline_entry(table, table_type, column_index, bbox, current_value)

        # Store references
        self.current_edit_entry = entry
        self.current_edit_item = item
        self.current_edit_column = column_index
        self.current_edit_table = table

        # Focus and select all text
        entry.focus_set()
        entry.select_range(0, tk.END)

    def create_inline_entry(self, parent_table, table_type, column_index, bbox, current_value):
        """Configuration-driven entry creation"""
        x, y, width, height = bbox

        # Define validation rules for each table/column combination
        validation_rules = {
            'compound': {
                0: None,  # Name - no validation
                1: {'allow_zero': True, 'allow_negative': False},     # KD - allow any positive number and zero
                2: {'allow_zero': False, 'allow_negative': False},  # Concentration - positive only
                3: {'allow_zero': False, 'allow_negative': False}  # Retention time - positive only
            },
            'switch_time': {
                0: None,  # Cycle name - no validation
                1: {'allow_zero': False, 'allow_negative': False},  # Duration - positive only
            }
        }

        # Get validation parameters for this table/column
        table_rules = validation_rules.get(table_type, {})
        validation_params = table_rules.get(column_index, {'allow_zero': False, 'allow_negative': False})

        print(f"Table: {table_type}, Column: {column_index}, Validation: {validation_params}")

        # Create entry with or without validation
        if validation_params is None:
            # No validation - text entry
            entry = tk.Entry(parent_table,
                             relief="solid",
                             bd=1,
                             highlightthickness=1,
                             highlightcolor="blue")
            print("Created text entry (no validation)")
        else:
            # Numerical validation
            entry = self.create_validated_entry_for_inline(parent_table,
                                                           validation_params=validation_params,
                                                           )
            print(f"Created validated entry with params: {validation_params}")

        # Position the entry over the cell
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)

        # Bind events (same for all entries)
        entry.bind("<Return>", lambda e: self.finish_inline_edit(save=True))
        entry.bind("<Escape>", lambda e: self.finish_inline_edit(save=False))
        entry.bind("<FocusOut>", lambda e: self.finish_inline_edit(save=True))

        def handle_tab(event):
            self.move_to_next_cell(table_type, 'next')
            return "break"

        def handle_shift_tab(event):
            self.move_to_next_cell(table_type, 'previous')
            return "break"

        entry.bind("<Tab>", handle_tab)
        entry.bind("<Shift-Tab>", handle_shift_tab)

        entry.focus_set()
        entry.select_range(0, tk.END)

        return entry

    def finish_inline_edit(self, save=True):
        """Finish inline editing and optionally save the value"""
        if not self.current_edit_entry or not self.current_edit_table:
            return

        try:
            if save:
                # Get the new value
                new_value = self.current_edit_entry.get()

                # Update the table
                if self.current_edit_item and self.current_edit_column is not None:
                    current_values = list(self.current_edit_table.item(self.current_edit_item, 'values'))
                    if self.current_edit_column < len(current_values):
                        current_values[self.current_edit_column] = new_value
                        self.current_edit_table.item(self.current_edit_item, values=current_values)

            # Clean up
            self.current_edit_entry.destroy()

        except Exception as e:
            print(f"Error finishing inline edit: {e}")
            if self.current_edit_entry:
                self.current_edit_entry.destroy()

        finally:
            # Reset references
            self.current_edit_entry = None
            self.current_edit_item = None
            self.current_edit_column = None
            self.current_edit_table = None

        return "break"

    # Easy way to add new tables to the inline editing system:
    def add_table_inline_editing(self, table_widget, table_type, validation_rules):
        """Add inline editing to any new table"""
        # Bind the event
        table_widget.bind("<Double-1>", lambda e: self.start_inline_edit(e, table_type))

        # Add validation rules to the system
        # This would require modifying create_inline_entry to accept custom rules
        pass

    def create_validated_entry_for_inline(self, parent, validation_params=None):
        """Create a validated tk.Entry widget specifically for inline editing"""
        if validation_params is None:
            validation_params = {}

        # Debug: Show what parameters we're actually passing
        print(f"create_validated_entry_for_inline called with: {validation_params}")

        # Create a validation function that properly captures the parameters
        def validation_wrapper(value):
            # Debug: Show what parameters are being used in validation
            print(f"validation_wrapper called with params: {validation_params}")
            # Call the validation with all the required tkinter parameters
            return self.validate_number_input(value, str(parent), 'key', **validation_params)

        # Register the validation function
        validate_cmd = (self.root.register(validation_wrapper), '%P')

        # Use tk.Entry with appropriate options for inline editing
        entry = tk.Entry(parent,
                         validate='key',
                         validatecommand=validate_cmd,
                         relief="solid",
                         bd=1,
                         highlightthickness=1,
                         highlightcolor="blue"
                         )

        return entry

    def move_to_next_cell(self, table_type, direction):
        """Move to the next or previous cell for editing"""
        if not self.current_edit_table or not self.current_edit_item:
            return "break"

        # SAVE CURRENT STATE before finishing edit
        table = self.current_edit_table
        current_item = self.current_edit_item
        current_column = self.current_edit_column

        # Save current cell first (but don't clear state yet)
        try:
            if self.current_edit_entry:
                new_value = self.current_edit_entry.get()
                current_values = list(table.item(current_item, 'values'))
                if current_column < len(current_values):
                    current_values[current_column] = new_value
                    table.item(current_item, values=current_values)
        except Exception as e:
            print(f"Error saving current cell: {e}")

        # Now finish the edit (this will clear the state)
        self.finish_inline_edit(save=False)  # Don't save again since we already did

        # Get all items in the table
        all_items = table.get_children()
        current_item_index = all_items.index(current_item) if current_item in all_items else 0

        # Get number of columns for this table
        column_count_map = {
            'compound': 4,      # Name, KD, Concentration, Retention Time
            'switch_time': 2    # Cycle Name, Duration
        }
        max_columns = column_count_map.get(table_type, 4)

        # Calculate next position
        if direction == 'next':
            # Move to next column, or next row if at end of columns
            next_column = current_column + 1
            next_item_index = current_item_index

            if next_column >= max_columns:
                # Move to first column of next row
                next_column = 0
                next_item_index += 1

            # If at last row, wrap to first row
            if next_item_index >= len(all_items):
                next_item_index = 0

        else:  # direction == 'previous'
            # Move to previous column, or previous row if at beginning of columns
            next_column = current_column - 1
            next_item_index = current_item_index

            if next_column < 0:
                # Move to last column of previous row
                next_column = max_columns - 1
                next_item_index -= 1

            # If at first row, wrap to last row
            if next_item_index < 0:
                next_item_index = len(all_items) - 1

        # Get the target item
        if 0 <= next_item_index < len(all_items):
            target_item = all_items[next_item_index]

            # Calculate the bounding box for the target cell
            column_id = f"#{next_column + 1}"  # Tkinter columns start at #1
            bbox = table.bbox(target_item, column_id)

            if bbox:
                # Get current value of target cell
                current_values = table.item(target_item, 'values')
                if next_column < len(current_values):
                    current_value = current_values[next_column]

                    # Create a small delay to ensure the previous edit is finished
                    self.root.after(10, lambda: self.start_edit_at_position(
                        table_type, table, target_item, next_column, bbox, current_value
                    ))

        return "break"

    def start_edit_at_position(self, table_type, table, item, column_index, bbox, current_value):
        """Start editing at a specific table position"""
        # Create entry widget for editing
        entry = self.create_inline_entry(table, table_type, column_index, bbox, current_value)

        # Store references
        self.current_edit_entry = entry
        self.current_edit_item = item
        self.current_edit_column = column_index
        self.current_edit_table = table

        # Focus and select all text
        entry.focus_set()
        entry.select_range(0, tk.END)

    # ===== Plotting Methods =====
    def compute_values(self):
        """Compute values needed for simulations"""
        try:
            # Get values from UI
            flow_rate = float(self.flow_rate_entry.get())

            # Get elution duration/volume
            elution_duration = float(self.elution_duration_entry.get())
            if self.volume_time_var.get() == "Time":
                vcm = flow_rate * elution_duration
            else:
                vcm = elution_duration

            # Handle column volume and dead volume
            vc = float(self.column_volume_entry.get())
            dead_volume = float(self.dead_volume_entry.get())

            # Handle injection volume
            vinj = float(self.injection_volume_entry.get())
            if not self.include_injection_var.get():
                vinj = 0

            # Get compounds data from table
            compounds_data = []
            for item_id in self.compound_table.get_children():
                item = self.compound_table.item(item_id)
                values = item["values"]
                compounds_data.append({
                    "name": values[0],
                    "kd": float(values[1]),
                    "conc": float(values[2]),
                    "ret_time": float(values[3])
                })

            # Get stationary phase retention
            if self.stationary_phase_var.get() == "Set Sf":
                sf = float(self.stationary_phase_single_entry.get())
            else:
                # Use coefficient-based calculation
                try:
                    a = float(self.sf_coefficient_a_entry.get())
                    b = float(self.sf_coefficient_b_entry.get())
                    sf = a + b * flow_rate
                    sf = max(0.1, min(0.9, sf))  # Keep within reasonable bounds
                except ValueError as e:
                    print(f"Error calculating stationary phase: {e}")
                    sf = 0.75  # Default value

            # Get column efficiency (N cups)
            if self.column_efficiency_var.get() == "Set N":
                n_cup = int(float(self.column_efficiency_single_entry.get()))
            else:
                # Use coefficient-based calculation
                try:
                    a = float(self.n_coefficient_a_entry.get())
                    b = float(self.n_coefficient_b_entry.get())
                    c = float(self.n_coefficient_c_entry.get())
                    n_cup = a + b * flow_rate + c * flow_rate * flow_rate
                    n_cup = max(50, int(n_cup))  # Keep reasonably high
                except ValueError as e:
                    print(f"Error calculating column efficiency: {e}")
                    n_cup = 400  # Provide an appropriate default value

            # Process compounds into arrays for modeling functions
            if self.mobile_phase_var.get() == "Lower":
                kd_array = np.array([c["kd"] for c in compounds_data])
            else:
                kd_array = np.array([1 / c["kd"] for c in compounds_data])
            conc_array = np.array([c["conc"] for c in compounds_data])

            return {
                'flow_rate': flow_rate,
                'sf': sf,
                'kd_array': kd_array,
                'vc': vc,
                'n_cup': n_cup,
                'vcm': vcm,
                'conc_array': conc_array,
                'vinj': vinj,
                'dead_volume': dead_volume,
                'compounds': compounds_data
            }
        except ValueError as e:
            messagebox.showerror("Input Error", f"Please check your inputs: {str(e)}")
            return None

    def plot_classic(self, stored_data=None):
        """Plot classic elution model - can use stored data or compute fresh"""
        
        self.classic_ax.clear()

        try:
            if stored_data:
                # Use stored data for restoration
                results = stored_data
                values = None  # We'll extract what we need from stored data
            else:
                # Get necessary values for simulation (existing logic)
                values = self.compute_values()
                if not values:
                    return

                # Run simulation with CupV6 (existing logic)
                vspan, cout, x, y = CupV6(
                    values['sf'],
                    values['kd_array'],
                    values['vc'],
                    values['n_cup'],
                    values['vcm'],
                    values['conc_array'],
                    values['vinj']
                )

                # Store results for later use
                results = {
                    'vspan': vspan,
                    'cout': cout,
                    'x': x,
                    'y': y
                }
                self.classic_results = results

            # Common plotting logic that works for both stored and fresh data
            self.render_classic_plot(results, values, stored_data is not None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Plot Error", f"Error plotting data: {str(e)}")

    def render_classic_plot(self, results, values, is_restored=False):
        """Common rendering logic for classic plots - maintains all original functionality"""
        
        # Extract data from results
        vspan = np.array(results['vspan'])
        cout = results['cout']
        x = results.get('x', [])
        y = results.get('y', [])
        
        # Get flow rate and dead volume
        if is_restored:
            try:
                flow_rate = float(self.flow_rate_entry.get())
                dead_volume = float(self.dead_volume_entry.get())
                vcm = float(self.column_volume_entry.get())
            except:
                flow_rate = 5.0
                dead_volume = 0.0
                vcm = 10.0
        else:
            flow_rate = values['flow_rate']
            dead_volume = values['dead_volume']
            vcm = values['vcm']

        # Add dead volume first
        telute = vspan + dead_volume

        # Convert to time if needed - FIX: Apply conversion correctly for restored data
        if self.volume_time_var.get() == "Time":
            telute = telute / flow_rate
            x_label = 'Elution Time (min)'
            if not is_restored:
                axis_limit = vcm / flow_rate
            else:
                axis_limit = max(telute) if len(telute) > 0 else vcm / flow_rate
        else:
            x_label = 'Elution Volume (mL)'
            if not is_restored:
                axis_limit = vcm
            else:
                axis_limit = max(telute) if len(telute) > 0 else vcm

        # Get compounds info
        if is_restored:
            compounds = []
            for item in self.compound_table.get_children():
                values_row = self.compound_table.item(item, 'values')
                compounds.append({'name': values_row[0]})
        else:
            compounds = values['compounds']

        # Plot each compound
        max_conc = 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_color = colors[i % len(colors)]
                self.classic_ax.plot(telute, cout[i], color=compound_color,
                                    label=compound['name'], linewidth=2)
                max_conc = max(max_conc, np.max(cout[i]))

        # Show sum if requested
        if self.classic_sum_var.get():
            sum_concentration = np.sum(cout, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.classic_ax.plot(telute, sum_concentration, '-.r',
                                label='Sum', linewidth=1.0)

        # Add peak labels if requested
        if self.classic_peaks_var.get():
            for i, compound in enumerate(compounds):
                if i < len(cout):
                    peaks, _ = find_peaks(cout[i], height=0.1*np.max(cout[i]))
                    for peak in peaks:
                        if peak < len(telute):
                            self.classic_ax.text(telute[peak], cout[i][peak],
                                                compound['name'], ha='center')

        # Overlay experimental data if requested
        if (hasattr(self, 'overlay_var') and self.overlay_var.get() and 
            hasattr(self, 'fit_data') and self.fit_data):
            try:
                X_exp = self.fit_data['X']
                Y_exp = self.fit_data['Y']

                # Adjust for threshold
                threshold = self.fit_threshold_var.get()
                Y_exp = Y_exp - threshold

                # Convert to volume if needed
                if self.volume_time_var.get() == "Volume":
                    X_exp = X_exp * flow_rate

                self.classic_ax.plot(X_exp, Y_exp, 'k-',
                                    label='Experimental', linewidth=2, alpha=0.7)
                max_conc = max(max_conc, np.max(Y_exp[Y_exp > 0]))
            except:
                pass  # Skip experimental overlay if there's an issue

        # Set labels and limits
        self.classic_ax.set_xlabel(x_label, fontsize=11)
        self.classic_ax.set_ylabel("Concentration (g/L)", fontsize=11)
        self.classic_ax.set_title("Classic Elution", fontsize=14, fontweight='bold')
        self.classic_ax.legend(loc='upper right', framealpha=0.95, fontsize=10)

        # Set axis limits - FIX: Use calculated axis limit
        self.classic_ax.set_xlim(0, axis_limit)
        self.classic_ax.set_ylim(0, max_conc * 1.1 if max_conc > 0 else 1)
        
        if self.classic_grid_var.get():
            self.classic_ax.grid(True, linestyle='--', alpha=0.7)

        # Update elution times in compound table (only for fresh simulations)
        if not is_restored:
            self.update_retention_times_from_results(results)

        # Draw the canvas
        self.classic_fig.tight_layout()
        self.classic_canvas.draw()

    def plot_extrusion(self, stored_data=None):
        """Plot elution-extrusion model - can use stored data or compute fresh"""

        self.extrusion_ax.clear()

        try:
            if stored_data:
                results = stored_data
                values = None
            else:
                # Get necessary values for simulation
                values = self.compute_values()
                if not values:
                    return

                # Get extrusion duration from UI
                extrusion_duration = float(self.extrusion_duration_entry.get())

                # Run classic simulation first (needed for EECCC)
                vspan, cout, x, y = CupV6(
                    values['sf'],
                    values['kd_array'],
                    values['vc'],
                    values['n_cup'],
                    values['vcm'],
                    values['conc_array'],
                    values['vinj']
                )

                # Run elution-extrusion simulation based on mode
                if self.ccc_cpc_var.get() == "CCC":
                    vspan_ee, cout_ee, xtot, ytot, vbc = EECCC_V8(
                        values['kd_array'],
                        values['vc'],
                        values['sf'],
                        x,
                        y,
                    )
                else:
                    vspan_ee, cout_ee, xtot, ytot, vbc = ECPC_V1(
                        values['kd_array'],
                        values['vc'],
                        values['sf'],
                        x,
                        y,
                    )

                results = {
                    'vspan': vspan_ee,
                    'cout': cout_ee,
                    'xtot': xtot,
                    'ytot': ytot,
                    'vbc': vbc
                }
                self.extrusion_results = results

            # Common rendering logic
            self.render_extrusion_plot(results, values, stored_data is not None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Plot Error", f"Error plotting data: {str(e)}")

    def render_extrusion_plot(self, results, values, is_restored=False):
        """Common rendering logic for extrusion plots - maintains all original functionality"""

        # Extract data from results
        vspan_ee = np.array(results['vspan'])
        cout_ee = results['cout']
        xtot = results['xtot']
        ytot = results['ytot']
        vbc = np.array(results['vbc'])

        # Get flow rate and dead volume
        if is_restored:
            try:
                flow_rate = float(self.flow_rate_entry.get())
                dead_volume = float(self.dead_volume_entry.get())
                # Get extrusion duration for axis limits
                extrusion_duration = float(self.extrusion_duration_entry.get())
                # Get vcm for calculations
                vcm = float(self.column_volume_entry.get())
            except:
                flow_rate = 1.0
                dead_volume = 0.0
                extrusion_duration = 10.0
                vcm = 10.0
        else:
            flow_rate = values['flow_rate']
            dead_volume = values['dead_volume']
            extrusion_duration = float(self.extrusion_duration_entry.get())
            vcm = values['vcm']

        # Add dead volume to both vspan and vbc (same as MATLAB)
        vspan_ee = vspan_ee + dead_volume
        vbc = vbc + dead_volume

        # Flow rate adjustment for volume display
        if self.volume_time_var.get() == "Volume":
            display_flow_rate = 1
        else:
            display_flow_rate = flow_rate

        # Calculate key times exactly as in MATLAB
        telute = vspan_ee / display_flow_rate
        column_volume_extruded_time = vbc[0] / display_flow_rate
        sweep_time = vbc[1] / display_flow_rate if len(vbc) > 1 else None
        extrusion_time = extrusion_duration + (vcm / display_flow_rate)

        # Get compounds info
        if is_restored:
            compounds = []
            for item in self.compound_table.get_children():
                values_row = self.compound_table.item(item, 'values')
                compounds.append({'name': values_row[0]})
        else:
            compounds = values['compounds']

        # Plot each compound
        max_conc = 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for i, compound in enumerate(compounds):
            if i < len(cout_ee):
                compound_color = colors[i % len(colors)]
                self.extrusion_ax.plot(telute, cout_ee[i], color=compound_color,
                                    label=compound['name'], linewidth=2)
                max_conc = max(max_conc, np.max(cout_ee[i]))

        # Show sum if requested
        if self.extrusion_sum_var.get():
            sum_concentration = np.sum(cout_ee, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.extrusion_ax.plot(telute, sum_concentration, '-.r', label='Sum', linewidth=1.0)

        # Add vertical lines for extrusion phases - exact match of MATLAB logic
        if self.extrusion_lines_var.get():
            # Set up labels based on user selection
            if self.extrusion_lines_labels_var.get():
                units = ' min' if self.volume_time_var.get() == "Time" else ' mL'
                elution_time = vcm / display_flow_rate

                if self.ccc_cpc_var.get() == "CCC":
                    sweep_start_label = f"Sweep Start\n{elution_time:.2f}{units}"
                    sweep_end_label = f"Extrusion Start\n{sweep_time:.2f}{units}" if sweep_time else ""
                else:  # CPC mode
                    sweep_start_label = f"Extrusion Start\n{elution_time:.2f}{units}"
                    sweep_end_label = ""
            else:
                sweep_start_label = ""
                sweep_end_label = ""

            if self.ccc_cpc_var.get() == "CCC":
                # Add vertical line at Column Volume Extruded Time
                self.extrusion_ax.axvline(x=column_volume_extruded_time, color='r',
                                        linestyle='-.', label="Sweep Start")
                if sweep_start_label:
                    self.extrusion_ax.text(column_volume_extruded_time, 0,
                                        sweep_start_label, ha="right", va="bottom", rotation=90)

                # Add vertical line at Sweep End/Extrusion Start (if applicable)
                if sweep_time is not None:
                    self.extrusion_ax.axvline(x=sweep_time, color='b',
                                            linestyle='-.', label="Extrusion Start")
                    if sweep_end_label:
                        self.extrusion_ax.text(sweep_time, 0,
                                            sweep_end_label, ha="right", va="bottom", rotation=90)
            else:  # CPC mode
                # Just one line at extrusion start for CPC
                self.extrusion_ax.axvline(x=column_volume_extruded_time, color='b',
                                        linestyle='-.', label="Extrusion Start")
                if sweep_start_label:
                    self.extrusion_ax.text(column_volume_extruded_time, 0,
                                        sweep_start_label, ha="right", va="bottom", rotation=90)

        # Add peak labels if requested
        if self.extrusion_peaks_var.get():
            for i, compound in enumerate(compounds):
                if i < len(cout_ee):
                    # Find peaks for this compound
                    compound_peaks, _ = find_peaks(cout_ee[i], height=0.1*np.max(cout_ee[i]))

                    # Add peak information
                    for peak in compound_peaks:
                        if peak < len(telute):
                            # Simple text label like MATLAB
                            self.extrusion_ax.text(telute[peak], cout_ee[i][peak],
                                                compound['name'], ha='center')

        # Overlay experimental data if requested (same as overlay_var in Python)
        if (hasattr(self, 'overlay_var') and self.overlay_var.get() and 
            hasattr(self, 'fit_data') and self.fit_data):
            try:
                X_exp = self.fit_data['X']
                Y_exp = self.fit_data['Y']

                # Adjust for threshold
                threshold = self.fit_threshold_var.get()
                Y_exp = Y_exp - threshold

                # Convert to volume if needed
                if self.volume_time_var.get() == "Volume":
                    X_exp = X_exp * flow_rate

                self.extrusion_ax.plot(X_exp, Y_exp, 'k-',
                                    label='Experimental', linewidth=2, alpha=0.7)
                max_conc = max(max_conc, np.max(Y_exp[Y_exp > 0]))
            except:
                pass  # Skip experimental overlay if there's an issue

        # Set labels and limits exactly like MATLAB
        x_label = 'Elution Volume (mL)' if self.volume_time_var.get() == "Volume" else 'Elution Time (min)'
        self.extrusion_ax.set_xlabel(x_label, fontsize=11)
        self.extrusion_ax.set_ylabel("Concentration (g/L)", fontsize=11)
        self.extrusion_ax.set_title("Elution-Extrusion", fontsize=14, fontweight='bold')
        self.extrusion_ax.legend(loc='upper right', framealpha=0.95, fontsize=10)

        # Set axis limits exactly as in MATLAB
        self.extrusion_ax.set_xlim(0, extrusion_time)
        self.extrusion_ax.set_ylim(0, max_conc * 1.1)
        if self.extrusion_grid_var.get():
            self.extrusion_ax.grid(True, linestyle='--', alpha=0.7)

        # Update elution times in compound table (only for fresh simulations)
        if not is_restored:
            self.update_retention_times_from_results(results)

        # Draw the canvas
        self.extrusion_fig.tight_layout()
        self.extrusion_canvas.draw()

    def plot_dual(self, stored_data=None):
        """Plot dual mode elution model - can use stored data or compute fresh"""

        self.dual_ax.clear()

        try:
            if stored_data:
                results = stored_data
                values = None
            else:
                # Get necessary values for simulation
                values = self.compute_values()
                if not values:
                    return

                # Get dual mode duration from UI
                dual_duration = float(self.dual_duration_entry.get())

                # Convert dual_duration to volume if in Time mode
                flow_rate = values['flow_rate']
                if self.volume_time_var.get() == "Time":
                    Vdm = dual_duration * flow_rate
                else:
                    Vdm = dual_duration

                # Run classic simulation first
                vspan, cout, x, y = CupV6(
                    values['sf'],
                    values['kd_array'],
                    values['vc'],
                    values['n_cup'],
                    values['vcm'],
                    values['conc_array'],
                    values['vinj']
                )

                # Run dual mode simulation
                vspan_dual, cout_dual, xtot, ytot = DualV2(
                    values['kd_array'],
                    values['vc'],
                    values['sf'],
                    flow_rate,
                    Vdm,
                    x,
                    y
                )

                results = {
                    'vspan': vspan_dual,
                    'cout': cout_dual,
                    'xtot': xtot,
                    'ytot': ytot,
                }
                self.dual_results = results

            # Common rendering logic
            self.render_dual_plot(results, values, stored_data is not None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Plot Error", f"Error plotting dual mode: {str(e)}")

    def render_dual_plot(self, results, values, is_restored=False):
        """Common rendering logic for dual mode plots - maintains all original functionality"""

        # Extract data from results
        vspan_dual = np.array(results['vspan'])
        cout_dual = results['cout']
        xtot = results['xtot']
        ytot = results['ytot']

        # Get flow rate and dead volume
        if is_restored:
            try:
                flow_rate = float(self.flow_rate_entry.get())
                dead_volume = float(self.dead_volume_entry.get())
                dual_duration = float(self.dual_duration_entry.get())
                vcm = float(self.column_volume_entry.get())
            except:
                flow_rate = 1.0
                dead_volume = 0.0
                dual_duration = 10.0
                vcm = 10.0
        else:
            flow_rate = values['flow_rate']
            dead_volume = values['dead_volume']
            dual_duration = float(self.dual_duration_entry.get())
            vcm = values['vcm']

        # Add dead volume to plot data
        telute = vspan_dual + dead_volume

        # FIXED: Calculate the switch point based on the elution duration, not vcm
        # The switch should occur at the end of the elution phase
        if is_restored:
            # For restored data, get the elution duration from the UI
            elution_duration = float(self.elution_duration_entry.get())
            if self.volume_time_var.get() == "Time":
                # elution_duration is already in the correct units (time or volume)
                classic_end_point = elution_duration
            else:
                # elution_duration is in volume units
                classic_end_point = elution_duration
        else:
            # For fresh data, use vcm from the simulation
            if self.volume_time_var.get() == "Time":
                classic_end_point = vcm / flow_rate
            else:
                classic_end_point = vcm

        # Convert to time if needed and calculate switch point
        if self.volume_time_var.get() == "Time":
            telute = telute / flow_rate
            x_label = 'Elution Time (min)'
            # FIXED: Switch occurs at end of elution phase + dead volume effect
            dual_switch_time = classic_end_point + (dead_volume / flow_rate)
            # Total time including dual mode duration
            if is_restored:
                stationary_phase_volume = max(telute) if len(telute) > 0 else dual_switch_time + dual_duration
            else:
                stationary_phase_volume = (vcm + dual_duration * flow_rate + dead_volume) / flow_rate
        else:
            x_label = 'Elution Volume (mL)'
            # FIXED: Switch occurs at end of elution phase + dead volume
            dual_switch_time = classic_end_point + dead_volume
            # Total volume including dual mode duration
            if is_restored:
                stationary_phase_volume = max(telute) if len(telute) > 0 else dual_switch_time + dual_duration
            else:
                stationary_phase_volume = vcm + dual_duration + dead_volume

        # ... rest of the method remains the same

        # Get compounds info
        if is_restored:
            compounds = []
            for item in self.compound_table.get_children():
                values_row = self.compound_table.item(item, 'values')
                compounds.append({'name': values_row[0]})
        else:
            compounds = values['compounds']

        # Plot each compound
        max_conc = 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for i, compound in enumerate(compounds):
            if i < len(cout_dual):
                compound_color = colors[i % len(colors)]
                self.dual_ax.plot(telute, cout_dual[i], color=compound_color,
                                label=compound['name'], linewidth=2)
                max_conc = max(max_conc, np.max(cout_dual[i]))

        # Add vertical line for dual mode transition
        if self.dual_lines_var.get():
            dual_switch_label = ''
            if self.dual_lines_labels_var.get():
                units = ' min' if self.volume_time_var.get() == "Time" else ' mL'
                dual_switch_label = f"Dual Switch\n{dual_switch_time:.2f}{units}"

            # Classic to dual
            self.dual_ax.axvline(x=dual_switch_time, color='r', linestyle='-.', label="Dual Switch")
            if dual_switch_label:
                self.dual_ax.text(dual_switch_time, max_conc * 0.8 if max_conc > 0 else 0.5,
                                  dual_switch_label, ha="left", va="bottom", rotation=90)

        # Show sum if requested
        if self.dual_sum_var.get():
            sum_concentration = np.sum(cout_dual, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.dual_ax.plot(telute, sum_concentration, 'r-.', label="Sum", linewidth=1.5)

        # Add peak labels if requested
        if self.dual_peaks_var.get():
            for i, compound in enumerate(compounds):
                if i < len(cout_dual):
                    # Find peaks
                    peaks, _ = find_peaks(cout_dual[i], height=0.1*np.max(cout_dual[i]))

                    # Add labels to peaks
                    for peak in peaks:
                        if peak < len(telute):
                            self.dual_ax.annotate(
                                f"{compound['name']}",
                                xy=(telute[peak], cout_dual[i][peak]),
                                xytext=(0, 5),
                                textcoords='offset points',
                                ha='center',
                                fontsize=9
                            )

        # Set labels and limits - match MATLAB exactly
        self.dual_ax.set_xlabel(x_label, fontsize=11)
        self.dual_ax.set_ylabel("Concentration (g/L)", fontsize=11)
        self.dual_ax.set_title("Dual Mode Elution", fontsize=14, fontweight='bold')
        self.dual_ax.legend(loc='upper right', framealpha=0.95, fontsize=10)
        self.dual_ax.set_xlim(0, stationary_phase_volume)
        self.dual_ax.set_ylim(0, max_conc * 1.1 if max_conc > 0 else 1)

        if self.dual_grid_var.get():
            self.dual_ax.grid(True, linestyle='--', alpha=0.7)

        # Update elution times in compound table (only for fresh simulations)
        if not is_restored:
            self.update_retention_times_from_results(results)

        # Draw the canvas
        self.dual_fig.tight_layout()
        self.dual_canvas.draw()

    def plot_multi(self, stored_data=None):
        """Plot multiple dual mode elution model - can use stored data or compute fresh"""

        self.multi_ax.clear()
        self.multi_pos_ax.clear()

        try:
            if stored_data:
                results = stored_data
                values = None
            else:
                # Get necessary values for simulation
                values = self.compute_values()
                if not values:
                    return

                # Get switching times from the table
                switch_times = []
                for item in self.switch_times_table.get_children():
                    values_row = self.switch_times_table.item(item, 'values')
                    try:
                        switch_times.append(float(values_row[1]))
                    except (ValueError, IndexError):
                        pass

                if not switch_times:
                    messagebox.showwarning("No Switch Times", "Please add at least one switch time")
                    return

                # Convert switch times to volumes if in Time mode
                if self.volume_time_var.get() == "Time":
                    switch_volumes = [t * values['flow_rate'] for t in switch_times]
                else:
                    switch_volumes = switch_times

                # Combine the main elution volume (vcm) with the switch volumes
                # This matches how MATLAB creates the vcm array: [Vcm; cell2mat(app.SwitchTimeList.Data(:,2))*F]
                vcm_array = np.concatenate(([values['vcm']], switch_volumes))

                # Run the multiple dual mode simulation with MDMV2 including all required parameters
                # Using the same parameter order as in the MATLAB code
                vspan_mdm, cout_mdm, xtot_mdm, ytot_mdm, tcut_mdm, vswdm, vswcm = MDMV2(
                    values['sf'],
                    values['kd_array'],
                    values['vc'],
                    values['n_cup'],
                    values['conc_array'],
                    values['vinj'],
                    vcm_array
                )

                # Store results for later use
                self.multi_results = {
                    'vspan': vspan_mdm,
                    'cout': cout_mdm,
                    'xtot': xtot_mdm,
                    'ytot': ytot_mdm,
                    'vbc': vswdm,
                    'vcyc': vswcm
                }

                results = {
                    'vspan': vspan_mdm,
                    'cout': cout_mdm,
                    'xtot': xtot_mdm,
                    'ytot': ytot_mdm,
                    'vbc': vswdm,
                    'vcyc': vswcm
                }
                self.multi_results = results

            # Common rendering logic
            self.render_multi_plots(results, values, stored_data is not None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Plot Error", f"Error plotting multiple dual mode: {str(e)}")

    def render_multi_plots(self, results, values, is_restored=False):
        """Common rendering logic for multiple dual mode plots - maintains all original functionality"""

        # Extract data from results
        vspan_mdm = np.array(results['vspan'])
        cout_mdm = results['cout']
        xtot_mdm = results['xtot']
        ytot_mdm = results['ytot']
        vswdm = np.array(results['vbc'])  # VswDM
        vswcm = np.array(results['vcyc'])  # VswCM

        # Get flow rate and dead volume
        if is_restored:
            try:
                flow_rate = float(self.flow_rate_entry.get())
                dead_volume = float(self.dead_volume_entry.get())
            except:
                flow_rate = 1.0
                dead_volume = 0.0
        else:
            flow_rate = values['flow_rate']
            dead_volume = values['dead_volume']

        # Add dead volume and convert to time if needed
        telute = vspan_mdm + dead_volume

        if self.volume_time_var.get() == "Time":
            telute = telute / flow_rate
            x_label = 'Elution Time (min)'
            x_label_unit = 'min'
        else:
            x_label = 'Elution Volume (mL)'
            x_label_unit = 'mL'

        # Get compounds info
        if is_restored:
            compounds = []
            for item in self.compound_table.get_children():
                values_row = self.compound_table.item(item, 'values')
                compounds.append({'name': values_row[0]})
        else:
            compounds = values['compounds']

        # Plot each compound in the concentration plot
        max_conc = 0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for i, compound in enumerate(compounds):
            if i < len(cout_mdm):
                compound_color = colors[i % len(colors)]
                self.multi_ax.plot(telute, cout_mdm[i], color=compound_color,
                                label=compound['name'], linewidth=2)
                max_conc = max(max_conc, np.max(cout_mdm[i]))

        # Show sum if requested
        if self.multi_sum_var.get():
            sum_concentration = np.sum(cout_mdm, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.multi_ax.plot(telute, sum_concentration, 'k--', label="Sum", linewidth=2)

        # Handle switching times separately like MATLAB (VswDM and VswCM)
        # Add dead volume to switching times (matching MATLAB: VswCM = VswCM+deadVolume)
        vswdm_with_dead = vswdm + dead_volume  # VswDM
        vswcm_with_dead = vswcm + dead_volume  # VswCM

        if self.volume_time_var.get() == "Time":
            vswdm_times = vswdm_with_dead / flow_rate
            vswcm_times = vswcm_with_dead / flow_rate
        else:
            vswdm_times = vswdm_with_dead
            vswcm_times = vswcm_with_dead

        # Add vertical lines for switching times with separate colors (matching MATLAB)
        if self.multi_lines_var.get():
            # Draw VswDM lines in red
            for i, v in enumerate(vswdm_times):
                self.multi_ax.axvline(x=v, color='r', linestyle='-.')
                if self.multi_lines_labels_var.get():
                    self.multi_ax.text(v, 0, f"DM {i+1}\n{v:.1f} {x_label_unit}",
                                    ha="right", va="bottom", rotation=90, fontsize=8)

            # Draw VswCM lines in blue
            for i, v in enumerate(vswcm_times):
                self.multi_ax.axvline(x=v, color='b', linestyle='-.')
                if self.multi_lines_labels_var.get():
                    self.multi_ax.text(v, 0, f"CM {i+1}\n{v:.1f} {x_label_unit}",
                                    ha="right", va="bottom", rotation=90, fontsize=8)

        # Add peak labels if requested
        if self.multi_peaks_var.get():
            for i, compound in enumerate(compounds):
                if i < len(cout_mdm):
                    # Find peaks - use cout_mdm instead of cout
                    peaks, _ = find_peaks(cout_mdm[i], height=0.1*np.max(cout_mdm[i]))

                    # Add simple labels like in classic plot
                    for peak in peaks:
                        if peak < len(telute):
                            self.multi_ax.text(telute[peak], cout_mdm[i][peak],
                                               compound['name'], ha='center')

        # Set up concentration plot
        self.multi_ax.set_xlabel(x_label)
        self.multi_ax.set_ylabel('Concentration (g/L)')
        self.multi_ax.legend(loc='upper right', fontsize=8)
        self.multi_ax.set_xlim(0, max(telute))
        self.multi_ax.set_ylim(0, max_conc * 1.1)
        if self.multi_grid_var.get():
            self.multi_ax.grid(True, linestyle='--', alpha=0.7)
        self.multi_ax.set_facecolor('#ffffff')

        # Create position contour plot using MDMV2 data (matching MATLAB implementation exactly)
        # MATLAB: xMatrix = sum(Xtot, 3) - sum across the 3rd dimension
        x_matrix = np.sum(xtot_mdm, axis=2)

        # Create y-axis for column position (matching MATLAB: yAxis = [1:size(xMatrix,1)].*(1/size(xMatrix,1)))
        y_axis = np.linspace(0, 1, x_matrix.shape[0])

        # Find the maximum concentration value for scaling
        matrix_scaler = np.max(x_matrix)

        # Create contour levels (matching MATLAB: linspace(0.001*matrixScaler, .05*matrixScaler, 30))
        contour_levels = np.linspace(0.001 * matrix_scaler, 0.05 * matrix_scaler, 30)

        # Try to match MATLAB's contourf exactly by interpolating x_matrix to match telute length
        # Create interpolation function
        original_time = np.linspace(0, len(x_matrix[0]), len(x_matrix[0]))
        target_time = np.linspace(0, len(x_matrix[0]), len(telute))

        # Interpolate x_matrix to match telute dimensions
        x_matrix_interp = np.zeros((x_matrix.shape[0], len(telute)))
        for i in range(x_matrix.shape[0]):
            x_matrix_interp[i, :] = np.interp(target_time, original_time, x_matrix[i, :])

        # Now use contourf like MATLAB
        try:
            cs = self.multi_pos_ax.contourf(telute, y_axis, x_matrix_interp, levels=contour_levels,
                                            cmap='viridis', extend='max')
        except:
            # Fallback to imshow if contourf fails
            extent = [telute[0], telute[-1], 0, 1]
            vmax = matrix_scaler * 0.05
            vmin = matrix_scaler * 0.001
            im = self.multi_pos_ax.imshow(x_matrix_interp, aspect='auto', extent=extent,
                                          cmap='viridis', interpolation='bilinear',
                                          origin='lower', vmin=vmin, vmax=vmax)

        # Add cycle indicators to position plot (matching MATLAB: separate DM and CM lines)
        for i, v in enumerate(vswdm_times):
            self.multi_pos_ax.axvline(x=v, color='r', linestyle='-.')

        for i, v in enumerate(vswcm_times):
            self.multi_pos_ax.axvline(x=v, color='b', linestyle='-.')

        # Set up position plot
        self.multi_pos_ax.set_xlabel(x_label)
        self.multi_pos_ax.set_ylabel('Column Position')
        if self.multi_grid_var.get():
            self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)
        self.multi_pos_ax.set_facecolor('#ffffff')

        # Set fixed subplot parameters for both plots (matching original exactly)
        layout_params = {
            'left': 0.12,
            'right': 0.97,
            'top': 0.93,
            'bottom': 0.20
        }

        # Set identical layouts BEFORE drawing
        self.multi_fig.subplots_adjust(**layout_params)
        self.multi_pos_fig.subplots_adjust(**layout_params)

        # Draw without tight_layout to preserve our manual positioning
        self.multi_canvas.draw()
        self.multi_pos_canvas.draw()

    def synchronize_multi_plot_layouts(self):
        """Ensure both multi mode plots have identical layouts"""
        # Get the position of the first plot's axes
        pos1 = self.multi_ax.get_position()

        # Set the second plot to match exactly
        self.multi_pos_ax.set_position(pos1)

        # Update both canvases
        self.multi_canvas.draw()
        self.multi_pos_canvas.draw()

    def refresh_all_plots(self):
        """Refresh all plots after unit conversion"""

        # Only refresh plots that have been generated (have stored results)
        if hasattr(self, 'classic_results'):
            self.plot_classic()

        if hasattr(self, 'extrusion_results'):
            self.plot_extrusion()

        if hasattr(self, 'dual_results'):
            self.plot_dual()

        if hasattr(self, 'multi_results'):
            self.plot_multi()

    def run_current_simulation(self):
        """Run simulation for the currently active tab"""
        try:
            current_tab = self.tab_control.index(self.tab_control.select())
        except AttributeError:
            self.show_notification("Cannot determine current tab", notif_type="error")
            return

        # Updated tab methods for all 6 tabs
        tab_methods = {
            0: self.plot_classic,        # Classic Elution
            1: self.plot_extrusion,      # Elution-Extrusion
            2: self.plot_dual,           # Dual Mode
            3: self.plot_multi,          # Multiple Dual Mode
            4: getattr(self, 'plot_pulse', lambda: self.show_notification("Pulse Test not implemented", notif_type="info")),     # Pulse Test
            5: getattr(self, 'plot_trace', lambda: self.show_notification("Trace Fitting not implemented", notif_type="info"))  # Trace Fitting
        }

        if current_tab in tab_methods:
            try:
                tab_methods[current_tab]()
                tab_names = ["Classic Elution", "Elution-Extrusion", "Dual Mode", "Multiple Dual Mode", "Pulse Test", "Trace Fitting"]
                self.show_notification(f"Ran {tab_names[current_tab]} simulation", duration=1500)
            except Exception as e:
                self.show_notification(f"Simulation failed: {str(e)}", notif_type="error")
        else:
            self.show_notification("No simulation available for this tab", notif_type="warning")

    # ===== Pulse and Fit Tab Methods =====
    def import_trace(self, trace_type, imported_data=None):
        """Import experimental trace data with flexible format support"""
        if imported_data is not None:
            # If data is provided directly, use it
            X = imported_data['X']
            Y = imported_data['Y']
            trace_type = imported_data['trace_type']
        else:

            filename = filedialog.askopenfilename(
                filetypes=[("All supported files", "*.csv *.txt *.xls *.xlsx *.mat *.dat"),
                        ("CSV files", "*.csv"),
                        ("Text files", "*.txt"),
                        ("Excel files", "*.xls *.xlsx"),
                        ("MATLAB files", "*.mat"),
                        ("Binary data", "*.dat"),
                        ("All files", "*.*")],
                title=f"Import {trace_type} trace"
            )

            if not filename:
                return

            try:
                # Determine file extension
                extension = filename.lower().split('.')[-1]
                if extension in ['xls', 'xlsx']:
                    # Excel file handling with robust numeric conversion
                    try:
                        # Try reading without headers first
                        df = pd.read_excel(filename, header=None)

                    except Exception as e:
                        raise ValueError(f"Could not read Excel file: {e}")

                    # Convert all cells to numeric, replacing non-numeric with NaN
                    numeric_df = df.copy()
                    for col in df.columns:
                        numeric_df[col] = pd.to_numeric(df[col], errors='coerce')

                    # Remove rows where ALL values are NaN (completely non-numeric rows)
                    numeric_df = numeric_df.dropna(how='all')

                    # Remove columns where ALL values are NaN (completely non-numeric columns)
                    numeric_df = numeric_df.dropna(axis=1, how='all')

                    if len(numeric_df) == 0 or len(numeric_df.columns) == 0:
                        messagebox.showerror("Import Error", "No usable numeric data found in the file")
                        return

                    # For remaining NaN values (mixed text/numbers), replace with 0
                    numeric_df = numeric_df.fillna(0)

                    # More lenient column filtering - keep columns with any significant data
                    columns_to_keep = []
                    for col in numeric_df.columns:
                        col_data = numeric_df[col].abs()
                        max_val = col_data.max()
                        non_zero_count = (col_data > 1e-10).sum()
                        # More lenient: keep if has ANY significant values
                        if -1e-10 < max_val > 1e-10 and non_zero_count >= 1:
                            columns_to_keep.append(col)

                    if len(columns_to_keep) < 2:
                        for col in numeric_df.columns:
                            col_data = numeric_df[col].abs()
                        messagebox.showerror("Import Error", f"Need at least 2 columns with numeric data. Found {len(columns_to_keep)} usable columns.")
                        return

                    # Filter to only useful columns and round to 3 decimal places
                    filtered_df = numeric_df[columns_to_keep]
                    filtered_df = filtered_df.round(3)

                    # Transpose to match format expected by column selection
                    imported_data = filtered_df.values.T

                elif extension == 'mat':
                    # MATLAB file
                    mat_data = loadmat(filename)
                    data_keys = [k for k in mat_data.keys() if not k.startswith('__')]

                    # Create matrix with all available data columns
                    data_arrays = []
                    for key in data_keys:
                        array_data = mat_data[key].flatten().astype(float)
                        data_arrays.append(array_data)

                    if len(data_arrays) == 0:
                        raise ValueError("No data arrays found in MATLAB file")

                    # Truncate to shortest array length
                    min_length = min(len(arr) for arr in data_arrays)
                    data_arrays = [arr[:min_length] for arr in data_arrays]

                    # Stack as columns, then transpose for column selection
                    imported_data = np.array(data_arrays)

                else:
                    # Text/CSV file handling
                    try:
                        # Read the file content
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()

                        lines = [line.rstrip('\r') for line in content.split('\n')]

                        # Find where actual data starts
                        data_start_line = -1
                        data_delimiter = '\t'

                        for i, line in enumerate(lines[:20]):
                            if line.strip():
                                # Try both comma and tab delimiters
                                for delimiter in ['\t', ',']:
                                    parts = line.split(delimiter)
                                    if len(parts) >= 2:
                                        # Check if ALL non-empty parts are numeric
                                        all_numeric = True
                                        non_empty_count = 0
                                        for part in parts:
                                            part_clean = part.strip().strip('"')
                                            if part_clean:
                                                non_empty_count += 1
                                                if not re.match(r'^-?\d+\.?\d*$', part_clean):
                                                    all_numeric = False
                                                    break

                                        if all_numeric and non_empty_count >= 2:
                                            data_start_line = i
                                            data_delimiter = delimiter
                                            break

                                if data_start_line >= 0:
                                    break

                        if data_start_line < 0:
                            raise ValueError("Could not find start of numeric data")

                        # Extract data lines
                        data_lines = []
                        for line in lines[data_start_line:]:
                            if line.strip():
                                data_lines.append(line)

                        # Parse the data
                        parsed_rows = []
                        for line in data_lines:
                            parts = line.split(data_delimiter)
                            numeric_parts = []
                            for part in parts:
                                part_clean = part.strip().strip('"')
                                if part_clean:
                                    try:
                                        val = float(part_clean)
                                        numeric_parts.append(val)
                                    except ValueError:
                                        pass

                            if len(numeric_parts) >= 2:
                                parsed_rows.append(numeric_parts)

                        if not parsed_rows:
                            raise ValueError("No valid data rows found")

                        # Ensure consistent column count
                        max_cols = max(len(row) for row in parsed_rows)
                        standardized_rows = []
                        for row in parsed_rows:
                            if len(row) < max_cols:
                                standardized_row = row + [0.0] * (max_cols - len(row))
                            else:
                                standardized_row = row[:max_cols]
                            standardized_rows.append(standardized_row)

                        # Convert to numpy array and transpose
                        data = np.array(standardized_rows, dtype=np.float64)
                        imported_data = data.T

                    except Exception as e:
                        # Fallback to numpy.loadtxt
                        data = None
                        for delimiter in [',', '\t', ' ', None]:
                            try:
                                if delimiter is None:
                                    data = np.loadtxt(filename)
                                else:
                                    data = np.loadtxt(filename, delimiter=delimiter)
                                break
                            except Exception:
                                continue

                        if data is None:
                            raise ValueError("Could not parse file in any format")

                        if data.ndim == 1:
                            Y = data.astype(np.float64)
                            X = np.arange(len(Y), dtype=np.float64)
                            imported_data = np.array([X, Y])
                        else:
                            imported_data = data.T.astype(np.float64)

                # Show column selection dialog
                x_col, y_col = self.show_column_select_popup(imported_data)

            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing trace: {str(e)}")

            if x_col is not None and y_col is not None:
                X = imported_data[x_col, :].astype(float)
                Y = imported_data[y_col, :].astype(float)

                if trace_type == 'fit':
                    self.fit_data = {'X': X, 'Y': Y}
                    self.fit_ax.clear()
                    self.fit_ax.plot(X, Y, linewidth=2.0)
                    self.fit_ax.set_xlabel('Elution Time')
                    self.fit_ax.set_ylabel('Concentration')
                    self.fit_ax.grid(True, linestyle='--', alpha=0.7)
                    self.fit_canvas.draw()
                    self.fit_span_var.set(min(20, len(Y)//2))

                elif trace_type == 'pulse':
                    self.pulse_data = {'X': X, 'Y': Y}
                    self.pulse_ax.clear()
                    self.pulse_ax.plot(X, Y, linewidth=2.0)
                    self.pulse_ax.set_xlabel('Elution Time')
                    self.pulse_ax.set_ylabel('Concentration')
                    self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
                    self.pulse_canvas.draw()

                self.show_notification(f"Imported {len(X)} data points", 3000, "info")

    def show_notification(self, message, duration=3000, notif_type="info"):
        # Create notification window
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)  # Remove window decorations
        notification.attributes('-topmost', True)  # Keep on top

        # Configure notification appearance based on type
        colors = {
            "info": {"bg": "#e3f2fd", "fg": "#1976d2", "border": "#2196f3"},
            "success": {"bg": "#e8f5e8", "fg": "#2e7d32", "border": "#4caf50"},
            "warning": {"bg": "#fff3e0", "fg": "#f57c00", "border": "#ff9800"},
            "error": {"bg": "#ffebee", "fg": "#d32f2f", "border": "#f44336"}
        }

        color_scheme = colors.get(notif_type, colors["info"])

        # Create main frame with border
        main_frame = tk.Frame(notification,
                              bg=color_scheme["border"],
                              relief="flat")
        main_frame.pack(fill="both", expand=True)

        # Create inner frame for content
        content_frame = tk.Frame(main_frame,
                                 bg=color_scheme["bg"],
                                 relief="flat")
        content_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Add message label
        label = tk.Label(content_frame,
                         text=message,
                         bg=color_scheme["bg"],
                         fg=color_scheme["fg"],
                         font=('TkDefaultFont', 10, 'normal'),
                         padx=20, pady=10,
                         wraplength=400)  # Wrap long messages
        label.pack()

        # Position notification in top-right corner of main window
        notification.update_idletasks()  # Calculate size

        # Get main window position and size
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # Calculate notification position (centered)
        notif_width = notification.winfo_reqwidth()
        notif_height = notification.winfo_reqheight()

        x = main_x + (main_width - notif_width) // 2   # Center horizontally
        y = main_y + (main_height - notif_height) // 2  # Center vertically

        notification.geometry(f"{notif_width}x{notif_height}+{x}+{y}")

        # Fade-out animation
        def fade_out():
            alpha = 1.0
            fade_step = 0.05  # How much to fade each step
            fade_delay = 50   # Milliseconds between fade steps

            def fade():
                nonlocal alpha
                alpha -= fade_step
                if alpha <= 0:
                    notification.destroy()
                else:
                    try:
                        notification.attributes('-alpha', alpha)
                        notification.after(fade_delay, fade)
                    except tk.TclError:
                        # Window already destroyed
                        pass

            fade()

        # Start fade-out after duration
        notification.after(duration, fade_out)

        return notification

    def show_column_select_popup(self, imported_data):
        """Show column selection dialog for imported data with clickable column headers"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Column Selection")
        dialog.geometry("1000x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create frame for table
        table_frame = ttk.Frame(dialog)
        table_frame.place(x=20, y=75, width=960, height=400)

        # Create treeview for data preview
        preview_tree = ttk.Treeview(table_frame)
        preview_tree.pack(fill="both", expand=True)

        # Configure columns
        num_cols = imported_data.shape[0]
        preview_tree["columns"] = [f"Col{i+1}" for i in range(num_cols)]
        preview_tree["show"] = "headings"

        # Variables to track selected columns
        selected_x = tk.IntVar(value=-1)
        selected_y = tk.IntVar(value=-1)

        # Configure column headers with click handling
        def on_header_click(event, col_index):
            """Handle column header clicks"""
            # Determine which selection this is for based on current state
            if selected_x.get() == -1:
                # First selection - set as X
                selected_x.set(col_index)
                update_column_display()
            elif selected_y.get() == -1:
                # Second selection - set as Y
                selected_y.set(col_index)
                update_column_display()
            else:
                # Both already selected - replace X with new selection
                selected_x.set(col_index)
                selected_y.set(-1)
                update_column_display()

        def update_column_display():
            """Update the column headers to show selection status"""
            for i in range(num_cols):
                col_id = f"Col{i+1}"
                if selected_x.get() == i:
                    preview_tree.heading(col_id, text=f"Column {i+1} ← X")
                elif selected_y.get() == i:
                    preview_tree.heading(col_id, text=f"Column {i+1} ← Y")
                else:
                    preview_tree.heading(col_id, text=f"Column {i+1}")

        # Set up column headers and click bindings
        for i in range(num_cols):
            col_id = f"Col{i+1}"
            preview_tree.heading(col_id, text=f"Column {i+1}")
            preview_tree.column(col_id, width=100, anchor="center")

            # Bind click event to header
            preview_tree.heading(col_id, command=lambda idx=i: on_header_click(None, idx))

        # Insert data (transposed for display)
        for row in imported_data.T[:100]:  # Show first 100 rows
            preview_tree.insert("", "end", values=[str(val) for val in row])

        # Instructions and status display
        # Create a frame for better status styling
        status_frame = tk.Frame(dialog, relief="flat", bg=dialog.cget('bg'))
        status_frame.place(x=20, y=20, width=530, height=40)

        dialogue_label = tk.Label(status_frame, text="Click column headers\nto select X and Y data",
                                  font=('TkDefaultFont', 12),
                                  bg=dialog.cget('bg'))
        dialogue_label.pack(side='left', expand=False)

        status_label = tk.Label(status_frame, text="X: None, Y: None",
                                font=('TkDefaultFont', 12),
                                bg=dialog.cget('bg'))
        status_label.pack(side='left', expand=False, padx=(30, 0))

        def update_status():
            """Update the status display"""
            x_text = f"Column {selected_x.get() + 1}" if selected_x.get() >= 0 else "None"
            y_text = f"Column {selected_y.get() + 1}" if selected_y.get() >= 0 else "None"
            status_label.config(text=f"X: {x_text}, Y: {y_text}")

        def on_header_click(event, col_index):
            """Handle column header clicks"""
            if selected_x.get() == -1:
                selected_x.set(col_index)
            elif selected_y.get() == -1:
                selected_y.set(col_index)
            else:
                # Both selected - replace X and clear Y
                selected_x.set(col_index)
                selected_y.set(-1)

            update_column_display()
            update_status()

        # Result variable
        result = {"x": None, "y": None}

        def on_select():
            if selected_x.get() >= 0 and selected_y.get() >= 0:
                result["x"] = selected_x.get()
                result["y"] = selected_y.get()
                dialog.destroy()
            else:
                messagebox.showwarning("Selection Required",
                                       "Please select both X and Y columns by clicking on the column headers.")

        select_button = ttk.Button(status_frame, text="Import", command=on_select)
        select_button.pack(side='right', expand=False, padx=(35, 0))

        # Initialize display
        update_column_display()
        update_status()

        # Wait for dialog to close
        dialog.wait_window()

        return result["x"], result["y"]

    def find_pulse_peaks(self):
        """Find peaks in the pulse test data"""
        if not self.pulse_data:
            messagebox.showinfo("No Data", "Please import pulse data first")
            return

        try:
            X = np.array(self.pulse_data['X'], dtype=np.float64)
            Y = np.array(self.pulse_data['Y'], dtype=np.float64)

            # Ensure we have valid data
            if len(X) == 0 or len(Y) == 0:
                messagebox.showerror("Data Error", "Invalid pulse data - arrays are empty")
                return

            if len(X) != len(Y):
                messagebox.showerror("Data Error", "X and Y data arrays must have the same length")
                return

            # Apply Savitzky-Golay filter to smooth data
            window_length = int(self.pulse_span_var.get())
            
            # Ensure window length is valid
            if window_length >= len(Y):
                window_length = len(Y) - 1
            if window_length % 2 == 0:
                window_length += 1  # Must be odd
            if window_length < 3:
                window_length = 3

            # Apply smoothing filter
            try:
                Y_smooth = savgol_filter(Y, window_length, min(3, window_length-1))
            except ValueError:
                # Fallback: use simple moving average if Savgol fails
                window_size = min(5, len(Y)//4)
                if window_size < 1:
                    window_size = 1
                Y_smooth = np.convolve(Y, np.ones(window_size)/window_size, mode='same')

            # Subtract baseline if specified
            baseline_value = float(self.pulse_baseline_var.get())
            if baseline_value > 0:
                Y_smooth = Y_smooth - baseline_value
                Y_smooth[Y_smooth < 0] = 0

            # Find peaks with specified prominence
            prominence_value = float(self.pulse_prominence_var.get())
            
            # Ensure we have valid data for peak finding
            if np.max(Y_smooth) <= prominence_value:
                messagebox.showwarning("No Peaks", 
                                    f"No peaks found above prominence threshold {prominence_value:.2f}. "
                                    f"Maximum signal is {np.max(Y_smooth):.2f}")
                return

            # Find peaks - convert to standard Python types to avoid numpy indexing issues
            peaks, properties = find_peaks(Y_smooth.astype(np.float64), 
                                        prominence=prominence_value)

            # Convert peaks to standard Python list of integers
            peaks = [int(p) for p in peaks if 0 <= int(p) < len(X)]

            if len(peaks) == 0:
                messagebox.showwarning("No Peaks", "No peaks found with current settings")
                return

            # Store flow rate for N calculation
            self.pulse_flow_rate = float(self.flow_rate_entry.get())
            self.pulse_sf = float(self.stationary_phase_single_entry.get())
            self.pulse_peaks = peaks
            self.pulse_X = X
            self.pulse_Y_smooth = Y_smooth

            # Plot results
            self.pulse_ax.clear()
            self.pulse_ax.plot(X, Y, 'k-', alpha=0.4, linewidth=1, label='Raw')
            self.pulse_ax.plot(X, Y_smooth, 'b-', linewidth=1.5, label='Smoothed')
            
            # Plot peaks using integer indices
            peak_x = [X[i] for i in peaks]
            peak_y = [Y_smooth[i] for i in peaks]
            self.pulse_ax.plot(peak_x, peak_y, 'ro', label='Peaks')

            # Add peak labels
            for i, peak_idx in enumerate(peaks):
                self.pulse_ax.annotate(f"Peak {i+1}",
                                    (X[peak_idx], Y_smooth[peak_idx]),
                                    xytext=(0, 10),
                                    textcoords="offset points",
                                    ha='center')

            self.pulse_ax.legend()
            self.pulse_ax.grid(True)
            self.pulse_ax.set_xlabel('Elution Time (min)')
            self.pulse_ax.set_ylabel('Signal')
            self.pulse_fig.tight_layout()
            self.pulse_canvas.draw()

            # Show success message
            self.show_notification(f"Found {len(peaks)} peaks", duration=2000, notif_type="success")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Peak Finding Error", f"Error finding peaks: {str(e)}")

    def add_n_value(self):
        """Add N value to the pulse list"""
        if not hasattr(self, 'pulse_peaks') or not self.pulse_peaks:
            messagebox.showinfo("No Peaks", "Please find peaks first")
            return

        try:
            # Calculate N value from peak properties
            # Using the first peak for simplicity
            peak_idx = self.pulse_peaks[0]  # This is now a Python int
            time = float(self.pulse_X[peak_idx])

            # Calculate width at half maximum for the peak
            max_height = float(self.pulse_Y_smooth[peak_idx])
            half_height = max_height / 2

            # Find indices of the left and right sides at half height
            left_idx = right_idx = peak_idx
            
            # Search left
            while left_idx > 0 and self.pulse_Y_smooth[left_idx] > half_height:
                left_idx -= 1
                
            # Search right
            while right_idx < len(self.pulse_Y_smooth) - 1 and self.pulse_Y_smooth[right_idx] > half_height:
                right_idx += 1

            # Calculate width in time units
            left_time = float(self.pulse_X[left_idx])
            right_time = float(self.pulse_X[right_idx])
            width = right_time - left_time

            if width <= 0:
                messagebox.showerror("Calculation Error", "Cannot calculate peak width - peak too narrow")
                return

            # Calculate N using 5.54 * (time/width)^2
            N = 5.54 * (time / width)**2

            # Add to pulse table
            self.pulse_table.insert("", "end", values=(
                f"{self.pulse_flow_rate:.1f}",
                f"{self.pulse_sf:.2f}",
                f"{N:.0f}",
                "No"
            ))

            # Enable regression buttons if we have enough data
            if len(self.pulse_table.get_children()) >= 3:
                self.use_n_button.config(state="normal")
                self.use_sf_button.config(state="normal")
                self.fit_coefficients()

            self.show_notification(f"Added N value: {N:.0f}", duration=2000, notif_type="success")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Calculation Error", f"Error calculating N: {str(e)}")

    def fit_coefficients(self):
        """Fit coefficients for N and Sf equations"""
        items = self.pulse_table.get_children()
        if len(items) < 3:
            return

        try:
            # Extract data from table
            flow_rates = []
            sf_values = []
            n_values = []

            for item in items:
                values = self.pulse_table.item(item, 'values')
                flow_rates.append(float(values[0]))
                sf_values.append(float(values[1]))
                n_values.append(float(values[2]))

            flow_rates = np.array(flow_rates)
            sf_values = np.array(sf_values)
            n_values = np.array(n_values)

            # Fit N = a + b*F + c*F^2
            X_n = np.column_stack((np.ones_like(flow_rates), flow_rates, flow_rates**2))
            n_coeffs = np.linalg.lstsq(X_n, n_values, rcond=None)[0]

            # Update N coefficient labels
            self.label_na.config(text=f"A: {n_coeffs[0]:.3f}")
            self.label_nb.config(text=f"B: {n_coeffs[1]:.3f}")
            self.label_nc.config(text=f"C: {n_coeffs[2]:.3f}")

            # Fit Sf = a + b*F
            X_sf = np.column_stack((np.ones_like(flow_rates), flow_rates))
            sf_coeffs = np.linalg.lstsq(X_sf, sf_values, rcond=None)[0]

            # Update Sf coefficient labels
            self.label_sf_a.config(text=f"A: {sf_coeffs[0]:.4f}")
            self.label_sf_b.config(text=f"B: {sf_coeffs[1]:.4f}")

            # Store coefficients for later use
            self.n_coeffs = n_coeffs
            self.sf_coeffs = sf_coeffs

        except Exception as e:
            messagebox.showerror("Fit Error", f"Error fitting coefficients: {str(e)}")

    def use_n_values(self):
        """Use fitted N coefficients in column properties"""
        if not hasattr(self, 'n_coeffs'):
            return

        # Switch to coefficient mode
        self.column_efficiency_var.set("Coeff.")
        self.toggle_efficiency()

        # Set coefficients
        self.n_coefficient_a_entry.delete(0, tk.END)
        self.n_coefficient_a_entry.insert(0, f"{self.n_coeffs[0]:.4f}")

        self.n_coefficient_b_entry.delete(0, tk.END)
        self.n_coefficient_b_entry.insert(0, f"{self.n_coeffs[1]:.4f}")

        self.n_coefficient_c_entry.delete(0, tk.END)
        self.n_coefficient_c_entry.insert(0, f"{self.n_coeffs[2]:.4f}")

        # Update the calculated value
        self.update_n_from_coefficients()

        messagebox.showinfo("Success", "N coefficients transferred to column properties")

    def use_sf_values(self):
        """Use fitted Sf coefficients in column properties"""
        if not hasattr(self, 'sf_coeffs'):
            return

        # Switch to coefficient mode
        self.stationary_phase_var.set("Coeff.")
        self.toggle_stationary()

        # Set coefficients
        self.sf_coefficient_a_entry.delete(0, tk.END)
        self.sf_coefficient_a_entry.insert(0, f"{self.sf_coeffs[0]:.4f}")

        self.sf_coefficient_b_entry.delete(0, tk.END)
        self.sf_coefficient_b_entry.insert(0, f"{self.sf_coeffs[1]:.4f}")

        # Update the calculated value
        self.update_sf_from_coefficients()

        messagebox.showinfo("Success", "Sf coefficients transferred to column properties")

    def save_pulse_list(self):
        """Save pulse test list to a CSV file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Pulse Test List"
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Flow Rate', 'Sf', 'N', 'Del?'])

                for item in self.pulse_table.get_children():
                    writer.writerow(self.pulse_table.item(item, 'values'))

            messagebox.showinfo("Success", "Pulse test list saved successfully")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving pulse list: {str(e)}")

    def open_pulse_list(self):
        """Open pulse test list from a CSV file"""
        filename = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Open Pulse Test List"
        )
        if not filename:
            return

        try:
            # Clear existing items
            for item in self.pulse_table.get_children():
                self.pulse_table.delete(item)

            with open(filename, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header

                for row in reader:
                    self.pulse_table.insert("", "end", values=row)

            # Update regression if we have enough data
            if len(self.pulse_table.get_children()) >= 3:
                self.use_n_button.config(state="normal")
                self.use_sf_button.config(state="normal")
                self.fit_coefficients()

            messagebox.showinfo("Success", "Pulse list loaded successfully")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading pulse list: {str(e)}")

    def find_fit_peaks(self):
        """Find peaks in fit data for KD determination"""
        if not hasattr(self, 'fit_data') or not self.fit_data:
            messagebox.showinfo("No Data", "Please import fit data first")
            return

        try:
            X = self.fit_data['X']
            Y = self.fit_data['Y']

            # Apply Savitzky-Golay filter to smooth data
            window_length = self.fit_span_var.get()
            if window_length % 2 == 0:
                window_length += 1  # Must be odd
            Y_smooth = savgol_filter(Y, window_length, 3)

            # Subtract threshold
            threshold = self.fit_threshold_var.get()
            Y_adjusted = Y_smooth - threshold
            Y_adjusted[Y_adjusted < 0] = 0

            # Find peaks with specified prominence

            peaks, properties = find_peaks(Y_adjusted, prominence=self.fit_prominence_var.get())

            # Calculate KD values
            sf = float(self.stationary_phase_single_entry.get())
            vc = float(self.column_volume_entry.get())
            flow_rate = float(self.flow_rate_entry.get())

            kd_values = []
            for peak in peaks:
                peak_time = X[peak]
                if self.volume_time_var.get() == "Volume":
                    peak_volume = peak_time
                else:
                    peak_volume = peak_time * flow_rate

                # Calculate KD using retention equation
                # V_retention = Vc * (1 - Sf + KD * Sf)
                # Solving for KD: KD = (V_retention - Vc * (1 - Sf)) / (Vc * Sf)
                kd = (peak_volume - vc * (1 - sf)) / (vc * sf)
                if kd > 0:  # Only include valid KD values
                    kd_values.append((peak, peak_time, Y_adjusted[peak], kd))

            # Store peak data
            self.fit_peaks = kd_values

            # Plot results
            self.fit_ax.clear()
            self.fit_ax.plot(X, Y, 'k-', alpha=0.4, linewidth=1, label='Raw')
            self.fit_ax.plot(X, Y_smooth, 'b-', linewidth=1.5, label='Smoothed')

            # Add horizontal line at threshold
            self.fit_ax.axhline(y=threshold, color='r', linestyle='--', label='Threshold')

            # Plot peaks with KD values
            for i, (peak_idx, time, height, kd) in enumerate(kd_values):
                self.fit_ax.plot(time, height + threshold, 'ro')
                self.fit_ax.annotate(f"KD={kd:.2f}",
                                     (time, height + threshold),
                                     xytext=(0, 10),
                                     textcoords="offset points",
                                     ha='center')

            self.fit_ax.legend()
            self.fit_ax.grid(True)
            self.fit_ax.set_xlabel('Time (min)')
            self.fit_ax.set_ylabel('Signal')
            self.fit_fig.tight_layout()
            self.fit_canvas.draw()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Peak Finding Error", f"Error finding peaks: {str(e)}")

    def update_compound_list_with_fits(self):
        """Update compound list with KD values from fit"""
        if not hasattr(self, 'fit_peaks') or not self.fit_peaks:
            messagebox.showinfo("No Peaks", "Please find peaks first")
            return

        try:
            # Clear existing compounds
            for item in self.compound_table.get_children():
                self.compound_table.delete(item)

            # Add compounds based on fit peaks
            for i, (_, time, _, kd) in enumerate(self.fit_peaks):
                retention_time = time
                if self.volume_time_var.get() == "Volume":
                    retention_time = time / float(self.flow_rate_entry.get())

                self.compound_table.insert("", "end", values=(
                    f"Compound {i+1}",
                    f"{kd:.3f}",
                    "1",
                    f"{retention_time:.2f}"
                ))

            messagebox.showinfo("Success", f"Added {len(self.fit_peaks)} compounds from fit data")
        except Exception as e:
            messagebox.showerror("Update Error", f"Error updating compounds: {str(e)}")

    # ===== Input Validation Methods =====
    def setup_validation(self):
        """Register validation functions with tkinter"""
        # Register the unified validation function
        self.validate_input = (self.root.register(self.validate_number_input), '%P', '%W', '%V')

    def validate_number_input(self, value, widget_name, validation_event,
                              min_val=None, max_val=None, allow_zero=True,
                              integer_only=False, allow_negative=True):

        # Allow empty string (user might be typing)
        if value == "":
            return True

        # Allow single decimal point or minus sign while typing (but only if negatives allowed)
        if value == "." and not integer_only:
            return True
        if value == "-" and allow_negative and not integer_only:
            return True

        # Throttle notifications to prevent spam (only show every 500ms)
        current_time = time.time() * 1000  # Convert to milliseconds
        if not hasattr(self, '_last_validation_notification'):
            self._last_validation_notification = 0

        def show_throttled_notification(message, notif_type="warning"):
            if current_time - self._last_validation_notification > 500:  # 500ms throttle
                self.show_notification(message, duration=2000, notif_type=notif_type)
                self._last_validation_notification = current_time

        try:
            num = float(value)
            # Check negative values
            if not allow_negative and num < 0:
                show_throttled_notification("Must be non-negative", notif_type="warning")
                return False

            # Check integer requirement
            if integer_only and num != int(num):
                self.show_notification("Must be an integer", notif_type="warning")
                return False

            # Check zero (only restrict if explicitly disabled)
            if not allow_zero and num == 0:
                show_throttled_notification("Cannot be zero", notif_type="warning")
                return False

            # Check minimum value
            if min_val is not None:
                if allow_zero and num == 0:
                    pass  # Zero is explicitly allowed
                elif num <= min_val:
                    self.show_notification(f"Must be greater than {min_val}", notif_type="warning")
                    return False

            # Check maximum value
            if max_val is not None and num >= max_val:
                self.show_notification(f"Must be less than {max_val}", notif_type="warning")
                return False

            return True

        except ValueError:
            show_throttled_notification("Must be a valid number", notif_type="error")
            return False

    def create_validated_entry(self, parent, validation_params=None, **kwargs):
        if validation_params is None:
            validation_params = {}

        # Create a partial function with the validation parameters
        def validation_wrapper(value, widget_name, validation_event):
            return self.validate_number_input(value, widget_name, validation_event, **validation_params)

        # Register this specific validation function
        validate_cmd = (self.root.register(validation_wrapper), '%P', '%W', '%V')

        entry = ttk.Entry(parent, validate='key', validatecommand=validate_cmd, **kwargs)
        return entry

    # ===== Export Methods =====
    def export_data_common(self, mode, results, mode_specific_params=None):
        """Common export functionality for all simulation modes"""
        # File selection with multiple format options
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            title=f"Export {mode.title()} Data"
        )
        if not filename:
            return

        try:
            values = self.compute_values()
            compounds = values['compounds']

            # Process volume/time data consistently
            vspan = results['vspan']
            cout = results['cout']

            # Add dead volume and convert to time if needed
            x_values = vspan + values['dead_volume']
            if self.volume_time_var.get() == "Time":
                x_values = x_values / values['flow_rate']
                x_label = 'Time (min)'
            else:
                x_label = 'Volume (mL)'

            # Prepare main data
            data_dict = {x_label: x_values}
            for i, compound in enumerate(compounds):
                data_dict[compound['name']] = cout[i]

            # Add sum if requested
            sum_var_map = {
                'classic': self.classic_sum_var,
                'extrusion': self.extrusion_sum_var,
                'dual': self.dual_sum_var,
                'multi': self.multi_sum_var
            }
            if mode in sum_var_map and sum_var_map[mode].get():
                data_dict['Sum'] = np.sum(cout, axis=0)

            # Create DataFrame
            df_data = pd.DataFrame(data_dict)

            # Prepare parameters data
            params_data = {
                'Parameter': [
                    'Simulation Mode',
                    'Flow Rate (mL/min)',
                    'Column Volume (mL)',
                    'Stationary Phase Retention',
                    'Column Efficiency (N)',
                    'Elution Duration (min)',
                    'Elution Volume (mL)',
                    'Dead Volume (mL)',
                    'Injection Volume (mL)',
                    'Include Injection Volume'
                ],
                'Value': [
                    mode.title(),
                    f"{values['flow_rate']:.2f}",
                    f"{values['vc']:.2f}",
                    f"{values['sf']:.4f}",
                    f"{values['n_cup']:.0f}",
                    f"{values['vcm'] / values['flow_rate']:.2f}",
                    f"{values['vcm']:.2f}",
                    f"{values['dead_volume']:.2f}",
                    f"{values['vinj']:.2f}",
                    'Yes' if self.include_injection_var.get() else 'No'
                ]
            }

            # Add mode-specific parameters
            if mode_specific_params:
                for param, value in mode_specific_params.items():
                    params_data['Parameter'].append(param)
                    params_data['Value'].append(value)

            df_params = pd.DataFrame(params_data)

            # Determine file format and export
            file_ext = filename.lower().split('.')[-1]

            if file_ext == 'xlsx':
                # Excel export with multiple sheets
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df_data.to_excel(writer, sheet_name='Data', index=False)
                    df_params.to_excel(writer, sheet_name='Parameters', index=False)

                    # Add compound information sheet
                    compound_info = pd.DataFrame([
                        {
                            'Compound': comp['name'],
                            'KD': comp['kd'],
                            'Concentration (g/L)': comp['conc'],
                            'Retention Time/Volume': comp['ret_time']
                        }
                        for comp in compounds
                    ])
                    compound_info.to_excel(writer, sheet_name='Compounds', index=False)

            else:
                # CSV export with parameters in separate columns
                # Combine data and parameters side by side
                max_rows = max(len(df_data), len(df_params))

                # Pad shorter dataframe with empty rows
                if len(df_data) < max_rows:
                    empty_data = pd.DataFrame([[np.nan] * len(df_data.columns)] * (max_rows - len(df_data)),
                                              columns=df_data.columns)
                    df_data = pd.concat([df_data, empty_data], ignore_index=True)

                if len(df_params) < max_rows:
                    empty_params = pd.DataFrame([[np.nan] * len(df_params.columns)] * (max_rows - len(df_params)),
                                                columns=df_params.columns)
                    df_params = pd.concat([df_params, empty_params], ignore_index=True)

                # Add separator column
                separator = pd.DataFrame({'': [''] * max_rows})

                # Combine all data
                combined_df = pd.concat([df_data, separator, df_params], axis=1)
                combined_df.to_csv(filename, index=False)

            # Export plot if Excel format
            if file_ext == 'xlsx':
                self.export_plot(mode, filename.replace('.xlsx', '_plot.pdf'))

            messagebox.showinfo("Export", f"{mode.title()} data exported successfully!\n" +
                                (f"Plot saved as PDF." if file_ext == 'xlsx' else ""))

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

    def export_plot(self, mode, filename):
        """Export the current plot as PDF"""
        try:
            # Map mode to figure objects
            fig_map = {
                'classic': self.classic_fig,
                'extrusion': self.extrusion_fig,
                'dual': self.dual_fig,
                'multi': [self.multi_fig, self.multi_pos_fig]  # Multi has two plots
            }

            if mode not in fig_map:
                return

            with PdfPages(filename) as pdf:
                if mode == 'multi':
                    pdf.savefig(self.multi_fig, bbox_inches='tight', dpi=300)
                    pdf.savefig(self.multi_pos_fig, bbox_inches='tight', dpi=300)
                else:
                    pdf.savefig(fig_map[mode], bbox_inches='tight', dpi=300)

        except Exception as e:
            print(f"Error exporting plot: {e}")
            # Don't show error to user - plot export is optional

    def get_mode_specific_params(self, mode):
        """Get mode-specific parameters for export"""
        params = {}

        if mode == 'extrusion':
            params['Extrusion Mode'] = self.ccc_cpc_var.get()
            extrusion_duration = float(self.extrusion_duration_entry.get())
            if self.volume_time_var.get() == "Time":
                params['Extrusion Duration (min)'] = f"{extrusion_duration:.2f}"
            else:
                params['Extrusion Duration (mL)'] = f"{extrusion_duration:.2f}"

        elif mode == 'dual':
            dual_duration = float(self.dual_duration_entry.get())
            if self.volume_time_var.get() == "Time":
                params['Dual Mode Duration (min)'] = f"{dual_duration:.2f}"
            else:
                params['Dual Mode Duration (mL)'] = f"{dual_duration:.2f}"

        elif mode == 'multi':
            # Add cycle information
            cycles = []
            for item in self.switch_times_table.get_children():
                values_row = self.switch_times_table.item(item, 'values')
                cycle_name = values_row[0]
                duration = values_row[1]
                unit = "min" if self.volume_time_var.get() == "Time" else "mL"
                cycles.append(f"{cycle_name}: {duration} {unit}")
            params['Cycle Information'] = "; ".join(cycles)

        return params

    def export_classic(self):
        """Export classic elution data"""
        if not hasattr(self, 'classic_results'):
            messagebox.showinfo("Export", "No data to export. Run simulation first.")
            return
        self.export_data_common('classic', self.classic_results)

    def export_extrusion(self):
        """Export elution-extrusion data"""
        if not hasattr(self, 'extrusion_results'):
            messagebox.showinfo("Export", "No data to export. Run simulation first.")
            return
        mode_params = self.get_mode_specific_params('extrusion')
        self.export_data_common('extrusion', self.extrusion_results, mode_params)

    def export_dual(self):
        """Export dual mode data"""
        if not hasattr(self, 'dual_results'):
            messagebox.showinfo("Export", "No data to export. Run simulation first.")
            return
        mode_params = self.get_mode_specific_params('dual')
        self.export_data_common('dual', self.dual_results, mode_params)

    def export_multi(self):
        """Export multiple dual mode data"""
        if not hasattr(self, 'multi_results'):
            messagebox.showinfo("Export", "No data to export. Run simulation first.")
            return
        mode_params = self.get_mode_specific_params('multi')
        self.export_data_common('multi', self.multi_results, mode_params)

    # ===== State Management Methods =====
    def clear_all_data(self):
        """Clear all data and reset the application to initial state (New file)"""
        result = messagebox.askyesno("New File", "Are you sure you want to create a new file? All current data and plots will be cleared.")
        if result:
            # Clear compound table
            for item in self.compound_table.get_children():
                self.compound_table.delete(item)

            # Reset to default compounds
            self.compound_table.insert("", "end", values=("Compound 1", "1", "1", "0"))
            self.compound_table.insert("", "end", values=("Compound 2", "2", "1", "0"))

            # Reset all entry fields to defaults
            self.flow_rate_entry.delete(0, tk.END)
            self.flow_rate_entry.insert(0, "5")

            self.column_volume_entry.delete(0, tk.END)
            self.column_volume_entry.insert(0, "81")

            self.elution_duration_entry.delete(0, tk.END)
            self.elution_duration_entry.insert(0, "60")

            self.injection_volume_entry.delete(0, tk.END)
            self.injection_volume_entry.insert(0, "1")

            self.dead_volume_entry.delete(0, tk.END)
            self.dead_volume_entry.insert(0, "0")

            # Reset stationary phase and efficiency to defaults
            self.stationary_phase_var.set("Set Sf")
            self.toggle_stationary()
            self.stationary_phase_single_entry.delete(0, tk.END)
            self.stationary_phase_single_entry.insert(0, "0.75")

            self.column_efficiency_var.set("Set N")
            self.toggle_efficiency()
            self.column_efficiency_single_entry.delete(0, tk.END)
            self.column_efficiency_single_entry.insert(0, "400")

            # Reset coefficient fields to defaults
            if hasattr(self, 'sf_coefficient_a_entry'):
                self.sf_coefficient_a_entry.delete(0, tk.END)
                self.sf_coefficient_a_entry.insert(0, "0.982")
                self.sf_coefficient_b_entry.delete(0, tk.END)
                self.sf_coefficient_b_entry.insert(0, "-0.142")

            if hasattr(self, 'n_coefficient_a_entry'):
                self.n_coefficient_a_entry.delete(0, tk.END)
                self.n_coefficient_a_entry.insert(0, "371.23")
                self.n_coefficient_b_entry.delete(0, tk.END)
                self.n_coefficient_b_entry.insert(0, "-7.204")
                self.n_coefficient_c_entry.delete(0, tk.END)
                self.n_coefficient_c_entry.insert(0, "0.1480")

            # Reset other duration entries if they exist
            if hasattr(self, 'extrusion_duration_entry'):
                self.extrusion_duration_entry.delete(0, tk.END)
                self.extrusion_duration_entry.insert(0, "5")

            if hasattr(self, 'dual_duration_entry'):
                self.dual_duration_entry.delete(0, tk.END)
                self.dual_duration_entry.insert(0, "10")

            # Reset switch times table to defaults
            if hasattr(self, 'switch_times_table'):
                for item in self.switch_times_table.get_children():
                    self.switch_times_table.delete(item)
                # Add default switch times
                self.switch_times_table.insert("", "end", values=("Cycle 1", "10"))
                self.switch_times_table.insert("", "end", values=("Cycle 2", "5"))

            # Reset all checkboxes and dropdowns to defaults
            self.include_injection_var.set(True)
            self.mobile_phase_var.set("Lower")
            self.volume_time_var.set("Time")

            # Reset tab-specific options to defaults
            self.classic_sum_var.set(False)
            self.classic_peaks_var.set(True)
            self.classic_grid_var.set(True)

            if hasattr(self, 'ccc_cpc_var'):
                self.ccc_cpc_var.set("CCC")
            self.extrusion_sum_var.set(False)
            self.extrusion_peaks_var.set(True)
            self.extrusion_lines_var.set(True)
            self.extrusion_lines_labels_var.set(True)
            self.extrusion_grid_var.set(True)

            self.dual_sum_var.set(False)
            self.dual_peaks_var.set(True)
            self.dual_lines_var.set(True)
            self.dual_lines_labels_var.set(True)
            self.dual_grid_var.set(True)

            self.multi_sum_var.set(False)
            self.multi_peaks_var.set(True)
            self.multi_lines_var.set(True)
            self.multi_lines_labels_var.set(True)
            self.multi_grid_var.set(True)

            # Clear all plots and reset to default state
            self.clear_all_plots()

            # Clear any stored results
            self.clear_stored_results()

            # Clear pulse and fit data
            if hasattr(self, 'pulse_data'):
                self.pulse_data = None
            if hasattr(self, 'fit_data'):
                self.fit_data = None

            # Clear pulse test table
            if hasattr(self, 'pulse_table'):
                for item in self.pulse_table.get_children():
                    self.pulse_table.delete(item)

            # Reset pulse test regression buttons
            if hasattr(self, 'use_n_button'):
                self.use_n_button.config(state="disabled")
            if hasattr(self, 'use_sf_button'):
                self.use_sf_button.config(state="disabled")

            # Reset regression labels
            if hasattr(self, 'label_na'):
                self.label_na.config(text="A: ")
                self.label_nb.config(text="B: ")
                self.label_nc.config(text="C: ")
                self.label_sf_a.config(text="A: ")
                self.label_sf_b.config(text="B: ")

            # Update UI labels to match current mode
            self.update_ui_labels()

            self.show_notification("New file created - all data cleared", duration=2000, notif_type="success")

    def clear_all_plots(self):
        """Clear all plots and reset them to default state"""
        # Clear classic plot
        self.classic_ax.clear()
        self.classic_ax.set_xlabel('Elution Time (min)')
        self.classic_ax.set_ylabel('Concentration (g/L)')
        self.classic_ax.set_facecolor('#ffffff')
        self.classic_ax.grid(True, linestyle='--', alpha=0.7)
        self.classic_ax.set_title("Classic Elution", fontsize=14, fontweight='bold')
        self.classic_fig.tight_layout()
        self.classic_canvas.draw()

        # Clear extrusion plot
        self.extrusion_ax.clear()
        self.extrusion_ax.set_xlabel('Elution Time (min)')
        self.extrusion_ax.set_ylabel('Concentration (g/L)')
        self.extrusion_ax.set_facecolor('#ffffff')
        self.extrusion_ax.grid(True, linestyle='--', alpha=0.7)
        self.extrusion_ax.set_title("Elution-Extrusion", fontsize=14, fontweight='bold')
        self.extrusion_fig.tight_layout()
        self.extrusion_canvas.draw()

        # Clear dual plot
        self.dual_ax.clear()
        self.dual_ax.set_xlabel('Elution Time (min)')
        self.dual_ax.set_ylabel('Concentration (g/L)')
        self.dual_ax.set_facecolor('#ffffff')
        self.dual_ax.grid(True, linestyle='--', alpha=0.7)
        self.dual_ax.set_title("Dual Mode Elution", fontsize=14, fontweight='bold')
        self.dual_fig.tight_layout()
        self.dual_canvas.draw()

        # Clear multi plots
        self.multi_ax.clear()
        self.multi_ax.set_xlabel('Elution Time (min)')
        self.multi_ax.set_ylabel('Concentration (g/L)')
        self.multi_ax.set_facecolor('#ffffff')
        self.multi_ax.grid(True, linestyle='--', alpha=0.7)
        self.multi_fig.tight_layout()
        self.multi_canvas.draw()

        self.multi_pos_ax.clear()
        self.multi_pos_ax.set_xlabel('Elution Time (min)')
        self.multi_pos_ax.set_ylabel('Column Position')
        self.multi_pos_ax.set_facecolor('#ffffff')
        self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)
        self.multi_pos_fig.tight_layout()
        self.multi_pos_canvas.draw()

        # Clear pulse plot
        if hasattr(self, 'pulse_ax'):
            self.pulse_ax.clear()
            self.pulse_ax.set_xlabel('Elution Time')
            self.pulse_ax.set_ylabel('Concentration')
            self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
            self.pulse_fig.tight_layout()
            self.pulse_canvas.draw()

        # Clear fit plot
        if hasattr(self, 'fit_ax'):
            self.fit_ax.clear()
            self.fit_ax.set_xlabel('Elution Time')
            self.fit_ax.set_ylabel('Concentration')
            self.fit_ax.grid(True, linestyle='--', alpha=0.7)
            self.fit_fig.tight_layout()
            self.fit_canvas.draw()

    def clear_stored_results(self):
        """Clear all stored simulation results"""
        # Remove stored results if they exist
        if hasattr(self, 'classic_results'):
            delattr(self, 'classic_results')
        if hasattr(self, 'extrusion_results'):
            delattr(self, 'extrusion_results')
        if hasattr(self, 'dual_results'):
            delattr(self, 'dual_results')
        if hasattr(self, 'multi_results'):
            delattr(self, 'multi_results')
        if hasattr(self, 'pulse_peaks'):
            delattr(self, 'pulse_peaks')
        if hasattr(self, 'fit_peaks'):
            delattr(self, 'fit_peaks')

    def save_state(self):
        """Save complete application state including all simulation data and plots"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cup",
            filetypes=[("CUP Simulation files", "*.cup"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Create comprehensive state dictionary
                state = {
                    "version": "2.0",
                    "timestamp": datetime.now().isoformat(),
                    "gui_state": {},
                    "simulation_data": {},
                    "plot_configurations": {},
                    "application_settings": {}
                }

                # Capture each section with individual error handling
                try:
                    state["gui_state"] = self.get_gui_state()
                except Exception as e:
                    state["gui_state"] = {}

                try:
                    state["simulation_data"] = self.get_simulation_data()
                except Exception as e:
                    state["simulation_data"] = {}

                try:
                    state["plot_configurations"] = self.get_plot_configurations()
                except Exception as e:
                    state["plot_configurations"] = {}

                try:
                    state["application_settings"] = self.get_application_settings()
                except Exception as e:
                    state["application_settings"] = {}

                # Save to file with custom encoder
                with open(file_path, 'w') as f:
                    json.dump(state, f, indent=2, cls=NumpyEncoder)

                self.show_notification(f"Complete state saved: {file_path}", duration=3000, notif_type="success")

            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save state: {str(e)}")

    def get_gui_state(self):
        """Capture complete GUI state"""
        gui_state = {
            # Entry fields
            "flow_rate": self.flow_rate_entry.get(),
            "column_volume": self.column_volume_entry.get(),
            "elution_duration": self.elution_duration_entry.get(),
            "injection_volume": self.injection_volume_entry.get(),
            "dead_volume": self.dead_volume_entry.get(),

            # Duration entries for other tabs
            "extrusion_duration": getattr(self, 'extrusion_duration_entry', None) and self.extrusion_duration_entry.get(),
            "dual_duration": getattr(self, 'dual_duration_entry', None) and self.dual_duration_entry.get(),

            # Stationary phase settings
            "stationary_phase_mode": self.stationary_phase_var.get(),
            "stationary_phase_single": self.stationary_phase_single_entry.get(),
            "sf_coefficient_a": getattr(self, 'sf_coefficient_a_entry', None) and self.sf_coefficient_a_entry.get(),
            "sf_coefficient_b": getattr(self, 'sf_coefficient_b_entry', None) and self.sf_coefficient_b_entry.get(),

            # Column efficiency settings
            "column_efficiency_mode": self.column_efficiency_var.get(),
            "column_efficiency_single": self.column_efficiency_single_entry.get(),
            "n_coefficient_a": getattr(self, 'n_coefficient_a_entry', None) and self.n_coefficient_a_entry.get(),
            "n_coefficient_b": getattr(self, 'n_coefficient_b_entry', None) and self.n_coefficient_b_entry.get(),
            "n_coefficient_c": getattr(self, 'n_coefficient_c_entry', None) and self.n_coefficient_c_entry.get(),

            # Checkboxes and options
            "include_injection": self.include_injection_var.get(),
            "mobile_phase": self.mobile_phase_var.get(),
            "volume_time_mode": self.volume_time_var.get(),
            "ccc_cpc_mode": getattr(self, 'ccc_cpc_var', None) and self.ccc_cpc_var.get(),

            # Plot options for each tab
            "classic_options": {
                "sum": self.classic_sum_var.get(),
                "peaks": self.classic_peaks_var.get(),
                "grid": self.classic_grid_var.get()
            },
            "extrusion_options": {
                "sum": self.extrusion_sum_var.get(),
                "peaks": self.extrusion_peaks_var.get(),
                "lines": self.extrusion_lines_var.get(),
                "lines_labels": self.extrusion_lines_labels_var.get(),
                "grid": self.extrusion_grid_var.get()
            },
            "dual_options": {
                "sum": self.dual_sum_var.get(),
                "peaks": self.dual_peaks_var.get(),
                "lines": self.dual_lines_var.get(),
                "lines_labels": self.dual_lines_labels_var.get(),
                "grid": self.dual_grid_var.get()
            },
            "multi_options": {
                "sum": self.multi_sum_var.get(),
                "peaks": self.multi_peaks_var.get(),
                "lines": self.multi_lines_var.get(),
                "lines_labels": self.multi_lines_labels_var.get(),
                "grid": self.multi_grid_var.get()
            },

            # Table data
            "compound_data": self.get_table_data(self.compound_table),
            "switch_times_data": hasattr(self, 'switch_times_table') and self.get_table_data(self.switch_times_table),
            "pulse_data": hasattr(self, 'pulse_table') and self.get_table_data(self.pulse_table),

            # Current tab
            "current_tab": self.tab_control.index(self.tab_control.select())
        }

        return gui_state

    def get_simulation_data(self):
        """Capture all simulation results with optimized storage"""
        sim_data = {}

        # Helper function to convert numpy arrays to lists with reduced precision
        def optimize_array(arr):
            if isinstance(arr, np.ndarray):
                return np.round(arr, 6).tolist()  # Reduce precision to 6 decimal places
            elif isinstance(arr, list):
                return [optimize_array(item) for item in arr]
            else:
                return arr

        # Store simulation results with optimized arrays
        if hasattr(self, 'classic_results'):
            sim_data['classic_results'] = {
                'vspan': optimize_array(self.classic_results.get('vspan', [])),
                'cout': optimize_array(self.classic_results.get('cout', [])),
                'x': optimize_array(self.classic_results.get('x', [])),
                'y': optimize_array(self.classic_results.get('y', []))
            }

        if hasattr(self, 'extrusion_results'):
            sim_data['extrusion_results'] = {
                'vspan': optimize_array(self.extrusion_results.get('vspan', [])),
                'cout': optimize_array(self.extrusion_results.get('cout', [])),
                'xtot': optimize_array(self.extrusion_results.get('xtot', [])),
                'ytot': optimize_array(self.extrusion_results.get('ytot', [])),
                'vbc': optimize_array(self.extrusion_results.get('vbc', []))
            }

        if hasattr(self, 'dual_results'):
            sim_data['dual_results'] = {
                'vspan': optimize_array(self.dual_results.get('vspan', [])),
                'cout': optimize_array(self.dual_results.get('cout', [])),
                'xtot': optimize_array(self.dual_results.get('xtot', [])),
                'ytot': optimize_array(self.dual_results.get('ytot', []))
            }

        if hasattr(self, 'multi_results'):
            sim_data['multi_results'] = {
                'vspan': optimize_array(self.multi_results.get('vspan', [])),
                'cout': optimize_array(self.multi_results.get('cout', [])),
                'xtot': optimize_array(self.multi_results.get('xtot', [])),
                'ytot': optimize_array(self.multi_results.get('ytot', [])),
                'vbc': optimize_array(self.multi_results.get('vbc', [])),
                'vcyc': optimize_array(self.multi_results.get('vcyc', []))
            }

        # Store trace data with optimization
        if hasattr(self, 'pulse_data') and self.pulse_data:
            sim_data['pulse_data'] = {
                'X': optimize_array(self.pulse_data.get('X')),
                'Y': optimize_array(self.pulse_data.get('Y')),
                'trace_type': 'pulse'
            }

        if hasattr(self, 'fit_data') and self.fit_data:
            sim_data['fit_data'] = {
                'X': optimize_array(self.fit_data.get('X')),
                'Y': optimize_array(self.fit_data.get('Y')),
                'trace_type': 'fit'
            }

        return sim_data

    def get_plot_configurations(self):
        """Enhanced plot configuration capture with more details"""
        plot_configs = {}

        def get_legend_location(ax):
            """Safely get legend location"""
            try:
                legend = ax.get_legend()
                if legend:
                    # Try to get location from legend._loc or return 'best' as default
                    return getattr(legend, '_loc', 'best')
                return 'best'
            except:
                return 'best'

        def has_legend(ax):
            """Safely check if axis has a legend"""
            try:
                legend = ax.get_legend()
                return legend is not None and legend.get_visible()
            except:
                return False

        # Enhanced classic plot config
        plot_configs['classic'] = {
            'title': self.classic_ax.get_title(),
            'xlabel': self.classic_ax.get_xlabel(),
            'ylabel': self.classic_ax.get_ylabel(),
            'xlim': self.classic_ax.get_xlim(),
            'ylim': self.classic_ax.get_ylim(),
            'grid': self.classic_grid_var.get(),  # Use the actual checkbox state
            'facecolor': self.classic_ax.get_facecolor(),
            'legend_visible': has_legend(self.classic_ax),
            'legend_location': get_legend_location(self.classic_ax),
            'tight_layout': True
        }

        # Enhanced extrusion plot config
        plot_configs['extrusion'] = {
            'title': self.extrusion_ax.get_title(),
            'xlabel': self.extrusion_ax.get_xlabel(),
            'ylabel': self.extrusion_ax.get_ylabel(),
            'xlim': self.extrusion_ax.get_xlim(),
            'ylim': self.extrusion_ax.get_ylim(),
            'grid': self.extrusion_grid_var.get(),
            'facecolor': self.extrusion_ax.get_facecolor(),
            'legend_visible': has_legend(self.extrusion_ax),
            'legend_location': get_legend_location(self.extrusion_ax),
            'tight_layout': True
        }

        # Enhanced dual plot config
        plot_configs['dual'] = {
            'title': self.dual_ax.get_title(),
            'xlabel': self.dual_ax.get_xlabel(),
            'ylabel': self.dual_ax.get_ylabel(),
            'xlim': self.dual_ax.get_xlim(),
            'ylim': self.dual_ax.get_ylim(),
            'grid': self.dual_grid_var.get(),
            'facecolor': self.dual_ax.get_facecolor(),
            'legend_visible': has_legend(self.dual_ax),
            'legend_location': get_legend_location(self.dual_ax),
            'tight_layout': True
        }

        # Enhanced multi plot configs
        plot_configs['multi_concentration'] = {
            'title': self.multi_ax.get_title(),
            'xlabel': self.multi_ax.get_xlabel(),
            'ylabel': self.multi_ax.get_ylabel(),
            'xlim': self.multi_ax.get_xlim(),
            'ylim': self.multi_ax.get_ylim(),
            'grid': self.multi_grid_var.get(),
            'facecolor': self.multi_ax.get_facecolor(),
            'legend_visible': has_legend(self.multi_ax),
            'legend_location': get_legend_location(self.multi_ax),
            'tight_layout': True
        }

        plot_configs['multi_position'] = {
            'title': self.multi_pos_ax.get_title(),
            'xlabel': self.multi_pos_ax.get_xlabel(),
            'ylabel': self.multi_pos_ax.get_ylabel(),
            'xlim': self.multi_pos_ax.get_xlim(),
            'ylim': self.multi_pos_ax.get_ylim(),
            'grid': self.multi_grid_var.get(),
            'facecolor': self.multi_pos_ax.get_facecolor(),
            'legend_visible': has_legend(self.multi_pos_ax),
            'legend_location': get_legend_location(self.multi_pos_ax),
            'tight_layout': True
        }

        # Pulse and fit plot configs with error handling
        if hasattr(self, 'pulse_ax'):
            try:
                plot_configs['pulse'] = {
                    'title': self.pulse_ax.get_title(),
                    'xlabel': self.pulse_ax.get_xlabel(),
                    'ylabel': self.pulse_ax.get_ylabel(),
                    'xlim': self.pulse_ax.get_xlim(),
                    'ylim': self.pulse_ax.get_ylim(),
                    'grid': True,  # Default for pulse plots
                    'facecolor': self.pulse_ax.get_facecolor(),
                    'legend_visible': has_legend(self.pulse_ax),
                    'legend_location': get_legend_location(self.pulse_ax),
                    'tight_layout': True
                }
            except Exception as e:
                plot_configs['pulse'] = None

        if hasattr(self, 'fit_ax'):
            try:
                plot_configs['fit'] = {
                    'title': self.fit_ax.get_title(),
                    'xlabel': self.fit_ax.get_xlabel(),
                    'ylabel': self.fit_ax.get_ylabel(),
                    'xlim': self.fit_ax.get_xlim(),
                    'ylim': self.fit_ax.get_ylim(),
                    'grid': True,  # Default for fit plots
                    'facecolor': self.fit_ax.get_facecolor(),
                    'legend_visible': has_legend(self.fit_ax),
                    'legend_location': get_legend_location(self.fit_ax),
                    'tight_layout': True
                }
            except Exception as e:
                plot_configs['fit'] = None

        return plot_configs

    def restore_plot_configurations_with_legends(self, plot_configs):
        """Enhanced version that also restores legend settings"""

        # Call the main restore function first
        self.restore_plot_configurations(plot_configs)

        # Then handle legend restoration for each plot
        plots_and_axes = [
            ('classic', self.classic_ax, self.classic_canvas),
            ('extrusion', self.extrusion_ax, self.extrusion_canvas),
            ('dual', self.dual_ax, self.dual_canvas),
            ('multi_concentration', self.multi_ax, self.multi_canvas),
            ('multi_position', self.multi_pos_ax, self.multi_pos_canvas)
        ]

        # Add pulse and fit if they exist
        if hasattr(self, 'pulse_ax'):
            plots_and_axes.append(('pulse', self.pulse_ax, self.pulse_canvas))
        if hasattr(self, 'fit_ax'):
            plots_and_axes.append(('fit', self.fit_ax, self.fit_canvas))

        for plot_name, ax, canvas in plots_and_axes:
            if plot_name in plot_configs:
                config = plot_configs[plot_name]
                try:
                    # Restore legend if it was visible
                    legend_visible = config.get('legend_visible', False)
                    if legend_visible and ax.get_legend():
                        legend_location = config.get('legend_location', 'best')
                        ax.legend(loc=legend_location)
                    elif not legend_visible and ax.get_legend():
                        ax.get_legend().set_visible(False)

                    # Apply tight layout if specified
                    if config.get('tight_layout', True):
                        ax.figure.tight_layout()

                    # Refresh the canvas
                    canvas.draw()

                except Exception as e:
                    print(f"Error restoring {plot_name} legend: {e}")

    def get_application_settings(self):
        """Capture application-level settings"""
        return {
            "window_geometry": self.root.geometry(),
            "window_state": self.root.state(),
            "application_version": "1.0",  # Your app version
            "units_system": self.volume_time_var.get(),
            "last_simulation_run": {
                "classic": hasattr(self, 'classic_results'),
                "extrusion": hasattr(self, 'extrusion_results'),
                "dual": hasattr(self, 'dual_results'),
                "multi": hasattr(self, 'multi_results'),
                "pulse": hasattr(self, 'pulse_data'),
                "fit": hasattr(self, 'fit_data')
            }
        }

    def get_table_data(self, table):
        """Extract data from a treeview table"""
        data = []
        for item in table.get_children():
            values = table.item(item)['values']
            data.append(list(values))
        return data

    def load_state(self):
        """Load complete application state"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CUP Simulation files", "*.cup"), ("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    state = json.load(f)

                # Check version compatibility
                version = state.get('version', '1.0')
                if version == '2.0':
                    self.load_enhanced_state(state)
                else:
                    # Fallback to old format
                    self.load_legacy_state(state)

                self.show_notification(f"Complete state loaded: {file_path}", duration=3000, notif_type="success")

            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load state: {str(e)}")

    def load_enhanced_state(self, state):
        """Load enhanced save format with validation"""

        # First clear current state
        self.clear_all_plots()

        try:
            # Restore GUI state first
            gui_state = state.get('gui_state', {})
            self.restore_gui_state(gui_state)

            # Restore simulation data and regenerate plots
            sim_data = state.get('simulation_data', {})
            if sim_data:
                self.restore_simulation_data(sim_data)

            # Restore plot configurations
            plot_configs = state.get('plot_configurations', {})
            if plot_configs:
                self.restore_plot_configurations(plot_configs)

            # Restore application settings
            app_settings = state.get('application_settings', {})
            if app_settings:
                self.restore_application_settings(app_settings)

            # Switch to the saved tab
            if 'current_tab' in gui_state:
                self.switch_to_tab(gui_state['current_tab'])
                
        except Exception as e:
            print(f"Error during state restoration: {e}")
            import traceback
            traceback.print_exc()

    def restore_gui_state(self, gui_state):
        """Restore all GUI elements to saved state"""

        # Entry fields
        self.flow_rate_entry.delete(0, tk.END)
        self.flow_rate_entry.insert(0, gui_state.get('flow_rate', '5'))

        self.column_volume_entry.delete(0, tk.END)
        self.column_volume_entry.insert(0, gui_state.get('column_volume', '81'))

        self.elution_duration_entry.delete(0, tk.END)
        self.elution_duration_entry.insert(0, gui_state.get('elution_duration', '60'))

        self.injection_volume_entry.delete(0, tk.END)
        self.injection_volume_entry.insert(0, gui_state.get('injection_volume', '1'))

        self.dead_volume_entry.delete(0, tk.END)
        self.dead_volume_entry.insert(0, gui_state.get('dead_volume', '0'))

        # Duration entries for other tabs
        if hasattr(self, 'extrusion_duration_entry') and gui_state.get('extrusion_duration'):
            self.extrusion_duration_entry.delete(0, tk.END)
            self.extrusion_duration_entry.insert(0, gui_state['extrusion_duration'])

        if hasattr(self, 'dual_duration_entry') and gui_state.get('dual_duration'):
            self.dual_duration_entry.delete(0, tk.END)
            self.dual_duration_entry.insert(0, gui_state['dual_duration'])

        # Stationary phase settings
        self.stationary_phase_var.set(gui_state.get('stationary_phase_mode', 'Set Sf'))
        self.toggle_stationary()

        self.stationary_phase_single_entry.delete(0, tk.END)
        self.stationary_phase_single_entry.insert(0, gui_state.get('stationary_phase_single', '0.75'))

        if hasattr(self, 'sf_coefficient_a_entry') and gui_state.get('sf_coefficient_a'):
            self.sf_coefficient_a_entry.delete(0, tk.END)
            self.sf_coefficient_a_entry.insert(0, gui_state['sf_coefficient_a'])

        if hasattr(self, 'sf_coefficient_b_entry') and gui_state.get('sf_coefficient_b'):
            self.sf_coefficient_b_entry.delete(0, tk.END)
            self.sf_coefficient_b_entry.insert(0, gui_state['sf_coefficient_b'])

        # Column efficiency settings
        self.column_efficiency_var.set(gui_state.get('column_efficiency_mode', 'Set N'))
        self.toggle_efficiency()

        self.column_efficiency_single_entry.delete(0, tk.END)
        self.column_efficiency_single_entry.insert(0, gui_state.get('column_efficiency_single', '400'))

        if hasattr(self, 'n_coefficient_a_entry') and gui_state.get('n_coefficient_a'):
            self.n_coefficient_a_entry.delete(0, tk.END)
            self.n_coefficient_a_entry.insert(0, gui_state['n_coefficient_a'])

        if hasattr(self, 'n_coefficient_b_entry') and gui_state.get('n_coefficient_b'):
            self.n_coefficient_b_entry.delete(0, tk.END)
            self.n_coefficient_b_entry.insert(0, gui_state['n_coefficient_b'])

        if hasattr(self, 'n_coefficient_c_entry') and gui_state.get('n_coefficient_c'):
            self.n_coefficient_c_entry.delete(0, tk.END)
            self.n_coefficient_c_entry.insert(0, gui_state['n_coefficient_c'])

        # Checkboxes and variables
        self.include_injection_var.set(gui_state.get('include_injection', True))
        self.mobile_phase_var.set(gui_state.get('mobile_phase', 'Lower'))
        self.volume_time_var.set(gui_state.get('volume_time_mode', 'Time'))

        if hasattr(self, 'ccc_cpc_var') and gui_state.get('ccc_cpc_mode'):
            self.ccc_cpc_var.set(gui_state['ccc_cpc_mode'])

        # Plot options
        classic_opts = gui_state.get('classic_options', {})
        self.classic_sum_var.set(classic_opts.get('sum', False))
        self.classic_peaks_var.set(classic_opts.get('peaks', True))
        self.classic_grid_var.set(classic_opts.get('grid', True))

        extrusion_opts = gui_state.get('extrusion_options', {})
        self.extrusion_sum_var.set(extrusion_opts.get('sum', False))
        self.extrusion_peaks_var.set(extrusion_opts.get('peaks', True))
        self.extrusion_lines_var.set(extrusion_opts.get('lines', True))
        self.extrusion_lines_labels_var.set(extrusion_opts.get('lines_labels', True))
        self.extrusion_grid_var.set(extrusion_opts.get('grid', True))

        dual_opts = gui_state.get('dual_options', {})
        self.dual_sum_var.set(dual_opts.get('sum', False))
        self.dual_peaks_var.set(dual_opts.get('peaks', True))
        self.dual_lines_var.set(dual_opts.get('lines', True))
        self.dual_lines_labels_var.set(dual_opts.get('lines_labels', True))
        self.dual_grid_var.set(dual_opts.get('grid', True))

        multi_opts = gui_state.get('multi_options', {})
        self.multi_sum_var.set(multi_opts.get('sum', False))
        self.multi_peaks_var.set(multi_opts.get('peaks', True))
        self.multi_lines_var.set(multi_opts.get('lines', True))
        self.multi_lines_labels_var.set(multi_opts.get('lines_labels', True))
        self.multi_grid_var.set(multi_opts.get('grid', True))

        # Restore table data
        self.restore_table_data(self.compound_table, gui_state.get('compound_data', []))

        if hasattr(self, 'switch_times_table') and gui_state.get('switch_times_data'):
            self.restore_table_data(self.switch_times_table, gui_state['switch_times_data'])

        if hasattr(self, 'pulse_table') and gui_state.get('pulse_data'):
            self.restore_table_data(self.pulse_table, gui_state['pulse_data'])

        # Update UI labels to match current mode
        self.update_ui_labels()

    def restore_simulation_data(self, sim_data):
        """Restore simulation results and regenerate plots"""

        # Restore classic results
        if 'classic_results' in sim_data:
            self.classic_results = sim_data['classic_results']
            self.classic_ax.clear()
            self.render_classic_plot(self.classic_results, None, is_restored=True)

        # Restore extrusion results
        if 'extrusion_results' in sim_data:
            self.extrusion_results = sim_data['extrusion_results']
            self.extrusion_ax.clear()
            self.render_extrusion_plot(self.extrusion_results, None, is_restored=True)

        # Restore dual results
        if 'dual_results' in sim_data:
            self.dual_results = sim_data['dual_results']
            self.dual_ax.clear()
            self.render_dual_plot(self.dual_results, None, is_restored=True)

        # Restore multi results
        if 'multi_results' in sim_data:
            self.multi_results = sim_data['multi_results']
            self.multi_ax.clear()
            self.multi_pos_ax.clear()
            self.render_multi_plots(self.multi_results, None, is_restored=True)

        # Restore pulse data - FIX: Import properly
        if 'pulse_data' in sim_data:
            pulse_info = sim_data['pulse_data']
            self.pulse_data = {'X': pulse_info['X'], 'Y': pulse_info['Y']}
            if hasattr(self, 'pulse_ax'):
                self.pulse_ax.clear()
                self.pulse_ax.plot(pulse_info['X'], pulse_info['Y'], linewidth=2.0)
                self.pulse_ax.set_xlabel('Elution Time')
                self.pulse_ax.set_ylabel('Concentration')
                self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
                self.pulse_canvas.draw()

        # Restore fit data - FIX: Import properly
        if 'fit_data' in sim_data:
            fit_info = sim_data['fit_data']
            self.fit_data = {'X': fit_info['X'], 'Y': fit_info['Y']}
            if hasattr(self, 'fit_ax'):
                self.fit_ax.clear()
                self.fit_ax.plot(fit_info['X'], fit_info['Y'], linewidth=2.0)
                self.fit_ax.set_xlabel('Elution Time')
                self.fit_ax.set_ylabel('Concentration')
                self.fit_ax.grid(True, linestyle='--', alpha=0.7)
                self.fit_canvas.draw()

    def restore_table_data(self, table, data):
        """Restore data to a treeview table"""
        # Clear existing data
        for item in table.get_children():
            table.delete(item)

        # Insert saved data
        for row in data:
            table.insert("", "end", values=row)

    def restore_plot_configurations(self, plot_configs):
        """Restore plot axis labels, limits, and styling for all plots"""

        # Classic plot configuration
        if 'classic' in plot_configs:
            config = plot_configs['classic']
            try:
                self.classic_ax.set_title(config.get('title', 'Classic Elution'))
                self.classic_ax.set_xlabel(config.get('xlabel', 'Elution Time (min)'))
                self.classic_ax.set_ylabel(config.get('ylabel', 'Concentration (g/L)'))

                # Restore axis limits if they were manually set
                if config.get('xlim') and config['xlim'] != (0.0, 1.0):  # Avoid default matplotlib limits
                    self.classic_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.classic_ax.set_ylim(config['ylim'])

                # Restore grid state
                grid_state = config.get('grid', True)
                if grid_state:
                    self.classic_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.classic_ax.grid(False)

                # Restore background color if different from default
                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.classic_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring classic plot config: {e}")

        # Extrusion plot configuration
        if 'extrusion' in plot_configs:
            config = plot_configs['extrusion']
            try:
                self.extrusion_ax.set_title(config.get('title', 'Elution-Extrusion'))
                self.extrusion_ax.set_xlabel(config.get('xlabel', 'Elution Time (min)'))
                self.extrusion_ax.set_ylabel(config.get('ylabel', 'Concentration (g/L)'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.extrusion_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.extrusion_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.extrusion_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.extrusion_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.extrusion_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring extrusion plot config: {e}")

        # Dual mode plot configuration
        if 'dual' in plot_configs:
            config = plot_configs['dual']
            try:
                self.dual_ax.set_title(config.get('title', 'Dual Mode Elution'))
                self.dual_ax.set_xlabel(config.get('xlabel', 'Elution Time (min)'))
                self.dual_ax.set_ylabel(config.get('ylabel', 'Concentration (g/L)'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.dual_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.dual_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.dual_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.dual_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.dual_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring dual plot config: {e}")

        # Multi dual mode concentration plot configuration
        if 'multi_concentration' in plot_configs:
            config = plot_configs['multi_concentration']
            try:
                self.multi_ax.set_title(config.get('title', 'Multiple Dual Mode - Concentration'))
                self.multi_ax.set_xlabel(config.get('xlabel', 'Elution Time (min)'))
                self.multi_ax.set_ylabel(config.get('ylabel', 'Concentration (g/L)'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.multi_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.multi_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.multi_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.multi_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.multi_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring multi concentration plot config: {e}")

        # Multi dual mode position plot configuration
        if 'multi_position' in plot_configs:
            config = plot_configs['multi_position']
            try:
                self.multi_pos_ax.set_title(config.get('title', 'Multiple Dual Mode - Position'))
                self.multi_pos_ax.set_xlabel(config.get('xlabel', 'Elution Time (min)'))
                self.multi_pos_ax.set_ylabel(config.get('ylabel', 'Column Position'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.multi_pos_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.multi_pos_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.multi_pos_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.multi_pos_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring multi position plot config: {e}")

        # Pulse test plot configuration
        if 'pulse' in plot_configs and hasattr(self, 'pulse_ax'):
            config = plot_configs['pulse']
            try:
                self.pulse_ax.set_title(config.get('title', 'Pulse Test'))
                self.pulse_ax.set_xlabel(config.get('xlabel', 'Elution Time'))
                self.pulse_ax.set_ylabel(config.get('ylabel', 'Concentration'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.pulse_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.pulse_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.pulse_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.pulse_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring pulse plot config: {e}")

        # Trace fitting plot configuration
        if 'fit' in plot_configs and hasattr(self, 'fit_ax'):
            config = plot_configs['fit']
            try:
                self.fit_ax.set_title(config.get('title', 'Trace Fitting'))
                self.fit_ax.set_xlabel(config.get('xlabel', 'Elution Time'))
                self.fit_ax.set_ylabel(config.get('ylabel', 'Concentration'))

                if config.get('xlim') and config['xlim'] != (0.0, 1.0):
                    self.fit_ax.set_xlim(config['xlim'])
                if config.get('ylim') and config['ylim'] != (0.0, 1.0):
                    self.fit_ax.set_ylim(config['ylim'])

                grid_state = config.get('grid', True)
                if grid_state:
                    self.fit_ax.grid(True, linestyle='--', alpha=0.7)
                else:
                    self.fit_ax.grid(False)

                facecolor = config.get('facecolor', '#ffffff')
                if facecolor != '#ffffff':
                    self.fit_ax.set_facecolor(facecolor)

            except Exception as e:
                print(f"Error restoring fit plot config: {e}")

        # Refresh all canvases to show the restored configurations
        try:
            self.classic_canvas.draw()
            self.extrusion_canvas.draw()
            self.dual_canvas.draw()
            self.multi_canvas.draw()
            self.multi_pos_canvas.draw()

            # Only draw pulse and fit canvases if they exist
            if hasattr(self, 'pulse_canvas'):
                self.pulse_canvas.draw()
            if hasattr(self, 'fit_canvas'):
                self.fit_canvas.draw()

        except Exception as e:
            print(f"Error refreshing canvases: {e}")

    def restore_application_settings(self, app_settings):
        """Restore application-level settings"""

        # Restore window geometry if desired
        geometry = app_settings.get('window_geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except:
                pass  # Ignore if geometry is invalid

    def show_about(self):
        """Display about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About CUP Modeler")
        about_window.geometry("500x260")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()

        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (250)
        y = (about_window.winfo_screenheight() // 2) - (130)
        about_window.geometry(f"500x260+{x}+{y}")

        # Get the window's background color
        window_bg = about_window.cget('bg')

        # Title
        title_label = tk.Label(about_window, text="CUP Modeler",
                               font=("Arial", 24, "bold"),
                               bg=window_bg)
        title_label.pack(pady=20)

        subtitle_label = tk.Label(about_window, text="Liquid-liquid chromatography modeling application",
                                  font=("Arial", 18),
                                  bg=window_bg)
        subtitle_label.pack()

        # Version
        version_label = tk.Label(about_window, text="Version 1.0",
                                 font=("Arial", 18),
                                 bg=window_bg)
        version_label.pack()

        # Citation info
        citation_frame = ttk.Frame(about_window)
        citation_frame.pack(pady=10)

        citation_label = tk.Label(citation_frame, text="To learn more, ",
                                  font=("Arial", 12),
                                  bg=window_bg)
        citation_label.pack(side="left")

        # Create clickable link
        link_label = tk.Label(citation_frame, text="check out our work.",
                              font=("Arial", 12), foreground="blue",
                              cursor="hand2",
                              bg=window_bg)
        link_label.pack(side="left")
        link_label.bind("<Button-1>", lambda e: webbrowser.open(
            "https://www.sciencedirect.com/science/article/pii/S1383586621020347"))

        # Credits
        credits_label = tk.Label(about_window,
                                 text="Mathematical modeling by Hoon Choi. Interface by Manar Alherech.",
                                 font=("Arial", 12),
                                 bg=window_bg)
        credits_label.pack(pady=10)

        # Close button
        close_button = ttk.Button(about_window, text="Close",
                                  command=about_window.destroy)
        close_button.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppV1(root)
    root.mainloop()
