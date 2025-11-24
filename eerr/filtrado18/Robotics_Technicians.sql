USE onet;

SELECT
    o.onetsoc_code,
    o.title,
    td.dwa_id,
    dwaref.dwa_title,

    MAX(CASE WHEN cmr.element_name = 'Consequence of Error' THEN w.data_value END) AS consequence_of_error,
    MAX(CASE WHEN cmr.element_name = 'Contact With Others' THEN w.data_value END) AS contact_with_others,
    MAX(CASE WHEN cmr.element_name = 'Coordinate or Lead Others' THEN w.data_value END) AS coordinate_or_lead_others,
    MAX(CASE WHEN cmr.element_name = 'Cramped Work Space, Awkward Positions' THEN w.data_value END) AS cramped_work_space,
    MAX(CASE WHEN cmr.element_name = 'Deal With External Customers' THEN w.data_value END) AS deal_with_external_customers,
    MAX(CASE WHEN cmr.element_name = 'Deal With Physically Aggressive People' THEN w.data_value END) AS deal_with_physically_aggressive_people,
    MAX(CASE WHEN cmr.element_name = 'Deal With Unpleasant or Angry People' THEN w.data_value END) AS deal_with_unpleasant_or_angry_people,
    MAX(CASE WHEN cmr.element_name = 'Degree of Automation' THEN w.data_value END) AS degree_of_automation,
    MAX(CASE WHEN cmr.element_name = 'Electronic Mail' THEN w.data_value END) AS electronic_mail,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Contaminants' THEN w.data_value END) AS exposed_to_contaminants,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Disease or Infections' THEN w.data_value END) AS exposed_to_disease_or_infections,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Hazardous Conditions' THEN w.data_value END) AS exposed_to_hazardous_conditions,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Hazardous Equipment' THEN w.data_value END) AS exposed_to_hazardous_equipment,
    MAX(CASE WHEN cmr.element_name = 'Exposed to High Places' THEN w.data_value END) AS exposed_to_high_places,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Minor Burns, Cuts, Bites, or Stings' THEN w.data_value END) AS exposed_to_minor_burns_cuts_bites_stings,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Radiation' THEN w.data_value END) AS exposed_to_radiation,
    MAX(CASE WHEN cmr.element_name = 'Exposed to Whole Body Vibration' THEN w.data_value END) AS exposed_to_whole_body_vibration,
    MAX(CASE WHEN cmr.element_name = 'Extremely Bright or Inadequate Lighting' THEN w.data_value END) AS bright_or_inadequate_lighting,
    MAX(CASE WHEN cmr.element_name = 'Face-to-Face Discussions' THEN w.data_value END) AS face_to_face_discussions,
    MAX(CASE WHEN cmr.element_name = 'Freedom to Make Decisions' THEN w.data_value END) AS freedom_to_make_decisions,
    MAX(CASE WHEN cmr.element_name = 'Frequency of Conflict Situations' THEN w.data_value END) AS frequency_of_conflict_situations,
    MAX(CASE WHEN cmr.element_name = 'Impact of Decisions on Co-workers or Company Results' THEN w.data_value END) AS impact_of_decisions,
    MAX(CASE WHEN cmr.element_name = 'Importance of Being Exact or Accurate' THEN w.data_value END) AS importance_of_being_exact_or_accurate,
    MAX(CASE WHEN cmr.element_name = 'Importance of Repeating Same Tasks' THEN w.data_value END) AS importance_of_repeating_same_tasks,
    MAX(CASE WHEN cmr.element_name = 'In an Enclosed Vehicle or Equipment' THEN w.data_value END) AS in_enclosed_vehicle_or_equipment,
    MAX(CASE WHEN cmr.element_name = 'In an Open Vehicle or Equipment' THEN w.data_value END) AS in_open_vehicle_or_equipment,
    MAX(CASE WHEN cmr.element_name = 'Indoors, Environmentally Controlled' THEN w.data_value END) AS indoors_environmentally_controlled,
    MAX(CASE WHEN cmr.element_name = 'Indoors, Not Environmentally Controlled' THEN w.data_value END) AS indoors_not_environmentally_controlled,
    MAX(CASE WHEN cmr.element_name = 'Letters and Memos' THEN w.data_value END) AS letters_and_memos,
    MAX(CASE WHEN cmr.element_name = 'Level of Competition' THEN w.data_value END) AS level_of_competition,
    MAX(CASE WHEN cmr.element_name = 'Outdoors, Exposed to Weather' THEN w.data_value END) AS outdoors_exposed_to_weather,
    MAX(CASE WHEN cmr.element_name = 'Outdoors, Under Cover' THEN w.data_value END) AS outdoors_under_cover,
    MAX(CASE WHEN cmr.element_name = 'Pace Determined by Speed of Equipment' THEN w.data_value END) AS pace_determined_by_equipment,
    MAX(CASE WHEN cmr.element_name = 'Physical Proximity' THEN w.data_value END) AS physical_proximity,
    MAX(CASE WHEN cmr.element_name = 'Public Speaking' THEN w.data_value END) AS public_speaking,
    MAX(CASE WHEN cmr.element_name = 'Responsibility for Outcomes and Results' THEN w.data_value END) AS responsibility_for_outcomes,
    MAX(CASE WHEN cmr.element_name = 'Responsible for Others'' Health and Safety' THEN w.data_value END) AS responsible_for_others_health_and_safety,
    MAX(CASE WHEN cmr.element_name = 'Sounds, Noise Levels Are Distracting or Uncomfortable' THEN w.data_value END) AS noise_levels_distracting,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Bending or Twisting the Body' THEN w.data_value END) AS spend_time_bending_or_twisting,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Climbing Ladders, Scaffolds, or Poles' THEN w.data_value END) AS spend_time_climbing_ladders,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Keeping or Regaining Balance' THEN w.data_value END) AS spend_time_keeping_balance,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Kneeling, Crouching, Stooping, or Crawling' THEN w.data_value END) AS spend_time_kneeling_crouching,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Sitting' THEN w.data_value END) AS spend_time_sitting,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Standing' THEN w.data_value END) AS spend_time_standing,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Using Your Hands to Handle, Control, or Feel Objects, Tools, or Controls' THEN w.data_value END) AS spend_time_using_hands,
    MAX(CASE WHEN cmr.element_name = 'Spend Time Walking and Running' THEN w.data_value END) AS spend_time_walking_running,
    MAX(CASE WHEN cmr.element_name = 'Structured versus Unstructured Work' THEN w.data_value END) AS structured_vs_unstructured_work,
    MAX(CASE WHEN cmr.element_name = 'Telephone' THEN w.data_value END) AS telephone,
    MAX(CASE WHEN cmr.element_name = 'Very Hot or Cold Temperatures' THEN w.data_value END) AS very_hot_or_cold_temperatures,
    MAX(CASE WHEN cmr.element_name = 'Wear Common Protective or Safety Equipment such as Safety Shoes, Glasses, Gloves, Hearing Protection, Hard Hats, or Life Jackets' THEN w.data_value END) AS wear_common_protective_equipment,
    MAX(CASE WHEN cmr.element_name = 'Wear Specialized Protective or Safety Equipment such as Breathing Apparatus, Safety Harness, Full Protection Suits, or Radiation Protection' THEN w.data_value END) AS wear_specialized_protective_equipment,
    MAX(CASE WHEN cmr.element_name = 'Work With Work Group or Team' THEN w.data_value END) AS work_with_team
