from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import get_conn

enrollment = Blueprint('enrollment', __name__)


@enrollment.route('/enrollment/<student_id>')
def enrollment_page(student_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            cc.volume,
            cc.course_class_id,
            l.lecturer_name
        FROM course_class cc
        JOIN course c ON cc.course_id = c.course_id
        JOIN lecturer l ON cc.lecturer_id = l.lecturer_id
    """)
    course_class = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("enrollment.html", student_id=student_id, course_class=course_class)


@enrollment.route('/enrollment/<student_id>/register', methods=['POST'])
def register_courses(student_id):
    conn = get_conn()
    selected = request.form.getlist('selected_courses')
    print(f"➡️ Bắt đầu xử lý đăng ký cho: {student_id}")
    print(f"🧩 Các môn được chọn: {selected}")

    has_error = False
    cursor = conn.cursor()

    try:
        for cc_id in selected:
            print(f"🔹 Đang thêm lớp {cc_id}...")
            cursor.execute("""
                INSERT INTO enrollment (student_id, course_class_id)
                VALUES (%s, %s)
            """, (student_id, cc_id))
        conn.commit()
        flash("✅ Đăng ký thành công!", "success")

    except Exception as e:
        conn.rollback()
        has_error = True
        print(f"⚠️ Lỗi SQL: {e}")
        flash(f"⚠️ bạn đã đăng ký lớp học này!", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('enrollment.enrollment_page', student_id=student_id))
