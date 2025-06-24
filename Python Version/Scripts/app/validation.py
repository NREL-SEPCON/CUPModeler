import tkinter as tk
from tkinter import ttk


class ValidationMixin:
    def setup_validation(self):
        """Register validation functions with tkinter"""
        # Set up styles for visual feedback
        self.setup_entry_styles()

        # Register the permissive keystroke validation
        self.validate_while_typing = (self.root.register(self.validate_keystroke), '%P', '%W', '%V')

    def validate_keystroke(self, value, widget_name, validation_event):
        """Permissive validation while typing - only block obviously wrong characters"""

        # Always allow empty string (user clearing field)
        if value == "":
            return True

        # Allow intermediate states like ".", "+", "0.", "12.", etc.
        # Note: We allow "-" during typing but adress it later
        if value in [".", "-", "+", "0.", "-0.", "+0.", "-."] or value.endswith('.'):
            return True

        # Allow partial scientific notation like "1e", "1e-", etc.
        if any(value.endswith(suffix) for suffix in ["e", "E", "e-", "e+", "E-", "E+"]):
            return True

        # Try to parse as float - if it works, allow it during typing
        # We'll enforce rules later on focus-out
        try:
            float(value)
            return True
        except ValueError:
            # Only block if it's clearly not heading toward a valid number
            # This catches things like typing letters
            return False

    def validate_final_value(self, entry_widget, validation_params):
        """Strict validation when user finishes editing"""
        value = entry_widget.get().strip()

        # Get validation parameters
        min_val = validation_params.get('min_val', None)
        max_val = validation_params.get('max_val', None)
        allow_zero = validation_params.get('allow_zero', True)
        integer_only = validation_params.get('integer_only', False)
        allow_negative = validation_params.get('allow_negative', True)
        default_value = validation_params.get('default_value', '1')

        # If empty or incomplete, set to default
        if value == "" or value in [".", "-", "+", "e", "E", "-.", "+."]:
            self.set_entry_value(entry_widget, default_value)
            if value != "":  # Only show message if they actually typed something incomplete
                self.show_notification(f"Incomplete entry replaced with {default_value}",
                                       duration=1500, notif_type="info")
            return

        try:
            num = float(value)
            original_value = value
            use_default = False

            # Check if we should use default value instead of trying to fix
            # Use default for violations of core business rules
            if not allow_negative and num < 0:
                use_default = True

            if not allow_zero and num == 0:
                use_default = True

            # Check minimum value (but allow zero if explicitly allowed)
            if min_val is not None and num <= min_val:
                if not (allow_zero and num == 0):
                    use_default = True

            # Check maximum value
            if max_val is not None and num >= max_val:
                use_default = True

            # If any core rule is violated, use default
            if use_default:
                self.set_entry_value(entry_widget, default_value)
                self.show_notification(f"Invalid value '{original_value}' replaced with {default_value}",
                                       duration=2000, notif_type="info")
                return

            # Only do minor fixes for format issues
            fixed = False

            # Check integer requirement (this is just formatting)
            if integer_only and num != int(num):
                num = int(round(num))
                fixed = True

            # Update field if we did minor formatting fixes
            if fixed:
                final_value = str(int(num)) if integer_only else str(num)
                self.set_entry_value(entry_widget, final_value)
                self.show_notification(f"Value formatted from {original_value} to {final_value}",
                                       duration=1500, notif_type="info")

            # Remove any error styling (works for both tk.Entry and ttk.Entry)
            try:
                entry_widget.configure(style="TEntry")
            except:
                # tk.Entry doesn't have style, just ignore
                pass

        except ValueError:
            # Invalid number, reset to default
            self.set_entry_value(entry_widget, default_value)
            self.show_notification(f"Invalid number '{value}' replaced with {default_value}",
                                   duration=2000, notif_type="warning")

    def set_entry_value(self, entry_widget, value):
        """Helper to set entry widget value"""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, str(value))

    def create_validated_entry(self, parent, validation_params=None, **kwargs):
        """Create entry with natural editing experience"""
        if validation_params is None:
            validation_params = {}

        # Set sensible defaults based on common field types
        if 'default_value' not in validation_params:
            if validation_params.get('integer_only'):
                validation_params['default_value'] = '400'  # Good for efficiency
            elif validation_params.get('max_val') == 1:
                validation_params['default_value'] = '0.75'  # Good for ratios
            else:
                validation_params['default_value'] = '1'     # General default

        # Create entry with permissive keystroke validation
        entry = ttk.Entry(parent, validate='key',
                          validatecommand=self.validate_while_typing, **kwargs)

        # Store validation params for later use
        entry.validation_params = validation_params

        # Add visual feedback as user types
        def on_text_change(*args):
            current_value = entry.get()

            # Check if current value violates any rules
            violates_rules = False

            if current_value and current_value not in ["", ".", "-", "+", "0.", "-0.", "+0.", "-.", "+."]:
                try:
                    num = float(current_value)

                    # Check against validation rules
                    if not validation_params.get('allow_negative', True) and num < 0:
                        violates_rules = True
                    elif not validation_params.get('allow_zero', True) and num == 0:
                        violates_rules = True
                    elif validation_params.get('min_val') is not None and num <= validation_params['min_val']:
                        if not (validation_params.get('allow_zero', True) and num == 0):
                            violates_rules = True
                    elif validation_params.get('max_val') is not None and num >= validation_params['max_val']:
                        violates_rules = True

                except ValueError:
                    # Invalid number format
                    violates_rules = True

            # Apply visual feedback
            if violates_rules:
                entry.configure(style="Invalid.TEntry")  # Red border
            else:
                entry.configure(style="TEntry")  # Normal appearance

        # Bind to text changes for visual feedback
        entry_var = tk.StringVar()
        entry.configure(textvariable=entry_var)
        entry_var.trace('w', on_text_change)

        # Add strict validation when user finishes editing
        def on_focus_out(event):
            self.root.after_idle(lambda: self.validate_final_value(entry, validation_params))

        def on_enter_key(event):
            self.validate_final_value(entry, validation_params)
            return 'break'  # Prevent default Enter behavior

        entry.bind('<FocusOut>', on_focus_out, '+')  # '+' means add to existing bindings
        entry.bind('<Tab>', lambda e: self.root.after_idle(lambda: self.validate_final_value(entry, validation_params)))
        entry.bind('<Return>', on_enter_key)
        entry.bind('<KP_Enter>', on_enter_key)  # Keypad Enter

        return entry

    def is_partial_valid(self, value):
        """Check if value could become valid (intermediate state)"""
        if value in ["", ".", "-", "+", "0.", "-0.", "+0.", "-.", "+."]:
            return True
        if any(value.endswith(suffix) for suffix in ["e", "E", "e-", "e+", "E-", "E+"]):
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_potentially_valid(self, value, params):
        """Check if value could eventually meet validation criteria"""
        if not self.is_partial_valid(value):
            return False

        try:
            num = float(value)
            # Even if it violates rules now, it could be fixed automatically
            return True
        except ValueError:
            return True  # Partial entries are potentially valid

    def setup_entry_styles(self):
        """Setup visual styles for validation feedback"""
        style = ttk.Style()

        # Invalid input style (subtle red border, no background change)
        style.configure("Invalid.TEntry",
                        bordercolor="#FF6B6B",
                        focuscolor="#FF6B6B")