FROM tasks_to_dwas td
JOIN occupation_data o           ON td.onetsoc_code = o.onetsoc_code
JOIN dwa_reference dwaref        ON td.dwa_id      = dwaref.dwa_id
JOIN work_context w              ON o.onetsoc_code = w.onetsoc_code
JOIN content_model_reference cmr ON w.element_id   = cmr.element_id
WHERE o.title   = 'Robotics Technicians'
  AND w.scale_id = 'CX'
  AND cmr.element_name IN (
    'Consequence of Error','Contact With Others','Coordinate or Lead Others',
    'Cramped Work Space, Awkward Positions','Deal With External Customers',
    'Deal With Physically Aggressive People','Deal With Unpleasant or Angry People',
    'Degree of Automation','Electronic Mail','Exposed to Contaminants',
    'Exposed to Disease or Infections','Exposed to Hazardous Conditions',
    'Exposed to Hazardous Equipment','Exposed to High Places',
    'Exposed to Minor Burns, Cuts, Bites, or Stings','Exposed to Radiation',
    'Exposed to Whole Body Vibration','Extremely Bright or Inadequate Lighting',
    'Face-to-Face Discussions','Freedom to Make Decisions',
    'Frequency of Conflict Situations','Impact of Decisions on Co-workers or Company Results',
    'Importance of Being Exact or Accurate','Importance of Repeating Same Tasks',
    'In an Enclosed Vehicle or Equipment','In an Open Vehicle or Equipment',
    'Indoors, Environmentally Controlled','Indoors, Not Environmentally Controlled',
    'Letters and Memos','Level of Competition','Outdoors, Exposed to Weather',
    'Outdoors, Under Cover','Pace Determined by Speed of Equipment','Physical Proximity',
    'Public Speaking','Responsibility for Outcomes and Results',
    'Responsible for Others'' Health and Safety','Sounds, Noise Levels Are Distracting or Uncomfortable',
    'Spend Time Bending or Twisting the Body','Spend Time Climbing Ladders, Scaffolds, or Poles',
    'Spend Time Keeping or Regaining Balance','Spend Time Kneeling, Crouching, Stooping, or Crawling',
    'Spend Time Sitting','Spend Time Standing',
    'Spend Time Using Your Hands to Handle, Control, or Feel Objects, Tools, or Controls',
    'Spend Time Walking and Running','Structured versus Unstructured Work','Telephone',
    'Very Hot or Cold Temperatures',
    'Wear Common Protective or Safety Equipment such as Safety Shoes, Glasses, Gloves, Hearing Protection, Hard Hats, or Life Jackets',
    'Wear Specialized Protective or Safety Equipment such as Breathing Apparatus, Safety Harness, Full Protection Suits, or Radiation Protection',
    'Work With Work Group or Team'
  )
GROUP BY o.onetsoc_code, o.title, td.dwa_id, dwaref.dwa_title
ORDER BY dwaref.dwa_title;


