import json
import logging
import os
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk, filedialog, simpledialog, messagebox

import pytesseract

from card_saving_and_loading import start_script, ImageFilesNotFoundError, CardsNotFoundError
from tooltip import Tooltip


def main():
    """
    TTS Object to PDF GUI Application

    This module provides a graphical user interface (GUI) for converting Tabletop Simulator (TTS) objects to PDF files.
    The GUI allows users to select TTS object files, configure various settings, and start the conversion process.

    The main features include:
    - File selection for TTS object files and cache folders.
    - Preset and custom image size options.
    - Sheet size selection.
    - Margin and DPI configuration.
    - Various boolean options for processing and PDF generation.

    The GUI is built using the Tkinter library and uses the ttk module for themed widgets.

    Functions:
        main(): Initializes and runs the GUI application.
    """
    logger = logging.getLogger("GUI")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(levelname)s: %(message)s")  # noqa; because the levelname is not a typo in this context
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Loading GUI...")

    def load_user_settings() -> dict:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else:
            return {
                "bleed_width": 3.0,
                "line_width": 1,
                "show_tooltips": True,
            }

    config = load_user_settings()

    def save_user_settings(user_config: dict):
        with open("config.json", "w") as f:
            # Erroneous flagging of a problem by PyCharm. See https://stackoverflow.com/questions/79049420/python3-pickle-expected-type-supportswritebytes-got-binaryio-instead
            # noinspection PyTypeChecker
            json.dump(user_config, f, indent=4)

    # Create a root window
    root = tk.Tk()
    root.title("TTSCards")
    root.resizable(False, False)
    style = ttk.Style()
    style.theme_use("alt")

    path_string = config["path"] if "path" in config else "No file or folder selected"
    path = tk.StringVar(value=path_string)

    def select_file():
        initial_dir = (
            os.path.dirname(path.get())
            if path.get() != "No file or folder selected"
            else os.getcwd()
        )
        selected_file = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select TTS Object file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected_file:
            path.set(selected_file)
            config["path"] = selected_file
            save_user_settings(config)

    def select_images_folder():
        initial_dir = (
            os.path.dirname(path.get())
            if path.get() != "No file or folder selected"
            else os.getcwd()
        )
        selected_folder = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Folder",
        )
        if selected_folder:
            path.set(selected_folder)
            config["path"] = selected_folder
            save_user_settings(config)

    def change_bleed_width():
        bleed_width = simpledialog.askfloat(
            "Input",
            "Enter bleed width (mm):",
            minvalue=0.0,
            initialvalue=config["bleed_width"],
        )
        if bleed_width is not None:
            config["bleed_width"] = bleed_width
            save_user_settings(config)

    def change_line_width():
        line_width = simpledialog.askfloat(
            "Input",
            "Enter line width (px):",
            minvalue=0,
            initialvalue=config["line_width"],
        )
        if line_width is not None:
            config["line_width"] = line_width
            save_user_settings(config)

    def select_cache_folder():
        selected_cachepath = filedialog.askdirectory()
        if selected_cachepath:
            config["cachepath"] = selected_cachepath
            save_user_settings(config)

    # Setup tooltips
    tooltips = []

    # Create a menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Create a File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Select TTS Object file", command=select_file)
    file_menu.add_command(label="Select Images Folder", command=select_images_folder)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    # Create a Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Change Bleed Width", command=change_bleed_width)
    settings_menu.add_command(label="Change Line Width", command=change_line_width)
    settings_menu.add_command(
        label="Select TTS mod images cache folder", command=select_cache_folder
    )
    # add a command to toggle the displaying of hover tooltips
    show_tooltips = tk.BooleanVar(value=config.get("show_tooltips", True))
    settings_menu.add_checkbutton(
        label="Show Tooltips",
        variable=show_tooltips,
        command=lambda: (
            [tooltip.enable() for tooltip in tooltips] if show_tooltips.get() else [tooltip.disable() for tooltip in tooltips],
            config.update({"show_tooltips": show_tooltips.get()}),
            save_user_settings(config)
        )
    )

    # Create an About menu
    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(
        label="About",
        command=lambda: messagebox.showinfo(
            "About",
            "This application converts Tabletop Simulator (TTS) cards to PDF files. You are responsible for how you use this software.\n\nThe following open-source libraries are used in this application:\n- Pillow\n- PyTesseract\n- OpenCV\n- TkInter\n\nThis application is not affiliated with Tabletop Simulator or Berserk Games."
        ),
    )
    # Add a command to donate, with a donate button that can be clicked to go directly to the Ko-fi page
    about_menu.add_command(
        label="Support the Developer",
        command=lambda: webbrowser.open("https://ko-fi.com/cyberviber")
    )

    # Create a Learn menu
    learn_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Learn", menu=learn_menu)
    learn_menu.add_command(
        label="Tutorial Videos on YouTube",
        command=lambda: webbrowser.open("https://www.youtube.com/channel/UC6ndLpnFI0BP4UcBD8aHtjg")
    )

    # Create a main frame that uses a grid layout
    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.grid(column=0, row=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # Create a frame for displaying the selected file or folder path
    path_display_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
    path_display_frame.grid(column=0, row=0, sticky=tk.W)

    # Display the selected file or folder path
    path_header_label = ttk.Label(path_display_frame, text="Selected file or folder:")
    path_header_label.grid(column=0, row=0, sticky=tk.W)
    tooltips.append(Tooltip(path_header_label,
                 "Select either a TTS object file (.json) or a folder containing images of cards (.png, .jpg, .jpeg)."))
    path_frame = ttk.Frame(path_display_frame, relief=tk.SUNKEN, borderwidth=1)
    path_frame.grid(column=0, row=1, sticky=tk.W)
    path_label = ttk.Label(path_frame, textvariable=path, wraplength=250)
    path_label.grid(column=0, row=0, sticky=tk.W)
    tooltips.append(Tooltip(path_frame,
                 "Select either a TTS object file (.json) or a folder containing images of cards (.png, .jpg, .jpeg). The expected TTS Object is either a card, a deck of cards, or a bag containing cards or decks."))

    # Create radio buttons for the preset image size
    preset_image_size = tk.StringVar(value="standard")
    image_size_frame = ttk.LabelFrame(main_frame, text="Preset Card Size")
    image_size_frame.grid(column=0, row=2, sticky=tk.W)

    standard_radio = ttk.Radiobutton(
        image_size_frame,
        text="Standard American Card (63.5x88)",
        variable=preset_image_size,
        value="standard",
    )
    standard_radio.grid(column=0, row=0, sticky=tk.W)

    mini_radio = ttk.Radiobutton(
        image_size_frame,
        text="Mini American Card (41x63)",
        variable=preset_image_size,
        value="mini",
    )
    mini_radio.grid(column=0, row=1, sticky=tk.W)

    # Create an entry field for custom card length
    custom_card_size_frame = ttk.LabelFrame(main_frame, text="Custom Card Size")
    custom_card_size_frame.grid(column=0, row=3, sticky=tk.W)
    custom_card_length = tk.DoubleVar()
    custom_card_length_label = ttk.Label(custom_card_size_frame, text="Card Length (mm):")
    custom_card_length_label.grid(column=0, row=0, sticky=tk.W)
    custom_card_length_entry = ttk.Entry(custom_card_size_frame, textvariable=custom_card_length)
    custom_card_length_entry.grid(column=1, row=0, sticky=tk.W)
    tooltips.append(Tooltip(custom_card_size_frame,
                 "If set to 0, the selected preset card size will be used. Otherwise if you enter a value, the custom card length will be used. When resizing, the aspect ratio is maintained."))

    # Create a dropdown list for the sheet size
    sheet_size = tk.StringVar(value="Letter")
    sheet_size_frame = ttk.LabelFrame(main_frame, text="Preset Sheet Size")
    sheet_size_frame.grid(column=0, row=4, sticky=tk.W)
    sheet_size_option_menu = tk.OptionMenu(
        sheet_size_frame,
        sheet_size,
        "Letter",
        "A4",
        "Legal"
    )
    sheet_size_option_menu.grid(column=0, row=4, sticky=tk.W)

    # Create entry fields for custom sheet size
    custom_sheet_size_frame = ttk.LabelFrame(main_frame, text="Custom Sheet Size")
    custom_sheet_size_frame.grid(column=0, row=5, sticky=tk.W)
    custom_sheet_width = tk.DoubleVar()
    custom_sheet_length = tk.DoubleVar()
    custom_sheet_width_label = ttk.Label(custom_sheet_size_frame, text="Sheet Width (mm):")
    custom_sheet_width_label.grid(column=0, row=0, sticky=tk.W)
    custom_sheet_width_entry = ttk.Entry(custom_sheet_size_frame, textvariable=custom_sheet_width)
    custom_sheet_width_entry.grid(column=1, row=0, sticky=tk.W)
    custom_sheet_length_label = ttk.Label(custom_sheet_size_frame, text="Sheet Length (mm):")
    custom_sheet_length_label.grid(column=0, row=1, sticky=tk.W)
    custom_sheet_length_entry = ttk.Entry(custom_sheet_size_frame, textvariable=custom_sheet_length)
    custom_sheet_length_entry.grid(column=1, row=1, sticky=tk.W)
    tooltips.append(Tooltip(custom_sheet_size_frame,
                 "If set to 0, the selected preset sheet size will be used. Otherwise if you enter a value, the custom sheet size will be used."))

    # Create entry fields for the margin size and dpi
    gutter_margin_size = tk.DoubleVar(value=3.175)
    dpi = tk.IntVar(value=360)
    margin_dpi_frame = ttk.LabelFrame(main_frame, text="Margin and DPI")
    margin_dpi_frame.grid(column=0, row=6, sticky=tk.W)

    gutter_margin_size_label = ttk.Label(margin_dpi_frame, text="Gutter Margin (mm):")
    gutter_margin_size_label.grid(column=0, row=0, sticky=tk.W)
    gutter_margin_size_entry = ttk.Entry(
        margin_dpi_frame, textvariable=gutter_margin_size
    )
    gutter_margin_size_entry.grid(column=1, row=0, sticky=tk.W)
    tooltips.append(Tooltip(gutter_margin_size_entry, "Gutter margin refers to the space in between cards on the sheet."))

    dpi_label = ttk.Label(margin_dpi_frame, text="DPI:")
    dpi_label.grid(column=0, row=1, sticky=tk.W)
    dpi_entry = ttk.Entry(margin_dpi_frame, textvariable=dpi)
    dpi_entry.grid(column=1, row=1, sticky=tk.W)
    tooltips.append(Tooltip(dpi_entry,
                 "DPI (dots per inch) is the resolution of the output PDF file. Higher DPI values result in higher quality images but larger file sizes."))

    # Create checkboxes for the Additional Options
    verbose = tk.BooleanVar(value=True)
    process_nested_containers = tk.BooleanVar(value=True)
    exclude_card_urls = tk.BooleanVar(value=True)
    exclude_card_backs = tk.BooleanVar()
    generate_bleed = tk.BooleanVar()
    sharpen_text = tk.BooleanVar()
    draw_cut_lines = tk.BooleanVar()
    split_double_and_single = tk.BooleanVar()
    double_only = tk.BooleanVar()
    single_only = tk.BooleanVar()
    save_images = tk.BooleanVar()
    skip_pdf_generation = tk.BooleanVar()
    cut_lines_on_margin_only = tk.BooleanVar()
    no_cut_lines_on_last_sheet = tk.BooleanVar()
    additional_options_frame = ttk.LabelFrame(main_frame, text="General Options")
    additional_options_frame.grid(column=1, row=0, rowspan=1, sticky=tk.W)

    verbose_checkbox = ttk.Checkbutton(
        additional_options_frame, text="Verbose Console Output", variable=verbose
    )
    verbose_checkbox.grid(column=0, row=0, sticky=tk.W)
    tooltips.append(Tooltip(verbose_checkbox, "The console output will have more details."))

    process_nested_containers_checkbox = ttk.Checkbutton(
        additional_options_frame,
        text="Process Nested Bags",
        variable=process_nested_containers,
    )
    process_nested_containers_checkbox.grid(column=0, row=1, sticky=tk.W)
    tooltips.append(Tooltip(process_nested_containers_checkbox, "Bags that are nested within other bags will be processed."))

    exclude_card_urls_checkbox = ttk.Checkbutton(
        additional_options_frame,
        text="Exclude specific card image URLs",
        variable=exclude_card_urls,
    )
    exclude_card_urls_checkbox.grid(column=0, row=2, sticky=tk.W)
    tooltips.append(Tooltip(exclude_card_urls_checkbox,
                 "You can create a file named `image_blacklist.txt` in the application directory and list the URLs of the card images you want to exclude from the output, where each URL is on separate lines. You have to look in the TTS object file to find the specific URLs of the card images."))

    exclude_card_backs_checkbox = ttk.Checkbutton(
        additional_options_frame,
        text="Exclude card backs",
        variable=exclude_card_backs,
    )
    exclude_card_backs_checkbox.grid(column=0, row=3, sticky=tk.W)
    tooltips.append(Tooltip(exclude_card_backs_checkbox, "All card backs will be excluded from the output"))

    save_images_checkbox = ttk.Checkbutton(
        additional_options_frame, text="Save Images to File", variable=save_images
    )
    save_images_checkbox.grid(column=0, row=4, sticky=tk.W)
    tooltips.append(Tooltip(save_images_checkbox,
                 "The card images will be saved to a folder named 'output/img' in the same directory as this application."))

    pdf_generation_options_frame = ttk.LabelFrame(
        main_frame, text="PDF Generation Options"
    )
    pdf_generation_options_frame.grid(column=1, row=1, rowspan=6, sticky=tk.W)

    generate_bleed_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame,
        text="Generate Bleed",
        variable=generate_bleed,
    )
    generate_bleed_checkbox.grid(column=0, row=1, sticky=tk.W)
    tooltips.append(Tooltip(generate_bleed_checkbox,
                 "A bleed area will be generated around the card images by mirroring the pixels at the edges of the card images. The bleed width can be configured in the Settings menu."))

    sharpen_text_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame,
        text="Sharpen Text",
        variable=sharpen_text,
    )
    sharpen_text_checkbox.grid(column=0, row=2, sticky=tk.W)
    tooltips.append(Tooltip(sharpen_text_checkbox,
                 "The text in the card images will be sharpened using Tesseract OCR and OpenCV. This option requires Tesseract to be installed and added to PATH."))

    draw_cut_lines_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame, text="Draw Cut Lines", variable=draw_cut_lines
    )
    draw_cut_lines_checkbox.grid(column=0, row=3, sticky=tk.W)
    tooltips.append(Tooltip(draw_cut_lines_checkbox,
                 "Cut lines that can make it easier to cut the cards will be drawn on the output PDF file."))

    cut_lines_on_margin_only_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame,
        text="Cut Lines on Margins Only",
        variable=cut_lines_on_margin_only,
    )
    cut_lines_on_margin_only_checkbox.grid(column=0, row=4, sticky=tk.W)
    tooltips.append(Tooltip(cut_lines_on_margin_only_checkbox,
                 "Cut lines will only be drawn on the margins of the sheet, instead of going through the cards and the bleed area."))

    no_cut_lines_on_last_sheet_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame,
        text="No Cut Lines on Last Sheet",
        variable=no_cut_lines_on_last_sheet,
    )
    no_cut_lines_on_last_sheet_checkbox.grid(column=0, row=5, sticky=tk.W)
    tooltips.append(Tooltip(no_cut_lines_on_last_sheet_checkbox,
                 "Cut lines will not be drawn on the last sheet of the output PDF file. This is useful if the last sheet only has a few cards and you want to reuse the remaining paper space for another print."))

    skip_pdf_generation_checkbox = ttk.Checkbutton(
        pdf_generation_options_frame,
        text="Test Mode (Skip PDF Generation)",
        variable=skip_pdf_generation,
    )
    skip_pdf_generation_checkbox.grid(column=0, row=6, sticky=tk.W)
    tooltips.append(Tooltip(skip_pdf_generation_checkbox,
                 "The PDF generation process will be skipped. You can use this together with the 'Save Images to File' option to verify that the correct card images are being loaded. You can make adjustments by moving/deleting any of the images."))

    split_double_and_single_frame = ttk.LabelFrame(
        pdf_generation_options_frame,
        text="Split Double-Sided and Single-Sided Cards"
    )
    split_double_and_single_frame.grid(column=0, row=7, sticky=tk.W)

    split_double_and_single_checkbox = ttk.Checkbutton(
        split_double_and_single_frame,
        text="Enable",
        variable=split_double_and_single,
    )
    split_double_and_single_checkbox.grid(column=0, row=0, sticky=tk.W, padx=0)
    tooltips.append(Tooltip(split_double_and_single_checkbox,
                 "Two PDF files will be generated: one for double-sided cards and one for single-sided cards."))

    double_only_checkbox = ttk.Checkbutton(
        split_double_and_single_frame,
        text="Double-Sided Cards Only",
        variable=double_only,
    )
    double_only_checkbox.grid(column=0, row=1, sticky=tk.W, padx=20)
    tooltips.append(Tooltip(double_only_checkbox, "Generate only the PDF for the double-sided cards."))

    single_only_checkbox = ttk.Checkbutton(
        split_double_and_single_frame,
        text="Single-Sided Cards Only",
        variable=single_only,
    )
    single_only_checkbox.grid(column=0, row=2, sticky=tk.W, padx=20)
    tooltips.append(Tooltip(single_only_checkbox, "Generate only the PDF for the single-sided cards."))

    # Create a button to start the script
    def start_script_wrapper():
        """
        Wrapper function to pass all the variables to the start_script function.
        This function also checks if Tesseract is installed if the sharpen text option is selected.
        It creates a progress window to indicate that the script is running.
        """
        # Create a list to store error messages
        error_messages = []

        # Check if tesseract is installed and added to PATH only if the sharpen text option is selected
        if sharpen_text.get():
            try:
                pytesseract.get_tesseract_version()
            except pytesseract.TesseractNotFoundError:
                error_messages.append(
                    "- Tesseract is not installed or not added to PATH. Please install Tesseract from https://tesseract-ocr.github.io/tessdoc/Installation.html or disable the 'Sharpen Text' option."
                )

        # Check if the path of the TTS mod images cache folder is set
        if "cachepath" not in config:
            error_messages.append(
                "- Please select your TTS mod images cache folder from the Settings menu before proceeding. The application will remember this setting for future use."
            )

        # Check if a file or folder was selected
        if path.get() == "No file or folder selected":
            error_messages.append("- You have not selected a TTS object file or an images folder.")

        # If there are any error messages, show them in a single message box
        if error_messages:
            messagebox.showerror("Error", "\n\n".join(error_messages))
            return

        def top_level_window_wrapper():
            """
            Wrapper function to create a top-level window to indicate that the script is running.
            This function calls the start_script function with the necessary parameters.
            """
            try:
                start_script(
                    path.get(),
                    config["cachepath"],
                    preset_image_size.get(),
                    custom_card_length.get(),
                    sheet_size.get(),
                    custom_sheet_width.get(),
                    custom_sheet_length.get(),
                    gutter_margin_size.get(),
                    dpi.get(),
                    verbose.get(),
                    process_nested_containers.get(),
                    exclude_card_urls.get(),
                    exclude_card_backs.get(),
                    generate_bleed.get(),
                    sharpen_text.get(),
                    draw_cut_lines.get(),
                    split_double_and_single.get(),
                    double_only.get(),
                    single_only.get(),
                    save_images.get(),
                    skip_pdf_generation.get(),
                    cut_lines_on_margin_only.get(),
                    no_cut_lines_on_last_sheet.get(),
                    bleed_width=config["bleed_width"],
                    line_width=int(config["line_width"]),
                )
            except ImageFilesNotFoundError as e:
                messagebox.showerror("Error", str(e))
            except CardsNotFoundError as e:
                messagebox.showerror("Error", str(e))
            finally:
                progress_window.destroy()

        progress_window = tk.Toplevel(root)
        progress_window.title("Processing")
        progress_window.grab_set()
        progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
        progress_window.resizable(False, False)

        # Center the progress window on the monitor screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        progress_window_width = 300
        progress_window_height = 100
        progress_window_x = (screen_width - progress_window_width) // 2
        progress_window_y = (screen_height - progress_window_height) // 2
        progress_window.geometry(
            f"{progress_window_width}x{progress_window_height}+{progress_window_x}+{progress_window_y}"
        )

        progress_label = ttk.Label(progress_window, text="Working on it...", anchor="center")
        progress_label.pack(expand=True, fill="both", padx=10, pady=10)

        threading.Thread(target=top_level_window_wrapper).start()

    start_button = ttk.Button(
        main_frame, text="Generate PDF", command=start_script_wrapper
    )
    start_button.grid(column=0, row=7, sticky=tk.W)

    donation_button = ttk.Button(
        main_frame, text="Support the Developer", command=lambda: webbrowser.open("https://ko-fi.com/cyberviber")
    )
    donation_button.grid(column=1, row=7, sticky=tk.W)

    # Apply padding to all widgets
    for child in main_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    # Set the initial state of tooltips based on the `show_tooltips` setting
    if not show_tooltips.get():
        [tooltip.disable() for tooltip in tooltips]

    logger.info("GUI loaded")

    root.mainloop()


if __name__ == "__main__":
    main()
