let isAdmin = false;

window.onload = () => {
  checkAdminStatus();
  loadTasks();
};

document.getElementById("taskForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const data = {
    short_name: document.getElementById("short_name").value,
    details: document.getElementById("details").value,
    owner: document.getElementById("owner").value,
    due_date: document.getElementById("due_date").value
  };

  await fetch('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  resetForm();
  loadTasks();
});

document.getElementById("updateBtn").addEventListener("click", async function () {
  const taskId = document.getElementById("task_id").value;
  const data = {
    short_name: document.getElementById("short_name").value,
    details: document.getElementById("details").value,
    owner: document.getElementById("owner").value,
    due_date: document.getElementById("due_date").value
  };

  await fetch(`/tasks/${taskId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  resetForm();
  loadTasks();
});

function resetForm() {
  document.getElementById("taskForm").reset();
  document.getElementById("task_id").value = '';
  document.getElementById("task_serial").value = '';
  document.getElementById("created_date").value = '';
  document.getElementById("addBtn").style.display = 'inline';
  document.getElementById("updateBtn").style.display = 'none';
}

async function checkAdminStatus() {
  const res = await fetch('/session-status');
  const data = await res.json();
  isAdmin = data.is_admin;

  const adminPanel = document.getElementById("adminPanel");
  adminPanel.innerHTML = isAdmin
    ? `<p>👑 Admin Mode: <strong>ON</strong> | <a href="/admin/logout">Logout</a></p>`
    : `<p><a href="/admin">Admin Login</a></p>`;
}

async function loadTasks() {
  const res = await fetch('/tasks');
  const tasks = await res.json();

  const list = document.getElementById("taskList");
  list.innerHTML = '';

  tasks.forEach(task => {
    const serial = String(task.id).padStart(3, '0');

    const li = document.createElement("li");
    li.innerHTML = `
      <b>${task.short_name}</b> (Task Serial: ${serial})<br>
      ${task.details}<br>
      Owner: ${task.owner}<br>
      Created: ${task.created_date}<br>
      Due: ${task.due_date}<br>
      Status: <span style="color:${task.is_approved ? 'green' : 'red'}">
        ${task.is_approved ? 'Approved ✅' : 'Pending ⏳'}
      </span><br>
    `;

    if (!task.is_approved) {
      const editBtn = document.createElement("button");
      editBtn.textContent = "Edit";
      editBtn.onclick = () => fillForm(task);
      li.appendChild(editBtn);

      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.onclick = () => deleteTask(task.id);
      li.appendChild(delBtn);
    }

    if (isAdmin && !task.is_approved) {
      const approveBtn = document.createElement("button");
      approveBtn.textContent = "Approve";
      approveBtn.onclick = () => approveTask(task.id);
      li.appendChild(approveBtn);
    }

    list.appendChild(li);
  });
}

function fillForm(task) {
  document.getElementById("task_id").value = task.id;
  document.getElementById("task_serial").value = String(task.id).padStart(3, '0');
  document.getElementById("short_name").value = task.short_name;
  document.getElementById("details").value = task.details;
  document.getElementById("owner").value = task.owner;
  document.getElementById("created_date").value = task.created_date;
  document.getElementById("due_date").value = task.due_date;

  document.getElementById("addBtn").style.display = 'none';
  document.getElementById("updateBtn").style.display = 'inline';
}

async function deleteTask(id) {
  await fetch(`/tasks/${id}`, { method: 'DELETE' });
  loadTasks();
}

async function approveTask(id) {
  await fetch(`/tasks/approve/${id}`, { method: 'POST' });
  loadTasks();
}
