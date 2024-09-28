from collections import namedtuple
import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog

from callbacks import start_script


# Define preset page and card sizes in pixels at 300dpi
SHEET_SIZES = {
    "A4": (2480, 3508),
    "Letter": (2550, 3300),
    "Legal": (2550, 4200),
}
CARD_SIZES = {"standard": (734, 1045), "mini": (500, 734)}


def main():
    logging.info("Loading GUI...")

    # Create a root window
    root = tk.Tk()
    root.title("TTS Object to PDF")
    style = ttk.Style()
    style.theme_use("alt")

    # Create a main frame that uses a grid layout
    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.grid(column=0, row=0, sticky=("n", "w", "e", "s"))
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # Create a button for selecting the file
    def select_file():
        filepath.set(
            filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
        )

    filepath = tk.StringVar(value="No file selected")
    select_file_button = ttk.Button(
        main_frame, text="Select TTS Object file", command=select_file
    )
    select_file_button.grid(column=0, row=0, sticky=tk.W)

    # Display the selected file path inside a white frame
    filepath_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
    filepath_frame.grid(column=0, row=1, sticky=tk.W)
    filepath_label = ttk.Label(filepath_frame, textvariable=filepath, wraplength=400)
    filepath_label.grid(column=0, row=0, sticky=tk.W)

    # Create a button for selecting the cache folder
    cachepath = tk.StringVar()
    if os.path.exists("cachepath.txt"):
        with open("cachepath.txt", "r") as f:
            cachepath.set(f.read().strip())

    def select_cache_folder():
        cachepath.set(filedialog.askdirectory())
        with open("cachepath.txt", "w") as f:
            f.write(cachepath.get())

    select_cache_folder_button = ttk.Button(
        main_frame,
        text="Select TTS mod images cache folder",
        command=select_cache_folder,
    )
    select_cache_folder_button.grid(column=0, row=2, sticky=tk.W)

    # Display the selected cache folder path inside a white frame
    cachepath_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
    cachepath_frame.grid(column=0, row=3, sticky=tk.W)
    cachepath_label = ttk.Label(cachepath_frame, textvariable=cachepath, wraplength=400)
    cachepath_label.grid(column=0, row=0, sticky=tk.W)

    # Create radio buttons for the preset image size
    preset_image_size = tk.StringVar(value="standard")
    image_size_frame = ttk.LabelFrame(main_frame, text="Preset Image Size")
    image_size_frame.grid(column=0, row=5, sticky=tk.W)

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

    # Create entry fields for the custom image size
    CustomImageSize = namedtuple("CustomImageSize", ["width", "length"])
    custom_image_size = CustomImageSize(tk.IntVar(), tk.IntVar())
    custom_image_size_frame = ttk.LabelFrame(main_frame, text="Custom Image Size")
    custom_image_size_frame.grid(column=0, row=6, sticky=tk.W)

    custom_size_width_label = ttk.Label(custom_image_size_frame, text="Width:")
    custom_size_width_label.grid(column=0, row=0, sticky=tk.W)
    custom_size_width_entry = ttk.Entry(
        custom_image_size_frame, textvariable=custom_image_size[0]
    )
    custom_size_width_entry.grid(column=1, row=0, sticky=tk.W)

    custom_size_length_label = ttk.Label(custom_image_size_frame, text="Length:")
    custom_size_length_label.grid(column=0, row=1, sticky=tk.W)
    custom_size_length_entry = ttk.Entry(
        custom_image_size_frame, textvariable=custom_image_size[1]
    )
    custom_size_length_entry.grid(column=1, row=1, sticky=tk.W)

    # Create radio buttons for the sheet size
    sheet_size = tk.StringVar(value="Letter")
    sheet_size_frame = ttk.LabelFrame(main_frame, text="Sheet Size")
    sheet_size_frame.grid(column=0, row=7, sticky=tk.W)

    a4_radio = ttk.Radiobutton(
        sheet_size_frame, text="A4", variable=sheet_size, value="A4"
    )
    a4_radio.grid(column=0, row=0, sticky=tk.W)
    letter_radio = ttk.Radiobutton(
        sheet_size_frame, text="Letter", variable=sheet_size, value="Letter"
    )
    letter_radio.grid(column=0, row=1, sticky=tk.W)
    legal_radio = ttk.Radiobutton(
        sheet_size_frame, text="Legal", variable=sheet_size, value="Legal"
    )
    legal_radio.grid(column=0, row=2, sticky=tk.W)

    # Create entry fields for the margin size and dpi
    outer_margin_size = tk.IntVar(value=36)
    inner_margin_size = tk.IntVar()
    dpi = tk.IntVar(value=360)
    margin_dpi_frame = ttk.LabelFrame(main_frame, text="Margin and DPI")
    margin_dpi_frame.grid(column=0, row=8, sticky=tk.W)

    outer_margin_size_label = ttk.Label(margin_dpi_frame, text="Outer Margin:")
    outer_margin_size_label.grid(column=0, row=0, sticky=tk.W)
    outer_margin_size_entry = ttk.Entry(
        margin_dpi_frame, textvariable=outer_margin_size
    )
    outer_margin_size_entry.grid(column=1, row=0, sticky=tk.W)

    inner_margin_size_label = ttk.Label(margin_dpi_frame, text="Inner Margin:")
    inner_margin_size_label.grid(column=0, row=1, sticky=tk.W)
    inner_margin_size_entry = ttk.Entry(
        margin_dpi_frame, textvariable=inner_margin_size
    )
    inner_margin_size_entry.grid(column=1, row=1, sticky=tk.W)

    dpi_label = ttk.Label(margin_dpi_frame, text="DPI:")
    dpi_label.grid(column=0, row=2, sticky=tk.W)
    dpi_entry = ttk.Entry(margin_dpi_frame, textvariable=dpi)
    dpi_entry.grid(column=1, row=2, sticky=tk.W)

    # Create checkboxes for the boolean options
    verbose = tk.BooleanVar(value=True)
    include_card_backs = tk.BooleanVar()
    exclude_card_urls = tk.BooleanVar()
    generate_bleed = tk.BooleanVar()
    sharpen_text = tk.BooleanVar()
    draw_cut_lines = tk.BooleanVar()
    save_images = tk.BooleanVar()
    load_images_from_directory = tk.BooleanVar()
    arrange_into_pdf = tk.BooleanVar()

    boolean_options_frame = ttk.LabelFrame(main_frame, text="Additional Options")
    boolean_options_frame.grid(column=0, row=9, rowspan=9, sticky=tk.W)

    verbose_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Verbose Console Output", variable=verbose
    )
    verbose_checkbox.grid(column=0, row=0, sticky=tk.W)

    back_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Include Card Backs", variable=include_card_backs
    )
    back_checkbox.grid(column=0, row=1, sticky=tk.W)

    exclude_card_urls_checkbox = ttk.Checkbutton(
        boolean_options_frame,
        text="Exclude specific card image URLs",
        variable=exclude_card_urls,
    )
    exclude_card_urls_checkbox.grid(column=0, row=2, sticky=tk.W)

    generate_bleed_checkbox = ttk.Checkbutton(
        boolean_options_frame,
        text="Generate Bleed",
        variable=generate_bleed,
    )
    generate_bleed_checkbox.grid(column=0, row=3, sticky=tk.W)

    sharpen_text_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Sharpen Text (Experimental)", variable=sharpen_text
    )
    sharpen_text_checkbox.grid(column=0, row=4, sticky=tk.W)

    draw_cut_lines_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Draw Cut Lines", variable=draw_cut_lines
    )
    draw_cut_lines_checkbox.grid(column=0, row=5, sticky=tk.W)

    save_images_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Save Images to File", variable=save_images
    )
    save_images_checkbox.grid(column=0, row=6, sticky=tk.W)

    load_images_from_directory_checkbox = ttk.Checkbutton(
        boolean_options_frame,
        text="Load Images from Directory",
        variable=load_images_from_directory,
    )
    load_images_from_directory_checkbox.grid(column=0, row=7, sticky=tk.W)

    arrange_into_pdf_checkbox = ttk.Checkbutton(
        boolean_options_frame, text="Arrange Images into PDF", variable=arrange_into_pdf
    )
    arrange_into_pdf_checkbox.grid(column=0, row=8, sticky=tk.W)

    # Create a button to start the script
    def start_script_wrapper():
        """Wrapper function to pass all the variables to the start_script function."""
        start_script(
            filepath.get(),
            cachepath.get(),
            preset_image_size.get(),
            custom_image_size.width.get(),
            custom_image_size.length.get(),
            sheet_size.get(),
            outer_margin_size.get(),
            inner_margin_size.get(),
            dpi.get(),
            verbose.get(),
            include_card_backs.get(),
            exclude_card_urls.get(),
            generate_bleed.get(),
            sharpen_text.get(),
            draw_cut_lines.get(),
            save_images.get(),
            load_images_from_directory.get(),
            arrange_into_pdf.get(),
        )

    start_button = ttk.Button(
        main_frame, text="Start script", command=start_script_wrapper
    )
    start_button.grid(column=0, row=18, sticky=tk.W)

    # Apply padding to all widgets
    for child in main_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    logging.info("GUI loaded")

    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
