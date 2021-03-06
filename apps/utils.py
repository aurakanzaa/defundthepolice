import glob
import json
import logging
import pandas as pd
import streamlit as st

from PIL import Image, ImageDraw, ImageFont

from apps.configs import STATES_FOLDER


def fonts():
    return ["fonts/Chunk_Five_Print.otf"] + glob.glob("fonts/*")


def draw_image(text, bg_color, text_color, font):
    # TODO make advanced pannel for deep customizations
    image_width = 600
    image_height = 335
    img = Image.new("RGB", (image_width, image_height), color=bg_color)
    canvas = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, size=24)
    pad = -25
    # print(text)
    for line in text:
        # print(line)

        # canvas.textsize(text, font=font)
        # canvas.text((10,10), text, fill=(255, 255, 0))
        text_width, text_height = canvas.textsize(line, font=font)

        x_pos = int((image_width - text_width) / 2)
        y_pos = int((image_height - text_height) / 2) + pad
        canvas.text((x_pos, y_pos), line, font=font, fill=text_color)
        pad += text_height + 5

    return img


def calc_percent(row, total_budget):
    return round((float(row["budget"] / float(total_budget)) * 100), 2)


def select_police_row(budget_df):
    try:
        police_df = budget_df.loc[budget_df["item"].str.contains("Police")]
        police_json = police_df.reset_index().to_json(orient="records")
        police_data = json.loads(police_json)[0]
    except Exception as no_police_row:
        logging.error(no_police_row)
        try:
            police_df = budget_df.loc[budget_df["item"].str.contains("Safety")]
            police_json = police_df.reset_index().to_json(orient="records")
            police_data = json.loads(police_json)[0]
        except Exception as no_safety_row:
            logging.error(no_safety_row)
            st.warning("No column named police, manually select")
            police_col = st.selectbox("Select Police budget", list(budget_df["item"]))
            police_df = budget_df.loc[budget_df["item"].str.contains(police_col)]
            police_json = police_df.reset_index().to_json(orient="records")
            police_data = json.loads(police_json)[0]

    return police_data


def create_budget_json(state, county):
    # read budget.csv
    budget_csv_path = STATES_FOLDER + state + "/" + county + "/budget.csv"
    budget_df = pd.read_csv(budget_csv_path, index_col=False)
    # st.write(budget_df)

    # add percentages to budget_df
    total_budget = budget_df["budget"].sum()
    budget_df["percent"] = budget_df.apply(
        lambda row: calc_percent(row, total_budget), axis=1
    )

    police_data = select_police_row(budget_df)
    return police_data, budget_df
