from tkinter import ttk
from .gui_elements import GUIElementsMixin
from .plot_handlers import PlotHandlersMixin, SimulationService
from .interface_controls import InterfaceControlsMixin
from .state_management import StateManagementMixin
from .validation import ValidationMixin
from .undo_manager import UndoManager


class AppV1(GUIElementsMixin, PlotHandlersMixin, StateManagementMixin, ValidationMixin, InterfaceControlsMixin):
    def __init__(self, root):
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
        # ... window setup ...
        self.setup_validation()
        self.create_menu()
        self.create_left_panel()
        self.create_right_panel()
        self.apply_global_plot_style()
        self.setup_inline_editing()
        self.undo_manager = UndoManager(max_history=50, notification_callback=self.show_notification)
        self.undo_manager.main_app = self
        self.setup_keyboard_shortcuts()
        self.show_notification("Welcome to CUP Modeler! I'll give you quick insights into what's going on down here throughout your use of the modeler, important errors will interrupt you with a dialogue window. Go ahead, try predicting a separation!", duration=5000, notif_type="info")
        self.force_consistent_fonts()
        self.simulation_service = SimulationService()
