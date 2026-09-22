// Fills the "Projects & Tasks" tab of the Employee form with every project and task the employee is part of.
// Projects and tasks point at Users rather than Employees, so the standard Connections counts cannot show
// them; the server matches them through the employee's User ID.
frappe.provide("classy_coat_addons.employee");

frappe.ui.form.on("Employee", {
	refresh(frm) {
		const field = frm.fields_dict.cc_project_task_assignment;
		if (!field || frm.is_new()) return;

		// The same form object is reused for the next employee, so drop the previous lists straight away.
		const employee = frm.doc.name;
		field.$wrapper.html(`<p class="text-muted">${__("Loading...")}</p>`);

		frappe.call({
			method: "classy_coat_addons.overrides.employee.project_assignment.get_project_task_assignment",
			args: { employee },
			callback({ message }) {
				// Ignore an answer that arrives after the form has moved on to another employee.
				if (!message || frm.doc.name !== employee) return;

				field.$wrapper.html(classy_coat_addons.employee.render_assignment(message));
			},
			error() {
				if (frm.doc.name !== employee) return;

				field.$wrapper.html(
					`<p class="text-muted">${__("Could not load the projects and tasks.")}</p>`
				);
			},
		});
	},
});

classy_coat_addons.employee.render_assignment = function (data) {
	if (!data.user) {
		return `<p class="text-muted">${__(
			"Set a User ID on this employee to see the projects and tasks assigned to them."
		)}</p>`;
	}

	const escape = frappe.utils.escape_html;
	const link = (doctype, name) => (name ? frappe.utils.get_form_link(doctype, name, true, escape(name)) : "");

	const table = (heading, headers, rows, empty_message) => {
		const body = rows.length
			? rows.map((cells) => `<tr>${cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")
			: `<tr><td colspan="${headers.length}" class="text-muted">${empty_message}</td></tr>`;

		return `
			<div style="margin-bottom: 20px">
				<div style="margin-bottom: 8px"><b>${heading}</b> (${rows.length})</div>
				<table class="table table-bordered" style="margin-bottom: 0">
					<thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
					<tbody>${body}</tbody>
				</table>
			</div>`;
	};

	const projects = table(
		__("Projects"),
		[__("Project"), __("Project Name"), __("Status"), __("Role")],
		data.projects.map((project) => [
			link("Project", project.name),
			escape(project.project_name || ""),
			escape(project.status || ""),
			escape(project.role),
		]),
		__("Not part of any project yet.")
	);

	const tasks = table(
		__("Tasks"),
		[__("Task"), __("Subject"), __("Project"), __("Status"), __("Due Date")],
		data.tasks.map((task) => [
			link("Task", task.name),
			escape(task.subject || ""),
			link("Project", task.project),
			escape(task.status || ""),
			task.exp_end_date ? frappe.datetime.str_to_user(task.exp_end_date) : "",
		]),
		__("No tasks assigned yet.")
	);

	return projects + tasks;
};
