from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Import your views file
from .views import (
    create_user,
    
    get_regions,
    get_strategic_goals,
    fetch_strategic_goals_departmental,
    fetch_kpis_departmental,
    manager_appraisal_view,
    create_user_view,
    superuser_dashboard,
    get_roles,
    kpi_tree_view,
    fetch_kpi_data,
    validate_login,
    fetch_employee_names_inheritance,
    fetch_employee_details_inheritance,
    fetch_sgs_kpis_del_dev,
    get_unique_industry,
    appraisal_page_view, 
    get_employee_status,
    get_mentees_by_reports_to_code,
    get_chat_messages,
    ai_recommendation_view,
    get_manager_code,
    review_periods,
    get_config_values,
    fetch_company_departments,
    create_multiple_questions,
    get_admin_employees,
    get_goals_by_employee_code,
    get_courses_by_employee_code,
    company_graph,
    chat_message_view,
    cascading_goals,
    retrieve_strategic_goals,
    fetch_common_employees,
    fetch_unmatched_employees,
    get_uoms,
    non_performance_reasons_view,
    get_assessments_by_employee,
    get_factor_descriptions,
    performa360_settings,
    performa360_main,

)

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('validate-login/', validate_login, name='validate_login'),
    path('dash_hr/', views.dash_hr, name='dash_hr'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Home & General Views
    path('', views.home_view, name='home'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

    # KPI Management
    path('kpi_scoring/', views.kpi_scoring, name='kpi_scoring'),
    path('enherit_kpis/', views.enherit_kpis, name='enherit_kpis'),
    path('evaluator_scoring/', views.evaluator_scoring_view, name='evaluator_scoring'),
    path('kpi-tree/', kpi_tree_view, name='kpi_tree'),
    path('eng_fedb/', views.eng_fedb, name='eng_fedb'),
    # Appraisals
    path('appraisal/', views.appraisal_view, name='appraisal'),
    path('self_appraisal/', views.self_appraisal_view, name='self_appraisal'),
    path('manager-appraisal/', manager_appraisal_view, name='manager_appraisal'),

    # Employee & User Data
    path('fetch-company-details/', views.fetch_company_details, name='fetch_company_details'),
    path('get_user_profile/<str:username>/', views.get_user_profile, name='get_user_profile'),
    path('get_employee_details/', views.get_employee_details, name='get_employee_details'),
    path('create_user/', create_user_view, name='create_user'),
    path('user_created_success/', views.user_created_success_view, name='user_created_success'),

    # Strategic Goals & KPI Data
    path('get_strategic_goals/', get_strategic_goals, name='get_strategic_goals'),
    path('get_kpis/', views.get_kpis_by_department, name='get_kpis'),
    path('get_deliverables/', views.get_deliverables_by_department, name='get_deliverables'),
    path('get_doc_evidence/', views.get_doc_evidence_by_department, name='get_doc_evidence'),
    path('api/kpi-data/<str:employee_name>/', views.fetch_kpi_data_by_employee, name='fetch_kpi_data_by_employee'),

    # Period & Reporting
    path('dash_staff/', views.dash_staff, name='dash_staff'),
    path('dash_exec/', views.dash_exec, name='dash_exec'),
    path('dash_partner/', views.dash_partner, name='dash_partner'),

    # Other Functionalities
    path('pdp/', views.pdp, name='pdp'),
    path('get-dropdown-data/', views.get_dropdown_data, name='get_dropdown_data'),

    # AJAX/API Endpoints
    
    path('get-roles/', get_roles, name='get_roles'),
    path('get_usernames/', views.get_usernames, name='get_usernames'),
    path('seek_company_code/', views.seek_company_code, name='seek_company_code'),

    path('fetch_employee_names/', views.fetch_employee_names, name='fetch_employee_names'),
    path('fetch_employee_details/', views.fetch_employee_details, name='fetch_employee_details'),
    path('fetch_kpi/', views.fetch_kpi, name='fetch_kpi'),
    path('fetch_deliverable/', views.fetch_deliverable, name='fetch_deliverable'),
    path('fetch_doc_evidence/', views.fetch_doc_evidence, name='fetch_doc_evidence'),
    path('fetch-strategic-goals-transversal/', views.fetch_strategic_goals_transversal, name='fetch_strategic_goals_transversal'),
    path('fetch-doc_evidence-transversal/', views.fetch_doc_evidence_transversal, name='fetch_doc_evidence_transversal'),
    path('fetch-kpis-transversal/', views.fetch_kpis_transversal, name='fetch_kpis_transversal'),
    path('fetch-deliverables-transversal/', views.fetch_deliverables_transversal, name='fetch_deliverables_transversal'),
    path('fetch_kpis/', fetch_kpis_departmental, name='fetch_kpis'),
    path('fetch_strategic_goals/', fetch_strategic_goals_departmental, name='fetch_strategic_goals'),
    path('report/', views.report_view, name='report'),
    path('dashboard/', superuser_dashboard, name='superuser_dashboard'),
    path('fetch-matching-values/', views.fetch_matching_values, name='fetch_matching_values'),
    path('fetch-matching-values-self/', views.fetch_matching_values_self, name='fetch_matching_values_self'),
    path('get-factor-description-self/', views.get_factor_description_self, name='get_factor_description_self'),
    path('fetch-matching-values-peer/', views.fetch_matching_values_peer, name='fetch_matching_values_peer'),
    path('get_factor_description_peer/', views.get_factor_description_peer, name='get_factor_description_peer'),
    path('fetch_matching_values_experience/', views.fetch_matching_values_experience, name='fetch_matching_values_experience'),
    path('get_factor_description_exprience/', views.get_factor_description_exprience, name='get_factor_description_exprience'),

    path('get_factor_description/', views.get_factor_description, name='get_factor_description'),
    path('fetch_kpi_data/', fetch_kpi_data, name='fetch_kpi_data'),
    path('dash_superuser/', views.dash_superuser, name='dash_superuser'),
    path('dash_mgmt/', views.dash_mgmt, name='dash_mgmt'),
    path('dash_dept/', views.dash_dept, name='dash_dept'),
    path('department/', views.department_dashboard, name='department_dashboard'),
    path("fetch_employee_names_inheritance/", fetch_employee_names_inheritance, name="fetch_employee_names_inheritance"),
    path('fetch_employee_details_inheritance/', fetch_employee_details_inheritance, name='fetch_employee_details_inheritance'),
    path('fetch_sgs_kpis_del_dev/', fetch_sgs_kpis_del_dev, name='fetch_sgs_kpis_del_dev'),
    path('get_subordinates/', views.get_subordinates, name='get_subordinates'),
    path('validate_login/', views.validate_login, name='validate_login'),
    path('appraisal/', views.appraisal_view, name='appraisal'),
    path('employee-appraisal/', views.employee_appraisal_view, name='employee_appraisal'),
    path('main/', views.main_view, name='main'),  # ✅ Ensure this exists
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),  # ✅ Correct logout URL
    path('self_appraisal.html', views.self_appraisal_view, name='self_appraisal'),
    path('evaluator-scoring/<str:username>/', views.evaluator_scoring_view, name='evaluator_scoring'),
    path('self-appraisal/', views.self_appraisal_view, name='self_appraisal'),
    path('get_unique_industry/', get_unique_industry, name='get_unique_industry'),
    path('get_user_profile/', views.get_user_profile, name='get_user_profile'),
    path('create_user/', views.create_user, name='create_user'),
    path('appraisal/', views.appraisal_view, name='appraisal'), 
    path('get_roles/', get_roles, name='get_roles'),
    path('setting/', views.setting_view, name='setting'), 
    path('appraisal/', appraisal_page_view, name='appraisal'),
    path('count-users/', views.count_users, name='count_users'),  # Add this line to link to the count_users view
    path('fetch-user-select/', views.fetch_user_select, name='fetch_user_select'),
    path('regions/', get_regions, name='get_regions'),
    path('get-departments/', views.get_departments, name='get_departments'),
    path('evaluate_management/', views.evaluate_management_view, name='evaluate_management'),
    path('get-employee-status/', get_employee_status, name='get_employee_status'),
    path('get_company_code/', views.get_company_code, name='get_company_code'),
    path('get-region-branch/', views.get_region_branch, name='get_region_branch'),


    path('send-message/', views.send_chat_message, name='send_chat_message'),
    path('get-mentees/', views.get_mentees, name='get_mentees'),
    path('get-manager/', views.get_manager_info, name='get_manager_info'),
    path('get_chat_messages/', get_chat_messages, name='get_chat_messages'),
    path('get-mentees-by-reports-to-code/', get_mentees_by_reports_to_code, name='get_mentees_by_reports_to_code'),
    path('api/assessment/', views.filter_by_employee_code, name='filter_by_employee_code'),
    path('api/get-surbodinate-code/', views.get_surbodinate_code, name='get_surbodinate_code'),
    path('self-appraisal-video/', views.video_page, name='video_page'),
    path("ai-recommendation/<str:employee_code>/", ai_recommendation_view, name="ai_recommendation"),
    path('get-manager-code/', get_manager_code, name='get_manager_code'),
    path('get_appraisal_chat_messages/', views.get_appraisal_chat_messages, name='get_appraisal_chat_messages'),
    path('send-appraisal-messages/', views.send_appraisal_messages, name='send_appraisal_messages'),
    path('upload-attachment/', views.upload_attachment, name='upload_attachment'),
    path('save-deliverable-comment/', views.save_deliverable_comment, name='save_deliverable_comment'),
    path('add_employee/', create_user, name='add_employee'),
    path('review-periods/', review_periods, name='review_periods'),
    path('get-config-values/', get_config_values, name='get_config_values'),
    path('fetch-company-departments/', fetch_company_departments, name='fetch_company_departments'),
    path('save-strategic-goals/', views.save_strategic_goals, name='save_strategic_goals'),
    path('retrieve_strategic_goals/', views.retrieve_strategic_goals, name='retrieve_strategic_goals'),
    path('submit-evaluation-questions/', create_multiple_questions, name='submit_evaluation_questions'),
   #path('save-company-login/', views.save_company_login, name='save_company_login'),
   path('save-login/', views.save_login, name='save__login'),
   path('populate-user-profiles/', views.populate_user_profiles, name='populate_user_profiles'),
   path('save-table-data/', views.save_table_data, name='save_table_data'),
   path('get-admin-employees/', get_admin_employees, name='get_admin_employees'),  # function-based view
   path('register_course/', views.register_course, name='register_course'),
   path('create_goal/', views.create_goal, name='create_goal'),
   path('get-region-branch/', views.get_region_branch, name='get_region_branch'),
   path('get_goals/', get_goals_by_employee_code, name='get_goals_by_employee_code'),
   path('get_courses/', get_courses_by_employee_code, name='get_courses_by_employee_code'),
   path('save-regions/', views.save_regions, name='save_regions'),
   path('get-regions/', views.get_regions_by_company, name='get_regions_by_company'),
   path('company-graph/', company_graph, name='company_graph'),
   path('dash_staff/', views.dash_staff, name='dash_staff'),
   path('generate-review-periods/', views.generate_review_periods, name='generate_review_periods'),
   path('chat/message/', chat_message_view, name='chat_message'),
   path('send-appraisee-message/', views.send_appraisee_message, name='send_appraisee_message'),
   path('get-active-login/', views.get_active_user_login, name='get_active_user_login'),
   path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
   path('setting/', views.setting, name='setting'),
   path('get-strategic-goals/', views.get_strategic_goals, name='get_strategic_goals'),
   path('cascading-goals/', cascading_goals, name='cascading_goals'),
   path('strategic-goals/', retrieve_strategic_goals, name='retrieve_strategic_goals'),
   path('fetch_common_employees/', fetch_common_employees, name='fetch_common_employees'),
   path('fetch_unmatched_employees/', fetch_unmatched_employees, name='fetch_unmatched_employees'),
   path('uoms/', get_uoms, name='get_uoms'),
   path('api/non-performance-reasons/', non_performance_reasons_view, name='non_performance_reasons'),
   path('get_employee_fields/', views.get_employee_fields, name='get_employee_fields'),
   path('get_subordinates/', views.get_subordinates, name='get_subordinates'),
   path('assessments/by-employee/', get_assessments_by_employee, name='get_assessments_by_employee'),
   path('dashboard/', views.management_dashboard, name='management_dashboard'),
   path('assessments/by-employee/', views.AssessmentsByEmployeeAPIView.as_view(), name='assessments_by_employee'),
   path('get_subordinates_by_reports_to/', views.get_subordinates_by_reports_to, name='get_subordinates_by_reports_to'),
   path('get_factor_descriptions/', get_factor_descriptions, name='get_factor_descriptions'),
   path('settings/application/', performa360_settings, name='settings'),
   path('main/application/', performa360_main, name='main'),
   path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
   path('settings_culture/', views.view_settings_culture, name='settings_culture'),
    path('policies/admin/', views.policies_admin, name='policies_admin'),
   path('leave/policy/', views.leave_policy, name='leave_policy'),
    
]

# Serve static/media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

