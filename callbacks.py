def start_script(
    verbose: bool,
    include_card_backs: bool,
    exclude_card_urls: bool,
    sharpen_text: bool,
    draw_cut_lines: bool,
    save_images: bool,
    load_images_from_directory: bool,
    arrange_into_pdf: bool,
    image_size: tuple,
    sheet_size: tuple,
    outer_margin_size: float,
    inner_margin_size: float,
    dpi: int,
) -> None:
    print(
        verbose,
        include_card_backs,
        exclude_card_urls,
        sharpen_text,
        draw_cut_lines,
        save_images,
        load_images_from_directory,
        arrange_into_pdf,
        image_size,
        sheet_size,
        outer_margin_size,
        inner_margin_size,
        dpi,
    )
