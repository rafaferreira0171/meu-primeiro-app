const form = document.querySelector('#task-form');
const taskInput = document.querySelector('#task-input');
const prioritySelect = document.querySelector('#priority-select');
const dateInput = document.querySelector('#date-input');
const taskList = document.querySelector('#task-list');

function formatDate(value) {
  if (!value) return 'Sem prazo';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
}

function createTaskElement(task, priority, date) {
  const li = document.createElement('li');
  li.className = 'task-item';

  const content = document.createElement('div');

  const title = document.createElement('strong');
  title.textContent = task;

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.innerHTML = `<span class="priority ${priority}">${priority}</span> • ${formatDate(date)}`;

  content.append(title, meta);

  const removeButton = document.createElement('button');
  removeButton.type = 'button';
  removeButton.className = 'remove-btn';
  removeButton.textContent = 'Remover';
  removeButton.addEventListener('click', () => li.remove());

  li.append(content, removeButton);
  return li;
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const task = taskInput.value.trim();
  if (!task) return;

  const taskElement = createTaskElement(task, prioritySelect.value, dateInput.value);
  taskList.prepend(taskElement);
  form.reset();
  prioritySelect.value = 'Média';
});
