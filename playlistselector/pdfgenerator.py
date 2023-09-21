from django.http.response import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from random import randint
from io import BytesIO


def fill_coords_list(coord_list: list, distance: int):
    for i in range(1, 7):
        coord_list.append(distance * i)


def split_word_in_half(word: str) -> tuple[str, str]:
    line_len = len(word)
    line_middle = line_len // 2

    first_half = word[:line_middle]
    second_half = word[line_middle:]
    return first_half, second_half


def make_bingo_card(track_names: list, unique_pages=1):
    # get the width and height based on the standard 'letter' dimensions
    width, height = letter
    # create a pdf Canvas object with the file name and page size
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, letter)

    # subtract an inch from the height and width to get the top and right margin
    # left and bottom margin are simply an inch, no need for calculation
    working_width = width - inch
    working_height = height - inch

    # calculate each column's (vertical line) start point on the x axis
    xpos = []
    column_width = working_width / 6
    fill_coords_list(xpos, column_width)

    # calculate each row's (horizontal line) start point on the y axis
    ypos = []
    row_height = working_height / 6
    fill_coords_list(ypos, row_height)

    # get the middle of the first row and first column
    row_middle = row_height / 2
    column_midde = column_width / 2

    # get the center of each box by adding the middle of the column/row to the starting value of each column/row
    # Excludes the last x and y because it takes 6 lines to create 5 boxes (including the last would add a center point to the right of each box's end)
    centers_x = [center_x + column_midde for center_x in xpos[:-1]]
    centers_y = [center_y + row_middle for center_y in ypos[:-1]]

    # used in generating the random number
    track_names_len = len(track_names)
    track_names_last_index = track_names_len - 1

    # Calculate the available width within the box and initialize font size
    inner_box_margin = 5
    available_width = column_width - inner_box_margin
    font_size = 12
    font = 'Helvetica'

    # loops based on how many unique bingo cards the user wants
    for pages in range(unique_pages):

        # create a list of numbers associated with the number of tracks so that a page doesn't have repeat entries
        chosen_tracks_indexes = []

        # creates a grid based on the previous calculations
        c.grid(xpos, ypos)

        loops = 0
        center_loop = 13
        for y in centers_y:
            for x in centers_x:
                loops += 1
                random_index = randint(0, track_names_last_index)
                while random_index in chosen_tracks_indexes:
                    random_index = randint(0, track_names_last_index)
                chosen_tracks_indexes.append(random_index)

                # Get the track name
                track_name = track_names[random_index]

                # Manually change track name to "Free" if the loop
                # is at the centermost box in the grid
                if loops == center_loop:
                    track_name = "Free"

                # Split track_name into seperate string based on available width
                words = track_name.split()

                lines = []
                line = words[0]

                # start the loop after the first item in words
                for word in words[1:]:

                    # get the width of the line after adding the next word in the sequence
                    new_line = line + " " + word
                    new_line_width = c.stringWidth(
                        new_line, font, font_size)

                    # get the width of the line without adding the next word
                    current_line_width = c.stringWidth(
                        line, font, font_size)

                    # if that fits in the box, add the word to the current line
                    if new_line_width <= available_width:
                        line += (" " + word)
                    # but if the current line is more than the available width,
                    # split the word into two parts
                    elif current_line_width > available_width:
                        first_half, second_half = split_word_in_half(line)
                        lines.extend([first_half, second_half])
                        line = word
                    else:
                        lines.append(line)
                        line = word

                # check if the line is too long
                line_too_long = c.stringWidth(
                    line, font, font_size) > available_width

                if line_too_long:
                    first_half, second_half = split_word_in_half(line)
                    lines.append(first_half)
                    lines.append(second_half)
                else:
                    lines.append(line)

                # change the starting point of the draw string by
                # calculating how many lines there are currently and divided
                # by two. Multiply that by the font size to get the number
                # of pixels to go up by, then add the current y value to
                # get the starting point of the first line
                adjusted_y = y + (len(lines) // 2) * font_size

                for line in lines:
                    text_width = c.stringWidth(
                        line, font, font_size)

                    # change the starting point of the draw string by
                    # similarly applying the same logic as before, but on
                    # the horizontal axis to move the cursor to the left
                    # as needed
                    adjusted_x = x - text_width / 2

                    c.drawString(adjusted_x, adjusted_y, text=line)

                    # moves the cursor down each loop to add a line break
                    adjusted_y -= font_size

        # shows the page on the pdf based on the information stored in the c object
        c.showPage()

    c.save()

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'filename="example.pdf"'
    return response
