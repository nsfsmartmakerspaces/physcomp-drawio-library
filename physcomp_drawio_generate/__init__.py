import asyncio
from glob import glob
from math import sqrt
from string import Template
import os
import pathlib
from shutil import rmtree
import sys

import yaml

from .const import *

# Requires >= Python 3.5
assert sys.version_info >= (3, 5)


def xmlEscape(in_str: str) -> str:
    return in_str.translate(str.maketrans({"\"":  "&quot;", "\\": r"\\"}))


# Quick schema-ish checker for yaml files
def check_drawing_yaml_file(name: str, src_data: dict, styles: dict) -> bool:
    res = True
    if DRAWING_YAML_SCHEMA_VERSION not in src_data or src_data[DRAWING_YAML_SCHEMA_VERSION] != "1.0.0":
        print(f"Wrong schema version in '{name}'")
        return False
    if DRAWING_YAML_DISABLE in src_data and type(src_data[DRAWING_YAML_DISABLE]) is not bool:
        res = False
        print(f"{DRAWING_YAML_DISABLE} must be bool in '{name}'")
    if DRAWING_YAML_DIP not in src_data or type(src_data[DRAWING_YAML_DIP]) is not bool:
        res = False
        print(f"Missing {DRAWING_YAML_DIP} or not bool in '{name}'")
    elif DRAWING_YAML_TOP in src_data and src_data[DRAWING_YAML_DIP]:
        res = False
        print(f"{DRAWING_YAML_DIP} cannot be used with {DRAWING_YAML_TOP} pins in '{name}'")
    if DRAWING_YAML_BLOCK not in src_data or type(src_data[DRAWING_YAML_BLOCK]) is not bool:
        res = False
        print(f"Missing {DRAWING_YAML_BLOCK} or not bool in '{name}'")
    elif (DRAWING_YAML_TOP in src_data or DRAWING_YAML_BOTTOM in src_data) and src_data[DRAWING_YAML_BLOCK]:
        res = False
        print(f"{DRAWING_YAML_BLOCK} cannot be used with {DRAWING_YAML_TOP} or {DRAWING_YAML_BOTTOM} pins in '{name}'")
    if DRAWING_YAML_STYLE not in src_data or type(src_data[DRAWING_YAML_STYLE]) is not str:
        res = False
        print(f"Missing {DRAWING_YAML_STYLE} or not str in '{name}'")
    elif (src_data[DRAWING_YAML_STYLE] not in styles):
        res = False
        print(f"{DRAWING_YAML_STYLE} '{src_data[DRAWING_YAML_STYLE]}' reference in '{name}' not loaded")

    if DRAWING_YAML_TITLE not in src_data:
        res = False
        print(f"Missing {DRAWING_YAML_TITLE} '{name}'")

    for key in [DRAWING_YAML_TITLE, DRAWING_YAML_TOP, DRAWING_YAML_BOTTOM, DRAWING_YAML_LEFT, DRAWING_YAML_RIGHT]:
        if key in src_data:
            if type(src_data[key]) is not list:
                res = False
                print(f"{key} is not list in '{name}'")
            else:
                for pin in src_data[key]:
                    if type(pin) is not str and type(pin) is not list:
                        res = False
                        print(f"An item in {key} is not str or list in '{name}'")
                    if (type(pin) is list and DRAWING_YAML_BLOCK in src_data and
                       src_data[DRAWING_YAML_BLOCK] and len(pin) > 2):
                        res = False
                        print(f"An item in {key} has more than two lines in block mode in '{name}'")
                    if type(pin) is list and len(pin) == 0:
                        res = False
                        print(f"An item in {key} has a multiline pin without any elements '{name}'")
                    elif type(pin) is list:
                        for line in pin:
                            if type(line) is not str:
                                res = False
                                print(f"An item in {key} has a multiline pin with a non-str element '{name}'")
    return res


