document.addEventListener("DOMContentLoaded", function () {
  const attributes = window.availableAttributes;

  const table1 = document.getElementById("table1");
  const table2 = document.getElementById("table2");
  const fieldContainer = document.getElementById("field-container");
  const sortSelect = document.getElementById("sort_field");

  // NEW dropdowns
  const groupBySelect = document.querySelector('select[name="group_by"]');
  const aggregateFieldSelect = document.getElementById("aggregate_field");

  function updateFields() {
    const t1 = table1.value;
    const t2 = table2.value;
    const fields1 = attributes[t1] || [];
    const fields2 = attributes[t2] || [];
    const allFields = [...new Set([...fields1, ...fields2])];

    // Clear previous content
    fieldContainer.innerHTML = '';
    sortSelect.innerHTML = '<option value="">-- No Sorting --</option>';
    groupBySelect.innerHTML = '<option value="">-- No Grouping --</option>';
    aggregateFieldSelect.innerHTML = '<option value="">-- Select Field --</option>';

    allFields.forEach(field => {
      // Create checkbox
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

      // Populate dropdowns
      const sortOption = new Option(field, field);
      sortSelect.appendChild(sortOption);

      const groupByOption = new Option(field, field);
      groupBySelect.appendChild(groupByOption);

      const aggregateOption = new Option(field, field);
      aggregateFieldSelect.appendChild(aggregateOption);
    });
  }

  table1.addEventListener("change", updateFields);
  table2.addEventListener("change", updateFields);

  updateFields(); // Initial call
});
