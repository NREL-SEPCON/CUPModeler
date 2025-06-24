import uuid
from collections import deque


class UndoCommand:
    def __init__(self, description: str):
        self.description = description

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


class EditCellCommand(UndoCommand):
    def __init__(self, table_widget, unique_id=None, item_id=None, column=None, old_value=None, new_value=None):
        # Handle both parameter names for compatibility
        if item_id is not None and unique_id is None:
            unique_id = item_id

        super().__init__(f"Edit {column}: {old_value} → {new_value}")
        self.table = table_widget
        self.unique_id = unique_id
        self.column = column
        self.old_value = old_value
        self.new_value = new_value

    def execute(self):
        try:
            self.table.set(self.unique_id, self.column, self.new_value)
            return True
        except Exception as e:
            print(f"Error applying edit: {e}")
            return False

    def undo(self):
        try:
            self.table.set(self.unique_id, self.column, self.old_value)
            return True
        except Exception as e:
            print(f"Error undoing edit: {e}")
            return False


class DeleteRowCommand(UndoCommand):
    def __init__(self, table_widget, unique_id, values, position, undo_manager=None):
        super().__init__(f"Delete row: {values[0] if values else 'Unknown'}")
        self.table = table_widget
        self.unique_id = unique_id  # Use unique_id instead of item_id
        self.values = values
        self.position = position
        # undo_manager parameter is not needed in command classes

    def execute(self):
        try:
            self.table.delete(self.unique_id)
            return True
        except Exception as e:
            print(f"Error deleting row: {e}")
            return False

    def undo(self):
        try:
            children = list(self.table.get_children())
            if 0 <= self.position < len(children):
                self.table.insert('', self.position, iid=self.unique_id, values=self.values)
            else:
                self.table.insert('', 'end', iid=self.unique_id, values=self.values)
            return True
        except Exception as e:
            print(f"Error restoring row: {e}")
            return False


class AddRowCommand(UndoCommand):
    def __init__(self, table_widget, unique_id=None, values=None, position='end'):
        super().__init__(f"Add row: {values[0] if values else 'Unknown'}")
        self.table = table_widget
        self.unique_id = unique_id or str(uuid.uuid4())  # Generate if not provided
        self.values = values or []
        self.position = position

    def execute(self):
        try:
            if self.position == 'end':
                self.table.insert('', 'end', iid=self.unique_id, values=self.values)
            else:
                children = list(self.table.get_children())
                if 0 <= self.position < len(children):
                    self.table.insert('', self.position, iid=self.unique_id, values=self.values)
                else:
                    self.table.insert('', 'end', iid=self.unique_id, values=self.values)
            return True
        except Exception as e:
            print(f"Error adding row: {e}")
            return False

    def undo(self):
        try:
            self.table.delete(self.unique_id)
            return True
        except Exception as e:
            print(f"Error undoing add: {e}")
            return False


class UndoManager:
    def __init__(self, max_history: int = 50, notification_callback=None):
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)
        self.main_app = None
        self.notification_callback = notification_callback

    def execute_command(self, command):
        if command.execute():
            self.undo_stack.append(command)
            self.redo_stack.clear()
            return True
        return False

    def undo(self):
        if not self.undo_stack:
            return False
        command = self.undo_stack.pop()

        # Direct check using main app reference
        if (self.main_app and hasattr(command, 'table') and command.table is self.main_app.switch_times_table):
            self.main_app.switch_to_tab(3)

        if command.undo():
            self.redo_stack.append(command)
            self.notification_callback(f"Undid: {command.description}", notif_type="info")
            return True
        else:
            self.undo_stack.append(command)
            return False

    def redo(self):
        if not self.redo_stack:
            return False
        command = self.redo_stack.pop()

        # Direct check using main app reference
        if (self.main_app and hasattr(command, 'table') and command.table is self.main_app.switch_times_table):
            self.main_app.switch_to_tab(3)

        if command.execute():
            self.undo_stack.append(command)
            self.notification_callback(f"Redid: {command.description}", notif_type="info")
            return True
        else:
            self.redo_stack.append(command)
            return False

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0
