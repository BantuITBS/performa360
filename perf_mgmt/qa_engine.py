import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_md")

# Updated Q&A data
qa_data = {
    # General Performance Management Questions
    "what is performance management": "Performance management is a process of continuous evaluation and improvement of employee performance.",
    "how often should performance reviews be conducted": "Performance reviews are usually conducted once or twice a year.",
    "what are the benefits of performance management": "It aligns employee goals with organizational objectives, improves productivity, and fosters development.",
    "what is a 360-degree appraisal": "A 360-degree appraisal collects feedback from peers, managers, and subordinates to evaluate performance.",
    "how do kpis support performance management": "KPIs align individual and organizational goals, providing measurable performance metrics.",
    "what is goal setting in performance management": "Goal setting involves defining specific, measurable objectives for employees to achieve.",
    "how does feedback improve performance": "Feedback provides insights for improvement, motivates employees, and aligns expectations.",

    # Strategic Configuration Questions
    "what is the purpose of strategic configuration": "Strategic configuration aligns appraisal processes with organizational goals via Performa360’s Goal Cascading, defining evaluation parameters like manager assessments, peer reviews, self-assessments, and employee feedback.",
    "how does strategic configuration support organizational growth": "It allows control over feedback requirements and shapes assessments to drive meaningful performance improvements.",
    "what is the balanced scorecard in strategic configuration": "The Balanced Scorecard (BSC) is a framework to align goals across financial, customer, internal processes, and learning & growth perspectives.",
    "what are the four perspectives of the balanced scorecard": "Financial (outcomes), Customer (satisfaction), Internal Business Processes (efficiency), and Learning & Growth (human capital development).",
    "what are the benefits of the balanced scorecard": "It provides a holistic view, aligns strategies, drives improvement, and supports data-driven decisions.",
    "how are strategic goals set in the system": "Users select goal types, define specific goals, assign weights, set due dates, and allocate goals to departments.",
    "what types of strategic goals can be set": "Options include Operational, Growth & Innovation, Compliance & Risk, Employee Development, Customer-Centric, Sustainability, Financial, and Internal Business Processes goals.",
    "how are weights assigned to strategic goals": "Weights are allocated from 0% to 100% to prioritize goals within the appraisal process.",
    "how are due dates set for strategic goals": "Due dates are set via a date picker, auto-populated with the latest appraisal period’s end date based on company code.",
    "how are goals assigned to departments": "Users select departments from a dropdown, with selected departments displayed as tags and saved for goal alignment.",
    "what is the retrieve strategic goals function": "It fetches previously saved goals by company code, allowing users to view, edit, or delete them in a table.",
    "how can strategic goals be edited or deleted": "Goals are edited in a table with fields for goal type, strategic goal, weight, due date, and department, with checkboxes for selecting rows to delete.",
    "how does the system fetch review periods": "It retrieves review periods by company code, setting the latest period’s end date as the goal due date.",
    "what happens if no company code is provided": "The system prompts for a company code and clears date fields if none is provided.",

    # Manager Evaluation Questions
    "what is the purpose of manager evaluation": "Manager evaluation analyzes leadership performance through feedback on competencies and custom questions.",
    "how is feedback configured for manager evaluation": "Users select anonymous or identified feedback, choose competency areas, and add or select questions.",
    "what is the role of due dates in manager evaluation": "Due dates, set via a date picker, align evaluations with appraisal periods for timely feedback.",
    "how are custom questions added in manager evaluation": "Users input new questions, which are added to a dropdown and can be removed by double-clicking.",
    "how are evaluation questions saved": "Questions are saved with company code, branch code, feedback type, and due date, with duplicates skipped.",
    "what are competence areas in manager evaluation": "Competence areas are predefined leadership skills or factors fetched from the system for evaluation.",
    "how does the system handle multiple questions": "Multiple questions are saved in a batch, with a formatted response listing saved and skipped questions.",

    # Peer Review Questions
    "what is the purpose of peer review configuration": "Peer review configuration enables cross-functional 360-degree assessments to evaluate team collaboration and performance.",
    "how is reviewer selection configured": "Options include random peer selection, employee-chosen peers, or manager-assigned peers.",
    "how is evaluation cadence set for peer reviews": "Users choose monthly pulse checks, quarterly deep dives, or annual comprehensive reviews.",
    "how is feedback visibility managed in peer reviews": "Feedback can be anonymous, identified, or visible only to managers.",
    "what is the competency framework in peer reviews": "It defines leadership or team competencies to guide peer assessments.",
    "what are assessment criteria in peer reviews": "Criteria are evaluation metrics or questions tailored to assess peer performance.",

    # Self-Assessment Questions
    "what is the purpose of self-assessment setup": "Self-assessment setup enables employees to reflect on their performance and competencies.",
    "how is assessment frequency configured": "Options include before manager reviews, quarterly self-checks, or after project completion.",
    "what are competence areas in self-assessment": "They are skill domains employees evaluate, selected from a predefined list.",
    "what are assessment questions in self-assessment": "Questions are selected to guide employee self-reflection on performance.",
    "what rating systems are available for self-assessment": "Options include a 5-star scale, percentage scale, or narrative-only responses.",

    # Employee Feedback Questions
    "what is the purpose of employee feedback configuration": "Employee feedback configuration gathers organizational sentiment through surveys to inform performance strategies.",
    "how is survey frequency set for employee feedback": "Options include monthly pulse checks, quarterly deep dives, or annual comprehensive surveys.",
    "what feedback types are available for employee feedback": "Feedback can be anonymous or identified submissions.",
    "what are competence areas in employee feedback": "They are predefined areas like team collaboration or leadership for survey focus.",
    "what question types are supported in employee feedback": "Supported types include multiple-choice, text answers, and true/false questions.",

    # Authentication and Data Management Questions
    "how does the system handle user authentication": "Users enter a username, password, company code, and branch code, with data saved in localStorage for persistence.",
    "how is company code used in the system": "Company code fetches company details, review periods, and departments, ensuring data alignment.",
    "how are branch details retrieved": "Branch code and name are fetched using company code and employee code for location-specific settings.",
    "what is the logout functionality": "Logout clears session data via a POST request and redirects to the main page.",
    "how does the system ensure data consistency": "Data like company code, branch code, and username are validated and synced with backend APIs.",

    # Self Appraisal System Questions
    "what is the purpose of the self appraisal system": "The self appraisal system enables employees to evaluate their performance against strategic goals, KPIs, and deliverables, fostering self-reflection and alignment with organizational objectives.",
    "how does the system fetch strategic goals for self appraisal": "It retrieves goals by employee code via an API, displaying them with weights, due dates, and status indicators based on working days left.",
    "what is the role of kpis in self appraisal": "KPIs provide measurable performance metrics linked to strategic goals, allowing employees to assess progress and outcomes.",
    "how are kpis displayed in the self appraisal system": "KPIs are shown with weights, descriptions, and due dates, clickable to navigate to associated deliverables.",
    "what are deliverables in the self appraisal system": "Deliverables are specific tasks or outcomes tied to KPIs, evaluated by weight, description, self-appraisal score, and due date.",
    "how are deliverables evaluated in self appraisal": "Employees assign a self-appraisal score (1-10) to each deliverable, reflecting their performance assessment.",
    "what is document evidence in self appraisal": "Document evidence is supporting material for deliverables, evaluated by weight, description, self-confirmation (Yes/No), and due date.",
    "how is document evidence confirmed in self appraisal": "Employees select 'Yes' or 'No' to confirm the validity or completion of document evidence.",
    "how does the self appraisal table summarize performance": "The table displays review cycle, dates, strategic goals, KPIs, deliverables, self and assessor scores, document evidence, confirmations, and a delete option.",
    "what is the purpose of the unique chat identifier": "The unique chat identifier combines employee and appraisor codes to create a unique channel for performance-related communication.",
    "how is the unique chat identifier generated": "It is automatically generated by combining trimmed employee and appraisor codes, updated every 300ms if either changes.",
    "what is the purpose of the chat functionality": "Chat enables real-time communication between employees and appraisors to discuss performance, goals, and feedback.",
    "how are chat messages filtered": "Messages can be filtered by strategic goal, KPI, deliverable, and date range to focus on specific appraisal topics.",
    "how are chat messages sent": "Employees type messages, optionally add attachments (images or PDFs), and send them via an API, tagged with selected goals, KPIs, or deliverables.",
    "what types of attachments are supported in chat": "Supported attachments include images (JPG, PNG, GIF) and PDFs, displayed or linked in the chat.",
    "how does the system handle typing indicators in chat": "It sends a typing status to the appraisor when the employee types, displaying a visual indicator for the recipient.",
    "what is the purpose of the email functionality": "Email allows employees to send formal communications to appraisors, including subjects, bodies, and attachments, for performance discussions.",
    "how is an email composed in the system": "Employees enter the appraisor’s email (auto-fetched), subject, body, and optional attachments (images, PDFs, or Word documents), then send via an API.",
    "how are assessment dropdowns populated": "Dropdowns for strategic goals, KPIs, and deliverables are populated by fetching assessment data via an API, processed to map unique goals and their dependencies.",
    "how is assessment data processed": "Data is organized into a map of strategic goals, each containing KPIs and deliverables, ensuring unique entries for dropdown filtering.",

    # Self-Appraisal Application Questions
    "how does the application align employee goals with organizational objectives": "The application fetches strategic goals via API using employee code, linking them to KPIs and deliverables to cascade organizational priorities to individual tasks, with clickable navigation for alignment.",
    "how does the application support objective self-assessment": "Employees assign self-appraisal scores (1-10) to deliverables, supported by weights, due dates, and required document evidence to encourage evidence-based scoring.",
    "how does the app facilitate feedback between employees and appraisors": "Chat and email functionalities enable real-time and formal communication, with messages filterable by strategic goals, KPIs, or deliverables for focused feedback.",
    "what is the role of the unique chat identifier in performance discussions": "It creates a secure, dedicated channel for private, traceable performance discussions between employees and appraisors.",
    "how does the app track performance over time": "The self-appraisal table tracks review cycles, dates, and scores, allowing historical data access, with LocalStorage saving dropdown selections for continuity.",
    "how does the app support evidence-based evaluations": "Employees upload document evidence (images, PDFs) for deliverables, confirmed via Yes/No dropdowns, organized by weight, description, and due date.",
    "how does the app enhance employee accountability in self-appraisal": "Employees must score deliverables and confirm evidence, with due date indicators prompting action, fostering accountability.",
    "how does the app handle self-appraisal and appraisor score discrepancies": "The self-appraisal table compares Self and Assessor Scores, with chat and email for discussions, but no formal mediation workflow.",
    "how does the app support appraisors in reviewing self-appraisals": "Appraisors view scores, confirmations, and evidence in the self-appraisal table, with chat and dropdown filters for focused reviews.",
    "how does the app accommodate different review cycles": "It tracks review cycle numbers and fetches periods via API, supporting multiple cycles, though cadence customization is not explicit.",
    "how does the app ensure data security and privacy in self-appraisal": "CSRF tokens and secure APIs protect data, with unique chat identifiers ensuring private channels, though encryption details are unspecified.",
    "how does the app help employees understand performance progress": "Due date indicators and the self-appraisal table show progress, but explicit trackers or recommendations are absent.",
    "how does the app integrate with HR systems": "API-based data retrieval suggests potential integration with HRIS platforms, requiring custom API development.",
    "how does the app support multi-level appraisals": "It focuses on employee-appraisor interactions, requiring additional modules for peer or 360-degree feedback.",
    "how does the app ensure fairness in appraisals": "Standardized scoring and evidence requirements promote consistency, with appraisor oversight, but no calibration tools.",
    "how does the app handle overdue tasks in self-appraisal": "Overdue goals and KPIs are flagged with red indicators, prompting action, but no escalation or reminders are implemented.",
    "what analytics does the app offer for performance insights": "The self-appraisal table compiles data, but no built-in analytics or reports are shown, requiring backend queries.",
    "how does the app support goal setting in self-appraisal": "It displays pre-set goals via API, but goal creation occurs externally, with alignment via hierarchical display.",
    "how does the app cater to different user roles": "It supports employees and appraisors with role-specific views, with potential for HR admin dashboards via company code data.",
    "what training does the app provide for self-appraisal users": "No tutorials are included, relying on intuitive design and organizational training.",
    "how does the app handle multilingual or global requirements": "It uses English and standard formats, requiring localization for multilingual or global support.",
    "what happens to self-appraisal data after review cycles": "Data is stored in the backend for historical access, with potential for talent development integration.",
    "how does the app encourage continuous performance improvement": "Due date tracking and score visibility encourage reflection, but no explicit development features are provided.",
    "how does the app ensure compliance with regulations": "CSRF tokens and secure APIs support integrity, but compliance features depend on backend configurations.",
    "how scalable is the app for different organization sizes": "API-based design suggests scalability, with performance dependent on backend infrastructure.",

    # Leadership Matrix Application Questions
    "how does the leadership matrix app support leadership assessment": "It provides Self, Peer, and Manager Assessment modules to evaluate leadership competencies with 1-10 ratings, ensuring a holistic assessment.",
    "what is the role of factor types in leadership assessment": "Factor types are leadership competencies fetched via API, organizing assessment questions to evaluate specific skills systematically.",
    "how does the app ensure anonymity in peer assessments": "Peer assessments can be anonymized via API configuration, with peer selection and feedback submission not requiring identifiable data.",
    "how are assessment questions tailored to leadership competencies": "Selecting a factor type fetches specific questions via API, ensuring targeted evaluation of leadership skills.",
    "how does the app save and manage assessment data": "Ratings (1-10) are collected and saved via API, linked to company code and user details for organized storage.",
    "how does the app support multi-source feedback for leadership": "It integrates self, peer, and manager assessments, allowing comparison of ratings across sources to identify leadership strengths and gaps.",
    "how does the app customize assessments for companies": "Factor types and questions are fetched based on an 8-digit company code, aligning assessments with organizational leadership frameworks.",
    "what feedback options are available in assessments": "Users provide qualitative feedback via contenteditable tiles and quantitative 1-10 ratings for specific questions.",
    "how does the app ensure secure user authentication": "Username, password, company code, and branch code are validated via API, with data stored in localStorage for persistence.",
    "how does the app facilitate ease of use for assessments": "A competency grid, clickable factor types, and clear modals with save buttons streamline the assessment process.",
    "how does the app track assessment progress": "Ratings are highlighted in real-time, with saved data logged, but progress tracking requires backend retrieval.",
    "how does the app ensure data integrity in assessments": "CSRF tokens and company code validation ensure secure API requests and accurate data submission.",
    "how does the app support leadership development post-assessment": "Ratings and feedback identify development areas, with potential for backend-generated reports or plans.",
    "how does the app handle incomplete assessments": "Assessments require user-initiated saving, with no persistence for unsaved changes or warnings for incomplete submissions.",
    "how scalable is the leadership matrix app": "API-based architecture and company code segmentation support scalability, with backend performance determining large-scale capacity."
}

# Convert keys to spaCy Doc objects for similarity comparison
qa_docs = {nlp(q): a for q, a in qa_data.items()}

def answer_question(user_question):
    user_doc = nlp(user_question)
    best_score = 0
    best_answer = "I'm not sure how to help with that yet, but I'm learning!"

    for q_doc, answer in qa_docs.items():
        similarity = user_doc.similarity(q_doc)
        if similarity > best_score and similarity > 0.75:
            best_score = similarity
            best_answer = answer

    return best_answer