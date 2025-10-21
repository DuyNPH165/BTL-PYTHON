from flask import Flask
from .auth import auth
from .lecturer_views import lecturer_views
from .student_views import student_views
from .admin_views import admin_views
from .enrollment import enrollment
import datetime
import re
import os


def _format_date_filter(value):
    """Jinja filter to format a date/datetime (or common date string) as dd/mm/YYYY.

    Returns an empty string for falsy values. Handles datetime.date/datetime
    objects and strings in ISO-like formats (YYYY-MM-DD...).
    """
    if not value:
        return ""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime('%d/%m/%Y')
    s = str(value)
    # Kiểm tra định dạng ngày ISO ở đầu: YYYY-MM-DD
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = m.groups()
        return f"{int(d):02d}/{int(mo):02d}/{int(y)}"
    return s


def create_app():
    # Đảm bảo Flask phục vụ thư mục `static/` ở cấp dự án.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    static_dir = os.path.join(base_dir, 'static')
    app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
    app.config["SECRET_KEY"] = 'quang anh dep trai vocolo'
    # đăng ký filter định dạng ngày cho template
    app.jinja_env.filters['format_date'] = _format_date_filter
    # Removed filters and upload config per request
    app.register_blueprint(auth)
    # đăng ký blueprint theo vai trò
    app.register_blueprint(lecturer_views)
    app.register_blueprint(student_views)
    app.register_blueprint(admin_views)
    app.register_blueprint(enrollment, url_prefix='/')
    return app
