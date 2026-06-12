#!/usr/bin/env python3
"""
Importar sedes desde un archivo Excel o CSV y registrar/actualizar bibliotecas en la BD.
Soporta formatos: .xls/.xlsx (si pandas/xlrd están instalados) y .csv (sin dependencias).

Uso:
  python3 scripts/import_sedes.py --file "Sedes Red26Servicios.xls"

El script intentará detectar columnas comunes y mapearlas a: nombre, parroquia, encargado, tipo.
"""
import os
import sys
import csv
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.biblioteca_controller import BibliotecaController

POSSIBLE_NAME_COLS = ['nombre', 'biblioteca', 'nombre_biblioteca', 'sede', 'sede_nombre']
POSSIBLE_PARROQUIA_COLS = ['parroquia', 'municipio', 'zona']
POSSIBLE_ENCARGADO_COLS = ['encargado', 'responsable', 'contacto']
POSSIBLE_TIPO_COLS = ['tipo', 'categoria', 'class']


def detect_column(headers, candidates):
    h = [c.lower().strip() for c in headers]
    for cand in candidates:
        if cand in h:
            return h.index(cand)
    # try partial matches
    for cand in candidates:
        for i, col in enumerate(h):
            if cand in col:
                return i
    return None


def read_xls_like(file_path):
    # Try pandas if available
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        headers = list(df.columns)
        rows = df.fillna("").to_dict(orient='records')
        return headers, rows
    except Exception:
        # Try xlrd only for .xls
        try:
            import xlrd
            book = xlrd.open_workbook(file_path)
            sh = book.sheet_by_index(0)
            headers = [str(sh.cell_value(0, j)).strip() for j in range(sh.ncols)]
            rows = []
            for i in range(1, sh.nrows):
                row = {}
                for j in range(sh.ncols):
                    row[headers[j]] = sh.cell_value(i, j)
                rows.append(row)
            return headers, rows
        except Exception as e:
            raise RuntimeError("No hay librería disponible para leer XLS. Convierta el archivo a CSV o instale pandas/xlrd.")


def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = [r for r in reader]
    return headers, rows


def normalize_value(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='Path to XLS/XLSX or CSV file', default='Sedes Red26Servicios.xls')
    args = parser.parse_args()

    path = args.file
    if not os.path.exists(path):
        print('File not found:', path)
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in ('.xls', '.xlsx'):
            headers, rows = read_xls_like(path)
        elif ext in ('.csv',):
            headers, rows = read_csv(path)
        else:
            # attempt xls first
            try:
                headers, rows = read_xls_like(path)
            except Exception:
                headers, rows = read_csv(path)
    except Exception as e:
        print('Error reading file:', e)
        sys.exit(1)

    print('Detected headers:', headers)

    # map columns
    name_idx = detect_column(headers, POSSIBLE_NAME_COLS)
    par_idx = detect_column(headers, POSSIBLE_PARROQUIA_COLS)
    enc_idx = detect_column(headers, POSSIBLE_ENCARGADO_COLS)
    tipo_idx = detect_column(headers, POSSIBLE_TIPO_COLS)

    created = 0
    updated = 0
    skipped = 0

    ctrl = BibliotecaController()

    for r in rows:
        # get values by header; r might be dict with keys = headers
        if isinstance(r, dict):
            # DictReader or pandas record
            # normalize key lookup ignoring case
            row = {k.lower().strip(): v for k, v in r.items()}
            # find name
            name = None
            for cand in POSSIBLE_NAME_COLS:
                if cand in row and str(row[cand]).strip():
                    name = normalize_value(row[cand])
                    break
            if not name:
                # try first non-empty column
                for k, v in row.items():
                    if str(v).strip():
                        name = normalize_value(v)
                        break
            parroquia = ''
            encargado = ''
            tipo = 'Sede Satélite'
            for cand in POSSIBLE_PARROQUIA_COLS:
                if cand in row and str(row[cand]).strip():
                    parroquia = normalize_value(row[cand])
                    break
            for cand in POSSIBLE_ENCARGADO_COLS:
                if cand in row and str(row[cand]).strip():
                    encargado = normalize_value(row[cand])
                    break
            for cand in POSSIBLE_TIPO_COLS:
                if cand in row and str(row[cand]).strip():
                    tipo = normalize_value(row[cand])
                    break
        else:
            # list-like row (xlrd output)
            vals = [normalize_value(v) for v in r]
            name = vals[name_idx] if name_idx is not None and name_idx < len(vals) else None
            parroquia = vals[par_idx] if par_idx is not None and par_idx < len(vals) else ''
            encargado = vals[enc_idx] if enc_idx is not None and enc_idx < len(vals) else ''
            tipo = vals[tipo_idx] if tipo_idx is not None and tipo_idx < len(vals) else 'Sede Satélite'

        if not name:
            skipped += 1
            continue

        # create or update
        try:
            bid = ctrl.crear_o_actualizar_biblioteca(name, parroquia, encargado, tipo)
            existing = ctrl.biblioteca_model.obtener_por_nombre(name)
            if existing and existing.get('id') == bid:
                # Could be new or existing; rough heuristic: if created recently we count as created
                # Try to detect by id value: assume IDs <= 4 exist as seed; else treat as created
                if bid and bid > 4:
                    created += 1
                else:
                    updated += 1
            else:
                created += 1
        except Exception as e:
            print('Error processing row', name, e)
            skipped += 1

    print(f"Import completed. created={created}, updated={updated}, skipped={skipped}")

if __name__ == '__main__':
    main()
