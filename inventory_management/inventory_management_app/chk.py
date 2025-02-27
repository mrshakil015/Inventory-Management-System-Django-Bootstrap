import pandas as pd
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import *
from django.contrib import messages
from django.http import HttpResponse
import io


def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            file_name = excel_file.name

            try:
                # Check file format
                if file_name.endswith(".csv"):
                    df = pd.read_csv(excel_file)
                elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
                    df = pd.read_excel(excel_file, engine="openpyxl")
                else:
                    messages.error(request, "Unsupported file format! Please upload a CSV or Excel file.")
                    return redirect("upload_excel")
                
                # Standardize column names
                df.columns = df.columns.str.strip().str.lower()
                required_columns = {"name", "age", "designation", "address"}
                
                # Missing column check
                if not required_columns.issubset(df.columns):
                    messages.error(request, f"Missing columns: {', '.join(required_columns - set(df.columns))}")
                    return redirect("upload_excel")

                allowed_designations = [choice[0] for choice in Employee.DESIGNATION_TYPES]
                
                df['age'] = df['age'].fillna(value=0)
                df['address'] = df['address'].fillna(value='Unknown')
                
                valid_rows = []
                invalid_rows = []
                valid_flag = False  # Use Boolean for clarity

                # Validate each row
                for _, row in df.iterrows():
                    row_dict = row.to_dict()
                    errors = []

                    # Validation
                    if pd.isna(row["name"]) or row["name"].strip() == "":
                        errors.append("Missing name")
                    if row["designation"] not in allowed_designations:
                        errors.append(f"Invalid designation: {row['designation']}")

                    # Store valid or invalid rows
                    if errors:
                        row_dict["error_reason"] = "; ".join(errors)
                        invalid_rows.append(row_dict)
                    else:
                        valid_rows.append(Employee(
                            name=row["name"],
                            age=int(row["age"]),
                            designation=row["designation"],
                            address=row["address"]
                        ))

                # Save valid rows to DB
                if valid_rows:
                    Employee.objects.bulk_create(valid_rows)
                    valid_flag = True

                # Generate an error file if needed
                if invalid_rows:
                    error_df = pd.DataFrame(invalid_rows)
                    error_file = io.BytesIO()
                    error_df.to_excel(error_file, index=False, engine="openpyxl")
                    error_file.seek(0)

                    # Set the appropriate message before sending the file
                    if valid_flag:
                        messages.success(request, "Data imported successfully! Some data had errors. Please review the error file.")
                    else:
                        messages.warning(request, "No valid data found. Please check the downloaded error file.")

                    # Create the HTTP response to send the error file
                    response = HttpResponse(error_file, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    response["Content-Disposition"] = 'attachment; filename="error_data.xlsx"'
                    
                    # Return the response and allow for file download
                    return response
                
                messages.success(request, "Data imported successfully!")

                return redirect("upload_excel")

            except Exception as e:
                messages.error(request, f"Error importing data: {str(e)}")
                return redirect("upload_excel")
    else:
        form = ExcelUploadForm()

    return render(request, "upload.html", {"form": form})

