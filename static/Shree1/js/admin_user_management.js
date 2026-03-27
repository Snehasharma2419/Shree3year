function openModal() {
  document.getElementById("modal").style.display = "block";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

function addUser() {
  let name = document.getElementById("name").value;
  let email = document.getElementById("email").value;
  let role = document.getElementById("role").value;
  let dept = document.getElementById("department").value;

  let table = document.getElementById("userTable");

  let row = table.insertRow();
  row.innerHTML = `
        <td>${name}</td>
        <td>${email}</td>
        <td><span class="role">${role}</span></td>
        <td>${dept}</td>
        <td><span class="status active">Active</span></td>
        <td>
            <i class="fa fa-pen" onclick="editUser(this)"></i>
            <i class="fa fa-trash" onclick="deleteUser(this)"></i>
        </td>
    `;

  closeModal();
}

function deleteUser(el) {
  el.closest("tr").remove();
}

function editUser(el) {
  alert("Edit feature (frontend only)");
}
