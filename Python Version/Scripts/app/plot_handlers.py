import re
import hashlib
import traceback
import numpy as np
import pandas as pd
import tkinter as tk
from enum import Enum
from scipy.io import loadmat
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Any
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass, field, replace
from scipy.signal import find_peaks, savgol_filter

from models.CupV6 import CupV6
from models.DualV2 import DualV2
from models.EECCC_V8 import EECCC_V8
from models.ECPC_V1 import ECPC_V1
from models.MDMV2 import MDMV2


class SimulationType(Enum):
    CLASSIC = "classic"
    EXTRUSION = "extrusion"
    DUAL = "dual"
    MULTI = "multi"


class VolumeTimeMode(Enum):
    TIME = "Time"
    VOLUME = "Volume"


@dataclass
class SimulationParameters:
    """Centralized parameter storage with validation"""
    flow_rate: float = 5.0
    column_volume: float = 81.0
    elution_duration: float = 60.0
    injection_volume: float = 1.0
    stationary_phase: float = 0.75
    column_efficiency: int = 400
    volume_time_mode: VolumeTimeMode = VolumeTimeMode.TIME

    # Coefficients (if using coefficient mode)
    use_sf_coefficients: bool = False
    sf_coeff_a: float = 0.982
    sf_coeff_b: float = -0.142

    use_n_coefficients: bool = False
    n_coeff_a: float = 371.23
    n_coeff_b: float = -7.204
    n_coeff_c: float = 0.1480

    def get_effective_sf(self) -> float:
        """Get stationary phase value (calculated or direct)"""
        if self.use_sf_coefficients:
            return max(0.01, min(0.99, self.sf_coeff_a + self.sf_coeff_b * self.flow_rate))
        return self.stationary_phase

    def get_effective_n(self) -> int:
        """Get column efficiency (calculated or direct)"""
        if self.use_n_coefficients:
            n = self.n_coeff_a + self.n_coeff_b * self.flow_rate + self.n_coeff_c * self.flow_rate**2
            return max(50, int(n))
        return self.column_efficiency

    def get_vcm(self) -> float:
        """Get elution volume in mL"""
        if self.volume_time_mode == VolumeTimeMode.TIME:
            return (self.flow_rate * self.elution_duration)
        return self.elution_duration

    def to_dict(self) -> Dict:
        """For serialization"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }


@dataclass
class CompoundData:
    """Individual compound properties"""
    name: str
    kd: float
    concentration: float
    retention_time: float

    def validate(self) -> List[str]:
        """Return list of validation errors"""
        errors = []
        if self.kd <= 0:
            errors.append(f"{self.name}: KD must be positive")
        if self.concentration <= 0:
            errors.append(f"{self.name}: Concentration must be positive")
        return errors


@dataclass
class PlotConfig:
    title: str = ""
    xlabel: str = ""
    ylabel: str = "Concentration (g/L)"
    show_peak_labels: bool = False

    # Font sizes
    title_fontsize: int = 14
    label_fontsize: int = 11
    legend_fontsize: int = 10
    tick_fontsize: int = 9

    # Line styles
    show_lines: bool = False
    show_line_labels: bool = False
    standard_linewidth: float = 2.0
    sum_linewidth: float = 1.5
    vertical_line_width: float = 1.0

    # Grid
    show_grid: bool = True
    grid_alpha: float = 0.7
    grid_linewidth: float = 0.5

    # Colors (consistent across all plots)
    compound_colors: List[str] = field(default_factory=lambda: [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'
    ])
    dm_line_color: str = 'red'
    cm_line_color: str = 'blue'
    sum_color: str = 'black'
    show_sum: bool = True

    # Layout
    figure_dpi: int = 100
    figure_facecolor: str = 'white'
    axes_facecolor: str = 'white'

    @classmethod
    def from_gui_vars(cls, title: str, **gui_vars) -> 'PlotConfig':
        """Create config from tkinter variables"""
        return cls(
            title=title,
            show_sum=gui_vars.get('sum_var', tk.BooleanVar()).get(),
            show_peak_labels=gui_vars.get('peaks_var', tk.BooleanVar()).get(),
            show_grid=gui_vars.get('grid_var', tk.BooleanVar()).get(),
            show_lines=gui_vars.get('lines_var', tk.BooleanVar()).get(),
            show_line_labels=gui_vars.get('line_labels_var', tk.BooleanVar()).get(),
        )


@dataclass
class SimulationResults:
    """Standardized result container"""
    simulation_type: SimulationType
    vspan: np.ndarray
    cout: np.ndarray
    parameters: SimulationParameters
    compounds: List[CompoundData]
    metadata: Dict = field(default_factory=dict)

    def get_plot_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Get data ready for plotting with unit conversion"""
        x_values = self.vspan.copy()

        if self.parameters.volume_time_mode == VolumeTimeMode.TIME:
            x_values /= self.parameters.flow_rate

        return x_values, self.cout


