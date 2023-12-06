import csv
import json
import os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import Candle
from datetime import datetime
from datetime import timedelta
# from .utils import convert_to_timeframe, save_to_json

async def process_csv(file_path, timeframe):
    # Read CSV data
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        candles = []
        for row in csv_reader:
            candles.append(Candle(
                open=float(row['OPEN']),
                high=float(row['HIGH']),
                low=float(row['LOW']),
                close=float(row['CLOSE']),
                date=datetime.strptime(row['DATE'] + ' ' + row['TIME'], '%Y%m%d %H:%M'),
                symbol=row['BANKNIFTY']
            ))

        # Implement logic to convert data to the desired timeframe
        # and save it as a JSON file
        converted_candles = convert_to_timeframe(candles, timeframe)
        save_to_json(converted_candles, 'converted_data.json')

def convert_to_timeframe(candles, timeframe):
     converted_candles = []
     current_timeframe_start = candles[0].date
     current_candle = candles[0].__dict__

     for candle in candles[1:]:
        if (candle.date - current_timeframe_start).total_seconds() < timeframe * 60:
            # Update current candle with new high, low, and close
            current_candle['high'] = max(current_candle['high'], candle.high)
            current_candle['low'] = min(current_candle['low'], candle.low)
            current_candle['close'] = candle.close
        else:
            # Add the current candle to the converted list
            converted_candles.append(current_candle)

            # Start a new timeframe
            current_timeframe_start = candle.date
            current_candle = candle.__dict__.copy()

    # Add the last candle to the converted list
     converted_candles.append(current_candle)

     return converted_candles

def save_to_json(data, file_path):
         with open(file_path, 'w') as json_file:
            json.dump(data, json_file)

# MainApp/views.py

from .models import UploadedFile

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            timeframe = form.cleaned_data['timeframe']

            # Save the CSV file to the server
            uploaded_file = UploadedFile(csv_file=file)
            uploaded_file.save()

            # Get the file path
            file_path = uploaded_file.csv_file.path

            # Process CSV data asynchronously
            candles=process_csv(file_path, timeframe)

            # # Provide a download link to the user
            # response = HttpResponse(content_type='application/json')
            # response['Content-Disposition'] = 'attachment; filename="converted_data.json"'
            # # Implement logic to read JSON file and write it to the response
            # Save converted data to JSON file
            json_file_path = 'converted_data.json'
            save_to_json(candles, json_file_path)
            with open(json_file_path, 'rb') as json_file:
                response = HttpResponse(json_file.read(), content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(json_file_path)}"'
              

                return response
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})
