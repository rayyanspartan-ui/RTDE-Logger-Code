from datetime import datetime

from openpyxl import Workbook, load_workbook

import config
from M2 import calculate_utilization, read_samples

path = config.EXCEL_PATH  # Use the EXCEL_PATH from config.py


sample = read_samples(config.CSV_PATH)  # Read samples from the CSV file

utilization_data = calculate_utilization(sample, config.ROBOTMODE_THRESHOLD)  # Calculate utilization data

date = month_label = datetime.now().strftime("%B %Y")   # "May 2026" in local time  # noqa: DTZ005

def write_to_excel(utilization_data, path, date):

    if path.exists():
        wb = load_workbook(path)
        ws = wb.active

    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Utilization Data"

        # Write headers
        headers = ["Date","Powered On Time (s)", "Active Time (s)", "Idle Time (s)", "Utilization (%)"]
        ws.append(headers)
    # Write data
    data_row = [
        utilization_data.powered_on_time,
        utilization_data.active_time,
        utilization_data.idle_time,
        utilization_data.utilization if utilization_data.utilization is not None else "N/A"
    ]
    ws.append(data_row)

    # Save the workbook
    wb.save(path)   



