import frappe
from frappe import _


@frappe.whitelist()
def get_project_task_assignment(employee):
	"""The projects and tasks an employee is part of, for the Connections tab of the Employee form.

	Projects and tasks point at Users, not Employees, so everything is matched through the employee's
	User ID. Only what the current user is allowed to read is returned.
	"""
	frappe.has_permission("Employee", "read", employee, throw=True)

	user = frappe.db.get_value("Employee", employee, "user_id")
	if not user:
		return frappe._dict(user=None, projects=[], tasks=[])

	tasks = get_tasks(user)
	return frappe._dict(user=user, projects=get_projects(user, tasks), tasks=tasks)


def get_tasks(user):
	if not frappe.has_permission("Task", "read"):
		return []

	# Everything ever assigned to the user except cancelled assignments, so completed tasks stay listed.
	task_names = frappe.get_all(
		"ToDo",
		filters={"reference_type": "Task", "allocated_to": user, "status": ["!=", "Cancelled"]},
		pluck="reference_name",
	)
	if not task_names:
		return []

	return frappe.get_list(
		"Task",
		filters={"name": ["in", task_names]},
		fields=["name", "subject", "project", "status", "exp_end_date"],
		order_by="modified desc",
		limit_page_length=0,
	)


def get_projects(user, tasks):
	if not frappe.has_permission("Project", "read"):
		return []

	# A project counts as the employee's when they supervise it, sit in its team, or have a task in it.
	memberships = (
		(_("Supervisor"), frappe.get_all("Project", filters={"cen_project_supervisor": user}, pluck="name")),
		(
			_("Team Member"),
			frappe.get_all("Project User", filters={"user": user}, parent_doctype="Project", pluck="parent"),
		),
		(_("Task Assignee"), [task.project for task in tasks if task.project]),
	)

	roles = {}
	for role, project_names in memberships:
		for project_name in dict.fromkeys(project_names):
			roles.setdefault(project_name, []).append(role)

	if not roles:
		return []

	projects = frappe.get_list(
		"Project",
		filters={"name": ["in", list(roles)]},
		fields=["name", "project_name", "status"],
		order_by="modified desc",
		limit_page_length=0,
	)
	for project in projects:
		project.role = ", ".join(roles[project.name])

	return projects