def check_style_yaml_file(name: str, src_data: dict) -> bool:
    res = True
    if DRAWING_YAML_SCHEMA_VERSION not in src_data or src_data[DRAWING_YAML_SCHEMA_VERSION] != "1.0.0":
        print(f"Wrong schema version in '{name}'")
        return False
    if STYLE_YAML_BASE not in src_data or type(src_data[STYLE_YAML_BASE]) is not dict:
        res = False
        print(f"{STYLE_YAML_BASE} missing or is not dict in '{name}'")
    else:
        for attr in [STYLE_YAML_BASE_WIDTH, STYLE_YAML_BASE_HEIGHT]:
            if (attr not in src_data[STYLE_YAML_BASE] or
               (type(src_data[STYLE_YAML_BASE][attr]) is not int and
               type(src_data[STYLE_YAML_BASE][attr]) is not float)):
                res = False
                print(f"{attr} in {STYLE_YAML_BASE} is not int or float in '{name}'")
    if STYLE_YAML_TITLE_TEXT not in src_data or type(src_data[STYLE_YAML_TITLE_TEXT]) is not dict:
        res = False
        print(f"{STYLE_YAML_TITLE_TEXT} missing or is not dict in '{name}'")
    else:
        for attr in [STYLE_YAML_TITLE_TEXT_SIZE, STYLE_YAML_TITLE_TEXT_LINE_SPACING]:
            if (attr not in src_data[STYLE_YAML_TITLE_TEXT] or
               (type(src_data[STYLE_YAML_TITLE_TEXT][attr]) is not int and
               type(src_data[STYLE_YAML_TITLE_TEXT][attr]) is not float)):
                res = False
                print(f"{attr} in {STYLE_YAML_TITLE_TEXT} is not int or float in '{name}'")
    if STYLE_YAML_PIN_TEXT not in src_data or type(src_data[STYLE_YAML_PIN_TEXT]) is not dict:
        res = False
        print(f"{STYLE_YAML_PIN_TEXT} missing or is not dict in '{name}'")
    else:
        for attr in [STYLE_YAML_PIN_TEXT_VERT_WIDTH, STYLE_YAML_PIN_TEXT_HORIZ_HEIGHT,
                     STYLE_YAML_PIN_TEXT_SIZE, STYLE_YAML_PIN_TEXT_PAD,
                     STYLE_YAML_PIN_TEXT_LINE_SPACING]:
            if (attr not in src_data[STYLE_YAML_PIN_TEXT] or
               (type(src_data[STYLE_YAML_PIN_TEXT][attr]) is not int and
               type(src_data[STYLE_YAML_PIN_TEXT][attr]) is not float)):
                res = False
                print(f"{attr} in {STYLE_YAML_PIN_TEXT} is not int or float in '{name}'")
                print(f"{attr} in {STYLE_YAML_TITLE_TEXT} is not int or float in '{name}'")
    if STYLE_YAML_PINS not in src_data or type(src_data[STYLE_YAML_PINS]) is not dict:
        res = False
        print(f"{STYLE_YAML_PINS} missing or is not dict in '{name}'")
    else:
        for attr in [STYLE_YAML_PINS_LENGTH, STYLE_YAML_PINS_ARROW_SIZE,
                     STYLE_YAML_PINS_LEFT_ARROW_PAD]:
            if (attr not in src_data[STYLE_YAML_PINS] or
               (type(src_data[STYLE_YAML_PINS][attr]) is not int and
               type(src_data[STYLE_YAML_PINS][attr]) is not float)):
                res = False
                print(f"{attr} in {STYLE_YAML_PINS} is not int or float in '{name}'")
    return res


