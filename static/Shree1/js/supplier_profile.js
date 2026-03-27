function validatePhone(input) {
  // remove non-digits
  input.value = input.value.replace(/[^0-9]/g, "");

  // prevent starting with 0
  if (input.value.startsWith("0")) {
    input.value = input.value.substring(1);
  }

  // max 10 digits
  if (input.value.length > 10) {
    input.value = input.value.slice(0, 10);
  }
}

document.getElementById("profileForm").addEventListener("submit", function (e) {
  const phone = document.querySelector("input[name='phone']").value;

  if (!/^[1-9][0-9]{9}$/.test(phone)) {
    alert("Phone must be exactly 10 digits and cannot start with 0");
    e.preventDefault();
  }
});
