USE onet;

SELECT DISTINCT
    o.onetsoc_code,
    o.title,
    td.dwa_id,
    dwaref.dwa_title,
    w.data_value AS degree_of_automation
FROM tasks_to_dwas td
JOIN occupation_data o      ON td.onetsoc_code = o.onetsoc_code
JOIN dwa_reference dwaref   ON td.dwa_id      = dwaref.dwa_id
JOIN work_context w         ON o.onetsoc_code = w.onetsoc_code
JOIN content_model_reference cmr ON w.element_id = cmr.element_id
WHERE o.title = 'Industrial Engineering Technologists and Technicians'
  AND w.scale_id = 'CX'
  AND cmr.element_name = 'Degree of Automation'
ORDER BY dwaref.dwa_title;