def read_yaml_file(src_file: str) -> dict:
    with open(src_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.DRAWING_YAMLError as exc:
            print(f"DRAWING_YAML error {src_file}: {exc}")
            return None


def save_file(file_path: str, data: str) -> None:
    pathlib.Path(os.path.split(file_path)[0]).mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(data)


async def generate(src_file: str, file_name: str, dest_file: str, templates: dict, styles: dict) -> None:
    # print(src_file, dest_file)
    src_data = read_yaml_file(src_file)

    if src_data is None:
        print(f"Skipping empty or invalid drawing {src_file}")
        return

    if DRAWING_YAML_DISABLE in src_data and src_data[DRAWING_YAML_DISABLE]:
        print(f"Skipping disabled drawing {src_file}")
        return

    check = check_drawing_yaml_file(src_file, src_data, styles)
    if not check:
        print(f"Skipping incorrect drawing file syntax {src_file}")
        return
    for key in [DRAWING_YAML_TOP, DRAWING_YAML_BOTTOM, DRAWING_YAML_LEFT, DRAWING_YAML_RIGHT]:
        if key not in src_data:
            src_data[key] = []
        for i, pin in enumerate(src_data[key]):
            if type(pin) is str:
                src_data[key][i] = [pin]

    style = styles[src_data[DRAWING_YAML_STYLE]]

    # Calculate total widths and heights
    template_opts = {}
    template_opts[DRAWING_TEMPLATE_NAME] = file_name
    template_opts[DRAWING_TEMPLATE_TITLE_TEXT_SIZE] = style["title_text"]["size"]
    template_opts[DRAWING_TEMPLATE_PIN_TEXT_SIZE] = style["pin_text"]["size"]
    template_opts[DRAWING_TEMPLATE_PIN_LENGTH] = style["pins"]["length"]
    template_opts[DRAWING_TEMPLATE_RECT_WIDTH] = style["base"]["width"] + (style["pin_text"]["vert_width"] * max(len(src_data[DRAWING_YAML_TOP]), len(src_data[DRAWING_YAML_BOTTOM])))
    template_opts[DRAWING_TEMPLATE_RECT_HEIGHT] = style["base"]["height"] + (style["pin_text"]["horiz_height"] * max(len(src_data[DRAWING_YAML_LEFT]), len(src_data[DRAWING_YAML_RIGHT])))
    template_opts[DRAWING_TEMPLATE_WIDTH] = template_opts[DRAWING_TEMPLATE_RECT_WIDTH]
    if len(src_data[DRAWING_YAML_LEFT]) > 0:
        template_opts[DRAWING_TEMPLATE_WIDTH] += style["pins"]["length"]
    if len(src_data[DRAWING_YAML_RIGHT]) > 0:
        template_opts[DRAWING_TEMPLATE_WIDTH] += style["pins"]["length"]
    template_opts[DRAWING_TEMPLATE_HEIGHT] = template_opts[DRAWING_TEMPLATE_RECT_HEIGHT]
    if len(src_data[DRAWING_YAML_TOP]) > 0:
        template_opts[DRAWING_TEMPLATE_HEIGHT] += style["pins"]["length"]
    if len(src_data[DRAWING_YAML_BOTTOM]) > 0:
        template_opts[DRAWING_TEMPLATE_HEIGHT] += style["pins"]["length"]
    template_opts[DRAWING_TEMPLATE_RECT_TOP] = 0
    template_opts[DRAWING_TEMPLATE_RECT_BOTTOM] = template_opts[DRAWING_TEMPLATE_RECT_HEIGHT]
    if len(src_data[DRAWING_YAML_TOP]) > 0:
        template_opts[DRAWING_TEMPLATE_RECT_TOP] += style["pins"]["length"]
        template_opts[DRAWING_TEMPLATE_RECT_BOTTOM] += style["pins"]["length"]
    template_opts[DRAWING_TEMPLATE_RECT_LEFT] = 0
    template_opts[DRAWING_TEMPLATE_RECT_RIGHT] = template_opts[DRAWING_TEMPLATE_RECT_WIDTH]
    if len(src_data[DRAWING_YAML_LEFT]) > 0:
        template_opts[DRAWING_TEMPLATE_RECT_LEFT] += style["pins"]["length"]
        template_opts[DRAWING_TEMPLATE_RECT_RIGHT] += style["pins"]["length"]
    template_opts[DRAWING_TEMPLATE_RECT_DIP_START] = template_opts[DRAWING_TEMPLATE_RECT_RIGHT] - (template_opts[DRAWING_TEMPLATE_RECT_WIDTH] / 3)
    # template_opts[DRAWING_TEMPLATE_TITLE_X] = template_opts[DRAWING_TEMPLATE_WIDTH] / 2
    # template_opts[DRAWING_TEMPLATE_TITLE_Y] = template_opts[DRAWING_TEMPLATE_HEIGHT] / 2

    dip_opts = {}
    dip_opts[DIP_TEMPLATE_END_X] = template_opts[DRAWING_TEMPLATE_RECT_RIGHT] - (2 * (template_opts[DRAWING_TEMPLATE_RECT_WIDTH] / 3))
    dip_opts[DIP_TEMPLATE_END_Y] = template_opts[DRAWING_TEMPLATE_RECT_TOP]
    dip_opts[DIP_TEMPLATE_RADIUS] = (template_opts[DRAWING_TEMPLATE_RECT_RIGHT] - dip_opts[DIP_TEMPLATE_END_X]) / 4

    if (src_data[DRAWING_YAML_DIP]):
        template_opts[DRAWING_TEMPLATE_RECT_DIP_INSERT] = Template(templates["dip"]).substitute(dip_opts)
    else:
        template_opts[DRAWING_TEMPLATE_RECT_DIP_INSERT] = Template(templates["no_dip"]).substitute(dip_opts)

    titles = ""
    title_lines = len(src_data[DRAWING_YAML_TITLE])
    title_height = (style["title_text"]["size"] * title_lines) + ((title_lines - 1) * style["title_text"]["line_spacing"])
    title_start = (template_opts[DRAWING_TEMPLATE_RECT_HEIGHT] / 2) - (title_height / 2)
    if len(src_data[DRAWING_YAML_TOP]) > 0:
        title_start += style["pins"]["length"]
    title_x = template_opts[DRAWING_TEMPLATE_RECT_WIDTH] / 2
    if len(src_data[DRAWING_YAML_LEFT]) > 0:
        title_x += style["pins"]["length"]
    for i, line in enumerate(src_data[DRAWING_YAML_TITLE]):
        title_opts = {}
        title_opts[TITLE_TEMPLATE_TITLE] = xmlEscape(line)
        title_opts[TITLE_TEMPLATE_X] = title_x
        title_opts[TITLE_TEMPLATE_Y] = title_start + (style["title_text"]["size"] * i) + (style["title_text"]["size"] / 2) + (style["title_text"]["line_spacing"] * i)
        titles += Template(templates["title"]).substitute(title_opts)
    template_opts[DRAWING_TEMPLATE_RECT_TITLE_INSERT] = titles

    connections = ""
    pins = ""
    for key in [DRAWING_YAML_TOP, DRAWING_YAML_BOTTOM, DRAWING_YAML_LEFT, DRAWING_YAML_RIGHT]:
        for i, pin in enumerate(src_data[key]):
            # skip blank lines
            if pin[0] == "":
                continue

            x = 0
            if len(src_data[DRAWING_YAML_LEFT]) > 0:
                x += style["pins"]["length"]
            if key == DRAWING_YAML_TOP or key == DRAWING_YAML_BOTTOM:
                x += (style["base"]["width"] / 2) + (style["pin_text"]["vert_width"] * i) + (style["pin_text"]["vert_width"] / 2)
            elif key == DRAWING_YAML_RIGHT:
                x += template_opts[DRAWING_TEMPLATE_RECT_WIDTH]
            y = 0
            if len(src_data[DRAWING_YAML_TOP]) > 0:
                y += style["pins"]["length"]
            if key == DRAWING_YAML_LEFT or key == DRAWING_YAML_RIGHT:
                y += (style["base"]["height"] / 2) + (style["pin_text"]["horiz_height"] * i) + (style["pin_text"]["horiz_height"] / 2)
            elif key == DRAWING_YAML_BOTTOM:
                y += template_opts[DRAWING_TEMPLATE_RECT_HEIGHT]

            conn_x = 0
            if key == DRAWING_YAML_TOP or key == DRAWING_YAML_BOTTOM:
                conn_x = x
            elif key == DRAWING_YAML_RIGHT:
                conn_x = template_opts[DRAWING_TEMPLATE_WIDTH]
            conn_y = 0
            if key == DRAWING_YAML_LEFT or key == DRAWING_YAML_RIGHT:
                conn_y = y
            elif key == DRAWING_YAML_BOTTOM:
                conn_y = template_opts[DRAWING_TEMPLATE_HEIGHT]

            lead_opts = {}
            lead_opts[LEAD_TEMPLATE_X_START] = conn_x
            lead_opts[LEAD_TEMPLATE_Y_START] = conn_y
            lead_opts[LEAD_TEMPLATE_X_END] = x
            lead_opts[LEAD_TEMPLATE_Y_END] = y
            pins += Template(templates["lead"]).substitute(lead_opts)

            pin_x = x
            if not src_data[DRAWING_YAML_BLOCK]:
                pin_align = TEXT_ALIGN_LEFT
                if key == DRAWING_YAML_LEFT:
                    pin_x += style["pin_text"]["pad"]
                elif key == DRAWING_YAML_RIGHT:
                    pin_align = TEXT_ALIGN_RIGHT
                    pin_x -= style["pin_text"]["pad"]
                else:
                    pin_align = TEXT_ALIGN_CENTER

                pin_start = y
                pin_lines = len(pin)
                pin_height = (style["pin_text"]["size"] * pin_lines) + ((pin_lines - 1) * style["pin_text"]["line_spacing"])
                pin_valign = TEXT_VALIGN_TOP
                if key == DRAWING_YAML_TOP:
                    # pin_start += style["pin_text"]["pad"] / 2
                    pass
                elif key == DRAWING_YAML_BOTTOM:
                    pin_valign = TEXT_VALIGN_BOTTOM
                    pin_start -= style["pin_text"]["pad"]
                else:
                    pin_valign = TEXT_VALIGN_MIDDLE
                    pin_start -= pin_height / 2

                for i, line in enumerate(pin):
                    pin_opts = {}
                    pin_opts[PIN_TEMPLATE_NAME] = xmlEscape(line)
                    pin_opts[PIN_TEMPLATE_TEXT_ALIGN] = pin_align
                    pin_opts[PIN_TEMPLATE_TEXT_VALIGN] = pin_valign
                    pin_opts[PIN_TEMPLATE_X] = pin_x
                    pin_opts[PIN_TEMPLATE_Y] = pin_start + (style["pin_text"]["size"] * i) + (style["pin_text"]["size"] / 2) + (style["pin_text"]["line_spacing"] * i)
                    if key == DRAWING_YAML_BOTTOM:
                        # pin_opts[PIN_TEMPLATE_Y] -= ((len(pin) - 1) - i) * (style["pin_text"]["line_spacing"] + style["pin_text"]["size"])
                        pin_opts[PIN_TEMPLATE_Y] -= (len(pin) - 1) * (style["pin_text"]["size"] + style["pin_text"]["line_spacing"])
                    pins += Template(templates["pin_horiz"]).substitute(pin_opts)
            else:
                pin_opts = {}
                pin_opts[PIN_TEMPLATE_NAME] = xmlEscape(pin[0])
                arrow_point_dist = sqrt((style["pins"]["arrow_size"]) ** 2 - ((style["pins"]["arrow_size"]) / 2) ** 2)
                pin_opts[PIN_TEMPLATE_TEXT_ALIGN] = TEXT_ALIGN_CENTER
                pin_opts[PIN_TEMPLATE_TEXT_VALIGN] = TEXT_VALIGN_BOTTOM
                pin_opts[PIN_TEMPLATE_Y] = y
                pin_opts[PIN_TEMPLATE_Y] += style["pin_text"]["size"] / 2
                pin_opts[PIN_TEMPLATE_Y] -= style["pin_text"]["pad"]
                if key == DRAWING_YAML_LEFT:
                    pin_x -= style["pins"]["length"] / 2
                    pin_x -= (arrow_point_dist + style["pins"]["left_arrow_pad"]) / 2
                else:
                    pin_x += style["pins"]["length"] / 2
                    pin_x -= arrow_point_dist / 2
                pin_opts[PIN_TEMPLATE_X] = pin_x

                arrow_opts = {}
                arrow_opts[ARROW_TEMPLATE_TOP] = y - (style["pins"]["arrow_size"] / 2)
                arrow_opts[ARROW_TEMPLATE_BOTTOM] = y + (style["pins"]["arrow_size"] / 2)
                arrow_opts[ARROW_TEMPLATE_MIDDLE] = y

                if key == DRAWING_YAML_LEFT:
                    arrow_opts[ARROW_TEMPLATE_X_POINT] = x - style["pins"]["left_arrow_pad"]
                    arrow_opts[ARROW_TEMPLATE_X_FLAT] = x - (arrow_point_dist + style["pins"]["left_arrow_pad"])
                else:
                    arrow_opts[ARROW_TEMPLATE_X_POINT] = conn_x
                    arrow_opts[ARROW_TEMPLATE_X_FLAT] = conn_x - arrow_point_dist
                pins += Template(templates["arrow"]).substitute(arrow_opts)
                pins += Template(templates["pin_horiz"]).substitute(pin_opts)

                if len(pin) == 2:
                    pin_opts[PIN_TEMPLATE_NAME] = xmlEscape(pin[1])
                    pin_opts[PIN_TEMPLATE_TEXT_VALIGN] = TEXT_VALIGN_TOP
                    pin_opts[PIN_TEMPLATE_Y] = y
                    # pin_opts[PIN_TEMPLATE_Y] += style["pin_text"]["size"] / 2
                    pin_opts[PIN_TEMPLATE_Y] += style["pin_text"]["pad"]
                    pins += Template(templates["pin_horiz"]).substitute(pin_opts)

            connection_opts = {}
            connection_opts[CONNECTION_TEMPLATE_NAME] = xmlEscape(" ".join(pin))
            connection_opts[CONNECTION_TEMPLATE_X] = conn_x / template_opts[DRAWING_TEMPLATE_WIDTH]
            connection_opts[CONNECTION_TEMPLATE_Y] = conn_y / template_opts[DRAWING_TEMPLATE_HEIGHT]
            connections += Template(templates["connection"]).substitute(connection_opts)

    template_opts[DRAWING_TEMPLATE_CONNECTION_INSERT] = connections
    template_opts[DRAWING_TEMPLATE_PINS_INSERT] = pins

    out = Template(templates["main"]).substitute(template_opts)
    save_file(dest_file, out)


async def load_style(styles: dict, name: str, path: str):
    src_data = read_yaml_file(path)

    if src_data is None:
        print(f"Skipping empty or invalid style {path}")
        return

    check = check_style_yaml_file(path, src_data)
    if not check:
        print(f"Skipping incorrect style file syntax {path}")
        return

    styles[name] = {
        "base": {
            "width": src_data[STYLE_YAML_BASE][STYLE_YAML_BASE_WIDTH],
            "height": src_data[STYLE_YAML_BASE][STYLE_YAML_BASE_HEIGHT]
        },
        "title_text": {
            "size": src_data[STYLE_YAML_TITLE_TEXT][STYLE_YAML_TITLE_TEXT_SIZE],
            "line_spacing": src_data[STYLE_YAML_TITLE_TEXT][STYLE_YAML_TITLE_TEXT_LINE_SPACING]
        },
        "pin_text": {
            "vert_width": src_data[STYLE_YAML_PIN_TEXT][STYLE_YAML_PIN_TEXT_VERT_WIDTH],
            "horiz_height": src_data[STYLE_YAML_PIN_TEXT][STYLE_YAML_PIN_TEXT_HORIZ_HEIGHT],
            "size": src_data[STYLE_YAML_PIN_TEXT][STYLE_YAML_PIN_TEXT_SIZE],
            "line_spacing": src_data[STYLE_YAML_PIN_TEXT][STYLE_YAML_PIN_TEXT_LINE_SPACING],
            "pad": src_data[STYLE_YAML_PIN_TEXT][STYLE_YAML_PIN_TEXT_PAD]
        },
        "pins": {
            "length": src_data[STYLE_YAML_PINS][STYLE_YAML_PINS_LENGTH],
            "arrow_size": src_data[STYLE_YAML_PINS][STYLE_YAML_PINS_ARROW_SIZE],
            "left_arrow_pad": src_data[STYLE_YAML_PINS][STYLE_YAML_PINS_LEFT_ARROW_PAD],
        }
    }


async def main() -> None:
    templates = {}
    with open(TEMPLATE_MAIN, 'r') as stream:
        templates["main"] = stream.read()
    with open(TEMPLATE_TITLE, 'r') as stream:
        templates["title"] = stream.read()
    with open(TEMPLATE_LEAD, 'r') as stream:
        templates["lead"] = stream.read()
    with open(TEMPLATE_PIN_HORIZ, 'r') as stream:
        templates["pin_horiz"] = stream.read()
    # with open(TEMPLATE_PIN_VERT, 'r') as stream:
    #     templates["pin_vert"] = stream.read()
    with open(TEMPLATE_CONNECTION, 'r') as stream:
        templates["connection"] = stream.read()
    with open(TEMPLATE_DIP, 'r') as stream:
        templates["dip"] = stream.read()
    with open(TEMPLATE_NO_DIP, 'r') as stream:
        templates["no_dip"] = stream.read()
    with open(TEMPLATE_ARROW, 'r') as stream:
        templates["arrow"] = stream.read()

    style_names = []
    styles = {}
    tasks = []
    style_paths = glob(f"./{YAML_STYLE_DIR}/*.yaml")
    style_paths.extend(glob(f"./{YAML_STYLE_DIR}/*.yml"))
    if len(style_paths) == 0:
        print("No styles defined, stopping")
        return
    for style_path in style_paths:
        base_name = os.path.basename(style_path)
        style_name = os.path.splitext(base_name)[0]
        file_path = os.path.splitext(style_path)[0]
        if (style_name in style_names):
            print(f"Duplicate style base name {style_name}")
            exit(1)
        style_names.append(style_name)
        tasks.append(load_style(styles, style_name, style_path))
    await asyncio.wait(tasks)

    file_names = []
    tasks = []
    src_files = glob(f"./{YAML_SRC_DIR}/*/*.yaml")
    src_files.extend(glob(f"./{YAML_SRC_DIR}/*/*.yml"))
    for src_file in src_files:
        base_name = os.path.basename(src_file)
        file_name = os.path.splitext(base_name)[0]
        file_path = os.path.splitext(src_file)[0]
        if (file_name in file_names):
            print(f"Duplicate drawing base name {file_name}")
            exit(1)
        file_names.append(file_name)
        dest_file = file_path.replace(YAML_SRC_DIR, YAML_DIST_DIR, 1)
        dest_file = f"{dest_file}.xml"
        if os.path.isdir(f"./{YAML_DIST_DIR}"):
            rmtree(f"./{YAML_DIST_DIR}")
        tasks.append(generate(src_file, file_name, dest_file, templates, styles))
    if len(tasks) > 0:
        await asyncio.wait(tasks)
    else:
        print("No drawings to process, stopping")
