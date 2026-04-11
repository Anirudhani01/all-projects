const fs = require('fs');

// Read ADF JSON file
const adfData = JSON.parse(fs.readFileSync('./adf.json', 'utf-8'));

function extractText(cell) {
  const paragraphs = cell.content || [];
  return paragraphs
    .map(p => (p.content || []).map(t => t.text || '').join(''))
    .join('');
}

function parseADF(adfData) {
  const issue = adfData.fields;
  const table = issue.description.content.find(item => item.type === 'table');
  const rows = table.content.slice(1); // Skip header

  const test_steps = rows.map((row, index) => {
    const cells = row.content;
    return {
      step_number: parseInt(extractText(cells[0])),
      step: extractText(cells[1]),
      expected_output: extractText(cells[2])
    };
  });

  return {
    test_case_description: issue.summary.replace(/^.*?:\s*/, ''), // remove "error:" prefix
    test_steps,
    test_case_type: "error",
    flow_index: 1,
    test_case_id: adfData.key
  };
}

// Convert and print result
const parsedOutput = parseADF(adfData);
console.log(JSON.stringify(parsedOutput, null, 2));

