from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import get_conn

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        # Kiểm tra sinh viên
        cursor.execute("SELECT * FROM student WHERE student_id=%s AND password=%s", (user_id, password))
        student = cursor.fetchone()
        if student:
            session.clear()
            session['user_id'] = user_id
            session['role'] = 'student'
            cursor.close()
            conn.close()
            return redirect(url_for('student_views.home', student_id=user_id))

        # Kiểm tra giảng viên
        cursor.execute("SELECT * FROM lecturer WHERE lecturer_id=%s AND password=%s", (user_id, password))
        lecturer = cursor.fetchone()
        if lecturer:
            session.clear()
            session['user_id'] = user_id
            session['role'] = 'lecturer'
            cursor.close()
            conn.close()
            return redirect(url_for('lecturer_views.lecturer_home', lecturer_id=user_id))

        # Kiểm tra admin
        cursor.execute("SELECT * FROM admin WHERE admin_id=%s AND password=%s", (user_id, password))
        admin = cursor.fetchone()
        if admin:
            session.clear()
            session['user_id'] = user_id
            session['role'] = 'admin'
            cursor.close()
            conn.close()
            return redirect(url_for('admin_views.admin_home', admin_id=user_id))

        # Không phải ai cả -> thông báo lỗi
    # hiển thị thông báo lỗi để template có thể định kiểu
        flash("Sai ID hoặc mật khẩu, vui lòng thử lại!", 'danger')

        cursor.close()
        conn.close()

    return render_template('login.html')

# Đăng xuất
@auth.route('/logout')
def logout():
    session.clear()
    # hiển thị thông báo thành công để template có thể định kiểu
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))