class PlotRenderer:
    """Unified plotting logic for all simulation types"""

    def __init__(self, ax, canvas, fig=None):
        self.ax = ax
        self.canvas = canvas
        self.fig = fig
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    def render_simulation(self, results: SimulationResults, config: 'PlotConfig', gui_context=None):
        """Main rendering method with complete visual fidelity matching original methods"""

        # Clear the plot
        self.ax.clear()

        # Get the data ready for plotting
        x_data, y_data = results.get_plot_data()

        # Handle different simulation types with their specific logic
        if results.simulation_type == SimulationType.CLASSIC:
            self._render_classic(results, config, x_data, y_data, gui_context)
        elif results.simulation_type == SimulationType.EXTRUSION:
            self._render_extrusion(results, config, x_data, y_data, gui_context)
        elif results.simulation_type == SimulationType.DUAL:
            self._render_dual(results, config, x_data, y_data, gui_context)
        elif results.simulation_type == SimulationType.MULTI:
            self._render_multi(results, config, x_data, y_data, gui_context)

        # Finalize the plot
        self._finalize_plot(results, config)

    def _standardize_line_styles(self):
        """Ensure consistent line styles across all plots"""
        # Standard line properties
        standard_linewidth = 2.0
        sum_linewidth = 1.5
        vertical_line_width = 1.0

        # Apply to regular lines (plot lines)
        for line in self.ax.get_lines():
            label = line.get_label()
            if label == 'Sum':
                line.set_linewidth(sum_linewidth)
                line.set_linestyle('--')
            elif any(keyword in label for keyword in ['Switch', 'DM', 'CM', 'Dual', 'Extrusion', 'Sweep']):
                # These are actually axvline objects, but if they show up as lines, handle them
                line.set_linewidth(vertical_line_width)
                line.set_linestyle('-.')
            else:
                # Regular compound lines
                line.set_linewidth(standard_linewidth)
                line.set_linestyle('-')

        # Handle vertical lines (axvline creates Line2D objects in ax.lines)
        # Check for vertical lines by looking at their x-data
        for line in self.ax.get_lines():
            # Check if this is a vertical line (constant x values)
            xdata = line.get_xdata()
            if len(xdata) == 2 and abs(xdata[0] - xdata[1]) < 1e-10:  # Vertical line
                line.set_linewidth(vertical_line_width)
                line.set_linestyle('-.')

    def _apply_consistent_formatting(self, results: SimulationResults, config: PlotConfig):
        """Apply consistent formatting across all plot types"""
        # Consistent font sizes
        # title_fontsize = 14
        label_fontsize = 11
        legend_fontsize = 10
        tick_fontsize = 9

        # Set title with consistent formatting
        if config.title:
            self.ax.set_title("")

        # Set axis labels with consistent formatting
        x_label = ('Elution Volume (mL)' if results.parameters.volume_time_mode == VolumeTimeMode.VOLUME
                   else 'Elution Time (min)')

        self.ax.set_xlabel(x_label, fontsize=label_fontsize, fontweight='normal')
        self.ax.set_ylabel(config.ylabel, fontsize=label_fontsize, fontweight='normal')

        # Consistent tick formatting
        self.ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        self.ax.tick_params(axis='both', which='minor', labelsize=tick_fontsize-1)

        # Legend formatting
        if 'classic' in self.ax.get_title().lower():
            legend_position = "upper right"
        else:
            legend_position = "upper left"
        legend = self.ax.legend(loc=legend_position, framealpha=0.95, fontsize=legend_fontsize)
        if legend:
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('gray')
            legend.get_frame().set_linewidth(0.5)

        # Grid formatting
        if config.show_grid:
            self.ax.grid(True, linestyle='--', alpha=0.7, linewidth=0.5)
            self.ax.set_axisbelow(True)  # Put grid behind data

        # Proper axis limits with consistent padding
        max_conc = getattr(self, '_max_conc', 1)
        self.ax.set_ylim(0, max_conc * 1.1 if max_conc > 0 else 1)

        # X-axis limits - always start at 0 and end at data max
        x_data, _ = results.get_plot_data()
        if len(x_data) > 0:
            self.ax.set_xlim(0, max(x_data))

        # Consistent background
        self.ax.set_facecolor('white')

        # Consistent spine formatting
        for spine in self.ax.spines.values():
            spine.set_color('gray')
            spine.set_linewidth(0.8)

    def _render_classic(self, results: SimulationResults, config: PlotConfig, x_data, y_data, gui_context):
        """Render classic simulation with all original visual features"""

        max_conc = 0
        cout = results.cout
        compounds = results.compounds

        # Plot each compound with original styling
        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_color = self.colors[i % len(self.colors)]
                self.ax.plot(x_data, cout[i], color=compound_color,
                             label=compound.name, linewidth=2)
                max_conc = max(max_conc, np.max(cout[i]))

        # Show sum if requested
        if config.show_sum:
            sum_concentration = np.sum(cout, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.ax.plot(x_data, sum_concentration, '-.r',
                         label='Sum', linewidth=1.0)

        # Add peak labels if requested
        if config.show_peak_labels:
            self._add_peak_labels(x_data, cout, compounds)

        # Overlay experimental data if available
        if gui_context:
            self._add_experimental_overlay(x_data, gui_context, max_conc)

        self._store_max_conc(max_conc)

    def _render_extrusion(self, results: SimulationResults, config: PlotConfig, x_data, y_data, gui_context):
        """Render extrusion simulation with all original visual features"""

        max_conc = 0
        cout = results.cout
        compounds = results.compounds

        # Plot each compound
        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_color = self.colors[i % len(self.colors)]
                self.ax.plot(x_data, cout[i], color=compound_color,
                             label=compound.name, linewidth=2)
                max_conc = max(max_conc, np.max(cout[i]))

        # Show sum if requested
        if config.show_sum:
            sum_concentration = np.sum(cout, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.ax.plot(x_data, sum_concentration, '-.r', label='Sum', linewidth=1.0)

        # Add vertical lines for extrusion phases
        if config.show_lines:
            self._add_extrusion_lines(results, config, gui_context)

        # Add peak labels if requested
        if config.show_peak_labels:
            self._add_extrusion_peak_labels(x_data, cout, compounds)

        # Overlay experimental data if available
        if gui_context:
            self._add_experimental_overlay(x_data, gui_context, max_conc)

        self._store_max_conc(max_conc)

    def _render_dual(self, results: SimulationResults, config: PlotConfig, x_data, y_data, gui_context):
        """Render dual mode simulation with all original visual features"""

        max_conc = 0
        cout = results.cout
        compounds = results.compounds

        # Plot each compound
        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_color = self.colors[i % len(self.colors)]
                self.ax.plot(x_data, cout[i], color=compound_color,
                             label=compound.name, linewidth=2)
                max_conc = max(max_conc, np.max(cout[i]))

        # Add vertical line for dual mode transition
        if config.show_lines:
            self._add_dual_mode_lines(results, config, x_data, gui_context)

        # Show sum if requested
        if config.show_sum:
            sum_concentration = np.sum(cout, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.ax.plot(x_data, sum_concentration, 'r-.', label="Sum", linewidth=1.5)

        # Add peak labels if requested
        if config.show_peak_labels:
            self._add_dual_peak_labels(x_data, cout, compounds)

        # Overlay experimental data if available
        if gui_context:
            self._add_experimental_overlay(x_data, gui_context, max_conc)

        self._store_max_conc(max_conc)

    def _render_multi(self, results: SimulationResults, config: PlotConfig, x_data, y_data, gui_context):
        """Render multiple dual mode simulation with your preferred contour approach"""

        max_conc = 0
        cout = results.cout
        compounds = results.compounds

        # Extract multi-specific data from metadata
        xtot_mdm = results.metadata.get('xtot')

        # Plot each compound
        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_color = self.colors[i % len(self.colors)]
                self.ax.plot(x_data, cout[i], color=compound_color,
                             label=compound.name, linewidth=2)
                max_conc = max(max_conc, np.max(cout[i]))

        # Show sum if requested
        if config.show_sum:
            sum_concentration = np.sum(cout, axis=0)
            max_conc = max(max_conc, np.max(sum_concentration))
            self.ax.plot(x_data, sum_concentration, 'k--', label="Sum", linewidth=2)

        # Add vertical lines for switching times
        if config.show_lines:
            self._add_multi_mode_lines(results, config, x_data, gui_context)

        # Add peak labels if requested
        if config.show_peak_labels:
            self._add_multi_peak_labels(x_data, cout, compounds)

        # Overlay experimental data if available
        if gui_context:
            self._add_experimental_overlay(x_data, gui_context, max_conc)

        # Handle position plot
        if gui_context and hasattr(gui_context, 'multi_pos_ax') and xtot_mdm is not None:
            self._render_multi_position_plot(results, config, x_data, xtot_mdm, gui_context)

        self._store_max_conc(max_conc)

    def _render_multi_position_plot(self, results: SimulationResults, config: PlotConfig, x_data, xtot_mdm, gui_context):
        """Render the position contour plot with consistent formatting"""

        try:
            xtot_mdm = np.array(xtot_mdm)
            x_matrix = np.sum(xtot_mdm, axis=2)
            y_axis = np.linspace(0, 1, x_matrix.shape[0])
            matrix_scaler = np.max(x_matrix)

            if matrix_scaler <= 0:
                self.show_notification("No valid concentration data for position plot",
                                       duration=2000, notif_type="warning")
                return

            contour_levels = np.linspace(0.001 * matrix_scaler, 0.05 * matrix_scaler, 30)

            if x_matrix.shape[1] > 0 and len(x_data) > 0:
                original_time = np.linspace(0, x_matrix.shape[1], x_matrix.shape[1])
                target_time = np.linspace(0, x_matrix.shape[1], len(x_data))

                x_matrix_interp = np.zeros((x_matrix.shape[0], len(x_data)))
                for i in range(x_matrix.shape[0]):
                    if len(x_matrix[i, :]) > 0:
                        x_matrix_interp[i, :] = np.interp(target_time, original_time, x_matrix[i, :])

                gui_context.multi_pos_ax.clear()

                try:
                    cs = gui_context.multi_pos_ax.contourf(x_data, y_axis, x_matrix_interp,
                                                           levels=contour_levels,
                                                           cmap='viridis', extend='max')
                except Exception as e:
                    self.show_notification(f"Contourf failed: {e}, trying imshow fallback",
                                           duration=2000, notif_type="warning")
                    extent = [x_data[0], x_data[-1], 0, 1]
                    vmax = matrix_scaler * 0.05
                    vmin = matrix_scaler * 0.001
                    im = gui_context.multi_pos_ax.imshow(x_matrix_interp, aspect='auto', extent=extent,
                                                         cmap='viridis', interpolation='bilinear',
                                                         origin='lower', vmin=vmin, vmax=vmax)

                # Add switching lines with consistent styling
                vswdm = np.array(results.metadata.get('vbc', []))
                vswcm = np.array(results.metadata.get('vcyc', []))

                if results.parameters.volume_time_mode == VolumeTimeMode.TIME:
                    vswdm_times = vswdm / results.parameters.flow_rate
                    vswcm_times = vswcm / results.parameters.flow_rate
                else:
                    vswdm_times = vswdm
                    vswcm_times = vswcm

                # Consistent line styling
                if config.show_lines:
                    for v in vswdm_times:
                        gui_context.multi_pos_ax.axvline(x=v, color='red', linestyle='-.', linewidth=1.0, alpha=0.8)
                    for v in vswcm_times:
                        gui_context.multi_pos_ax.axvline(x=v, color='blue', linestyle='-.', linewidth=1.0, alpha=0.8)

                # Consistent formatting for position plot
                x_label = ('Elution Volume (mL)' if results.parameters.volume_time_mode == VolumeTimeMode.VOLUME
                           else 'Elution Time (min)')

                gui_context.multi_pos_ax.set_xlabel(x_label, fontsize=11, fontweight='normal')
                gui_context.multi_pos_ax.set_ylabel('Column Position', fontsize=11, fontweight='normal')
                gui_context.multi_pos_ax.tick_params(axis='both', which='major', labelsize=9)
                if config.show_grid:
                    gui_context.multi_pos_ax.grid(True, linestyle='--', alpha=0.7, linewidth=0.5)
                gui_context.multi_pos_ax.set_facecolor('white')
                gui_context.multi_pos_ax.set_axisbelow(True)

                # Consistent spine formatting
                for spine in gui_context.multi_pos_ax.spines.values():
                    spine.set_color('gray')
                    spine.set_linewidth(0.8)

                if len(x_data) > 0:
                    both_xlim = (0, max(x_data))

                # Apply to both plots
                self.ax.set_xlim(both_xlim)
                gui_context.multi_pos_ax.set_xlim(both_xlim)

                # Use the enhanced synchronization
                if hasattr(gui_context, 'synchronize_multi_plot_layouts'):
                    gui_context.synchronize_multi_plot_layouts()

        except Exception as e:
            self.show_notification(f"Error rendering position plot: {e}",
                                   duration=2000, notif_type="error")
            traceback.print_exc()

    def _add_peak_labels(self, x_data, cout, compounds):
        """Add peak labels using scipy find_peaks"""
        for i, compound in enumerate(compounds):
            if i < len(cout):
                peaks, _ = find_peaks(cout[i], height=0.1*np.max(cout[i]))
                for peak in peaks:
                    if peak < len(x_data):
                        label_offset = max(self.ax.get_ylim()) * 0.02
                        self.ax.text(x_data[peak], cout[i][peak] + label_offset,
                                     compound.name, ha='center')

    def _add_extrusion_peak_labels(self, x_data, cout, compounds):
        """Add peak labels for extrusion plots"""
        for i, compound in enumerate(compounds):
            if i < len(cout):
                compound_peaks, _ = find_peaks(cout[i], height=0.1*np.max(cout[i]))
                for peak in compound_peaks:
                    if peak < len(x_data):
                        label_offset = max(self.ax.get_ylim()) * 0.02
                        self.ax.text(x_data[peak], cout[i][peak] + label_offset,
                                     compound.name, ha='center')

    def _add_dual_peak_labels(self, x_data, cout, compounds):
        """Add peak labels for dual mode plots"""
        for i, compound in enumerate(compounds):
            if i < len(cout):
                peaks, _ = find_peaks(cout[i], height=0.1*np.max(cout[i]))
                for peak in peaks:
                    if peak < len(x_data):
                        label_offset = max(self.ax.get_ylim()) * 0.02
                        self.ax.annotate(
                            f"{compound.name}",
                            xy=(x_data[peak], cout[i][peak] + label_offset),
                            xytext=(0, 5),
                            textcoords='offset points',
                            ha='center',
                            fontsize=9
                        )

    def _add_multi_peak_labels(self, x_data, cout, compounds):
        """Add peak labels for multi mode plots"""
        for i, compound in enumerate(compounds):
            if i < len(cout):
                peaks, _ = find_peaks(cout[i], height=0.1*np.max(cout[i]))
                for peak in peaks:
                    if peak < len(x_data):
                        label_offset = max(self.ax.get_ylim()) * 0.02
                        self.ax.annotate(
                            f"{compound.name}",
                            xy=(x_data[peak], cout[i][peak] + label_offset),
                            xytext=(0, 5),
                            textcoords='offset points',
                            ha='center',
                            fontsize=9
                        )

    def _add_extrusion_lines(self, results: SimulationResults, config: PlotConfig, gui_context):
        """Add vertical lines specific to extrusion plots"""

        # Get timing data from metadata
        params = results.parameters
        column_volume_extruded_time = results.metadata.get('column_volume_extruded_time')
        sweep_time = results.metadata.get('sweep_time')
        elution_time = results.metadata.get('elution_time')
        ccc_cpc_mode = results.metadata.get('ccc_cpc_mode', 'CCC')
        volume_time_mode = results.metadata.get('volume_time_mode', VolumeTimeMode.TIME)

        # Set up labels
        if config.show_line_labels:
            units = ' min' if volume_time_mode == VolumeTimeMode.TIME else ' mL'
            if ccc_cpc_mode == "CCC":
                sweep_start_label = f"Sweep Start\n{elution_time:.2f}{units}"
                sweep_end_label = f"Extrusion Start\n{sweep_time:.2f}{units}" if sweep_time else ""
            else:  # CPC mode
                sweep_start_label = f"Extrusion Start\n{elution_time:.2f}{units}"
                sweep_end_label = ""
        else:
            sweep_start_label = ""
            sweep_end_label = ""

        # Draw lines based on mode
        if ccc_cpc_mode == "CCC":
            # Sweep start line
            self.ax.axvline(x=column_volume_extruded_time, color='r',
                            linestyle='-.', label="Sweep Start")
            if sweep_start_label:
                # Get y-axis limits for positioning text at top
                _, y_max = self.ax.get_ylim()
                text_y_position = y_max * 0.95
                self.ax.text(column_volume_extruded_time, text_y_position,
                             sweep_start_label, ha="right", va="top", rotation=90)

            # Extrusion start line (if applicable)
            if sweep_time is not None:
                self.ax.axvline(x=sweep_time, color='b',
                                linestyle='-.', label="Extrusion Start")
                if sweep_end_label:
                    self.ax.text(sweep_time, text_y_position,
                                 sweep_end_label, ha="right", va="top", rotation=90)
        else:  # CPC mode
            self.ax.axvline(x=column_volume_extruded_time, color='b',
                            linestyle='-.', label="Extrusion Start")
            if sweep_start_label:
                self.ax.text(column_volume_extruded_time, 0,
                             sweep_start_label, ha="right", va="top", rotation=90)

    def _add_dual_mode_lines(self, results: SimulationResults, config: PlotConfig, x_data, gui_context):
        """Add vertical lines for dual mode transitions"""
        # Calculate dual switch time from parameters and data
        params = results.parameters

        # Get the actual elution duration from metadata
        elution_time = results.metadata.get('elution_time')
        if elution_time is None:
            # Fallback to calculating from VCM
            if params.volume_time_mode == VolumeTimeMode.TIME:
                elution_time = params.get_vcm() / params.flow_rate
            else:
                elution_time = params.get_vcm()
        # Draw the line
        self.ax.axvline(x=elution_time, color='r', linestyle='-.', label="Dual Switch")

        if config.show_line_labels:
            units = ' min' if params.volume_time_mode == VolumeTimeMode.TIME else ' mL'
            dual_switch_label = f"Dual Switch\n{elution_time:.2f}{units}"
            _, y_max = self.ax.get_ylim()
            text_y_position = y_max * 0.95
            self.ax.text(elution_time, text_y_position,
                         dual_switch_label, ha="right", va="top", rotation=90)

    def _add_multi_mode_lines(self, results: SimulationResults, config: PlotConfig, x_data, gui_context):
        """Add vertical lines for multiple dual mode switching"""
        # Add switching lines with consistent styling
        vswdm = np.array(results.metadata.get('vbc', []))
        vswcm = np.array(results.metadata.get('vcyc', []))

        if results.parameters.volume_time_mode == VolumeTimeMode.TIME:
            vswdm_times = vswdm / results.parameters.flow_rate
            vswcm_times = vswcm / results.parameters.flow_rate
        else:
            vswdm_times = vswdm
            vswcm_times = vswcm

        # Consistent line styling
        if config.show_lines:
            for v in vswdm_times:
                gui_context.multi_pos_ax.axvline(x=v, color='red', linestyle='-.', linewidth=1.0, alpha=0.8)
            for v in vswcm_times:
                gui_context.multi_pos_ax.axvline(x=v, color='blue', linestyle='-.', linewidth=1.0, alpha=0.8)

        # Get switching data from metadata
        vswdm = results.metadata.get('vbc', np.array([]))  # VswDM
        vswcm = results.metadata.get('vcyc', np.array([]))  # VswCM

        params = results.parameters

        if params.volume_time_mode == VolumeTimeMode.TIME:
            vswdm_times = vswdm / params.flow_rate
            vswcm_times = vswcm / params.flow_rate
            units = ' min'
        else:
            vswdm_times = vswdm
            vswcm_times = vswcm
            units = ' mL'

        # Get y-axis limits for positioning text at top
        _, y_max = self.ax.get_ylim()
        text_y_position = y_max * 0.95

        # Draw VswDM lines in red
        for i, v in enumerate(vswdm_times):
            self.ax.axvline(x=v, color='r', linestyle='-.')
            if config.show_line_labels:
                self.ax.text(v, text_y_position, f"DM {i+1}\n{v:.1f}{units}",
                             ha="right", va="top", rotation=90, fontsize=8)

        # Draw VswCM lines in blue
        for i, v in enumerate(vswcm_times):
            self.ax.axvline(x=v, color='b', linestyle='-.')
            if config.show_line_labels:
                self.ax.text(v, text_y_position, f"CM {i+1}\n{v:.1f}{units}",
                             ha="right", va="top", rotation=90, fontsize=8)

    def _add_experimental_overlay(self, x_data, gui_context, max_conc):
        """Add experimental data overlay if available"""
        if not gui_context:
            return

        # Check each condition separately for debugging
        has_overlay_var = hasattr(gui_context, 'overlay_var')

        if has_overlay_var:
            overlay_enabled = gui_context.overlay_var.get()
        else:
            return

        has_fit_data = hasattr(gui_context, 'fit_data') and gui_context.fit_data

        # Only proceed if all conditions are met
        if has_overlay_var and overlay_enabled and has_fit_data:
            try:
                X_exp = gui_context.fit_data['X']
                Y_exp = gui_context.fit_data['Y']

                # Check if threshold variable exists
                if hasattr(gui_context, 'fit_threshold_var'):
                    threshold = gui_context.fit_threshold_var.get()
                else:
                    threshold = 0

                Y_exp = Y_exp - threshold
                Y_exp = Y_exp * (max_conc * 0.9) / np.max(Y_exp)

                # Convert to volume if needed
                if hasattr(gui_context, 'volume_time_var') and gui_context.volume_time_var.get() == "Volume":
                    if hasattr(gui_context, 'flow_rate_entry'):
                        flow_rate = float(gui_context.flow_rate_entry.get())
                        X_exp = X_exp * flow_rate

                # Plot the overlay
                self.ax.plot(X_exp, Y_exp, 'k-',
                             label='Experimental', linewidth=2, alpha=0.7)


            except Exception as e:

                traceback.print_exc()

    def _store_max_conc(self, max_conc):
        """Store max concentration for axis scaling"""
        self._max_conc = max_conc

    def _finalize_plot(self, results: SimulationResults, config: PlotConfig):
        """Enhanced finalization with complete consistency"""

        # Apply all consistency formatting
        self._apply_consistent_formatting(results, config)
        self._standardize_line_styles()

        # Final canvas draw
        self.canvas.draw()


class SimulationService:
    """Centralized simulation computation with caching"""

    def __init__(self):
        self.cache = {}
        self.max_cache_size = 100  # Prevent memory issues

    def run_simulation(self, sim_type: SimulationType,
                       parameters: SimulationParameters,
                       compounds: List[CompoundData],
                       extra_params: Optional[Dict] = None) -> SimulationResults:
        """Main simulation runner with automatic caching"""

        # Create cache key from parameters and compounds
        cache_key = self._create_cache_key(sim_type, parameters, compounds, extra_params)

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Convert compounds to arrays
        kd_array = np.array([c.kd for c in compounds])
        conc_array = np.array([c.concentration for c in compounds])

        # Run appropriate simulation - these already return SimulationResults objects
        if sim_type == SimulationType.CLASSIC:
            result = self._run_classic(parameters, compounds, kd_array, conc_array)
        elif sim_type == SimulationType.EXTRUSION:
            result = self._run_extrusion(parameters, compounds, kd_array, conc_array, extra_params)
        elif sim_type == SimulationType.DUAL:
            result = self._run_dual(parameters, compounds, kd_array, conc_array, extra_params)
        elif sim_type == SimulationType.MULTI:
            result = self._run_multi(parameters, compounds, kd_array, conc_array, extra_params)
        else:
            raise ValueError(f"Unknown simulation type: {sim_type}")

        # Cache result with size management
        self._cache_result(cache_key, result)
        return result

    def _create_cache_key(self, sim_type: SimulationType,
                          parameters: SimulationParameters,
                          compounds: List[CompoundData],
                          extra_params: Optional[Dict] = None) -> str:
        """Create hash-based cache key"""
        data = {
            'type': sim_type.value,
            'params': parameters.to_dict(),
            'compounds': [(c.name, c.kd, c.concentration) for c in compounds],
            'extra': extra_params or {}
        }
        return hashlib.md5(str(sorted(data.items())).encode()).hexdigest()

    def _cache_result(self, key: str, result: SimulationResults):
        """Cache result with size management"""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = result

    def clear_cache(self):
        """Clear simulation cache"""
        self.cache.clear()

    def _run_classic(self, params: SimulationParameters, compounds, kd_array, conc_array):
        """Run classic simulation"""
        vspan, cout, x, y, vmcup = CupV6(
            params.get_effective_sf(),
            kd_array,
            params.column_volume,
            params.get_effective_n(),
            params.get_vcm(),
            conc_array,
            params.injection_volume
        )

        return SimulationResults(
            simulation_type=SimulationType.CLASSIC,
            vspan=vspan,
            cout=cout,
            parameters=params,
            compounds=compounds,
            metadata={
                'x': x,
                'y': y,
                'simulation_type': 'classic',
                'n_cups': params.get_effective_n(),
                'sf': params.get_effective_sf(),
                'vmcup': vmcup
            }
        )

    def _run_extrusion(self, params: SimulationParameters, compounds, kd_array, conc_array, extra_params: Dict):
        """Run elution-extrusion simulation"""
        # Extract parameters
        elution_duration = extra_params.get('elution_duration')
        extrusion_duration = extra_params.get('extrusion_duration')
        ccc_cpc_mode = extra_params.get('ccc_cpc_mode')

        effective_elution_duration = elution_duration

        classic_params = replace(params, elution_duration=effective_elution_duration)

        flow_rate = params.flow_rate
        n_cups = params.get_effective_n()

        # Run classic simulation with correct elution duration
        classic_results = self._run_classic(classic_params, compounds, kd_array, conc_array)
        x_classic = classic_results.metadata.get('x')
        y_classic = classic_results.metadata.get('y')

        # Convert durations to volumes consistently
        def to_volume(duration):
            if params.volume_time_mode == VolumeTimeMode.TIME:
                return duration * flow_rate
            return duration

        extrusion_volume = to_volume(extrusion_duration)

        # Calculate extrusion steps based on mode
        if ccc_cpc_mode == 'CCC':
            # CCC: Calculate sweep phase and actual extrusion
            mobile_phase_volume = params.column_volume * (1 - params.get_effective_sf())
            sweep_duration = mobile_phase_volume / flow_rate

            # Determine actual extrusion needed after sweep
            if params.volume_time_mode == VolumeTimeMode.TIME:
                actual_extrusion_duration = max(0, extrusion_duration - sweep_duration)
                actual_extrusion_volume = actual_extrusion_duration * flow_rate
            else:
                actual_extrusion_time = extrusion_duration / flow_rate
                actual_extrusion_duration = max(0, actual_extrusion_time - sweep_duration)
                actual_extrusion_volume = actual_extrusion_duration * flow_rate

            # Calculate steps based on stationary phase per cup
            if actual_extrusion_volume <= 0:
                extrusion_steps = 0
            else:
                vs_cup = (params.column_volume * params.get_effective_sf()) / n_cups
                extrusion_steps = int(round(actual_extrusion_volume / vs_cup))
        else:
            # CPC: Simple displacement of entire cell volumes
            vcell = params.column_volume / n_cups
            extrusion_steps = int(round(extrusion_volume / vcell))

        # Run simulation
        if ccc_cpc_mode == 'CCC':
            vspan, cout, xtot, ytot, vbc = EECCC_V8(
                kd_array, params.column_volume, params.get_effective_sf(),
                x_classic, y_classic, extrusion_steps=extrusion_steps
            )
        else:
            vspan, cout, xtot, ytot, vbc = ECPC_V1(
                kd_array, params.column_volume, params.get_effective_sf(),
                x_classic, y_classic, extrusion_steps=extrusion_steps
            )

        # Calculate timing values for display
        display_flow_rate = 1 if params.volume_time_mode == VolumeTimeMode.VOLUME else flow_rate

        column_volume_extruded_time = vbc[0] / display_flow_rate if len(vbc) > 0 else elution_duration
        sweep_time = vbc[1] / display_flow_rate if len(vbc) > 1 else None

        return SimulationResults(
            simulation_type=SimulationType.EXTRUSION,
            vspan=vspan,
            cout=cout,
            parameters=params,
            compounds=compounds,
            metadata={
                'xtot': xtot,
                'ytot': ytot,
                'vbc': vbc,
                'vcm': classic_params.get_vcm(),
                'column_volume_extruded_time': column_volume_extruded_time,
                'sweep_time': sweep_time,
                'elution_time': elution_duration,
                'ccc_cpc_mode': ccc_cpc_mode,
                'volume_time_mode': params.volume_time_mode,
                'elution_duration': effective_elution_duration,
                'extrusion_duration': extrusion_duration
            }
        )

    def _run_dual(self, params: SimulationParameters, compounds: List[CompoundData], kd_array, conc_array, extra_params: Dict):
        """Run dual mode simulation"""
        effective_elution_duration = params.elution_duration

        classic_params = replace(params, elution_duration=effective_elution_duration)

        # First run classic simulation to get initial conditions
        classic_results = self._run_classic(classic_params, compounds, kd_array, conc_array)
        x_classic = classic_results.metadata.get('x')
        y_classic = classic_results.metadata.get('y')

        # Get dual mode duration from extra_params
        dual_duration = extra_params.get('dual_duration', 10.0)

        # Convert dual_duration to volume if in Time mode
        if params.volume_time_mode == VolumeTimeMode.TIME:
            vdm = dual_duration * params.flow_rate
        else:
            vdm = dual_duration

        # Run dual mode simulation
        vspan_dual, cout_dual, xtot, ytot = DualV2(
            kd_array,
            params.column_volume,
            params.get_effective_sf(),
            params.flow_rate,
            vdm,
            x_classic,
            y_classic
        )

        return SimulationResults(
            simulation_type=SimulationType.DUAL,
            vspan=vspan_dual,
            cout=cout_dual,
            parameters=params,
            compounds=compounds,
            metadata={
                'xtot': xtot,
                'ytot': ytot,
                'simulation_type': 'dual',
                'dual_duration': dual_duration,
                'dual_volume': vdm,
                'classic_results': classic_results
            }
        )

    def _run_multi(self, params: SimulationParameters, compounds: List[CompoundData], kd_array, conc_array, extra_params: Dict):
        """Run multiple dual mode simulation"""
        # Get switching times from extra_params
        switch_times = extra_params.get('switch_times', [10.0, 5.0])

        # Convert switch times to volumes if in Time mode
        if params.volume_time_mode == VolumeTimeMode.TIME:
            switch_volumes = [t * params.flow_rate for t in switch_times]
        else:
            switch_volumes = switch_times

        # Adjust the main elution volume based on injection volume inclusion
        main_elution_volume = params.get_vcm()

        # Combine the main elution volume (vcm) with the switch volumes
        vcm_array = np.concatenate(([main_elution_volume], switch_volumes))

        # Run multiple dual mode simulation - MDMV2 returns 7 values
        vtot, ctot, xtot, ytot, tcut, vswdm, vswcm = MDMV2(
            params.get_effective_sf(),
            kd_array,
            params.column_volume,
            params.get_effective_n(),
            conc_array,
            params.injection_volume,
            vcm_array
        )

        return SimulationResults(
            simulation_type=SimulationType.MULTI,
            vspan=vtot,
            cout=ctot,
            parameters=params,
            compounds=compounds,
            metadata={
                'xtot': xtot,
                'ytot': ytot,
                'vbc': vswdm,  # Switching volumes for DM
                'vcyc': vswcm,  # Switching volumes for CM
                'simulation_type': 'multi',
                'switch_times': switch_times,
                'switch_volumes': switch_volumes,
                'vcm_array': vcm_array.tolist(),
                'tcut': tcut.tolist() if hasattr(tcut, 'tolist') else tcut
            }
        )

    def get_cached_result(self, sim_type: SimulationType,
                          parameters: SimulationParameters,
                          compounds: List[CompoundData],
                          extra_params: Optional[Dict] = None) -> Optional[SimulationResults]:
        """Get cached result if available"""
        cache_key = self._create_cache_key(sim_type, parameters, compounds, extra_params)
        return self.cache.get(cache_key)

    def invalidate_cache_for_type(self, sim_type: SimulationType):
        """Remove all cached results for a specific simulation type"""
        keys_to_remove = []
        for key, result in self.cache.items():
            if result.simulation_type == sim_type:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.cache[key]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging"""
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cached_types': [result.simulation_type.value for result in self.cache.values()],
            'memory_usage_mb': sum(
                result.vspan.nbytes + result.cout.nbytes
                for result in self.cache.values()
            ) / (1024 * 1024)
        }


class PlotHandlersMixin:
    def __init__(self):
        """Initialize plotting components"""
        # Initialize colors for plotting
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        # Initialize result storage
        self.classic_results = None
        self.extrusion_results = None
        self.dual_results = None
        self.multi_results = None

        # Initialize trace data
        self.pulse_data = None
        self.fit_data = None
        self.pulse_peaks = None
        self.fit_peaks = None

    def force_consistent_fonts(self):
        """Force font sizes to be consistent regardless of plot content"""
        # List all your actual axes attributes
        axes_list = [
            getattr(self, 'classic_ax', None),
            getattr(self, 'dual_ax', None),
            getattr(self, 'extrusion_ax', None),
            getattr(self, 'multi_ax', None),
            getattr(self, 'pulse_ax', None)
            # Add any other axes you have
        ]

        for ax in axes_list:
            if ax is not None:
                ax.set_xlabel(ax.get_xlabel(), fontsize=11)
                ax.set_ylabel(ax.get_ylabel(), fontsize=11)
                ax.tick_params(axis='both', which='major', labelsize=9)

    def plot_classic(self):
        """Plot classic elution model using enhanced PlotRenderer"""
        self.classic_ax.clear()  # Keep this for safety

        try:
            parameters = self._extract_parameters_from_gui()
            compounds = self._extract_compounds_from_gui()

            results = self.simulation_service.run_simulation(
                SimulationType.CLASSIC, parameters, compounds
            )

            # Store for export
            self.classic_results = {
                'vspan': results.vspan,
                'cout': results.cout,
                'x': results.metadata.get('x'),
                'y': results.metadata.get('y')
            }

            config = PlotConfig(
                title="",
                show_sum=self.classic_sum_var.get(),
                show_peak_labels=self.classic_peaks_var.get(),
                show_grid=self.classic_grid_var.get()
            )

            renderer = PlotRenderer(self.classic_ax, self.classic_canvas, self.classic_fig)
            renderer.render_simulation(results, config, gui_context=self)

            # Update retention times in the compound table
            self.update_retention_times_from_results(results)

        except Exception as e:
            self.show_notification(f"Classic simulation failed: {str(e)}", notif_type="error")

    def plot_extrusion(self):
        """Plot elution-extrusion model using enhanced PlotRenderer"""
        self.extrusion_ax.clear()  # Keep this for safety

        try:
            parameters = self._extract_parameters_from_gui()
            compounds = self._extract_compounds_from_gui()

            extra_params = {
                'ccc_cpc_mode': self.ccc_cpc_var.get(),
                'extrusion_duration': float(self.extrusion_duration_entry.get()),
                'elution_duration': float(self.elution_duration_entry.get())
            }

            results = self.simulation_service.run_simulation(
                SimulationType.EXTRUSION, parameters, compounds, extra_params
            )

            # Store for export
            self.extrusion_results = {
                'vspan': results.vspan,
                'cout': results.cout,
                'xtot': results.metadata.get('xtot'),
                'ytot': results.metadata.get('ytot'),
                'vbc': results.metadata.get('vbc')
            }

            config = PlotConfig(
                title="",
                show_sum=self.extrusion_sum_var.get(),
                show_peak_labels=self.extrusion_peaks_var.get(),
                show_grid=self.extrusion_grid_var.get(),
                show_lines=self.extrusion_lines_var.get(),
                show_line_labels=self.extrusion_lines_labels_var.get()
            )

            renderer = PlotRenderer(self.extrusion_ax, self.extrusion_canvas, self.extrusion_fig)
            renderer.render_simulation(results, config, gui_context=self)

            # Update retention times in the compound table
            self.update_retention_times_from_results(results)

        except Exception as e:
            self.show_notification(f"Extrusion simulation failed: {str(e)}", notif_type="error")

    def plot_dual(self):
        """Plot dual mode elution model using enhanced PlotRenderer"""
        self.dual_ax.clear()  # Keep this for safety

        try:
            parameters = self._extract_parameters_from_gui()
            compounds = self._extract_compounds_from_gui()

            extra_params = {
                'dual_duration': float(self.dual_duration_entry.get())
            }

            results = self.simulation_service.run_simulation(
                SimulationType.DUAL, parameters, compounds, extra_params
            )

            # Store for export
            self.dual_results = {
                'vspan': results.vspan,
                'cout': results.cout,
                'xtot': results.metadata.get('xtot'),
                'ytot': results.metadata.get('ytot')
            }

            config = PlotConfig(
                title="",
                show_sum=self.dual_sum_var.get(),
                show_peak_labels=self.dual_peaks_var.get(),
                show_grid=self.dual_grid_var.get(),
                show_lines=self.dual_lines_var.get(),
                show_line_labels=self.dual_lines_labels_var.get()
            )

            renderer = PlotRenderer(self.dual_ax, self.dual_canvas, self.dual_fig)
            renderer.render_simulation(results, config, gui_context=self)

            # Update retention times in the compound table
            self.update_retention_times_from_results(results)

        except Exception as e:
            self.show_notification(f"Dual simulation failed: {str(e)}", notif_type="error")

    def plot_multi(self):
        """Plot multiple dual mode elution model using enhanced PlotRenderer"""
        self.multi_ax.clear()
        self.multi_pos_ax.clear()

        try:
            parameters = self._extract_parameters_from_gui()
            compounds = self._extract_compounds_from_gui()

            # Get switching times
            switch_times = []
            for item in self.switch_times_table.get_children():
                values_row = self.switch_times_table.item(item, 'values')
                try:
                    switch_times.append(float(values_row[1]))
                except (ValueError, IndexError):
                    pass

            if not switch_times:
                self.show_notification("Please add at least one switch time", notif_type="warning")
                return

            extra_params = {'switch_times': switch_times}

            # Use simulation service to get results
            results = self.simulation_service.run_simulation(
                SimulationType.MULTI, parameters, compounds, extra_params
            )

            # Store for export
            self.multi_results = {
                'vspan': results.vspan,
                'cout': results.cout,
                'xtot': results.metadata.get('xtot'),
                'ytot': results.metadata.get('ytot'),
                'vbc': results.metadata.get('vbc'),
                'vcyc': results.metadata.get('vcyc')
            }

            # Create plot config
            config = PlotConfig(
                title="",
                show_sum=getattr(self, 'multi_sum_var', None) and self.multi_sum_var.get(),
                show_peak_labels=getattr(self, 'multi_peaks_var', None) and self.multi_peaks_var.get(),
                show_grid=getattr(self, 'multi_grid_var', None) and self.multi_grid_var.get(),
                show_lines=getattr(self, 'multi_lines_var', None) and self.multi_lines_var.get(),
                show_line_labels=getattr(self, 'multi_lines_labels_var', None) and self.multi_lines_labels_var.get()
            )

            # Use PlotRenderer with the updated _render_multi method
            renderer = PlotRenderer(self.multi_ax, self.multi_canvas, self.multi_fig)
            renderer.render_simulation(results, config, gui_context=self)

            # Update retention times in the compound table
            self.update_retention_times_from_results(results)

        except Exception as e:
            traceback.print_exc()
            self.show_notification(f"Multi simulation failed: {str(e)}", notif_type="error")

    def synchronize_multi_plot_layouts(self):
        """Ensure both multi mode plots have identical layouts"""
        # Synchronize positions and x-axis limits
        if hasattr(self, 'multi_ax') and hasattr(self, 'multi_pos_ax'):
            # Get the position of the main plot
            pos1 = self.multi_ax.get_position()
            self.multi_pos_ax.set_position(pos1)

            # Apply consistent formatting to both axes
            for ax in [self.multi_ax, self.multi_pos_ax]:
                ax.tick_params(axis='both', which='major', labelsize=9)
                ax.set_facecolor('white')
                ax.set_axisbelow(True)

                for spine in ax.spines.values():
                    spine.set_color('gray')
                    spine.set_linewidth(0.8)

        # Draw both canvases
        if hasattr(self, 'multi_canvas'):
            self.multi_canvas.draw()
        if hasattr(self, 'multi_pos_canvas'):
            self.multi_pos_canvas.draw()

    def apply_global_plot_style(self):
        """Apply consistent styling to all matplotlib plots"""

        # Set global matplotlib parameters for consistency
        plt.rcParams.update({
            'font.size': 9,
            'axes.titlesize': 14,
            'axes.labelsize': 11,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 10,
            'figure.titlesize': 16,
            'axes.linewidth': 0.8,
            'grid.linewidth': 0.5,
            'lines.linewidth': 2.0,
            'axes.facecolor': 'white',
            'figure.facecolor': 'white',
            'savefig.facecolor': 'white',
            'axes.edgecolor': 'gray',
            'axes.grid': False,  # We'll control this per plot
            'grid.alpha': 0.7
        })

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
                    self.fit_span_entry.delete(0, tk.END)  # Clear existing content
                    self.fit_span_entry.insert(0, str(min(20, len(Y)//2)))  # Insert new value

                elif trace_type == 'pulse':
                    self.pulse_data = {'X': X, 'Y': Y}
                    self.pulse_ax.clear()
                    self.pulse_ax.plot(X, Y, linewidth=2.0)
                    self.pulse_ax.set_xlabel('Elution Time')
                    self.pulse_ax.set_ylabel('Concentration')
                    self.pulse_ax.grid(True, linestyle='--', alpha=0.7)
                    self.pulse_canvas.draw()

                self.show_notification(f"Imported {len(X)} data points", 3000, "info")

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

        baseline = self.pulse_baseline_var.get()

        try:
            X = np.array(self.pulse_data['X'], dtype=np.float64)
            Y = np.array(self.pulse_data['Y'], dtype=np.float64) - baseline

            # Ensure we have valid data
            if len(X) == 0 or len(Y) == 0:
                messagebox.showerror("Data Error", "Invalid pulse data - arrays are empty")
                return

            if len(X) != len(Y):
                messagebox.showerror("Data Error", "X and Y data arrays must have the same length")
                return

            # Apply Savitzky-Golay filter to smooth data
            window_length = int(self.pulse_span_entry.get())

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

            # Find peaks with specified prominence
            prominence_value = float(self.pulse_prominence_entry.get())

            # Ensure we have valid data for peak finding
            if np.max(Y_smooth) <= prominence_value:
                messagebox.showwarning("No Peaks found")
                return

            # Find peaks - convert to standard Python types to avoid numpy indexing issues
            peaks, properties = find_peaks(Y_smooth.astype(np.float64),
                                           prominence=prominence_value)

            # Convert peaks to standard Python list of integers
            peaks = [int(p) for p in peaks if 0 <= int(p) < len(X)]

            if len(peaks) == 0:
                messagebox.showwarning("No Peaks", "No peaks found with current settings")
                return

            # Check for single peak requirement
            if len(peaks) > 1:
                # Multiple peaks found - show warning and don't enable N calculation
                self.show_notification(f"Found {len(peaks)} peaks. Please adjust the baseline, prominence, and span parameters to isolate a single peak.",
                                       duration=2000, notif_type="warning")

                # Still plot the results so user can see what was found
                self._plot_pulse_results(X, Y, Y_smooth, peaks, multiple_peaks=True)
                self.pulse_peaks = peaks
                return

            # Exactly one peak found - success!
            self.show_notification(f"Found 1 peak at time {X[peaks[0]]:.3f} min.", duration=2000, notif_type="success")

            # Store flow rate for N calculation
            self.pulse_flow_rate = float(self.flow_rate_entry.get())
            self.pulse_sf = float(self.stationary_phase_single_entry.get())
            self.pulse_peaks = peaks
            self.pulse_X = X
            self.pulse_Y_smooth = Y_smooth

            # Plot results
            self._plot_pulse_results(X, Y, Y_smooth, peaks, multiple_peaks=False)

            # Show success message
            self.show_notification("Ready for N calculation", duration=2000, notif_type="success")

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Peak Finding Error", f"Error finding peaks: {str(e)}")

    def _plot_pulse_results(self, X, Y, Y_smooth, peaks, multiple_peaks=False):
        """Helper method to plot pulse results"""

        self.pulse_ax.clear()
        self.pulse_ax.plot(X, Y, 'k-', alpha=0.4, linewidth=1, label='Raw')
        self.pulse_ax.plot(X, Y_smooth, 'b-', linewidth=1.5, label='Smoothed')

        # Plot peaks using integer indices
        peak_x = [X[i] for i in peaks]
        peak_y = [Y_smooth[i] for i in peaks]

        if multiple_peaks:
            # Red X for multiple peaks (not usable for N calculation)
            self.pulse_ax.plot(peak_x, peak_y, 'rx', markersize=8, markeredgewidth=2, label='Multiple Peaks')

            # Add warning text
            self.pulse_ax.text(0.5, 0.95, f"⚠ {len(peaks)} peaks found",
                               transform=self.pulse_ax.transAxes, ha='center', va='top',
                               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
                               fontsize=10, fontweight='bold')
        else:
            # Green circle for single peak (ready for N calculation)
            self.pulse_ax.plot(peak_x, peak_y, 'go', markersize=10, label='Selected Peak')

            # Add success text
            self.pulse_ax.text(0.5, 0.95, "✓ 1 peak found",
                               transform=self.pulse_ax.transAxes, ha='center', va='top',
                               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
                               fontsize=10, fontweight='bold')

        # Add peak labels
        for i, peak_idx in enumerate(peaks):
            label_text = f"Peak {i+1}" if multiple_peaks else "Selected Peak"
            self.pulse_ax.annotate(label_text,
                                   (X[peak_idx], Y_smooth[peak_idx]*0.97),
                                   xytext=(0, 15),
                                   textcoords="offset points",
                                   ha='center',
                                   fontweight='bold' if not multiple_peaks else 'normal')

        self.pulse_ax.legend(loc='upper left')
        self.pulse_ax.grid(True)
        self.pulse_ax.set_xlabel('Elution Time (min)')
        self.pulse_ax.set_ylabel('Signal')
        self.pulse_ax.set_ylim(bottom=None, top=max(Y_smooth) * 1.1)
        self.pulse_canvas.draw()

    def find_fit_peaks(self):
        """Find peaks in fit data for KD determination"""
        if not hasattr(self, 'fit_data') or not self.fit_data:
            messagebox.showinfo("No Data", "Please import fit data first")
            return

        if self.volume_time_var.get() == "Volume":
            self.volume_time_var.set("Time")  # Ensure consistent mode for KD calculation

        try:
            X = self.fit_data['X']
            Y = self.fit_data['Y']

            # Apply Savitzky-Golay filter to smooth data
            window_length = int(self.fit_span_entry.get())
            if window_length % 2 == 0:
                window_length += 1  # Must be odd
            Y_smooth = savgol_filter(Y, window_length, 3)

            # Subtract threshold
            threshold = self.fit_threshold_var.get()
            Y_adjusted = Y_smooth - threshold
            Y_adjusted[Y_adjusted < 0] = 0

            # Find peaks with specified prominence

            peaks, properties = find_peaks(Y_adjusted, prominence=float(self.fit_prominence_entry.get()))

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

            self.fit_ax.legend(loc='upper left')
            self.fit_ax.grid(True)
            self.fit_ax.set_xlabel('Time (min)')
            self.fit_ax.set_ylabel('Signal')
            self.fit_canvas.draw()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Peak Finding Error", f"Error finding peaks: {str(e)}")

    def _extract_parameters_from_gui(self) -> SimulationParameters:
        """Extract SimulationParameters from GUI widgets"""
        return SimulationParameters(
            flow_rate=float(self.flow_rate_entry.get()),
            column_volume=float(self.column_volume_entry.get()),
            elution_duration=float(self.elution_duration_entry.get()),
            injection_volume=float(self.injection_volume_entry.get()),
            stationary_phase=float(self.stationary_phase_single_entry.get()),
            column_efficiency=int(float(self.column_efficiency_single_entry.get())),
            volume_time_mode=VolumeTimeMode(self.volume_time_var.get()),
            use_sf_coefficients=(self.stationary_phase_var.get() == "Coeff."),
            sf_coeff_a=float(self.sf_coefficient_a_entry.get()) if hasattr(self, 'sf_coefficient_a_entry') else 0.982,
            sf_coeff_b=float(self.sf_coefficient_b_entry.get()) if hasattr(self, 'sf_coefficient_b_entry') else -0.142,
            use_n_coefficients=(self.column_efficiency_var.get() == "Coeff."),
            n_coeff_a=float(self.n_coefficient_a_entry.get()) if hasattr(self, 'n_coefficient_a_entry') else 371.23,
            n_coeff_b=float(self.n_coefficient_b_entry.get()) if hasattr(self, 'n_coefficient_b_entry') else -7.204,
            n_coeff_c=float(self.n_coefficient_c_entry.get()) if hasattr(self, 'n_coefficient_c_entry') else 0.1480
        )

    def _extract_compounds_from_gui(self) -> List[CompoundData]:
        """Extract compounds from GUI table"""
        compounds = []
        for item in self.compound_table.get_children():
            values = self.compound_table.item(item, 'values')
            kd = float(values[1])

            if self.mobile_phase_var.get() == 'Upper':
                kd = 1.0 / kd

            compounds.append(CompoundData(
                name=values[0],
                kd=kd,
                concentration=float(values[2]),
                retention_time=float(values[3])
            ))
        return compounds
