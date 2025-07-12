document.addEventListener("DOMContentLoaded", function () {
  const attributes = window.availableAttributes;
  const table1 = document.getElementById("table1");
  const table2 = document.getElementById("table2");
  const fieldContainer = document.getElementById("field-container");
  const sortSelect = document.getElementById("sort_field");

  function updateFields() {
    const t1 = table1.value;
    const t2 = table2.value;
    const fields1 = attributes[t1] || [];
    const fields2 = attributes[t2] || [];
    const allFields = [...new Set([...fields1, ...fields2])];

    // Clear previous fields
    fieldContainer.innerHTML = '';
    sortSelect.innerHTML = '<option value="">-- No Sorting --</option>';

    allFields.forEach(field => {
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.name = "fields";
      checkbox.value = field;
      checkbox.id = `field_${field}`;

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.textContent = field;

      const div = document.createElement("div");
      div.appendChild(checkbox);
      div.appendChild(label);

      fieldContainer.appendChild(div);

      // Also add to sort dropdown
      const opt = document.createElement("option");
      opt.value = field;
      opt.textContent = field;
      sortSelect.appendChild(opt);
    });
  }

  table1.addEventListener("change", updateFields);
  table2.addEventListener("change", updateFields);

  updateFields(); // Initial
});
