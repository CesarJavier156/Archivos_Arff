import os
import pandas as pd
import re
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

def upload_arff(request):
    data = None
    columns = []
    error = None

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        filepath = fs.path(filename)

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            attributes = []
            data_lines = []
            in_data = False

            for line in lines:
                line = line.strip()
                if not line or line.startswith('%'):
                    continue

                if line.lower().startswith('@attribute'):
                    parts = re.split(r'\s+', line, maxsplit=2)
                    if len(parts) >= 3:
                        name = parts[1].strip("'\"")
                        attributes.append(name)

                elif line.lower().startswith('@data'):
                    in_data = True
                    continue

                elif in_data:
                    data_lines.append(line)

            if attributes and data_lines:
                rows = [re.split(r',\s*', row) for row in data_lines]
                data = pd.DataFrame(rows, columns=attributes)
                columns = data.columns

        except Exception as e:
            error = str(e)

    data_html = None
    if data is not None and not data.empty:
        data_html = data.head(100).to_html(classes="table table-striped", index=False)

    return render(request, 'upload.html', {
        'data_html': data_html,
        'columns': columns,
        'error': error,
    })

