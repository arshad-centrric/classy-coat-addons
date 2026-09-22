def get_employee_fields():
	# The employee's name, ID, passport, department, designation, contact details and joining date are already
	# standard Employee fields.
	#
	# Frappe puts a new Section Break at the end of the section it is inserted after, even when that is the last
	# section of a tab, which moves it into the next tab. So Iqama Details is anchored to the section above
	# Passport Details (same tab), and Documents gets a tab of its own, which Frappe places right after the tab
	# it is anchored to.
	return {
		"Employee": [
			{
				"fieldname": "cc_iqama_details_section",
				"label": "Iqama Details",
				"fieldtype": "Section Break",
				"insert_after": "health_insurance_no",
			},
			{
				"fieldname": "cc_iqama_number",
				"label": "Iqama Number",
				"fieldtype": "Data",
				"insert_after": "cc_iqama_details_section",
			},
			{
				"fieldname": "cc_iqama_column_break",
				"fieldtype": "Column Break",
				"insert_after": "cc_iqama_number",
			},
			{
				"fieldname": "cc_iqama_expiry",
				"label": "Iqama Expiry",
				"fieldtype": "Date",
				"insert_after": "cc_iqama_column_break",
			},
			{
				"fieldname": "cc_documents_tab",
				"label": "Documents",
				"fieldtype": "Tab Break",
				"insert_after": "place_of_issue",
			},
			{
				"fieldname": "cc_documents",
				"label": "Documents",
				"fieldtype": "Table",
				"options": "Employee Document Detail",
				"insert_after": "cc_documents_tab",
			},
			# Nothing to list until the employee is saved. The HTML field stores nothing: public/js/employee.js
			# fills it with the projects and tasks the employee is part of.
			{
				"fieldname": "cc_project_task_tab",
				"label": "Projects & Tasks",
				"fieldtype": "Tab Break",
				"insert_after": "cc_documents",
				"depends_on": "eval:!doc.__islocal",
			},
			{
				"fieldname": "cc_project_task_assignment",
				"label": "Project Task Assignment",
				"fieldtype": "HTML",
				"insert_after": "cc_project_task_tab",
			},
		]
	}
