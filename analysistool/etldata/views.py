# views.py
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from .forms import CSVFileForm, PartForm, ExcelFileForm
from .models import Measurements, Part
from datetime import date
import io
from django.core.files.storage import FileSystemStorage
from io import BytesIO

def upload_csv(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Bind the form to the request data
        
        form = CSVFileForm(request.POST, request.FILES)

        # Check if the form is valid
        if form.is_valid():
            # Get the uploaded file
            csv_file = request.FILES['file']

            # Check if the file is a CSV file
            if not csv_file.name.endswith('.csv'):
                # Return an error message
                return HttpResponse("The uploaded file is not a CSV file!")

            filename = csv_file.name

            upload_time = date.today()
            part_id = "none"
            for word in filename.split(" "):
                if "-" in word:
                    part_id = word
                    
            
            if ".csv" in part_id:
                part_id = part_id[:-4]

            # Open the CSV file using pandas
            print("before pd.read_csv")
            file_loc = request.FILES['file'].temporary_file_path()
            print(request.FILES['file'].temporary_file_path())
            data = pd.read_csv(io.BytesIO(csv_file.read()), encoding="cp1252")
            print("after read csv")
            next = False
            length_units = ""
            for row in data.itertuples():
                new_dict = {}
                if row[1] == "Length Units":
                    length_units = row[2]
                if pd.isnull(row[2]) and pd.isnull(row[3]):
                    next = False
                if row[2] == "Control" and row[3] == "Nom":
                    next = True
                if next and row[2] != "Control":
                    new_dict["part_id"] = part_id
                    new_dict["part_name"] = row[1]
                    new_dict["control"] = row[2]
                    new_dict["nom"] = row[3]
                    new_dict["measurement"] = row[4]
                    if not pd.isnull(row[5]):
                        new_dict["tolerance"] = row[5][1:]
                    else:
                        new_dict["tolerance"] = row[5]
                    new_dict["deviation"] = row[6]
                    new_dict["test_result"] = row[7]
                    new_dict["out_of_tolerance"] = row[8]
                    new_dict["upload_time"] = upload_time
                    new_dict["length_units"] = length_units
                    print("object is saved")
                    object = Measurements(**new_dict)
                    object.save()

            # Return a response to the client
            return HttpResponse("CSV file processed successfully!")
    else:
        # Initialize a new form
        form = CSVFileForm()

    # Render the form
    return render(request, 'getCsvForm.html', {'form': form})

def upload_excel(request):
    if request.method == 'POST':
        
        form = ExcelFileForm(request.POST, request.FILES)        

        if form.is_valid():
            # Get the uploaded file
            excel_file = request.FILES['excel_file']
            filename_string = excel_file.name
            
            part_id = "none"
            for word in filename_string.split(" "):
                if "-" in word:
                    part_id = word
            
            if not excel_file.name.endswith('.xls') or (not excel_file.name.endswith('.xlsx')):
                # Return an error message
                return HttpResponse("The uploaded file is not a Excel file!")

            if ".xls" in part_id:         
                part_id = part_id[:-4]
            
            if ".xlsx" in part_id:
                part_id = part_id[:-5]
            
            new_instance = Part()
            new_instance.part_id = part_id
            new_instance.excel_file = form.cleaned_data['excel_file']
           

            new_instance.save()
            print("Instanced saved")
            
            new_form = ExcelFileForm()

            return render(request, 'getExcelForm.html', {'form':new_form})

    else:
        form = ExcelFileForm()
    
    return render(request, 'getExcelForm.html', {'form':form})


def home_page(request):
    return render(request, 'homepage.html')

def read_table_data(request):
    instances = Measurements.objects.all()
    fields = ["part_id", "part_name",
                 "length_units", "control",
                 "nom", "measurement", 
                 "tolerance", "deviation",
                  "test_result", 
                  "out_of_tolerance", "upload_time"]

    return render(request, 'data_table.html', {'instances': instances, 'fields': fields})

def read_excel_files(request):
    instances = Part.objects.all()
    fields = ["part_id", "upload_time"]

    return render(request, 'excel_table.html', {'instances': instances, 'fields':fields})

def get_excel_file(request, part_id):
    with BytesIO() as b:
        instance = Part.objects.get(part_id=part_id)
        measurements = Measurements.objects.filter(part_id=part_id)
        
        df = pd.read_excel(instance.excel_file, sheet_name=-1)

        moving_data = False
        letter_kode = "z"
        for row in df.itertuples():
            
            if (len(str(row[3])) == 1) and (str(row[3]).isalpha()) and (str(row[4]).lower() == "dimension"):
                letter_kode = row[3].lower()
                moving_data = True
            
            if moving_data and (type(row[3])==float or type(row[3])==int) and (type(row[4])==str):
                
                letter_kode_name = letter_kode+ str(row[3]) 
                dimension_low = row[4].lower()
                query_string = "SELECT * FROM etldata_measurements WHERE lower(part_name) LIKE '%{} %' and\
                                lower(part_name) LIKE '%{}%'".format(letter_kode_name, dimension_low)
                queried_measurements = measurements.raw(query_string)
                if len(queried_measurements)>0:
                    df.iloc[row[0], 32] = queried_measurements[0].measurement


        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
        writer.save()
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = "attachment; filename={}.xlsx".format(part_id)
        return response
