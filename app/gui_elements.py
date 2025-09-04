import uuid
import platform
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .undo_manager import UndoManager


class GUIElementsMixin:
    def create_menu(self):
        """Create the menu bar"""
        # Detect the operating system
        system = platform.system()

        # Set the appropriate modifier key
        if system == "Darwin":  # macOS
            modifier = "Command"
        else:  # Windows, Linux, etc.
            modifier = "Control"

        self.keyboard_modifier = modifier

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", accelerator=f"{modifier}+N", command=self.clear_all_data)
        self.file_menu.add_command(label="Save", accelerator=f"{modifier}+S", command=self.save_state)
        self.file_menu.add_command(label="Open", accelerator=f"{modifier}+O", command=self.load_state)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Info", accelerator=f"{modifier}+I", command=self.show_shortcuts_help)
        self.file_menu.add_command(label="About", command=self.show_about)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Run Current Simulation", accelerator=f"{modifier}+R", command=self.run_current_simulation)
        self.edit_menu.add_command(label="Update All Computed Simulations", accelerator=f"{modifier}+E", command=self.refresh_all_plots)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", accelerator=f"{modifier}+Z", command=self.undo_last_action)
        self.edit_menu.add_command(label="Redo", accelerator=f"{modifier}+Y", command=self.redo_last_action)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Add Compound", accelerator=f"{modifier}+=", command=self.add_compound)
        self.edit_menu.add_command(label="Remove Compound", accelerator=f"{modifier}+-", command=self.remove_compound)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Toggle Volume/Time", accelerator=f"{modifier}+T", command=self.toggle_volume_time)

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
                                                           validation_params={'allow_zero': False, 'default_value': 5, 'min_val': 0, 'allow_negative': False},
                                                           width=5
                                                           )
        self.flow_rate_entry.grid(row=row, column=1, sticky="w", padx=(0, 0))
        self.flow_rate_entry.insert(0, "5")
        ttk.Label(self.column_properties_frame, text="mL/min").grid(row=row, column=2, sticky="w", padx=(0, 15))

        ttk.Label(self.column_properties_frame, text="Column\nVolume").grid(row=row, column=3, sticky="w", padx=(0, 5))
        self.column_volume_entry = self.create_validated_entry(self.column_properties_frame,
                                                               validation_params={'allow_zero': False, 'default_value': 81, 'min_val': 0},
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
                                                                  validation_params={'allow_zero': False, 'default_value': 10, 'min_val': 0},
                                                                  width=5
                                                                  )
        self.elution_duration_entry.grid(row=row, column=1, sticky="w", padx=(0, 5), pady=(10, 0))
        self.elution_duration_entry.insert(0, "60")
        self.elution_unit_label = ttk.Label(self.column_properties_frame, text="min")
        self.elution_unit_label.grid(row=row, column=2, sticky="w", padx=(0, 15), pady=(10, 0))

        ttk.Label(self.column_properties_frame, text="Injection\nVolume").grid(row=row, column=3, sticky="w", padx=(0, 5), pady=(10, 0))
        self.injection_volume_entry = self.create_validated_entry(self.column_properties_frame,
                                                                  validation_params={'allow_zero': False, 'default_value': 1, 'min_val': 0},
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
                                                     state="readonly"
                                                     )
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

        # Initially hide coefficient fields
        self.hide_sf_coefficients()
        self.hide_n_coefficients()

        # Connect coefficient fields to recalculating single entries
        self.bind_update_events()

    def create_compound_list(self):
        """Create the compound list section using grid"""
        # Header
        header_label = ttk.Label(self.left_frame, text="Compound List",
                                 font=("Arial", 18, "bold")
                                 )
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
                                           show="headings", height=8
                                           )

        # Configure columns
        self.compound_table.heading("Compound", text="Compound")
        self.compound_table.heading("KD", text="KD")
        self.compound_table.heading("Conc", text="Conc. (g/L)")
        self.compound_table.heading("RetTime", text="Ret. Time (min)")
        self.compound_table.column("Compound", width=120, anchor='center')
        self.compound_table.column("KD", width=60, anchor='center')
        self.compound_table.column("Conc", width=80, anchor='center')
        self.compound_table.column("RetTime", width=100, anchor='center')

        # Place table
        self.compound_table.grid(row=0, column=0, sticky="nsew")

        # Initialize undo manager
        self.undo_manager = UndoManager()

        # Add initial data with unique IDs
        self.add_compound_with_undo("Compound 1", "1", "1", "0")
        self.add_compound_with_undo("Compound 2", "2", "1", "0")

        # Button frame
        button_frame = ttk.Frame(self.compound_list_frame)
        button_frame.grid(row=1, column=0, sticky="ew")

        # Buttons
        ttk.Button(button_frame, text="+", width=2, command=self.add_compound).grid(row=0, column=0, padx=(0, 0))
        ttk.Button(button_frame, text="-", width=2, command=self.remove_compound).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Save", width=5, command=self.save_compounds).grid(row=0, column=2, padx=(0, 0))
        ttk.Button(button_frame, text="Open", width=5, command=self.open_compounds).grid(row=0, column=3, padx=(0, 10))

        ttk.Label(button_frame, text="Mobile\nPhase").grid(row=0, column=4, sticky="w", padx=(0, 0))
        self.mobile_phase_var = tk.StringVar(value="Lower")
        self.mobile_phase_switch = ttk.Combobox(button_frame,
                                                textvariable=self.mobile_phase_var,
                                                values=["Lower", "Upper"],
                                                width=5,
                                                state="readonly")
        self.mobile_phase_switch.grid(row=0, column=5, sticky="w", padx=(0, 10))

        ttk.Label(button_frame, text="X-Axis").grid(row=0, column=6, padx=(0, 0), sticky="w")
        self.volume_time_var = tk.StringVar(value="Time")
        self.volume_time_switch = ttk.Combobox(button_frame,
                                               textvariable=self.volume_time_var,
                                               values=["Time", "Volume"],
                                               width=5,
                                               state="readonly"
                                               )
        self.volume_time_switch.grid(row=0, column=7, sticky="w", padx=(0, 0))
        self.volume_time_switch.bind("<<ComboboxSelected>>", self.toggle_volume_time)

        # Bind double-click to edit table cells and delete/backspace keys to remove compounds
        self.compound_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'compound'))
        self.compound_table.bind('<Delete>', lambda e: self.table_delete(e, self.remove_compound))
        self.compound_table.bind('<BackSpace>', lambda e: self.table_delete(e, self.remove_compound))

    def create_notification_area(self):
        """Create the notification display area"""
        try:
            # Create notification frame at the bottom of the main window
            self.notification_frame = ttk.Frame(self.root)
            self.notification_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

            # Configure grid weight
            self.root.grid_rowconfigure(1, weight=0)

            # Create notification label
            self.notification_label = ttk.Label(
                self.notification_frame,
                text="Ready",
                foreground="gray",
                font=("Arial", 9)
            )
            self.notification_label.pack(side="left", padx=5)

            # Create status indicator
            self.status_indicator = ttk.Label(
                self.notification_frame,
                text="●",
                foreground="green",
                font=("Arial", 12)
            )
            self.status_indicator.pack(side="right", padx=5)

        except Exception as e:
            self.show_notification(f"Failed to create notification area {e}.",
                                   duration=2000,
                                   notif_type="error"
                                   )

    def show_notification(self, message, duration=2000, notif_type="info"):
        """
        Show a notification message

        Args:
            message: The message to display
            duration: How long to show the message (ms)
            notif_type: Type of notification (info, success, warning, error)
        """
        try:
            # Color scheme for different notification types
            colors = {
                "info": {"fg": "blue", "status": "blue"},
                "success": {"fg": "green", "status": "green"},
                "warning": {"fg": "orange", "status": "orange"},
                "error": {"fg": "red", "status": "red"}
            }

            color_scheme = colors.get(notif_type, colors["info"])

            # Create notification area if it doesn't exist
            if not hasattr(self, 'notification_label') or self.notification_label is None:
                self.create_notification_area()

            # Update notification label
            if self.notification_label:
                self.notification_label.config(
                    text=message,
                    foreground=color_scheme["fg"]
                )

                # Update status indicator
                if hasattr(self, 'status_indicator'):
                    self.status_indicator.config(foreground=color_scheme["status"])

            # Also print to console for debugging
            prefix = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "❌"}.get(notif_type, "•")
            print(f"{prefix} {message}")

        except Exception as e:
            # Fallback to console if GUI notification fails
            print(f"Notification failed: {e}")
            print(f"Original message: {message}")

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
        self.classic_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0', constrained_layout=True)
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
        self.extrusion_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0', constrained_layout=True)
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
                                                                    validation_params={'allow_zero': False, 'default_value': 10, 'min_val': 0},
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
        self.dual_fig = plt.Figure(figsize=(8, 6), dpi=100, facecolor='#f0f0f0', constrained_layout=True)
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
                                                               validation_params={'allow_zero': False, 'default_value': 10, 'min_val': 0},
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
                                               show="headings", height=8
                                               )
        self.switch_times_table.heading("Iteration", text="Iteration")
        self.switch_times_table.heading("min", text="min")
        self.switch_times_table.column("Iteration", width=80, anchor='center')
        self.switch_times_table.column("min", width=60, anchor='center')
        self.switch_times_table.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Initial data for switching times
        # Add default cycles with unique IDs
        default_cycles = [
            ["Cycle 1", "10"],
            ["Cycle 2", "5"]
        ]

        for cycle_data in default_cycles:
            unique_id = str(uuid.uuid4())
            self.switch_times_table.insert('', 'end', iid=unique_id, values=cycle_data)

        self.switch_times_table.bind("<Double-1>", lambda e: self.start_inline_edit(e, 'switch_time'))

        # Buttons for managing switching times
        switch_button_frame = ttk.Frame(switch_frame)
        switch_button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Configure grid to center the buttons
        switch_button_frame.grid_columnconfigure(0, weight=1)
        switch_button_frame.grid_columnconfigure(1, weight=0)
        switch_button_frame.grid_columnconfigure(2, weight=0)
        switch_button_frame.grid_columnconfigure(3, weight=1)

        ttk.Button(switch_button_frame, text="+", width=3,
                   command=self.add_cycle).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(switch_button_frame, text="-", width=3,
                   command=self.remove_cycle).grid(row=0, column=1)

        ttk.Button(switch_button_frame, text="Save", width=4,
                   command=self.save_switch_times).grid(row=0, column=2, padx=(5, 5))
        ttk.Button(switch_button_frame, text="Open", width=4,
                   command=self.open_switch_times).grid(row=0, column=3)

        # Plots area (right side)
        plots_frame = ttk.Frame(content_frame)
        plots_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        plots_frame.grid_rowconfigure(0, weight=1)  # Top plot
        plots_frame.grid_rowconfigure(1, weight=1)  # Bottom plot
        plots_frame.grid_columnconfigure(0, weight=1)

        # Top plot - concentration
        self.multi_fig = plt.Figure(figsize=(8, 3.2), dpi=100, facecolor='#f0f0f0', constrained_layout=True)
        self.multi_ax = self.multi_fig.add_subplot(111)
        self.multi_ax.set_xlabel('Elution Time (min)')
        self.multi_ax.set_ylabel('Concentration (g/L)')
        self.multi_ax.set_facecolor('#ffffff')
        self.multi_ax.grid(True, linestyle='--', alpha=0.7)

        # Bottom plot - position contour
        self.multi_pos_fig = plt.Figure(figsize=(8, 3.2), dpi=100, facecolor='#f0f0f0', constrained_layout=True)
        self.multi_pos_ax = self.multi_pos_fig.add_subplot(111)
        self.multi_pos_ax.set_xlabel('Elution Time (min)')
        self.multi_pos_ax.set_ylabel('Column Position')
        self.multi_pos_ax.set_facecolor('#ffffff')
        self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)

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

        self.switch_times_table.bind('<Delete>', lambda e: self.table_delete(e, self.remove_cycle))
        self.switch_times_table.bind('<BackSpace>', lambda e: self.table_delete(e, self.remove_cycle))

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

        self.pulse_fig = plt.Figure(figsize=(6, 4), dpi=100, constrained_layout=True)
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
        self.pulse_columns = ("Flow Rate", "Sf", "N")
        self.pulse_table = ttk.Treeview(table_frame, columns=self.pulse_columns,
                                        show="headings", height=8)

        for col in self.pulse_columns:
            self.pulse_table.heading(col, text=col)
            self.pulse_table.column(col, width=70, anchor='center')

        self.pulse_table.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Pulse list table save/open button frame
        pulse_button_frame = ttk.Frame(right_panel)
        pulse_button_frame.grid(row=2, column=0, sticky="s", pady=(10, 0))
        pulse_button_frame.grid_rowconfigure(0, weight=1)
        pulse_button_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(pulse_button_frame, text="Add N", width=6,
                   command=self.add_n_value).pack(side="left", padx=(2, 2))

        ttk.Button(pulse_button_frame, text="Remove", width=6,
                   command=self.remove_n_value).pack(side="left", padx=(2, 2))

        ttk.Button(pulse_button_frame, text="Save", width=6,
                   command=self.save_pulse_list).pack(side="left", padx=(2, 2))

        ttk.Button(pulse_button_frame, text="Open", width=6,
                   command=self.open_pulse_list).pack(side="left", padx=(2, 2))

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
        self.pulse_span_entry = self.create_validated_entry(control_frame,
                                                            validation_params={
                                                                'integer_only': True,
                                                                'allow_zero': False,
                                                                'min_val': 3,  # Minimum for Savgol filter
                                                                'default_value': '40'
                                                            },
                                                            width=4)
        self.pulse_span_entry.grid(row=0, column=col, padx=(0, 20))
        self.pulse_span_entry.insert(0, "40")
        col += 1

        ttk.Label(control_frame, text="Prominence").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.pulse_prominence_entry = self.create_validated_entry(control_frame,
                                                                  validation_params={
                                                                      'allow_zero': False,
                                                                      'min_val': 0.1,
                                                                      'default_value': '10'},
                                                                  width=4
                                                                  )
        self.pulse_prominence_entry.grid(row=0, column=col, padx=(0, 20))
        self.pulse_prominence_entry.insert(0, "10")
        col += 1

        ttk.Label(control_frame, text="Baseline").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.pulse_baseline_var = tk.DoubleVar(value=5)
        ttk.Entry(control_frame, textvariable=self.pulse_baseline_var, width=4).grid(row=0, column=col, padx=(0, 60))
        col += 1

        ttk.Button(control_frame, text="Find Peak",
                   command=self.find_pulse_peaks).grid(row=0, column=col, padx=(0, 10))

        # Bind keyboard shortcuts for deletion
        self.pulse_table.bind('<Delete>', lambda e: self.table_delete(e, self.remove_n_value))
        self.pulse_table.bind('<BackSpace>', lambda e: self.table_delete(e, self.remove_n_value))

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
        self.fit_fig = plt.Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
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
        self.fit_span_entry = self.create_validated_entry(control_frame,
                                                          validation_params={
                                                              'integer_only': True,
                                                              'allow_zero': False,
                                                              'min_val': 3,  # Minimum for Savgol filter
                                                              'default_value': '40'
                                                            },
                                                          width=4)
        self.fit_span_entry.grid(row=0, column=col, padx=(0, 20))
        self.fit_span_entry.insert(0, "40")
        col += 1

        ttk.Label(control_frame, text="Prominence").grid(row=0, column=col, padx=(0, 5))
        col += 1
        self.fit_prominence_entry = self.create_validated_entry(control_frame,
                                                                validation_params={
                                                                    'allow_zero': False,
                                                                    'min_val': 0.1,
                                                                    'default_value': '10'},
                                                                width=4
                                                                )
        self.fit_prominence_entry.grid(row=0, column=col, padx=(0, 20))
        self.fit_prominence_entry.insert(0, "10")
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
        modifier = self.keyboard_modifier

        # File operations
        self.root.bind(f"<{modifier}-n>", lambda e: self.clear_all_data())           # Ctrl+N: New/Clear
        self.root.bind(f"<{modifier}-s>", lambda e: self.save_state())               # Ctrl+S: Save
        self.root.bind(f"<{modifier}-o>", lambda e: self.load_state())               # Ctrl+O: Open/Load
        self.root.bind(f"<{modifier}-i>", lambda e: self.show_shortcuts_help())      # Ctrl+I: Help

        # Simulation shortcuts
        self.root.bind(f"<{modifier}-r>", lambda e: self.run_current_simulation())   # Ctrl+R: Run current simulation
        self.root.bind(f"<{modifier}-e>", lambda e: self.refresh_all_plots())        # Ctrl+E: Update run simulations

        # Tab navigation
        self.root.bind(f"<{modifier}-Key-1>", lambda e: self.switch_to_tab(0) or "break")          # Ctrl+1: Classic
        self.root.bind(f"<{modifier}-Key-2>", lambda e: self.switch_to_tab(1) or "break")          # Ctrl+2: Extrusion
        self.root.bind(f"<{modifier}-Key-3>", lambda e: self.switch_to_tab(2) or "break")          # Ctrl+3: Dual Mode
        self.root.bind(f"<{modifier}-Key-4>", lambda e: self.switch_to_tab(3) or "break")          # Ctrl+4: Multiple Dual
        self.root.bind(f"<{modifier}-Key-5>", lambda e: self.switch_to_tab(4) or "break")          # Ctrl+5: Pulse Test
        self.root.bind(f"<{modifier}-Key-6>", lambda e: self.switch_to_tab(5) or "break")          # Ctrl+6: Trace Fitting

        # Data entry shortcuts
        self.root.bind(f"<{modifier}-equal>", lambda e: self.add_compound())         # Ctrl+=: Add compound
        self.root.bind(f"<{modifier}-minus>", lambda e: self.remove_compound())      # Ctrl+-: Remove compound

        self.root.bind(f"<{modifier}-t>", lambda e: self.toggle_volume_time())       # Ctrl+T to toggle units

        # Undo/Redo shortcuts
        self.root.bind(f"<{modifier}-z>", lambda e: self.undo_last_action())         # Ctrl+Z for undo
        self.root.bind(f"<{modifier}-y>", lambda e: self.redo_last_action())         # Ctrl+Y for redo or
        self.root.bind(f"<{modifier}-Shift-Z>", lambda e: self.redo_last_action())   # Ctrl+Shift+Z for redo
