# Student-related Flask routes and helpers
from flask import Blueprint, render_template, request
from .models import get_conn

student_views = Blueprint('student_views', __name__)


@student_views.route('/home/<student_id>')
def home(student_id):
	conn = get_conn()
	cursor = conn.cursor(dictionary=True)

	# Lấy thông tin sinh viên
	cursor.execute("SELECT * FROM Student WHERE student_id = %s", (student_id,))
	student = cursor.fetchone()

	if not student:
		cursor.close()
		return "Không tìm thấy sinh viên", 404

	# Xác định tab hiện tại
	active_tab = request.args.get("tab", "hoso")

	# Nếu tab = lop-hanh-chinh => lấy danh sách lớp hành chính
	students = []
	if active_tab == "lop-hanh-chinh":
		cursor.execute("SELECT * FROM Student WHERE administrative_class = %s", (student['administrative_class'],))
		students = cursor.fetchall()

	# Nếu tab = hoc-tap => lấy kết quả học tập
	scores = []
	if active_tab == "hoc-tap":
		cursor.execute("""
			SELECT 
				c.course_name,
				sc.attendance_scr,
				sc.midterm_scr,
				sc.finalterm_scr
			FROM Score sc
			JOIN Course_Class cc ON sc.course_class_id = cc.course_class_id
			JOIN Course c ON cc.course_id = c.course_id
			WHERE sc.student_id = %s
		""", (student_id,))
		scores = cursor.fetchall()

	cursor.close()
	conn.close()

	return render_template(
		"home.html",
		student=student,
		active_tab=active_tab,
		students=students,
		scores=scores
	)
