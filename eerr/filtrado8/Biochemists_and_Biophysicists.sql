USE onet;

SELECT
  o.onetsoc_code,
  o.title,
  td.task_id,
  t.task,
  td.dwa_id,
  dwaref.dwa_title
FROM tasks_to_dwas td
JOIN occupation_data o ON td.onetsoc_code = o.onetsoc_code
JOIN dwa_reference dwaref ON td.dwa_id = dwaref.dwa_id
JOIN task_statements t ON td.task_id = t.task_id
WHERE o.title = 'Biochemists and Biophysicists';
