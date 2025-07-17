import csv
import uuid
import webbrowser
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .undo_manager import EditCellCommand, DeleteRowCommand, AddRowCommand


class InterfaceControlsMixin:
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

        # Toggle to the opposite mode
        if was_volume_mode:
            new_mode = "Time"
            will_be_volume_mode = False
        else:
            new_mode = "Volume"
            will_be_volume_mode = True

        # Update the combobox to reflect the new mode
        self.volume_time_switch.set(new_mode)
        self.volume_time_var.set(new_mode)

        # Perform the conversion
        self.convert_all_values(was_volume_mode, will_be_volume_mode, flow_rate)

        # Update UI labels AFTER conversion
        self.update_ui_labels()

        # Update all plots
        self.refresh_all_plots()

        # Show success notification
        direction = "Volume → Time" if was_volume_mode and not will_be_volume_mode else "Time → Volume"
        self.show_notification(f"Converted all values: {direction}", duration=2000, notif_type="info")

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

        # Convert elution duration
        try:
            current_elution = float(self.elution_duration_entry.get())

            if was_volume_mode and not is_volume_mode:  # Volume to Time
                new_elution = current_elution / flow_rate
            else:  # Time to Volume
                new_elution = current_elution * flow_rate

            self.elution_duration_entry.delete(0, tk.END)
            self.elution_duration_entry.insert(0, f"{new_elution:.2f}")

        except ValueError as e:
            self.show_notification(f"Failed to convert elution: {e}", notif_type="error")

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
            except ValueError as e:
                self.show_notification(f"Failed to convert extrusion: {e}", notif_type="error")
        else:
            self.show_notification("No extrusion duration found", notif_type="error")

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
            except ValueError as e:
                self.show_notification(f"Failed to convert dual mode: {e}", notif_type="error")
        else:
            self.show_notification("No dual duration found", notif_type="error")

    def convert_all_values(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert all time/volume values in the application"""

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
            else:  # Time to Volume
                new_value = current_value * flow_rate

            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f"{new_value:.2f}")

        except ValueError as e:
            self.show_notification(f"Failed to convert {field_name}: {e}", notif_type="error")

    def convert_compound_retention_times(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert retention times in the compound table"""

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

            except (ValueError, IndexError) as e:
                self.show_notification(f"Failed to convert compound {current_values[0] if current_values else 'unknown'}: {e}", notif_type="error")

    def convert_switch_times(self, was_volume_mode, is_volume_mode, flow_rate):
        """Convert switch times in the multiple dual mode table"""

        if not hasattr(self, 'switch_times_table'):
            self.show_notification("Switch times table not found", notif_type="warning")
            return

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

            except (ValueError, IndexError) as e:
                self.show_notification(f"Failed to convert switch time {current_values[0] if current_values else 'unknown'}: {e}", notif_type="error")

    def switch_to_tab(self, tab_index):
        """Switch to specified tab by index"""

        try:
            # Get all tabs - these are the actual widget references
            tabs = self.tab_control.tabs()

            if 0 <= tab_index < len(tabs):
                # Get current tab before switching
                current_tab = self.tab_control.index(self.tab_control.select())

                # Use the actual tab widget reference, not the index
                self.tab_control.select(tabs[tab_index])

                # Verify the switch worked
                new_tab = self.tab_control.index(self.tab_control.select())

                # Updated tab names to match your actual tabs
                tab_names = [
                    "Classic Elution",           # Tab 0
                    "Elution-Extrusion",         # Tab 1
                    "Dual Mode",                 # Tab 2
                    "Multiple Dual Mode",        # Tab 3
                    "Pulse Test",                # Tab 4
                    "Trace Fitting"              # Tab 5
                ]

                if tab_index < len(tab_names):
                    self.show_notification(f"Switched to {tab_names[tab_index]}", duration=1000)
            else:
                self.show_notification(f"Invalid tab index: {tab_index}. Available indicies: 1-6.", notif_type="error")

        except AttributeError as e:
            self.show_notification(f"Cannot switch tabs: {e}", notif_type="error")
        except Exception as e:
            self.show_notification(f"Tab switching error: {e}", notif_type="error")

    def show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        if hasattr(self, 'keyboard_modifier'):
            if self.keyboard_modifier == "Command":
                mod_symbol = "⌘"  # Command symbol on Mac
            else:
                mod_symbol = "Ctrl"
        else:
            mod_symbol = "Ctrl"
        help_text = f"""Keyboard Shortcuts:

    File operations:
    {mod_symbol}+N          Clear all data (New)
    {mod_symbol}+S          Save data
    {mod_symbol}+O          Open and load data

    Simulations:
    {mod_symbol}+R          (Re)run current tab simulation
    {mod_symbol}+E          Update all previously run simulations

    Navigation:
    {mod_symbol}+1          Switch to Classic Gradient
    {mod_symbol}+2          Switch to Extrusion
    {mod_symbol}+3          Switch to Dual Mode
    {mod_symbol}+4          Switch to Multiple Dual Mode
    {mod_symbol}+5          Switch to Pulse Test
    {mod_symbol}+6          Switch to Trace Fitting

    Data entry:
    {mod_symbol}+=          Add new compound
    {mod_symbol}+-          Remove selected or last compound
    {mod_symbol}+T          Toggle Time/Volume units

    Help:
    {mod_symbol}+I          Show this dialog"""

        messagebox.showinfo("Keyboard Shortcuts", help_text)

    # ===== Table Management Methods =====
    def add_compound(self, compound_data=None):
        """Add a new compound"""
        if compound_data is None:
            count = len(self.compound_table.get_children()) + 1
            # Default values
            compound_data = (f"Compound {count}", "1", "1", "0")

        return self.add_compound_with_undo(*compound_data)

    def add_compound_with_undo(self, compound, kd, conc, ret_time):
        """Add a compound row with undo support"""
        # Generate unique ID
        unique_id = str(uuid.uuid4())

        # Prepare values
        values = (compound, kd, conc, ret_time)

        # Get position for undo
        position = len(self.compound_table.get_children())

        # Create and execute add command
        add_command = AddRowCommand(self.compound_table, unique_id, list(values), position)
        self.undo_manager.execute_command(add_command)

        return unique_id

    def remove_compound(self):
        """Delete selected compound(s) from table"""
        self.remove_selected_compounds()

    def remove_selected_compounds(self):
        """Remove selected compounds with undo support"""
        selected_items = self.compound_table.selection()

        if not selected_items:
            # No selection - delete the last item with undo support
            items = self.compound_table.get_children()
            if not items:
                self.show_notification("No compounds to delete", notif_type="warning")
                return

            last_item_id = items[-1]
            try:
                # Get current data for undo
                values = list(self.compound_table.item(last_item_id, 'values'))
                position = len(items) - 1  # Last position

                # Create and execute delete command for last item
                delete_command = DeleteRowCommand(self.compound_table, last_item_id, values, position)
                if self.undo_manager.execute_command(delete_command):
                    self.show_notification("Deleted last compound", notif_type="success")
                else:
                    self
            except Exception as e:
                print(f"Error removing last compound: {e}")
            return

        # Selected items exist - delete them with undo support
        deleted_count = 0
        for unique_id in selected_items:
            try:
                # Get current data for undo
                values = list(self.compound_table.item(unique_id, 'values'))
                children = list(self.compound_table.get_children())
                position = children.index(unique_id)

                # Create and execute delete command
                delete_command = DeleteRowCommand(self.compound_table, unique_id, values, position)
                if self.undo_manager.execute_command(delete_command):
                    deleted_count += 1
            except Exception as e:
                print(f"Error removing compound: {e}")

        self.show_notification(f"Deleted {deleted_count} compound(s)", notif_type="success")

    def edit_compound_cell(self, unique_id, column, new_value):
        """Edit a compound cell with undo support"""
        try:
            # Get current value
            current_values = list(self.compound_table.item(unique_id, 'values'))
            column_index = self.compound_columns.index(column)
            old_value = current_values[column_index]

            # Only create command if value actually changed
            if old_value != new_value:
                edit_command = EditCellCommand(self.compound_table, unique_id, column, old_value, new_value)
                self.undo_manager.execute_command(edit_command)

        except Exception as e:
            print(f"Error editing compound: {e}")

    def undo_last_action(self):
        """Undo the last action"""
        return self.undo_manager.undo()

    def redo_last_action(self):
        """Redo the last undone action"""
        return self.undo_manager.redo()

    def update_retention_times_from_results(self, results):
        """Update compound retention times based on simulation results"""
        try:
            if not results or not hasattr(results, 'cout') or not hasattr(results, 'vspan'):
                return

            cout = results.cout
            vspan = results.vspan
            parameters = results.parameters
            compounds = results.compounds

            # Find peaks for each compound and update retention times
            for i, compound_item in enumerate(self.compound_table.get_children()):
                current_values = list(self.compound_table.item(compound_item, 'values'))

                if i < len(cout) and i < len(compounds):
                    # Find the peak (maximum) for this compound
                    peak_index = np.argmax(cout[i])
                    peak_volume = vspan[peak_index]

                    # Convert to time if needed
                    if parameters.volume_time_mode.value == "Time":
                        peak_time = peak_volume / parameters.flow_rate
                        current_values[3] = f"{peak_time:.2f}"
                    else:
                        current_values[3] = f"{peak_volume:.2f}"

                    # Update the table
                    self.compound_table.item(compound_item, values=current_values)

        except Exception as e:
            self.show_notification(f"Error updating retention times: {e}", notif_type="error")

    def add_cycle(self):
        """Add a new cycle to the switch times table with unique ID"""
        next_cycle = len(self.switch_times_table.get_children()) + 1

        # Generate unique ID
        unique_id = str(uuid.uuid4())

        # Default values for new cycle
        new_cycle = [f"Cycle {next_cycle}", "5"]

        # Get position for undo
        position = len(self.switch_times_table.get_children())

        # Create add command with unique ID
        add_command = AddRowCommand(
            table_widget=self.switch_times_table,
            unique_id=unique_id,  # Use unique_id instead of letting treeview assign
            values=new_cycle,
            position=position  # Use actual position instead of 'end'
        )

        # Execute through undo manager
        if self.undo_manager.execute_command(add_command):
            # Select the new item using unique ID
            self.switch_times_table.selection_set(unique_id)
            self.switch_times_table.focus(unique_id)
            self.switch_times_table.see(unique_id)
            self.show_notification("Added new cycle", notif_type="success")
            return unique_id
        else:
            self.show_notification("Failed to add cycle", notif_type="error")
            return None

    def remove_cycle(self):
        """Remove selected cycle from the switch times table with unique ID support"""
        selected_items = self.switch_times_table.selection()

        if not selected_items:
            # No selection - delete the last item with undo support
            items = self.switch_times_table.get_children()
            if not items:
                self.show_notification("No cycles to delete", notif_type="warning")
                return

            last_item = items[-1]
            try:
                # Get values and position for undo
                values = list(self.switch_times_table.item(last_item, 'values'))
                position = len(items) - 1

                # Create delete command
                delete_command = DeleteRowCommand(
                    table_widget=self.switch_times_table,
                    unique_id=last_item,  # This should already be a unique ID
                    values=values,
                    position=position
                )

                if self.undo_manager.execute_command(delete_command):
                    self.show_notification("Deleted last cycle", notif_type="success")
                else:
                    self.show_notification("Failed to delete last cycle", notif_type="error")
            except Exception as e:
                print(f"Error removing last cycle: {e}")
                self.show_notification("Error deleting last cycle", notif_type="error")
            return

        # Selected items exist - delete them with undo support
        deleted_count = 0
        for unique_id in selected_items:
            try:
                # Get the current values and position BEFORE deletion
                values = list(self.switch_times_table.item(unique_id, 'values'))
                children = list(self.switch_times_table.get_children())
                position = children.index(unique_id)

                # Create delete command
                delete_command = DeleteRowCommand(
                    table_widget=self.switch_times_table,
                    unique_id=unique_id,  # Use unique_id consistently
                    values=values,
                    position=position
                )

                # Execute through undo manager
                if self.undo_manager.execute_command(delete_command):
                    deleted_count += 1
            except Exception as e:
                print(f"Error removing cycle: {e}")

        if deleted_count > 0:
            self.show_notification(f"Deleted {deleted_count} cycle(s)", notif_type="success")
        else:
            self.show_notification("No cycles were deleted", notif_type="warning")

    def save_switch_times(self):
        """Save switch times list to a CSV file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Switch Times List"
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Add header with current units
                units = "mL" if self.volume_time_var.get() == "Volume" else "min"
                writer.writerow(['Cycle', f'Duration ({units})'])

                for item in self.switch_times_table.get_children():
                    writer.writerow(self.switch_times_table.item(item, 'values'))

            self.show_notification("Switch times saved successfully", duration=2000, notif_type="success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving switch times: {str(e)}")

    def open_switch_times(self):
        """Open switch times list from a CSV file"""
        filename = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Open Switch Times List"
        )
        if not filename:
            return

        try:
            # Clear existing switch times
            for item in self.switch_times_table.get_children():
                self.switch_times_table.delete(item)

            # Read from CSV
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header

                for row in reader:
                    if len(row) >= 2:  # Ensure we have both cycle name and duration
                        self.switch_times_table.insert("", "end", values=row)

            # Show success message with count
            item_count = len(self.switch_times_table.get_children())
            self.show_notification(f"Switch times loaded successfully ({item_count} cycles)", duration=2000, notif_type="success")

        except Exception as e:
            messagebox.showerror("Open Error", f"Error opening switch times: {str(e)}")

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

            self.show_notification("Compound list saved successfully", duration=2000, notif_type="success")
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

            self.show_notification("Compound list loaded successfully", duration=2000, notif_type="success")
        except Exception as e:
            messagebox.showerror("Open Error", f"Error opening compounds: {str(e)}")

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
                1: {'allow_zero': False, 'allow_negative': False, 'default_value': '1'},     # KD
                2: {'allow_zero': False, 'allow_negative': False, 'default_value': '1'},   # Concentration
                3: {'allow_zero': True, 'allow_negative': False, 'default_value': '0'}    # Retention time
            },
            'switch_time': {
                0: None,  # Cycle name - no validation
                1: {'allow_zero': False, 'allow_negative': False, 'default_value': '5'},   # Duration
            }
        }

        # Get validation parameters for this table/column
        table_rules = validation_rules.get(table_type, {})
        validation_params = table_rules.get(column_index)

        # Create entry with or without validation
        if validation_params is None:
            # No validation - text entry
            entry = tk.Entry(parent_table,
                             relief="solid",
                             bd=1,
                             highlightthickness=1,
                             highlightcolor="blue"
                             )
        else:
            # Numerical validation - use the ValidationMixin methods properly
            validate_cmd = (self.root.register(self.validate_keystroke), '%P', '%W', '%V')

            entry = tk.Entry(parent_table,
                             validate='key',
                             validatecommand=validate_cmd,
                             relief="solid",
                             bd=1,
                             highlightthickness=1,
                             highlightcolor="blue"
                             )

            # Store validation params
            entry.validation_params = validation_params

            def validate_on_focus_out(event):
                self.root.after_idle(lambda: self.validate_final_value(entry, validation_params))

            # Bind focus out with delay
            entry.bind('<FocusOut>', validate_on_focus_out, '+')

        # Position the entry over the cell
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)

        def finish_edit_wrapper(save=True):
            """Wrapper to ensure we can finish editing"""
            if entry.winfo_exists():  # Check if entry still exists
                self.finish_inline_edit(save=save)

        # Bind events (same for all entries)
        entry.bind("<Return>", lambda e: finish_edit_wrapper(save=True))
        entry.bind("<Escape>", lambda e: finish_edit_wrapper(save=False))

        def handle_tab(event):
            # Validate before moving to next cell
            if hasattr(entry, 'validation_params'):
                self.validate_final_value(entry, entry.validation_params)
            self.move_to_next_cell(table_type, 'next')
            return "break"

        def handle_shift_tab(event):
            # Validate before moving to previous cell
            if hasattr(entry, 'validation_params'):
                self.validate_final_value(entry, entry.validation_params)
            self.move_to_next_cell(table_type, 'previous')
            return "break"

        entry.bind("<Tab>", handle_tab)
        entry.bind("<Shift-Tab>", handle_shift_tab)

        def on_click_outside(event):
            """Handle clicks outside the entry field"""
            # Check if click was outside the entry widget
            widget = event.widget

            # If click was on the entry itself, ignore
            if widget == entry:
                return

            # If click was on a child of entry, ignore
            try:
                if widget.winfo_parent() == str(entry):
                    return
            except:
                pass

            # Click was outside - finish editing
            finish_edit_wrapper(save=True)

        # Bind click detection to root and parent table
        def setup_click_detection():
            """Set up click detection after entry is created"""
            # Bind to the parent table (treeview)
            parent_table.bind("<Button-1>", on_click_outside, '+')

            # Bind to the root window for clicks elsewhere
            self.root.bind("<Button-1>", on_click_outside, '+')

            # Store these bindings so we can remove them later
            entry.click_bindings = [
                (parent_table, "<Button-1>", on_click_outside),
                (self.root, "<Button-1>", on_click_outside)
            ]

        # Set up click detection after a brief delay
        self.root.after(1, setup_click_detection)

        entry.focus_set()
        entry.select_range(0, tk.END)

        return entry

    def finish_inline_edit(self, save=True):
        """Finish inline editing and optionally save the value"""
        if not self.current_edit_entry or not self.current_edit_table:
            return

        try:
            if save:
                old_value = ""
                # Get old value BEFORE validation
                if self.current_edit_item and self.current_edit_column is not None:
                    current_values = list(self.current_edit_table.item(self.current_edit_item, 'values'))
                    old_value = current_values[self.current_edit_column] if self.current_edit_column < len(current_values) else ""

                # Run validation if this entry has validation params
                if hasattr(self.current_edit_entry, 'validation_params'):
                    self.validate_final_value(self.current_edit_entry, self.current_edit_entry.validation_params)

                # Get the new value (after potential validation correction)
                new_value = self.current_edit_entry.get()

                # Only create undo command if value actually changed
                if old_value != new_value:
                    # Create undo command for the edit
                    edit_command = EditCellCommand(
                        table_widget=self.current_edit_table,
                        item_id=self.current_edit_item,
                        column=self.current_edit_column,
                        old_value=old_value,
                        new_value=new_value
                    )

                    # Execute through undo manager (this also updates the table)
                    self.undo_manager.execute_command(edit_command)

                else:

                    # Update the table
                    if self.current_edit_item and self.current_edit_column is not None:
                        current_values = list(self.current_edit_table.item(self.current_edit_item, 'values'))
                        if self.current_edit_column < len(current_values):
                            current_values[self.current_edit_column] = new_value
                            self.current_edit_table.item(self.current_edit_item, values=current_values)

            # Clean up click detection bindings
            if hasattr(self.current_edit_entry, 'click_bindings'):
                for widget, event, callback in self.current_edit_entry.click_bindings:
                    try:
                        # Remove the specific binding we added
                        widget.unbind(event, callback)
                    except:
                        pass  # Binding might already be gone

            # Clean up
            self.current_edit_entry.destroy()

        except Exception as e:
            self.show_notification(f"Error finishing inline edit: {e}", notif_type="error")
            if self.current_edit_entry:
                self.current_edit_entry.destroy()

        finally:
            # Reset references
            self.current_edit_entry = None
            self.current_edit_item = None
            self.current_edit_column = None
            self.current_edit_table = None

        return "break"

    def create_validated_entry_for_inline(self, parent, validation_params=None):
        """Create a validated tk.Entry widget specifically for inline editing"""
        if validation_params is None:
            validation_params = {'allow_zero': False, 'allow_negative': False, 'default_value': '1'}

        # Set default if not provided
        if 'default_value' not in validation_params:
            validation_params['default_value'] = '1'

        # For inline editing, create tk.Entry with validation
        validate_cmd = (self.root.register(self.validate_keystroke), '%P', '%W', '%V')

        entry = tk.Entry(parent,
                         validate='key',
                         validatecommand=validate_cmd,
                         relief="solid",
                         bd=1,
                         highlightthickness=1,
                         highlightcolor="blue")

        # Store validation params for focus-out validation
        entry.validation_params = validation_params

        # Add focus-out validation using the same logic
        def on_focus_out(event):
            self.validate_final_value(entry, validation_params)

        def on_enter_key(event):
            self.validate_final_value(entry, validation_params)
            return 'break'

        entry.bind('<FocusOut>', on_focus_out)
        entry.bind('<Return>', on_enter_key)

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
            self.show_notification(f"Error saving current cell: {e}", notif_type="error")
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

    def table_delete(self, event, handler):
        """Safely handle table deletion with confirmation for multiple items"""
        table = event.widget
        selected_items = table.selection()

        if not selected_items:
            return "break"

        # Call the appropriate handler
        handler()
        return "break"

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

    def add_n_value(self):
        """Add N value to the pulse list"""
        if not hasattr(self, 'pulse_peaks') or not self.pulse_peaks:
            messagebox.showinfo("No Peaks", "Please find peaks first")
            return

        if len(self.pulse_peaks) > 1:
            messagebox.showerror("Multiple Peaks Found",
                                 f"Cannot calculate N with {len(self.pulse_peaks)} peaks selected.\n\n"
                                 # f"Please adjust the peak detection parameters to find exactly one peak.\n\n"
                                 # f"Current peaks found at times: {[f'{self.pulse_X[p]:.3f}' for p in self.pulse_peaks]} min"
                                 )
            return

        try:
            # Calculate N value from peak properties
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
                messagebox.showerror("Calculation Error", "Cannot calculate peak width - peak too narrow or detection error.")
                return

            # Calculate N using 5.54 * (time/width)^2
            N = 5.54 * (time / width)**2

            # Validate N is in reasonable range
            if not (10 <= N <= 10000):
                messagebox.askyesno("Unusual N Value",
                                    f"Calculated N = {N:.0f} is outside the typical range (10 - 10,000).\n\n"
                                    "Do you want to add this N value anyway?"
                                    # f"Peak details:\n"
                                    # f"• Retention time: {time:.3f} min\n"
                                    # f"• Half-height width: {width:.4f} min\n"
                                    # f"• Peak height: {max_height:.3f}\n\n"
                                    # f"Please verify your data and peak identification parameters."
                                    )
                return

            # Highlight the half-height region
            x_highlight = self.pulse_X[left_idx:right_idx+1]
            y_highlight = self.pulse_Y_smooth[left_idx:right_idx+1]

            # Add filled region
            self.pulse_ax.fill_between(x_highlight, half_height, y_highlight,
                                       alpha=0.3, color='blue',
                                       label='N Calculation Region')

            # Update legend and redraw
            self.pulse_ax.legend(loc='upper left')
            self.pulse_canvas.draw()

            # Add to pulse table
            self.pulse_table.insert("", "end", values=(
                f"{self.pulse_flow_rate:.1f}",
                f"{self.pulse_sf:.2f}",
                f"{N:.0f}"
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

    def remove_n_value(self):
        """Remove selected N value(s) from the pulse test table"""
        selection = self.pulse_table.selection()

        if not selection:
            # If nothing selected, remove the last item
            items = self.pulse_table.get_children()
            if items:
                self.pulse_table.delete(items[-1])
        else:
            # Remove all selected items
            for item in selection:
                self.pulse_table.delete(item)

        # Update regression buttons state based on remaining data
        remaining_items = len(self.pulse_table.get_children())
        if remaining_items >= 3:
            # Keep buttons enabled and update coefficients
            self.fit_coefficients()
        else:
            # Disable buttons if insufficient data
            self.use_n_button.config(state="disabled")
            self.use_sf_button.config(state="disabled")
            # Clear regression labels
            self.label_na.config(text="A: ")
            self.label_nb.config(text="B: ")
            self.label_nc.config(text="C: ")
            self.label_sf_a.config(text="A: ")
            self.label_sf_b.config(text="B: ")

        self.show_notification("Removed N value(s).",
                               duration=2000, notif_type="info")

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

        self.show_notification("N coefficients transferred to column properties", duration=2000, notif_type="success")

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

        self.show_notification("Sf coefficients transferred to column properties", duration=2000, notif_type="success")

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

            self.show_notification(f"Added {len(self.fit_peaks)} compounds from fit data", duration=2000, notif_type="success")
        except Exception as e:
            messagebox.showerror("Update Error", f"Error updating compounds: {str(e)}")
