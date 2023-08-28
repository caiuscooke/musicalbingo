from django.http.response import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from random import randint
from io import BytesIO


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
    for i in range(1, 7):
        xpos.append(column_width * i)

    # calculate each row's (horizontal line) start point on the y axis
    ypos = []
    row_height = working_height / 6
    for i in range(1, 7):
        ypos.append(row_height * i)

    # get the middle of the first row and first column
    row_middle = row_height / 2
    column_midde = column_width / 2

    # get the center of each box by adding the middle of the column/row to the starting value of each column/row
    # Excludes the last x and y because it takes 6 lines to create 5 boxes (including the last would add a center point to the right of each box's end)
    centers_x = [center_x + column_midde for center_x in xpos[:-1]]
    centers_y = [center_y + row_middle for center_y in ypos[:-1]]

    # used in generating the random number
    track_names_last_index = len(track_names) - 1

    # loops based on how many unique bingo cards the user wants
    for pages in range(unique_pages):

        # creates a grid based on the previous calculations
        c.grid(xpos, ypos)

        for y in centers_y:
            for x in centers_x:
                random_index = randint(0, track_names_last_index)

                # Get the track name
                track_name = track_names[random_index]

                # Calculate the available width within the box and initialize font size
                available_width = column_width - 10
                font_size = 12

                # Split track_name into seperate string based on available width
                words = track_name.split()
                lines = []
                line = words[0]

                for word in words[1:]:
                    if c.stringWidth(line + " " + word, 'Helvetica', font_size) <= available_width:
                        line = line + " " + word
                    elif c.stringWidth(line, 'Helvetica', font_size) > available_width:
                        line_len = len(line) - 1
                        line_middle = line_len // 2

                        lines.append(line[:line_middle])
                        lines.append(line[line_middle:])

                        line = word
                    else:
                        lines.append(line)
                        line = word

                if c.stringWidth(line, 'Helvetica', font_size) > available_width:
                    line_len = len(line) - 1
                    line_middle = line_len // 2

                    lines.append(line[:line_middle])
                    lines.append(line[line_middle:])
                else:
                    lines.append(line)

                # if c.stringWidth(line, 'Helvetica', font_size) > available_width:
                #     line_len = len(line) - 1
                #     line_middle = line_len // 2
                #     lines.append(line[:line_middle])
                #     lines.append(line[line_middle:])

                adjusted_y = y + (len(lines) // 2) * font_size
                for line in lines:
                    text_width = c.stringWidth(
                        line, 'Helvetica', font_size)
                    adjusted_x = x - text_width / 2
                    c.drawString(adjusted_x, adjusted_y, text=line)
                    adjusted_y -= font_size

        c.showPage()

    c.save()

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'filename="example.pdf"'
    return response
