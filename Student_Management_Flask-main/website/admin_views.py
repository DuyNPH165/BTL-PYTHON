from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .models import get_conn
import json

admin_views = Blueprint('admin_views', __name__)


@admin_views.route('/admin/home/<admin_id>')
def admin_home(admin_id):
	conn = get_conn()
	cursor = conn.cursor(dictionary=True)
	cursor.execute("SELECT * FROM Admin WHERE admin_id = %s", (admin_id,))
	admin = cursor.fetchone()
	cursor.close()
	conn.close()
	if not admin:
		return "Không tìm thấy admin", 404
	return render_template("admin_dashboard.html", admin=admin)


@admin_views.route('/admin/score_proposals/<admin_id>')
def admin_score_proposals(admin_id):
	conn = get_conn()
	cur = conn.cursor(dictionary=True)
	cur.execute("SELECT * FROM Admin WHERE admin_id = %s", (admin_id,))
	admin = cur.fetchone()
	if not admin:
		cur.close()
		conn.close()
		return "Không tìm thấy admin", 404

	cur.execute("SELECT id, course_class_id, proposer_id, payload, status, created_at, reviewed_at, reviewer_id FROM score_proposals ORDER BY created_at DESC")
	proposals = cur.fetchall() or []
	cur.close()
	conn.close()
	return render_template('admin_proposals.html', admin=admin, proposals=proposals)


@admin_views.route('/admin/score_proposals/<admin_id>/review/<int:proposal_id>', methods=['POST'])
def admin_review_proposal(admin_id, proposal_id):
	# expects form 'action' = 'approve'/'reject'
	action = request.form.get('action')
	if action not in ('approve', 'reject'):
		return 'Invalid action', 400

	conn = get_conn()
	cur = conn.cursor()
	try:
		# get proposal
		cur.execute("SELECT id, course_class_id, proposer_id, payload FROM score_proposals WHERE id=%s", (proposal_id,))
		row = cur.fetchone()
		if not row:
			cur.close()
			conn.close()
			return 'Proposal not found', 404

		if action == 'approve':
			# apply the payload into Score table
			data = json.loads(row[3])
			
			upsert_sql = """
				INSERT INTO Score (student_id, course_class_id, attendance_scr, midterm_scr, finalterm_scr)
				VALUES (%s, %s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
				  attendance_scr = VALUES(attendance_scr), midterm_scr = VALUES(midterm_scr), finalterm_scr = VALUES(finalterm_scr)
			"""

			for sid, scores in data.items():
				# chấp nhận cả key cũ 'attendane_scr' để tương thích ngược
				att = scores.get('attendance_scr', scores.get('attendane_scr'))
				mid = scores.get('midterm_scr')
				fin = scores.get('finalterm_scr')
				params = (sid, row[1], att, mid, fin)
				cur.execute(upsert_sql, params)

			# mark proposal approved
			cur.execute("UPDATE score_proposals SET status='approved', reviewed_at=NOW(), reviewer_id=%s WHERE id=%s", (admin_id, proposal_id))
			conn.commit()
		else:
			# reject
			cur.execute("UPDATE score_proposals SET status='rejected', reviewed_at=NOW(), reviewer_id=%s WHERE id=%s", (admin_id, proposal_id))
			conn.commit()
	except Exception:
		conn.rollback()
		current_app.logger.exception('Failed to review proposal')
		cur.close()
		conn.close()
		return 'Server error', 500
	cur.close()
	conn.close()
	return redirect(url_for('admin_views.admin_score_proposals', admin_id=admin_id))
