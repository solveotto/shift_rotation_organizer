from flask import Blueprint, send_from_directory
from config import conf

downloads = Blueprint('downloads', __name__)

@downloads.route('/download_excel')
def download_excel():
    filename = f'{conf.CURRENT_TURNUS}/turnuser_R25.xlsx'  # Replace with your actual file name
    return send_from_directory(conf.static_dir, filename, as_attachment=True)

@downloads.route('/download_turnusnokler_zip')
def download_turnusnokler_zip():
    filename = f'{conf.CURRENT_TURNUS}/turnusnøkler.zip'  # Replace with your actual file name
    return send_from_directory(conf.static_dir, filename, as_attachment=True) 