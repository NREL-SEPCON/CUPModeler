import csv
import json
import numpy as np
import pandas as pd
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_pdf import PdfPages


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


class StateManagementMixin:
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
        self.classic_ax.set_title("")
        self.classic_canvas.draw()

        # Clear extrusion plot
        self.extrusion_ax.clear()
        self.extrusion_ax.set_xlabel('Elution Time (min)')
        self.extrusion_ax.set_ylabel('Concentration (g/L)')
        self.extrusion_ax.set_facecolor('#ffffff')
        self.extrusion_ax.grid(True, linestyle='--', alpha=0.7)
        self.extrusion_ax.set_title("")
        self.extrusion_canvas.draw()

        # Clear dual plot
        self.dual_ax.clear()
        self.dual_ax.set_xlabel('Elution Time (min)')
        self.dual_ax.set_ylabel('Concentration (g/L)')
        self.dual_ax.set_facecolor('#ffffff')
        self.dual_ax.grid(True, linestyle='--', alpha=0.7)
        self.dual_ax.set_title("")
        self.dual_canvas.draw()

        # Clear multi plots
        self.multi_ax.clear()
        self.multi_ax.set_xlabel('Elution Time (min)')
        self.multi_ax.set_ylabel('Concentration (g/L)')
        self.multi_ax.set_facecolor('#ffffff')
        self.multi_ax.grid(True, linestyle='--', alpha=0.7)
    
        self.multi_canvas.draw()

        self.multi_pos_ax.clear()
        self.multi_pos_ax.set_xlabel('Elution Time (min)')
        self.multi_pos_ax.set_ylabel('Column Position')
        self.multi_pos_ax.set_facecolor('#ffffff')
        self.multi_pos_ax.grid(True, linestyle='--', alpha=0.7)
        self.multi_pos_canvas.draw()

        # Clear pulse plot
        if hasattr(self, 'pulse_ax'):
            self.pulse_ax.clear()
            self.pulse_ax.set_xlabel('Elution Time')
            self.pulse_ax.set_ylabel('Concentration')
            self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
            self.pulse_canvas.draw()

        # Clear fit plot
        if hasattr(self, 'fit_ax'):
            self.fit_ax.clear()
            self.fit_ax.set_xlabel('Elution Time')
            self.fit_ax.set_ylabel('Concentration')
            self.fit_ax.grid(True, linestyle='--', alpha=0.7)
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
            'constrained_layout': True
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
            'constrained_layout': True
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
            'constrained_layout': True
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
            'constrained_layout': True
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
            'constrained_layout': True
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
                    'constrained_layout': True
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
                    'constrained_layout': True
                }
            except Exception as e:
                plot_configs['fit'] = None

        return plot_configs

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
            self.notification(f"Error restoring state: {e}", duration=2000, notif_type="error")
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
            try:
                self.plot_classic()
            except Exception as e:
                self.show_notification(f"Error regenerating classic plot: {e}", duration=2000, notif_type="error")

        # Restore extrusion results
        if 'extrusion_results' in sim_data:
            self.extrusion_results = sim_data['extrusion_results']
            try:
                self.plot_extrusion()
            except Exception as e:
                self.show_notification(f"Error regenerating extrusion plot: {e}", duration=2000, notif_type="error")

        # Restore dual results
        if 'dual_results' in sim_data:
            self.dual_results = sim_data['dual_results']
            try:
                self.plot_dual()
            except Exception as e:
                self.show_notification(f"Error regenerating dual plot: {e}", duration=2000, notif_type="error")

        # Restore multi results
        if 'multi_results' in sim_data:
            self.multi_results = sim_data['multi_results']
            try:
                self.plot_multi()
            except Exception as e:
                self.show_notification(f"Error regenerating multi plot: {e}", duration=2000, notif_type="error")

        # Restore pulse data
        if 'pulse_data' in sim_data:
            pulse_info = sim_data['pulse_data']
            self.pulse_data = {'X': np.array(pulse_info['X']), 'Y': np.array(pulse_info['Y'])}
            if hasattr(self, 'pulse_ax'):
                try:
                    self.pulse_ax.clear()
                    self.pulse_ax.plot(pulse_info['X'], pulse_info['Y'], linewidth=2.0)
                    self.pulse_ax.set_xlabel('Elution Time')
                    self.pulse_ax.set_ylabel('Concentration')
                    self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
                    self.pulse_canvas.draw()
                except Exception as e:
                    self.show_notification(f"Error regenerating pulse plot: {e}", duration=2000, notif_type="error")

        # Restore fit data
        if 'fit_data' in sim_data:
            fit_info = sim_data['fit_data']
            self.fit_data = {'X': np.array(fit_info['X']), 'Y': np.array(fit_info['Y'])}
            if hasattr(self, 'fit_ax'):
                try:
                    self.fit_ax.clear()
                    self.fit_ax.plot(fit_info['X'], fit_info['Y'], linewidth=2.0)
                    self.fit_ax.set_xlabel('Elution Time')
                    self.fit_ax.set_ylabel('Concentration')
                    self.fit_ax.grid(True, linestyle='--', alpha=0.7)
                    self.fit_canvas.draw()
                except Exception as e:
                    self.show_notification(f"Error regenerating fit plot: {e}", duration=2000, notif_type="error")

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
                self.classic_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring classic plot config: {e}", duration=2000, notif_type="error")

        # Extrusion plot configuration
        if 'extrusion' in plot_configs:
            config = plot_configs['extrusion']
            try:
                self.extrusion_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring extrusion plot config: {e}", duration=2000, notif_type="error")

        # Dual mode plot configuration
        if 'dual' in plot_configs:
            config = plot_configs['dual']
            try:
                self.dual_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring dual plot config: {e}", duration=2000, notif_type="error")

        # Multi dual mode concentration plot configuration
        if 'multi_concentration' in plot_configs:
            config = plot_configs['multi_concentration']
            try:
                self.multi_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring multi concentration plot config: {e}", duration=2000, notif_type="error")

        # Multi dual mode position plot configuration
        if 'multi_position' in plot_configs:
            config = plot_configs['multi_position']
            try:
                self.multi_pos_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring multi position plot config: {e}", duration=2000, notif_type="error")

        # Pulse test plot configuration
        if 'pulse' in plot_configs and hasattr(self, 'pulse_ax'):
            config = plot_configs['pulse']
            try:
                self.pulse_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring pulse plot config: {e}", duration=2000, notif_type="error")

        # Trace fitting plot configuration
        if 'fit' in plot_configs and hasattr(self, 'fit_ax'):
            config = plot_configs['fit']
            try:
                self.fit_ax.set_title(config.get('title', ''))
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
                self.show_notification(f"Error restoring fit plot config: {e}", duration=2000, notif_type="error")

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
            self.show_notification(f"Error refreshing canvases: {e}", duration=2000, notif_type="error")

    def restore_application_settings(self, app_settings):
        """Restore application-level settings"""

        # Restore window geometry if desired
        geometry = app_settings.get('window_geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except:
                pass  # Ignore if geometry is invalid

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
            parameters = self._extract_parameters_from_gui()
            compounds = self._extract_compounds_from_gui()

            # Process volume/time data consistently
            vspan = results['vspan']
            cout = results['cout']

            # Convert to time if needed
            if parameters.volume_time_mode.value == "Time":
                x_values = vspan / parameters.flow_rate
                x_label = 'Time (min)'
            else:
                x_values = vspan
                x_label = 'Volume (mL)'

            # Prepare main data
            data_dict = {x_label: x_values}
            for i, compound in enumerate(compounds):
                data_dict[compound.name] = cout[i]

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
                    'Injection Volume (mL)',
                    'Volume/Time Mode'
                ],
                'Value': [
                    mode.title(),
                    f"{parameters.flow_rate:.2f}",
                    f"{parameters.column_volume:.2f}",
                    f"{parameters.get_effective_sf():.4f}",
                    f"{parameters.get_effective_n():.0f}",
                    f"{parameters.elution_duration:.2f}",
                    f"{parameters.get_vcm():.2f}",
                    f"{parameters.injection_volume:.2f}",
                    parameters.volume_time_mode.value
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
                            'Compound': comp.name,
                            'KD': comp.kd,
                            'Concentration (g/L)': comp.concentration,
                            'Retention Time/Volume': comp.retention_time
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
            base_filename = filename.rsplit('.', 1)[0]  # Remove file extension
            plot_filename = f"{base_filename}_plot.pdf"
            self.export_plot(mode, plot_filename)

            self.show_notification(f"{mode.title()} data exported successfully!", duration=2000, notif_type="success")

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
            self.show_notification(f"Error exporting {mode} plot: {str(e)}", duration=2000, notif_type="error")

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
                writer.writerow(['Flow Rate', 'Sf', 'N'])

                for item in self.pulse_table.get_children():
                    writer.writerow(self.pulse_table.item(item, 'values'))

            self.show_notification("Pulse test list saved successfully", duration=2000, notif_type="success")
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

            self.show_notification("Pulse list loaded successfully", duration=2000, notif_type="success")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading pulse list: {str(e)}")
