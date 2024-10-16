import tkinter as tk


class Tooltip:
    """
    A class to create and manage tooltips for Tkinter widgets.

    Attributes:
    widget (tk.Widget): The widget to which the tooltip is attached.
    text (str): The text to display in the tooltip.
    tip_window (tk.Toplevel): The window that displays the tooltip.
    id (str): The ID of the scheduled event to show the tooltip.
    """

    def __init__(self, widget, text):
        """
        Initializes the Tooltip instance.

        Args:
        widget (tk.Widget): The widget to which the tooltip is attached.
        text (str): The text to display in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        """
        Event handler for when the mouse enters the widget.
        Schedules the tooltip to be shown.
        """
        self.schedule()

    def leave(self, event=None):
        """
        Event handler for when the mouse leaves the widget.
        Unschedules and hides the tooltip.
        """
        self.unschedule()
        self.hidetip()

    def schedule(self):
        """
        Schedules the tooltip to be shown after a delay.
        """
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        """
        Unschedules the tooltip if it is scheduled.
        """
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event=None):
        """
        Displays the tooltip.

        Args:
        event (tk.Event, optional): The event that triggered the tooltip.
        """
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + cy + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """
        Hides the tooltip if it is currently displayed.
        """
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def enable(self):
        """
        Enables the tooltip by binding the enter and leave events.
        """
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def disable(self):
        """
        Disables the tooltip by unbinding the enter and leave events.
        """
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
