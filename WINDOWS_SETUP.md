# Windows Setup Instructions

## Prerequisites
- Python 3.8 or higher (Python 3.12 recommended)
- ArcGIS License Manager installed (for `lmutil.exe`)

## Installation Steps

1. **Extract the zip file** to your desired location (e.g., `C:\arcgis-license-tracker\`)

2. **Open Command Prompt or PowerShell** and navigate to the project directory:
   ```cmd
   cd C:\arcgis-license-tracker
   ```

3. **Create a virtual environment**:
   ```cmd
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
   You should see `(venv)` in your prompt.

5. **Upgrade pip**:
   ```cmd
   python -m pip install --upgrade pip
   ```

6. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

7. **Configure license servers** in `app\arcgis_config.py`:
   - Update the `license_servers` list with your license server hostnames and ports
   - The `lm_util` path will be automatically detected for Windows
   - If `lmutil.exe` is in a non-standard location, set the `LMUTIL_PATH` environment variable or edit the path directly

8. **Initialize the database**:
   ```cmd
   python manage.py recreate-db
   ```

9. **Test license reading** (optional):
   ```cmd
   python manage.py read-once
   ```

10. **Run the development server**:
    ```cmd
    python manage.py runserver
    ```
    Or use Flask CLI:
    ```cmd
    flask run
    ```

11. **Access the application**:
    Open your browser and navigate to: `http://localhost:5001`

## Windows-Specific Notes

- **Path to lmutil.exe**: The application will automatically look for:
  - `C:\Program Files (x86)\ArcGIS\LicenseManager\bin\lmutil.exe`
  - If it's elsewhere, set the `LMUTIL_PATH` environment variable:
    ```cmd
    set LMUTIL_PATH=C:\Your\Path\To\lmutil.exe
    ```

- **Database Options**: 
  - **SQLite (default)**: Database will be created in `instance\app.db`
  - **SQL Server**: See `SQL_SERVER_SETUP.md` for detailed instructions on connecting to SQL Server
  - The application supports SQL Server, PostgreSQL, MySQL, and SQLite

- **Running as a Service**: For production, consider using Windows Task Scheduler or IIS to run the application as a service

## Troubleshooting

- **Python not found**: Make sure Python is in your PATH or use the full path to `python.exe`
- **Port already in use**: Change the port in `manage.py` or use `flask run --port 5002`
- **lmutil not found**: Verify ArcGIS License Manager is installed and the path is correct

## Next Steps

- Configure Windows Task Scheduler to run `python manage.py read-once` every 5 minutes
- Set up IIS or another web server for production deployment
- Review `helper_guide.md` for more detailed information


