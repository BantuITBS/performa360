from django.http import JsonResponse
from django.db import connection
from .models import StrategicGoals
from django.views.decorators.http import require_GET
from .models import PerfMgmtAssessment
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, F, ExpressionWrapper, FloatField
from django.db.models.functions import Abs
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserCreationModel
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ReviewPeriod, Region, AppraisalMessage
from django.db import connection, OperationalError
import logging
import os  # Added to fix NameError
import json
from django.conf import settings  # Added for MEDIA_ROOT and MEDIA_URL
from django.contrib.auth import get_user_model
logger = logging.getLogger(__name__)
UserCreationModel = get_user_model()
import traceback
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .qa_engine import answer_question
# Third-party imports
import requests
from dateutil.relativedelta import relativedelta
from psycopg2 import OperationalError

# Django core imports
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.storage import default_storage
from django.db import (
    connection,
    transaction,
    IntegrityError,
    DatabaseError,
)
from django.db.models import (
    Avg,
    Count,
    F,
    Q,
    Sum,
    ExpressionWrapper,
    fields,
)
from django.db.models.functions import TruncMonth
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.middleware.csrf import get_token
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.template import RequestContext
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views import View
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

# Local application imports
from .forms import UserCreationForm
from .utils import get_ai_recommendation
from .models import (
    AIRecommendation,
    AppraisalMessage,
    ChatMessage,
    CompanyLogin,
    Course,
    EmpExFactorResults,
    EvaluateYourManager,
    EvaluateYourMgtSetting,
    EvaluateYourPeerResults,
    Goal,
    ManagerSelfEvaluationResults,
    PerfMgmtAssessment,
    PerfMgmtKpiDeliDoc,
    Region,
    ReviewPeriod,
    Role,
    SGSKPIsDelDev,
    StrategicGoals,
    UserCreationModel,
    UserLogin,
    UserProfile,
)


def populate_details(request):
    try:
        # Add the logic for populating details
        return JsonResponse({'message': 'Populate details endpoint works!'})
    except Exception as e:
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

def kpi_tree_view(request):
    return render(request, 'kpi_tree.html')

# This view will be used to show the success message after creating a user.
def user_created_success_view(request):
    # You can optionally add a success message
    messages.success(request, "The user has been created successfully!")
    # Return the template that shows the success message
    return render(request, 'user_created_success.html')

def get_departments(request):
    """Return a list of all departments (from Role model)."""
    departments = Role.objects.values_list('department_name', flat=True).distinct()
    return JsonResponse({"departments": list(departments)})

def get_roles(request):
    """Return a list of roles for a selected department from the Role model."""
    department_name = request.GET.get('department')
    if department_name:
        roles = Role.objects.filter(department_name=department_name).values_list('role_name', flat=True)
        return JsonResponse({"roles": list(roles)})
    return JsonResponse({"roles": []})

def sign_up(request):
    """Render the signup page."""
    return render(request, 'sign_up.html')

def self_appraisal_view(request):
    """Render the self-appraisal page."""
    return render(request, 'self_appraisal.html')

def signup_view(request):
    """Render the signup page."""
    return render(request, 'signup.html')  # Ensure 'signup.html' is the correct template name

def signup_modal_view(request):
    """Render the signup modal."""
    return render(request, 'sign_up.html')

def enherit_kpis(request):
    """Render the enherit_kpis page."""
    return render(request, 'enherit_kpis.html')

def home_view(request):
    """Render the main home page."""
    return render(request, 'main.html')  # Ensure 'main.html' is the correct template name

# Password view
class PasswordView(View):
    def get(self, request):
        return render(request, 'password.html')

# User login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('final_password')

        # Validate username against employee_name in UserCreationModel
        try:
            employee = UserCreationModel.objects.get(employee_name=username)
            user = authenticate(request, username=employee.company_code, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')  # Use Django messages
                return render(request, 'login.html')
        except UserCreationModel.DoesNotExist:
            messages.error(request, 'Invalid username or password')  # Handle user not found
            return render(request, 'login.html')

    return render(request, 'login.html')

# Validate login credentials
@require_GET
def validate_login(request):
    company_code = request.GET.get('company_code')
    username = request.GET.get('username')
    final_password = request.GET.get('final_password')

    try:
        employee = UserCreationModel.objects.get(
            company_code=company_code,
            employee_name=username,
            final_password=final_password
        )
        return JsonResponse({'valid': True})
    except UserCreationModel.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Invalid login credentials'})




def fetch_company_details(request):
    company_code = request.GET.get('company_code')
    try:
        company_details = UserProfile.objects.get(company_code=company_code)
        data = {
            'company': company_details.company,
            'country': company_details.country,
            'headquarters': company_details.headquarters,  # Changed key to headquarters
        }
        return JsonResponse(data)
    except UserCreationModel.DoesNotExist:
        return JsonResponse({'error': 'Company code not found'})




# Create user view for admin
def create_user_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # Using the correct form for user creation
        if form.is_valid():
            form.save()  # Save the new entry
            messages.success(request, "User was saved successfully.")  # Add success message
            return redirect('success_page')  # Redirect to a success page
    else:
        form = UserCreationForm()  # Create a blank form instance
    return render(request, 'create_user.html', {'form': form})

# Success page view
def success_page(request):
    return render(request, 'success.html')

# Create user view
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # Use the form class, not the model
        if form.is_valid():  # Check if the form is valid
            form.save()  # Save the new user
            messages.success(request, "User was saved successfully.")  # Add success message
            return redirect('success_url')  # Redirect to a success URL
    else:
        form = UserCreationForm()  # Create a blank form instance

    return render(request, 'create_user.html', {'form': form})  # Render the form

def appraisal_view(request):
    return render(request, 'appraisal.html')

def kpi_scoring(request):
    return render(request, 'kpi_scoring.html')


def get_user_profile(request):
    company_code = request.GET.get('company_code')  # Get the company_code from the query string
    
    if company_code:
        try:
            # Query the UserProfile model for the company_code
            user_profile = UserProfile.objects.get(company_code=company_code)
            
            # Return the data from the UserProfile as a JSON response
            data = {
                'company': user_profile.company,  # Use 'company' field here
                'country': user_profile.country,
                'headquarters': user_profile.headquarters,
                'exists': True
            }
            return JsonResponse(data)
        except UserProfile.DoesNotExist:
            # Return a response if no matching record is found
            return JsonResponse({'exists': False, 'message': 'Company not found'})
    else:
        # Return a response if no company_code is provided
        return JsonResponse({'exists': False, 'message': 'No company code provided'})

def render_template(request, template_name):
    return render(request, f'{template_name}.html')

# Usage
appraisal_view = lambda request: render_template(request, 'appraisal')
report_view = lambda request: render_template(request, 'report')
new_kpis_view = lambda request: render_template(request, 'new_kpis')
enherit_kpis_view = lambda request: render_template(request, 'enherit_kpis')
evaluator_scoring_view = lambda request: render_template(request, 'evaluator_scoring')
pdp_view = lambda request: render_template(request, 'pdp')
eng_fedb_view = lambda request: render_template(request, 'eng_fedb')


@require_GET  # Only allow GET requests
def fetch_kpi(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'error': 'No username provided.'}, status=400)

    # Fetch user KPIs based on the username directly from the database
    try:
        with connection.cursor() as cursor:
            query = '''
                SELECT kpi_number, kpi, deliverable, doc_evidence 
                FROM perf_mgmt_managekpis 
                WHERE username = %s
            '''
            cursor.execute(query, [username])
            rows = cursor.fetchall()

        # Process the fetched data
        kpis = {}
        for row in rows:
            kpi_number, kpi, deliverable, doc_evidence = row
            if kpi_number not in kpis:
                kpis[kpi_number] = {
                    "kpi": kpi,
                    "deliverables": []
                }
            kpis[kpi_number]["deliverables"].append({
                "deliverable": deliverable,
                "doc_evidence": doc_evidence
            })

        return JsonResponse({"kpis": kpis})

    except Exception as e:
        return JsonResponse({'error': f'An error occurred while fetching KPI data: {str(e)}'}, status=500)

def fetch_employee_name(request):
    username = request.GET.get('username')  # Get the username from the request

    try:
        # Execute a raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("SELECT employee_name FROM perf_mgmt_managekpis WHERE username = %s", [username])
            row = cursor.fetchone()  # Fetch one row

        if row:
            employee_name = row[0]  # Access the first column in the result
            return JsonResponse({'employee_name': employee_name})
        else:
            return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)


def check_username(request, username):
    try:
        with connection.cursor() as cursor:
            # Check if the user is registered and has permission
            cursor.execute(
                "SELECT manager_or_supervisor FROM user_creation_model WHERE username = %s",
                [username]
            )
            result = cursor.fetchone()
            
            if not result:
                return JsonResponse({'message': "Username not registered"}, status=404)
            
            manager_or_supervisor = result[0]
            if manager_or_supervisor == "No":
                return JsonResponse({'message': "You don't have permission to assign KPIs"}, status=403)

            # Fetch all employee names associated with the user
            cursor.execute(
                "SELECT employee_name FROM perf_mgmt_user_creation_model WHERE username = %s",
                [username]
            )
            employee_names = [row[0] for row in cursor.fetchall()]

        return JsonResponse({'employee_names': employee_names})

    except Exception as e:
        return JsonResponse({'message': f"Error: {str(e)}"}, status=500)

def get_employee_details(request):
    try:
        # Extract the `employee_name` parameter from the query string
        employee_name = request.GET.get('employee_name', None)

        if not employee_name:
            return JsonResponse({'message': "Employee name is required"}, status=400)

        # Define the SQL query to fetch the employee details
        query = """
            SELECT department, region_branch, position
            FROM user_creation_model
            WHERE employee_name = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [employee_name])
            row = cursor.fetchone()

        if row:
            data = {
                'department': row[0],        # department
                'region_branch': row[1],    # region_branch
                'position': row[2],         # position
            }
        else:
            return JsonResponse({'message': "Employee not found"}, status=404)

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'message': f"Error: {str(e)}"}, status=500)

    
def get_dropdown_data(request):
    strategic_goals = PerfMgmtKpiDeliDoc.objects.values_list('strategic_goal', flat=True).distinct()
    selected_strategic_goal = request.GET.get('strategic_goal')
    
    if selected_strategic_goal:
        kpis = PerfMgmtKpiDeliDoc.objects.filter(strategic_goal=selected_strategic_goal).values_list('kpi', flat=True).distinct()
        selected_kpi = request.GET.get('kpi')
        
        if selected_kpi:
            deliverables = PerfMgmtKpiDeliDoc.objects.filter(
                strategic_goal=selected_strategic_goal,
                kpi=selected_kpi
            ).values_list('deliverable', flat=True).distinct()
            
            selected_deliverable = request.GET.get('deliverable')
            
            if selected_deliverable:
                doc_evidences = PerfMgmtKpiDeliDoc.objects.filter(
                    strategic_goal=selected_strategic_goal,
                    kpi=selected_kpi,
                    deliverable=selected_deliverable
                ).values_list('doc_evidence', flat=True).distinct()
                return render(request, 'dropdowns.html', {
                    'doc_evidences': doc_evidences,
                })
            
            return render(request, 'dropdowns.html', {
                'deliverables': deliverables,
            })
        return render(request, 'dropdowns.html', {
            'kpis': kpis,
        })
    return render(request, 'dropdowns.html', {
        'strategic_goals': strategic_goals,
    })


# View to fetch KPIs, Deliverables, Document Evidence, and Strategic Goals based on department
def get_kpis_by_department(request):
    if request.method == 'GET':
        try:
            department = request.GET.get('department', None)

            if not department:
                return JsonResponse({'error': 'Department is required.'}, status=400)

            # Query to fetch KPIs related to the department
            kpi_query = """
                SELECT DISTINCT kpi, deliverable, doc_evidence
                FROM perf_mgmt_managekpis
                WHERE department = %s
            """
            
            # Query to fetch Strategic Goals for the department
            strategic_goal_query = """
                SELECT DISTINCT kpi, strategic_goal
                FROM perf_mgmt_kpi_deli_doc
                WHERE department = %s
            """

            # Query to fetch Deliverables and Document Evidence for the department
            deliverable_doc_evidence_query = """
                SELECT DISTINCT deliverable, doc_evidence
                FROM perf_mgmt_managekpis
                WHERE department = %s
            """

            with connection.cursor() as cursor:
                # Fetch KPIs, Deliverable, and Doc Evidence for the department
                cursor.execute(kpi_query, [department])
                kpi_results = cursor.fetchall()

                # Fetch Strategic Goals for the department
                cursor.execute(strategic_goal_query, [department])
                strategic_goal_results = cursor.fetchall()

                # Fetch Deliverables and Document Evidence for the department
                cursor.execute(deliverable_doc_evidence_query, [department])
                deliverable_doc_evidence_results = cursor.fetchall()

            if kpi_results:
                # Structure KPI data into a hierarchical format
                hierarchical_data = {}
                for row in kpi_results:
                    kpi = row[0]
                    deliverable = row[1]
                    doc_evidence = row[2]

                    if kpi not in hierarchical_data:
                        hierarchical_data[kpi] = {
                            'deliverables': {},
                        }

                    if deliverable:
                        if deliverable not in hierarchical_data[kpi]['deliverables']:
                            hierarchical_data[kpi]['deliverables'][deliverable] = []

                        if doc_evidence:
                            hierarchical_data[kpi]['deliverables'][deliverable].append(doc_evidence)

                # Format the hierarchical data for KPIs and Deliverables
                response_data = []
                for kpi, deliverables in hierarchical_data.items():
                    deliverables_list = []
                    for deliverable, doc_evidences in deliverables['deliverables'].items():
                        deliverables_list.append({
                            'deliverable': deliverable,
                            'doc_evidences': doc_evidences,
                        })

                    response_data.append({
                        'kpi': kpi,
                        'deliverables': deliverables_list,
                    })

                # Structure Strategic Goals data for the department
                strategic_goals = {}
                for row in strategic_goal_results:
                    kpi = row[0]
                    strategic_goal = row[1]

                    if kpi not in strategic_goals:
                        strategic_goals[kpi] = []

                    strategic_goals[kpi].append(strategic_goal)

                # Combine response data with strategic goals
                for kpi_entry in response_data:
                    kpi_value = kpi_entry['kpi']
                    if kpi_value in strategic_goals:
                        kpi_entry['strategic_goals'] = strategic_goals[kpi_value]

                # Structure Deliverables and Document Evidence for the department
                deliverables_data = []
                for row in deliverable_doc_evidence_results:
                    deliverable = row[0]
                    doc_evidence = row[1]

                    deliverables_data.append({
                        'deliverable': deliverable,
                        'doc_evidences': doc_evidence,
                    })

                # Prepare the response with KPIs, Deliverables, Document Evidence, and Strategic Goals
                return JsonResponse({
                    'data': response_data,
                    'strategic_goals': list(set([goal for row in strategic_goal_results for goal in row[1:]])),
                    'deliverables_data': deliverables_data,
                })

            else:
                # If no results found, return an error response
                return JsonResponse({'error': 'No KPIs found for the specified department.'}, status=404)

        except Exception as e:
            # Return error response if there is an exception
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed.'}, status=405)


def fetch_kpi_data_by_employee(request, employee_name):
    """
    Fetch distinct KPI, deliverable, document evidence, and strategic goals
    based on the employee_name and department, and structure the response.
    """
    try:
        # Extract department from the request (assuming it's passed as a query parameter)
        department = request.GET.get('department', None)
        if not department:
            return JsonResponse({'error': 'Department is required.'}, status=400)

        # Query to fetch distinct KPI, deliverable, and document evidence
        kpi_query = """
            SELECT DISTINCT kpi, deliverable, doc_evidence
            FROM perf_mgmt_managekpis
            WHERE employee_name = %s AND department = %s
        """
        
        # Query to fetch strategic goals from the perf_mgmt_kpi_deli_doc table
        strategic_goal_query = """
            SELECT DISTINCT kpi, strategic_goal
            FROM perf_mgmt_kpi_deli_doc
            WHERE department = %s
        """

        with connection.cursor() as cursor:
            # Fetch KPI, Deliverable, and Doc Evidence
            cursor.execute(kpi_query, [employee_name, department])
            kpi_results = cursor.fetchall()

            # Fetch Strategic Goals from perf_mgmt_kpi_deli_doc table
            cursor.execute(strategic_goal_query, [department])
            strategic_goal_results = cursor.fetchall()

        if kpi_results:
            # Structure KPI data into a hierarchical format
            hierarchical_data = {}
            for row in kpi_results:
                kpi = row[0]
                deliverable = row[1]
                doc_evidence = row[2]

                if kpi not in hierarchical_data:
                    hierarchical_data[kpi] = {
                        'deliverables': {},
                    }

                if deliverable:
                    if deliverable not in hierarchical_data[kpi]['deliverables']:
                        hierarchical_data[kpi]['deliverables'][deliverable] = []

                    if doc_evidence:
                        hierarchical_data[kpi]['deliverables'][deliverable].append(doc_evidence)

            # Format the hierarchical data for JSON response
            response_data = []
            for kpi, deliverables in hierarchical_data.items():
                deliverables_list = []
                for deliverable, doc_evidences in deliverables['deliverables'].items():
                    deliverables_list.append({
                        'deliverable': deliverable,
                        'doc_evidences': doc_evidences,
                    })

                response_data.append({
                    'kpi': kpi,
                    'deliverables': deliverables_list,
                })

            # Structure Strategic Goals data
            strategic_goals = {}
            for row in strategic_goal_results:
                kpi = row[0]
                strategic_goal = row[1]

                if kpi not in strategic_goals:
                    strategic_goals[kpi] = []

                strategic_goals[kpi].append(strategic_goal)

            # Combine response data with strategic goals
            for kpi_entry in response_data:
                kpi_value = kpi_entry['kpi']
                if kpi_value in strategic_goals:
                    kpi_entry['strategic_goals'] = strategic_goals[kpi_value]

            # Prepare the list for 'Strategic goal:' dropdown (with all available goals)
            all_strategic_goals = list(set([goal for row in strategic_goal_results for goal in row[1:]]))

            # Include the list of all strategic goals in the response
            return JsonResponse({
                'data': response_data,
                'strategic_goals': all_strategic_goals,
            })

        else:
            # If no results found, return an error response
            return JsonResponse({'error': 'No data found for the specified employee and department.'}, status=404)

    except Exception as e:
        # Return error response if there is an exception
        return JsonResponse({'error': str(e)}, status=500)

def sign_up(request):
    return render(request, 'sign_up.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def terms_and_conditions(request):
    current_date = datetime.now().strftime('%B %d, %Y')  # Example format: November 13, 2024
    return render(request, 'terms_and_conditions.html', {'current_date': current_date})

# Create your views here.

def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user to the database
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')  # Redirect to the login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()  # Empty form for GET request
    
    return render(request, 'sign_up.html', {'form': form})


def sign_up(request):
    # Create the employee range list
    employee_ranges = [(i, i + 49) for i in range(0, 10050, 50)]
    
    return render(request, 'sign_up.html', {'employee_ranges': employee_ranges})


def appraisal_view(request):
    return render(request, 'appraisal.html')





def main_view(request):
    return render(request, 'main.html')  # ✅ Ensure 'main.html' exists in templates
    


def employee_appraisal_view(request):
    username = request.GET.get('username', '')  # Get username from query parameters

    # Store username in session
    if username:
        request.session['username'] = username

    # Retrieve the stored username from session
    stored_username = request.session.get('username', 'Guest')

    return render(request, 'appraisal.html', {'username': stored_username})

def evaluator_scoring_view(request, username=None):
    if username is None:
        username = request.user.username
    return render(request, 'evaluator_scoring.html', {'username': username})

def self_appraisal_view(request):
    username = request.session.get('username', 'Guest')
    return render(request, 'self_appraisal.html', {'username': username})


def create_user_view(request):
    username = request.session.get('username', 'Guest')
    return render(request, 'create_user.html', {'username': username})


@csrf_exempt
def get_unique_industry(request):
    """
    Retrieve a list of unique industries from the Role model.
    Accepts GET or POST requests and returns a JSON array of industries.
    """
    try:
        # Fetch unique industries from Role model
        unique_industries = list(Role.objects.values_list('industry', flat=True).distinct())
        
        # Check if the result is empty
        if not unique_industries:
            logger.warning("No industries found in Role model")
            return JsonResponse({
                'status': 'success',
                'industries': [],
                'message': 'No industries available'
            }, status=200)
        
        # Return the industry list
        return JsonResponse(unique_industries, safe=False, status=200)
    
    except ObjectDoesNotExist:
        logger.error("Role model does not exist")
        return JsonResponse({
            'status': 'error',
            'message': 'Role model not found'
        }, status=500)
    except Exception as e:
        logger.error(f"Error fetching industries: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


def sign_up(request):
    return render(request, 'sign_up.html')

def validate_parameters(company_code, company, employee_name, employee_code):
    """Ensure at least company_code and company or employee_name and employee_code are provided."""
    if not ((company_code and company) or (employee_name and employee_code)):
        return {'error': "Either Company Code and Company or Employee Name and Employee Code are required."}
    return None  # No validation errors

def validate_company(cursor, company_code):
    """Check if company_code exists in perf_mgmt_userprofile and fetch company details."""
    query = """
        SELECT company, headquarters, country FROM perf_mgmt_userprofile 
        WHERE company_code = %s
    """
    cursor.execute(query, [company_code])
    return cursor.fetchone()  # Returns (company, headquarters, country) if found

def validate_employee(cursor, employee_name, employee_code):
    """Retrieve company_code for the given employee_name and employee_code."""
    query = """
        SELECT company_code FROM perf_mgmt_user_creation_model 
        WHERE employee_name = %s AND employee_code = %s
    """
    cursor.execute(query, [employee_name, employee_code])
    result = cursor.fetchone()  # Returns (company_code,) if found
    return result[0] if result else None  # Extract company_code if found

def validate_login(request):
    """Validate login credentials."""
    company_code = request.GET.get("company_code")
    company = request.GET.get("company")  
    employee_name = request.GET.get("employee_name")
    employee_code = request.GET.get("employee_code")

    # Debug Log
    print(f"Company Code: {company_code}, Company: {company}, Employee Name: {employee_name}, Employee Code: {employee_code}")

    validation_error = validate_parameters(company_code, company, employee_name, employee_code)
    if validation_error:
        return JsonResponse(validation_error)

    response_data = {'valid': False, 'error': "Access denied."}

    with connection.cursor() as cursor:
        try:
            # Step 1: Check if company_code and company are provided
            if company_code and company:
                company_result = validate_company(cursor, company_code)
                if not company_result:
                    response_data['error'] = "Company details not found."
                    return JsonResponse(response_data)
            # Step 2: If not, validate employee and get company_code
            elif employee_name and employee_code:
                company_code = validate_employee(cursor, employee_name, employee_code)
                if not company_code:
                    response_data['error'] = "Invalid employee name or employee code."
                    return JsonResponse(response_data)
                company_result = validate_company(cursor, company_code)
                if not company_result:
                    response_data['error'] = "Company details not found."
                    return JsonResponse(response_data)
            else:
                response_data['error'] = "Either Company Code and Company or Employee Name and Employee Code are required."
                return JsonResponse(response_data)

            # Extract company details
            company, headquarters, country = company_result

            # Step 3: Return success response
            response_data = {
                'valid': True,
                'company': company,
                'headquarters': headquarters,
                'country': country
            }

        except Exception as e:
            response_data['error'] = f"Database error: {str(e)}"
            print("Error:", e)

    return JsonResponse(response_data)


def fetch_kpi_data(request):
    # Fetch data from the PerfMgmtKpiDeliDoc table
    kpis = PerfMgmtKpiDeliDoc.objects.all().values('kpi', 'deliverable', 'doc_evidence', 'strategic_goal')  
    # Return the data as JSON
    return JsonResponse(list(kpis), safe=False)

def appraisal(request):
    profile_image = request.session.get('profile_image', 'admin/img/ai_bg.png')
    return render(request, 'appraisal.html', {'profile_image': profile_image})


def kpi_tree_view(request):
    if request.method == 'GET':
        # Fetch KPI tree data from database or other data source
        kpi_tree_data = []  # Replace with actual data

        return render(request, 'kpi_tree.html', {'kpi_tree_data': kpi_tree_data})

    elif request.method == 'POST':
        # Handle form submissions or other POST requests
        pass

    return JsonResponse({'error': 'Invalid request method'})


def manager_appraisal(request):
    return render(request, 'manager_appraisal.html')

def get_roles(request):
    department_name = request.GET.get('department_name')
    
    if department_name:
        # Fetch roles associated with the selected department
        roles = Role.objects.filter(department_name=department_name).values_list('role_name', flat=True)
        
        if roles:
            return JsonResponse({'roles': list(roles)})
        else:
            return JsonResponse({'roles': []}, status=404)  # Return empty list if no roles are found
    
    return JsonResponse({'roles': []})  # Return empty roles if no department specified


def get_departments(request):
    # Fetch unique departments from the Role model
    departments = Role.objects.values_list('department_name', flat=True).distinct()
    return JsonResponse({'departments': list(departments)})



def get_usernames(request):
    try:
        manager_name = request.GET.get('manager_name')
        if manager_name:
            employee_names = UserCreationModel.objects.filter(manager_name=manager_name).values_list('employee_name', flat=True).distinct()
            return JsonResponse(list(employee_names), safe=False)
        return JsonResponse({'error': 'Manager name is required'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


def get_employee_details(request): 
    try:
        employee_code = request.GET.get('employee_code')
        if not employee_code:
            return JsonResponse({'error': 'Employee code is required'}, status=400)

        # Fetch department, position, and company_code from UserCreationModel
        employee = UserCreationModel.objects.filter(employee_code=employee_code).values(
            'department', 'position', 'company_code'
        ).first()

        if not employee:
            return JsonResponse({'error': 'Employee details not found'}, status=404)

        # Fetch company, country, and headquarters from UserProfile using company_code
        profile = UserProfile.objects.filter(company_code=employee['company_code']).values(
            'company', 'country', 'headquarters'
        ).first()

        if not profile:
            return JsonResponse({'error': 'Company details not found'}, status=404)

        # Combine results
        response_data = {
            'department': employee['department'],
            'position': employee['position'],
            'company': profile['company'],
            'country': profile['country'],
            'headquarters': profile['headquarters'],
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_strategic_goals(request):
    department = request.GET.get('department', '').strip()  # Get the department from the GET request
    
    if department:
        with connection.cursor() as cursor:
            query = """
                SELECT id, strategic_goal
                FROM perf_mgmt_kpi_deli_doc
                WHERE LOWER(department) = LOWER(%s)
            """
            cursor.execute(query, [department])
            results = cursor.fetchall()
            goals_data_list = [{"id": row[0], "strategic_goal": row[1]} for row in results]
    else:
        goals_data_list = []  # Return an empty list if no department is provided
    
    return JsonResponse({'strategic_goals': goals_data_list})


def get_kpis_by_department(request):
    department = request.GET.get('department', '').strip()  

    if department:
        kpis_data_list = list(PerfMgmtKpiDeliDoc.objects.filter(department__iexact=department).values_list('kpi', flat=True).distinct())
        kpis_data_list = [{"kpi": kpi} for kpi in kpis_data_list]
    else:
        kpis_data_list = []  

    return JsonResponse({'kpis': kpis_data_list})


def get_deliverables_by_department(request):
    department = request.GET.get('department', '').strip()

    if department:
        deliverables_data_list = list(PerfMgmtKpiDeliDoc.objects.filter(department__iexact=department).values_list('deliverable', flat=True).distinct())
        deliverables_data_list = [{"deliverable": deliverable} for deliverable in deliverables_data_list]
    else:
        deliverables_data_list = []

    return JsonResponse({'deliverables': deliverables_data_list})


def get_doc_evidence_by_department(request):
    department = request.GET.get('department', '').strip()

    if department:
        doc_evidence_data_list = list(PerfMgmtKpiDeliDoc.objects.filter(department__iexact=department).values_list('doc_evidence', flat=True).distinct())
        doc_evidence_data_list = [{"doc_evidence": doc_evidence} for doc_evidence in doc_evidence_data_list]
    else:
        doc_evidence_data_list = []

    return JsonResponse({'doc_evidence': doc_evidence_data_list})


def pdp(request):
    return render(request, 'pdp.html')

def eng_fedb(request):
    return render(request, 'eng_fedb.html')

def dash_staff(request):
    return render(request, 'dash_staff.html')

def dash_hr(request):
    return render(request, 'dash_hr.html')

def dash_exec(request):
    return render(request, 'dash_exec.html')

def dash_mngt(request):
    return render(request, 'dash_mngt.html')

def dash_partner(request):
    return render(request, 'dash_partner.html')

def sign_up(request):
    return render(request, 'sign_up.html')



from .models import SGSKPIsDelDev

from django.http import JsonResponse
from django.views.decorators.http import require_GET
import traceback
from .models import SGSKPIsDelDev

@require_GET
def get_strategic_goals(request):
    employee_code = request.GET.get('employee_code', '').strip()

    if not employee_code:
        return JsonResponse({'error': 'Missing employee_code'}, status=400)

    try:
        strategic_goals = SGSKPIsDelDev.objects.filter(
            employee_code=employee_code
        ).values_list('strategic_goal', flat=True).distinct()

        if not strategic_goals:
            return JsonResponse({'error': 'Employee not found or no strategic goals'}, status=404)

        response_data = []

        for strategic_goal in strategic_goals:
            if not strategic_goal:
                continue

            goal_record = SGSKPIsDelDev.objects.filter(
                employee_code=employee_code,
                strategic_goal=strategic_goal
            ).values(
                'strategic_goal_number',
                'strategic_goal_due_date',
                'strategic_goal_weight'
            ).first()

            if not goal_record:
                continue

            goal_data = {
                'strategic_goal': strategic_goal,
                'strategic_goal_number': goal_record['strategic_goal_number'],
                'strategic_goal_due_date': (
                    goal_record['strategic_goal_due_date'].isoformat()
                    if goal_record['strategic_goal_due_date'] else None
                ),
                'strategic_goal_weight': goal_record['strategic_goal_weight'],
                'kpis': []
            }

            kpis = SGSKPIsDelDev.objects.filter(
                employee_code=employee_code,
                strategic_goal=strategic_goal
            ).values_list('kpi', flat=True).distinct()

            for kpi in kpis:
                if not kpi:
                    continue

                kpi_record = SGSKPIsDelDev.objects.filter(
                    employee_code=employee_code,
                    strategic_goal=strategic_goal,
                    kpi=kpi
                ).values(
                    'kpi_number',
                    'kpi_due_date',
                    'kpi_weight',
                    'short_term_target',
                    'intermediate_term_target',
                    'long_term_target',
                    'uom',
                    'short_term_actual',
                    'intermediate_term_actual',
                    'long_term_actual'
                ).first()

                if not kpi_record:
                    continue

                kpi_data = {
                    'kpi': kpi,
                    'kpi_number': kpi_record['kpi_number'],
                    'kpi_due_date': (
                        kpi_record['kpi_due_date'].isoformat()
                        if kpi_record['kpi_due_date'] else None
                    ),
                    'kpi_weight': kpi_record['kpi_weight'],
                    'short_term_target': kpi_record['short_term_target'],
                    'intermediate_term_target': kpi_record['intermediate_term_target'],
                    'long_term_target': kpi_record['long_term_target'],
                    'uom': kpi_record['uom'],
                    'short_term_actual': kpi_record['short_term_actual'],
                    'intermediate_term_actual': kpi_record['intermediate_term_actual'],
                    'long_term_actual': kpi_record['long_term_actual'],
                    'deliverables': []
                }

                deliverables = SGSKPIsDelDev.objects.filter(
                    employee_code=employee_code,
                    strategic_goal=strategic_goal,
                    kpi=kpi
                ).values_list('deliverable', flat=True).distinct()

                for deliverable in deliverables:
                    if not deliverable:
                        continue

                    deliv_record = SGSKPIsDelDev.objects.filter(
                        employee_code=employee_code,
                        strategic_goal=strategic_goal,
                        kpi=kpi,
                        deliverable=deliverable
                    ).values(
                        'deliverable_number',
                        'deliverable_due_date',
                        'deliverable_weight'
                    ).first()

                    if not deliv_record:
                        continue

                    deliverable_data = {
                        'deliverable': deliverable,
                        'deliverable_number': deliv_record['deliverable_number'],
                        'deliverable_due_date': (
                            deliv_record['deliverable_due_date'].isoformat()
                            if deliv_record['deliverable_due_date'] else None
                        ),
                        'deliverable_weight': deliv_record['deliverable_weight'],
                        'doc_evidence': []
                    }

                    doc_evidence = SGSKPIsDelDev.objects.filter(
                        employee_code=employee_code,
                        strategic_goal=strategic_goal,
                        kpi=kpi,
                        deliverable=deliverable
                    ).values_list('doc_evidence', flat=True).distinct()

                    for doc in doc_evidence:
                        if not doc:
                            continue

                        doc_record = SGSKPIsDelDev.objects.filter(
                            employee_code=employee_code,
                            strategic_goal=strategic_goal,
                            kpi=kpi,
                            deliverable=deliverable,
                            doc_evidence=doc
                        ).values(
                            'doc_evidence_number',
                            'doc_evidence_due_date',
                            'doc_evidence_weight'
                        ).first()

                        if not doc_record:
                            continue

                        doc_data = {
                            'doc_evidence': doc,
                            'doc_evidence_number': doc_record['doc_evidence_number'],
                            'doc_evidence_due_date': (
                                doc_record['doc_evidence_due_date'].isoformat()
                                if doc_record['doc_evidence_due_date'] else None
                            ),
                            'doc_evidence_weight': doc_record['doc_evidence_weight'],
                        }

                        deliverable_data['doc_evidence'].append(doc_data)

                    kpi_data['deliverables'].append(deliverable_data)

                goal_data['kpis'].append(kpi_data)

            response_data.append(goal_data)

        return JsonResponse({'strategic_goals': response_data}, status=200)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)

def seek_company_code(request):
    try:
        username = request.GET.get('username', '').strip()
        if not username:
            return JsonResponse({'error': 'Security clearance required'}, status=403)  # Changed to 403 Forbidden

        with connection.cursor() as cursor:
            # Parameterized query with exact schema
            cursor.execute("""
                SELECT company_code 
                FROM public.public.perf_mgmt_user_creation_model 
                WHERE LOWER(employee_name) = LOWER(%s)
                LIMIT 1
            """, [username])
            
            result = cursor.fetchone()

        if result:
            return JsonResponse({
                'company_code': result[0],
                'security_level': 'Tier3'  # Add authorization tier
            })
        else:
            return JsonResponse({'error': 'Identity not in registry'}, status=401)  # 401 Unauthorized

    except OperationalError as oe:
        logger.critical(f"Database breach attempt: {str(oe)}")
        return JsonResponse({'error': 'Security lockdown engaged'}, status=503)
    
    except Exception as e:
        logger.error(f"Protocol violation: {traceback.format_exc()}")
        return JsonResponse({'error': 'Terminal system failure'}, status=500)



def fetch_matching_values(request):
    company_code = request.GET.get('company_code', '').strip()
    if not company_code:
        return JsonResponse({'error': 'Company code is required'}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT factor_type 
                FROM perf_mgmt_evaluateyourmgtsetting 
                WHERE company_code = %s
            """, [company_code])
            result = cursor.fetchall()

        if result:
            data = [{"factor_type": row[0]} for row in result]
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'No matching values found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_factor_description(request):
    company_code = request.GET.get('company_code', '').strip()
    factor_type = request.GET.get('factor_type', '').strip()
    
    if not company_code or not factor_type:
        return JsonResponse({'error': 'Both parameters required'}, status=400)

    with connection.cursor() as cursor:
        # Get all unique descriptions for the factor_type
        cursor.execute("""
            SELECT DISTINCT description 
            FROM public.perf_mgmt_evaluateyourmgtsetting 
            WHERE company_code = %s 
            AND factor_type = %s
        """, [company_code, factor_type])

        results = cursor.fetchall()

    if results:
        # Extract descriptions from tuple results
        descriptions = [desc[0] for desc in results]
        return JsonResponse({'descriptions': descriptions}, safe=False)
    else:
        return JsonResponse({'error': 'No descriptions found'}, status=404)




def fetch_matching_values_self(request):
    company_code = request.GET.get('company_code', '').strip()
    if not company_code:
        return JsonResponse({'error': 'Company code is required'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT factor_type 
            FROM perf_mgmt_managerselfevaluationsetting
            WHERE company_code = %s
        """, [company_code])

        result = cursor.fetchall()

    if result:
        data = [{"factor_type": value[0]} for value in result]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'No matching values found'}, status=404)


def get_factor_description_self(request):
    company_code = request.GET.get('company_code', '').strip()
    factor_type = request.GET.get('factor_type', '').strip()
    
    if not company_code or not factor_type:
        return JsonResponse({'error': 'Both parameters required'}, status=400)

    with connection.cursor() as cursor:
        # Get all unique descriptions for the factor_type
        cursor.execute("""
            SELECT DISTINCT description 
            FROM perf_mgmt_managerselfevaluationsetting 
            WHERE company_code = %s 
            AND factor_type = %s
        """, [company_code, factor_type])

        results = cursor.fetchall()

    if results:
        # Extract descriptions from tuple results
        descriptions = [desc[0] for desc in results]
        return JsonResponse({'descriptions': descriptions}, safe=False)
    else:
        return JsonResponse({'error': 'No descriptions found'}, status=404)

def fetch_matching_values_peer(request):
    company_code = request.GET.get('company_code', '').strip()
    if not company_code:
        return JsonResponse({'error': 'Company code is required'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT factor_type 
            FROM public.perf_mgmt_evaluateyourpeersetting
            WHERE company_code = %s
        """, [company_code])

        result = cursor.fetchall()

    if result:
        data = [{"factor_type": value[0]} for value in result]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'No matching values found'}, status=404)


def get_factor_description_peer(request):
    company_code = request.GET.get('company_code', '').strip()
    factor_type = request.GET.get('factor_type', '').strip()
    
    if not company_code or not factor_type:
        return JsonResponse({'error': 'Both parameters required'}, status=400)

    with connection.cursor() as cursor:
        # Get all unique descriptions for the factor_type
        cursor.execute("""
            SELECT DISTINCT description 
            FROM public.perf_mgmt_evaluateyourpeersetting
            WHERE company_code = %s 
            AND factor_type = %s
        """, [company_code, factor_type])

        results = cursor.fetchall()

    if results:
        # Extract descriptions from tuple results
        descriptions = [desc[0] for desc in results]
        return JsonResponse({'descriptions': descriptions}, safe=False)
    else:
        return JsonResponse({'error': 'No descriptions found'}, status=404)




def fetch_matching_values_experience(request):
    company_code = request.GET.get('company_code', '').strip()
    if not company_code:
        return JsonResponse({'error': 'Company code is required'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT factor_type 
            FROM public.perf_mgmt_empexfactorsetting
            WHERE company_code = %s
        """, [company_code])

        result = cursor.fetchall()

    if result:
        data = [{"factor_type": value[0]} for value in result]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'No matching values found'}, status=404)


def get_factor_description_exprience(request):
    company_code = request.GET.get('company_code', '').strip()
    factor_type = request.GET.get('factor_type', '').strip()
    
    if not company_code or not factor_type:
        return JsonResponse({'error': 'Both parameters required'}, status=400)

    with connection.cursor() as cursor:
        # Get all unique descriptions for the factor_type
        cursor.execute("""
            SELECT DISTINCT description 
            FROM public.perf_mgmt_empexfactorsetting
            WHERE company_code = %s 
            AND factor_type = %s
        """, [company_code, factor_type])

        results = cursor.fetchall()

    if results:
        # Extract descriptions from tuple results
        descriptions = [desc[0] for desc in results]
        return JsonResponse({'descriptions': descriptions}, safe=False)
    else:
        return JsonResponse({'error': 'No descriptions found'}, status=404)



def fetch_employee_names(request):
    reports_to_code = request.GET.get('reports_to_code')
    if reports_to_code is None:
        return JsonResponse({'error': 'reports_to_code parameter is required'}, status=400)
    
    try:
        employee_names = list(UserCreationModel.objects.filter(reports_to_code=reports_to_code).values_list('employee_name', flat=True))
        return JsonResponse(employee_names, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def fetch_employee_details(request):
    employee_name = request.GET.get('employee_name')
    try:
        employee_details = UserCreationModel.objects.get(employee_name=employee_name)
        company_code = employee_details.company_code
        region_branch_details = UserProfile.objects.get(company_code=company_code)
        data = {
            'department': employee_details.department,
            'region_branch': region_branch_details.region_branch,
            'position': employee_details.position
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except UserCreationModel.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'Employee not found'}), content_type='application/json', status=404)


def fetch_strategic_goals_departmental(request):
    # Get the department parameter from the GET request
    department = request.GET.get('department')

    if not department:
        return JsonResponse({'error': 'Department parameter is missing'}, status=400)

    # Query your database for strategic goals based on the department
    try:
        strategic_goals = get_strategic_goals_for_department(department)
        return JsonResponse(strategic_goals, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_strategic_goals_for_department(department):
    try:
        # Case-insensitive query if necessary
        strategic_goals = PerfMgmtKpiDeliDoc.objects.filter(Q(department__iexact=department)).values_list('strategic_goal', flat=True).distinct()
        return list(strategic_goals)
    except Exception as e:
        raise Exception(f"Error fetching strategic goals: {str(e)}")
    

def fetch_kpis_departmental(request):
    # Get the department parameter from the GET request
    department = request.GET.get('department')

    if not department:
        return JsonResponse({'error': 'Department parameter is missing'}, status=400)

    # Query your database for KPI values based on the department
    try:
        kpis = get_kpis_for_department(department)
        return JsonResponse(kpis, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_kpis_for_department(department):
    try:
        # Case-insensitive query if necessary
        kpis = PerfMgmtKpiDeliDoc.objects.filter(Q(department__iexact=department)).values_list('kpi', flat=True).distinct()
        return list(kpis)
    except Exception as e:
        raise Exception(f"Error fetching KPIs: {str(e)}")


def manager_appraisal_view(request):
    return render(request, 'manager_appraisal.html')

def create_user_view(request):
    return render(request, 'create_user.html')  # Ensure this template exists

def dash_hr(request):
    return render(request, 'dash_hr.html')  # Ensure this template exists

def eng_fedb(request):
    return render(request, 'eng_fedb.html')  # Replace 'your_template.html' with the actual template name

def dash_superuser(request):
    return render(request, 'dash_superuser.html')  # Replace 'your_template.html' with the actual template name

def dash_mgmt(request):
    return render(request, 'dash_mgmt.html')  # Replace 'your_template.html' with the actual template name

def dash_dept(request):
    return render(request, 'dash_dept.html')  # Replace 'your_template.html' with the actual template name


def fetch_kpi(request):
    department = request.GET.get('department')
    kpi = list(set(PerfMgmtKpiDeliDoc.objects.filter(department=department).values_list('kpi', flat=True)))
    return HttpResponse(json.dumps(kpi), content_type='application/json')

def fetch_deliverable(request):
    department = request.GET.get('department')
    deliverable = list(set(PerfMgmtKpiDeliDoc.objects.filter(department=department).values_list('deliverable', flat=True)))
    return HttpResponse(json.dumps(deliverable), content_type='application/json')

def fetch_doc_evidence(request):
    department = request.GET.get('department')
    doc_evidence = list(set(PerfMgmtKpiDeliDoc.objects.filter(department=department).values_list('doc_evidence', flat=True)))
    return HttpResponse(json.dumps(doc_evidence), content_type='application/json')

def fetch_strategic_goals_transversal(request):
    logger.debug("fetch_strategic_goals_transversal view called")
    try:
        # Fetch unique strategic goals
        strategic_goals = PerfMgmtKpiDeliDoc.objects.values_list('strategic_goal', flat=True).distinct()
        logger.debug(f"Fetched strategic goals: {list(strategic_goals)}")
        # Return as JSON response
        return JsonResponse(list(strategic_goals), safe=False)
    except Exception as e:
        logger.error(f"Error fetching strategic goals: {e}")
        return JsonResponse({'error': 'An error occurred while fetching strategic goals.'}, status=500)
    

def fetch_kpis_transversal(request):
    logger.debug("fetch_kpis_transversal view called")
    try:
        # Fetch unique kpi values
        kpis = PerfMgmtKpiDeliDoc.objects.values_list('kpi', flat=True).distinct()
        logger.debug(f"Fetched kpis: {list(kpis)}")
        # Return as JSON response
        return JsonResponse(list(kpis), safe=False)
    except Exception as e:
        logger.error(f"Error fetching kpis: {e}")
        return JsonResponse({'error': 'An error occurred while fetching kpis.'}, status=500)


def fetch_deliverables_transversal(request):
    logger.debug("fetch_deliverables_transversal view called")
    try:
        # Fetch unique deliverable values
        deliverables = PerfMgmtKpiDeliDoc.objects.values_list('deliverable', flat=True).distinct()
        logger.debug(f"Fetched deliverables: {list(deliverables)}")
        # Return as JSON response
        return JsonResponse(list(deliverables), safe=False)
    except Exception as e:
        logger.error(f"Error fetching deliverables: {e}")
        return JsonResponse({'error': 'An error occurred while fetching deliverables.'}, status=500)
    

def fetch_doc_evidence_transversal(request):
    logger.debug("fetch_doc_evidence_transversal view called")  # Debug log to check if the view is hit
    try:
        # Fetch distinct document evidence values from the database
        doc_evidence = PerfMgmtKpiDeliDoc.objects.values_list('doc_evidence', flat=True).distinct()
        logger.debug(f"Fetched doc_evidence: {list(doc_evidence)}")  # Log the fetched values
        return JsonResponse(list(doc_evidence), safe=False)  # Return as JSON response
    except Exception as e:
        logger.error(f"Error fetching doc_evidence: {e}")  # Log any errors
        return JsonResponse({'error': 'An error occurred while fetching doc_evidence.'}, status=500)


def superuser_dashboard(request):
    total_active = UserProfile.objects.filter(activity_status="active").values('company').distinct().count()
    total_revenue = UserProfile.objects.aggregate(Sum('base_rate'))['base_rate__sum'] or 0
    avg_monthly = UserProfile.objects.aggregate(Avg('monthly_payment'))['monthly_payment__avg'] or 0

    revenue_by_industry = UserProfile.objects.values('industry').annotate(
        total=Sum('base_rate'),
        count=Count('id')
    ).order_by('-total')

    payment_plan_dist = UserProfile.objects.values('payment_plan').annotate(
        percentage=Count('id') * 100 / UserProfile.objects.count()
    )

    top_countries = UserProfile.objects.values('country').annotate(
        total=Sum('base_rate'),
        users=Count('id')
    ).order_by('-total')

    upcoming_renewals = UserProfile.objects.filter(
        end_date__range=[datetime.today(), datetime.today() + timedelta(days=30)]
    ).order_by('end_date')

    countries = UserProfile.objects.values_list('country', flat=True).distinct()
    selected_country = request.GET.get('country', '')

    if selected_country:
        top_countries = top_countries.filter(country=selected_country)
        revenue_by_industry = revenue_by_industry.filter(country=selected_country)
        payment_plan_dist = payment_plan_dist.filter(country=selected_country)
        upcoming_renewals = upcoming_renewals.filter(country=selected_country)

    top_countries = top_countries[:5]

    # Additional insights
    company_activity_status = UserProfile.objects.values('activity_status').annotate(
        count=Count('id')
    ).order_by('-count')

    revenue_growth = UserProfile.objects.annotate(month=TruncMonth('date_created')).values('month').annotate(
        monthly_revenue=Sum('base_rate')
    ).order_by('month')

    payment_plan_changes = UserProfile.objects.filter(
        start_date__gte=datetime.today() - timedelta(days=365)
    ).values('payment_plan').annotate(
        count=Count('id')
    )

    # Calculate market share percentage based on review_number and base_rate
    total_revenue_all_industries = UserProfile.objects.aggregate(
        total_revenue=Sum(F('review_number') * F('base_rate'))
    )['total_revenue'] or 0

    industry_market_share = UserProfile.objects.values('industry').annotate(
        total_revenue=Sum(F('review_number') * F('base_rate'))
    ).order_by('-total_revenue')

    for industry in industry_market_share:
        industry['market_share_percentage'] = (industry['total_revenue'] / total_revenue_all_industries) * 100 if total_revenue_all_industries > 0 else 0

    churn_rate = (UserProfile.objects.filter(activity_status='inactive').count() / UserProfile.objects.count()) * 100

    soon_to_renew = UserProfile.objects.filter(
        end_date__range=[datetime.today(), datetime.today() + timedelta(days=14)]
    ).order_by('end_date')

    recent_user_profiles = UserProfile.objects.order_by('-date_created')[:5]

    subscription_types = UserProfile.objects.values('review_cycle').annotate(
        total_revenue=Sum('base_rate')
    ).order_by('-total_revenue')

    contract_lengths = UserProfile.objects.annotate(
        contract_duration=F('end_date') - F('start_date')
    ).aggregate(Avg('contract_duration'))

    context = {
        'total_active': total_active,
        'total_revenue': total_revenue,
        'avg_monthly': avg_monthly,
        'revenue_by_industry': revenue_by_industry,
        'payment_plan_dist': payment_plan_dist,
        'top_countries': top_countries,
        'upcoming_renewals': upcoming_renewals,
        'countries': countries,
        'selected_country': selected_country,
        'company_activity_status': company_activity_status,
        'revenue_growth': revenue_growth,
        'payment_plan_changes': payment_plan_changes,
        'industry_market_share': industry_market_share,
        'churn_rate': churn_rate,
        'soon_to_renew': soon_to_renew,
        'recent_user_profiles': recent_user_profiles,
        'subscription_types': subscription_types,
        'contract_lengths': contract_lengths
    }

    return render(request, 'superuser_dashboard.html', context)



def department_dashboard(request):
    context = RequestContext(request)
    # Heatmap data
    context['kpi_heatmap'] = {
        'z': [[80, 90], [75, 85]],
        'x': ['Team A', 'Team B'],
        'y': ['Objective 1', 'Objective 2']
    }
    
    # Add other heatmap data sources
    return render(request, 'department.html', context)


@csrf_exempt  # Remove this if CSRF protection is required
def fetch_employee_names_inheritance(request):
    if request.method == "GET":
        try:
            reports_to_value = request.GET.get("reports_to")  # Get input from front-end

            if not reports_to_value:
                return JsonResponse({"error": "Missing 'reports_to' parameter"}, status=400)

            # Step 1: Get all employee_code(s) where reports_to matches the input
            employee_codes = list(
                UserCreationModel.objects.filter(reports_to=reports_to_value)
                .values_list("employee_code", flat=True)
            )

            if not employee_codes:
                return JsonResponse({"error": "No employees found under this manager"}, status=404)

            # Step 2: Match employee_code values in sgs_kpis_del_dev
            matching_employee_codes = list(
                SGSKPIsDelDev.objects.filter(employee_code__in=employee_codes)
                .values_list("employee_code", flat=True)
            )

            if not matching_employee_codes:
                return JsonResponse({"error": "No matching KPIs found for these employees"}, status=404)

            # Step 3: Fetch corresponding employee_name values from user_creation_model
            employee_names = list(
                UserCreationModel.objects.filter(employee_code__in=matching_employee_codes)
                .values_list("employee_name", flat=True)
            )

            return JsonResponse({"employee_names": employee_names}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def fetch_employee_details_inheritance(request):
    if request.method == "GET":
        try:
            reports_to_code = request.GET.get("reports_to_code")
            if not reports_to_code:
                return JsonResponse({"error": "Missing 'reports_to_code' parameter"}, status=400)

            # Step 1: Get direct reports
            direct_reports = UserCreationModel.objects.filter(reports_to_code=reports_to_code)
            report_codes = list(direct_reports.values_list("employee_code", flat=True))
            report_names = list(direct_reports.values_list("employee_name", flat=True))

            if not report_codes:
                return JsonResponse({"error": "No direct reports found"}, status=404)

            # Step 2: Create a mapping of employee_code to employee_name
            code_to_name = {
                obj.employee_code: obj.employee_name for obj in direct_reports
            }

            # Step 3: Fetch KPI records where employee_code is in report_codes
            raw_kpi_records = SGSKPIsDelDev.objects.filter(
                employee_code__in=report_codes
            ).values(
                "employee_code",
                "kpi",
                "deliverable",
                "strategic_goal",
                "doc_evidence",
                "date_created",
                "review_cycle_number"
            )

            # Step 4: Add employee_name to each KPI record
            kpi_records = []
            for record in raw_kpi_records:
                employee_code = record["employee_code"]
                employee_name = code_to_name.get(employee_code)
                if employee_name:
                    record["employee_name"] = employee_name
                    kpi_records.append(record)

            # Step 5: Return response
            return JsonResponse({
                "direct_reports": report_names,
                "report_employee_codes": report_codes,
                "kpi_records": kpi_records
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def fetch_common_employees(request):
    if request.method == "GET":
        try:
            reports_to_code = request.GET.get("reports_to_code")
            if not reports_to_code:
                return JsonResponse({"error": "Missing 'reports_to_code' parameter"}, status=400)

            # Step 1: Get direct reports from UserCreationModel
            direct_reports = UserCreationModel.objects.filter(reports_to_code=reports_to_code)
            report_codes = list(direct_reports.values_list("employee_code", flat=True))

            if not report_codes:
                return JsonResponse({"error": "No direct reports found"}, status=404)

            # Step 2: Get employee_codes from SGSKPIsDelDev that are in report_codes
            kpi_employee_codes = SGSKPIsDelDev.objects.filter(
                employee_code__in=report_codes
            ).values_list("employee_code", flat=True).distinct()

            # Step 3: Get employee_name for only those employee_codes present in both models
            matched_employees = UserCreationModel.objects.filter(
                employee_code__in=kpi_employee_codes
            ).values("employee_code", "employee_name")

            # Step 4: Return result
            return JsonResponse({
                "matched_employees": list(matched_employees)
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def fetch_unmatched_employees(request):
    if request.method == "GET":
        try:
            reports_to_code = request.GET.get("reports_to_code")
            if not reports_to_code:
                return JsonResponse({"error": "Missing 'reports_to_code' parameter"}, status=400)

            # Step 1: Get direct reports from UserCreationModel
            direct_reports = UserCreationModel.objects.filter(reports_to_code=reports_to_code)
            report_codes = list(direct_reports.values_list("employee_code", flat=True))

            if not report_codes:
                return JsonResponse({"error": "No direct reports found"}, status=404)

            # Step 2: Get employee_codes from SGSKPIsDelDev that are in report_codes
            kpi_employee_codes = SGSKPIsDelDev.objects.filter(
                employee_code__in=report_codes
            ).values_list("employee_code", flat=True).distinct()

            # Step 3: Get employee_name for only those employee_codes in UserCreationModel but NOT in SGSKPIsDelDev
            unmatched_employees = UserCreationModel.objects.filter(
                employee_code__in=report_codes
            ).exclude(employee_code__in=kpi_employee_codes).values("employee_code", "employee_name")

            # Step 4: Return result
            return JsonResponse({
                "unmatched_employees": list(unmatched_employees)
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)




@csrf_exempt
def fetch_sgs_kpis_del_dev(request):
    employee_name = request.GET.get("employee_name", "")
    department = request.GET.get("department", "")
    position = request.GET.get("position", "")

    if not employee_name or not department or not position:
        return JsonResponse({"error": "Employee name, department, and position are required"}, status=400)

    employee = UserCreationModel.objects.filter(
        employee_name=employee_name, department=department, position=position
    ).values("employee_code").first()

    if not employee:
        return JsonResponse({"error": "No matching employee found"}, status=404)

    employee_code = employee["employee_code"]

    # Fetch data from SGSKPIsDelDev using the employee_code
    kpis = list(SGSKPIsDelDev.objects.filter(employee_code=employee_code).values(
        "kpi", "deliverable", "doc_evidence", "strategic_goal", 
        "strategic_goal_weight", "strategic_goal_due_date", "kpi_weight", 
        "kpi_due_date", "deliverable_weight", "deliverable_due_date", 
        "doc_evidence_weight", "doc_evidence_due_date"
    ))

    if not kpis:
        return JsonResponse({"error": "No matching KPIs found"}, status=404)

    return JsonResponse({"employee_code": employee_code, "kpis": kpis}, safe=False)


def get_subordinates(request) -> JsonResponse:
    """
    Retrieves employee names based on the entered reports_to value.

    Args:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing the employee names.
    """
    try:
        entered_value = request.GET.get('reports_to', '')
        subordinates = UserCreationModel.objects.filter(reports_to=entered_value).values_list('employee_name', flat=True)
        return JsonResponse(list(subordinates), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def create_user(request):
    return render(request, 'create_user.html')
    

def appraisal_view(request):
    return render(request, 'appraisal.html')

def setting_view(request):
    return render(request, 'setting.html')


def appraisal_page_view(request):
    return render(request, 'appraisal.html')  # Change 'home.html' to your actual template

def custom_login_view(request):
    return render(request, 'main.html')


def count_users(request):
    company_code = request.GET.get('company_code', None)

    if company_code:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM perf_mgmt_user_creation_model WHERE company_code = %s", [company_code])
            count = cursor.fetchone()[0]
            return JsonResponse({'count': count})
    
    return JsonResponse({'error': 'Company code not provided.'}, status=400)


def fetch_user_select(request):
    company_code = request.GET.get('company_code', None)

    if not company_code:
        return JsonResponse({'error': 'Company code is required.'}, status=400)

    try:
        with connection.cursor() as cursor:
            # Direct table reference using raw SQL
            cursor.execute(
                "SELECT user_select FROM perf_mgmt_userprofile WHERE company_code = %s",
                [company_code]
            )
            result = cursor.fetchone()

            if result:
                return JsonResponse({'user_select': result[0]})
            else:
                return JsonResponse({'error': 'Company code not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@require_GET
def get_regions(request):
    # Retrieve region_code from the query parameter
    region_code = request.GET.get('region_code')
    
    # If region_code is provided, fetch the corresponding region branch
    if region_code:
        region = Region.objects.filter(region_code=region_code).values('region_branch').first()
        
        # Return the region branch if found, otherwise return a blank response
        if region:
            return JsonResponse(region, safe=False)
        else:
            return JsonResponse({'region_branch': ''}, safe=False)
    
    return JsonResponse({'error': 'region_code parameter missing'}, status=400)


def evaluate_management_view(request):
    # Querying all rows from the table
    factors = EvaluateYourManager.objects.all()

    # Prepare a list of dictionaries to return as JSON
    factors_list = list(factors.values('factor_type', 'description'))

    # Return the JSON response
    return JsonResponse(factors_list, safe=False)

def get_employee_status(request):
    employee_code = request.GET.get('employee_code')
    try:
        employee = UserCreationModel.objects.get(employee_code=employee_code)
        employee_status = employee.employee_status
        return JsonResponse({'employee_status': employee_status})
    except UserCreationModel.DoesNotExist:
        return JsonResponse({'error': 'Employee code not found'}, status=404)

def get_company_code(request):
    employee_code = request.GET.get('employee_code')

    if not employee_code:
        return JsonResponse({'error': 'Employee code is required'}, status=400)

    # Query the database for the company_code corresponding to employee_code
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT company_code 
            FROM perf_mgmt_user_creation_model 
            WHERE employee_code = %s
            """, 
            [employee_code]
        )
        row = cursor.fetchone()

    if row:
        # Return the company_code if found
        return JsonResponse({'company_code': row[0]})
    else:
        return JsonResponse({'error': 'Employee not found'}, status=404)


@require_GET
def get_region_branch(request):
    company_code = request.GET.get('company_code')
    employee_code = request.GET.get('employee_code')

    if not company_code or not employee_code:
        return JsonResponse({'error': 'Missing company_code or employee_code'}, status=400)

    with connection.cursor() as cursor:
        # Step 1: Fetch region_branch from user_creation using correct column name
        cursor.execute("""
            SELECT region_branch 
            FROM perf_mgmt_user_creation_model 
            WHERE company_code = %s AND employee_code = %s
            LIMIT 1
        """, [company_code, employee_code])
        user_row = cursor.fetchone()

        if user_row and user_row[0]:
            region_branch = user_row[0]

            # Step 2: Fetch region_code from Region using company_code_id and region_branch
            cursor.execute("""
                SELECT region_code 
                FROM perf_mgmt_region 
                WHERE company_code_id = %s AND region_branch = %s
                LIMIT 1
            """, [company_code, region_branch])
            region_row = cursor.fetchone()

            if region_row:
                return JsonResponse({
                    'region_branch': region_branch,
                    'region_code': region_row[0]
                })

            return JsonResponse({
                'region_branch': region_branch,
                'message': 'No region_code found for this region_branch.'
            }, status=404)

        # Step 3: Fallback if region_branch is NULL
        cursor.execute("""
            SELECT region_code
            FROM perf_mgmt_region
            WHERE company_code_id = %s AND region_branch IS NULL
            LIMIT 1
        """, [company_code])
        fallback_row = cursor.fetchone()

        if fallback_row:
            return JsonResponse({
                'region_branch': None,
                'region_code': fallback_row[0],
                'message': 'Used fallback: region_branch was NULL.'
            })

        return JsonResponse({'error': 'No matching region_code found.'}, status=404)



@csrf_exempt
def send_chat_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed.'}, status=405)

    try:
        # Parse JSON payload from frontend
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        unique_chat = data.get('unique_chat')
        recipient_code = data.get('recipient_code')
        chat_type = data.get('chat_type')
        sender_code = data.get('sender_code')  # From frontend, not request.user

        # Validate required fields
        if not all([message, unique_chat, recipient_code, sender_code]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Verify sender exists
        try:
            sender = UserCreationModel.objects.get(employee_code=sender_code)
            sender_name = sender.employee_name
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Sender not found'}, status=404)

        # Verify recipient exists
        try:
            receiver = UserCreationModel.objects.get(employee_code=recipient_code)
            receiver_name = receiver.employee_name
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Receiver not found'}, status=404)

        # Validate unique_chat
        expected_chat = '_'.join(sorted([sender_code, recipient_code]))
        if unique_chat != expected_chat:
            return JsonResponse({'error': 'Invalid unique_chat'}, status=400)

        # Validate chat_type
        valid_chat_types = ['mentor', 'mentee']
        chat_type = chat_type if chat_type in valid_chat_types else None

        # Store message if not empty
        if not message:
            return JsonResponse({
                'status': 'No message provided',
                'mentor': receiver_name if chat_type == 'mentor' else sender_name,
                'mentee': sender_name if chat_type == 'mentee' else receiver_name
            }, status=200)

        # Create message in perf_mgmt_chatmessage
        ChatMessage.objects.create(
            sender_id=sender_code,
            receiver_id=recipient_code,
            message=message,
            unique_chat=unique_chat,
            chat_type=chat_type
        )

        return JsonResponse({
            'status': 'Message sent',
            'mentor': receiver_name if chat_type == 'mentor' else sender_name,
            'mentee': sender_name if chat_type == 'mentee' else receiver_name
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        print(f"Error in send_chat_message: {str(e)}")  # Log for debugging
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_mentees(request):
    current_user_code = request.user.employee_code

    try:
        # Get current user (mentor)
        mentor = UserCreationModel.objects.get(employee_code=current_user_code)
        mentor_name = mentor.employee_name

        # Get mentees who report to this mentor
        mentees = UserCreationModel.objects.filter(reports_to=mentor_name).values(
            'employee_code', 'employee_name', 'position'
        )

        mentee_list = [
            {
                'employee_code': mentee['employee_code'],
                'employee_name': mentee['employee_name'],
                'position': mentee['position']
            }
            for mentee in mentees
        ]

        return JsonResponse({'mentees': mentee_list}, status=200)

    except UserCreationModel.DoesNotExist:
        return JsonResponse({'error': 'Mentor not found'}, status=404)
    except Exception as e:
        print(f"Error in get_mentees: {str(e)}")  # Log for debugging
        return JsonResponse({'error': str(e)}, status=500)
    

@require_GET
def get_chat_messages(request):
    unique_chat = request.GET.get('unique_chat')

    if not unique_chat:
        return JsonResponse({'error': 'unique_chat parameter is required.'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.message,
                m.timestamp,
                m.sender_id,
                m.receiver_id,
                s.employee_name AS sender_name,
                r.employee_name AS receiver_name
            FROM perf_mgmt_chatmessage m
            LEFT JOIN perf_mgmt_user_creation_model s ON m.sender_id = s.employee_code
            LEFT JOIN perf_mgmt_user_creation_model r ON m.receiver_id = r.employee_code
            WHERE m.unique_chat = %s
            ORDER BY m.timestamp ASC
        """, [unique_chat])

        rows = cursor.fetchall()

    messages = []
    for row in rows:
        messages.append({
            'message': row[0],
            'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else '',
            'sender_id': row[2],
            'receiver_id': row[3],
            'sender_name': row[4] or 'Unknown',
            'receiver_name': row[5] or 'Unknown',
        })

    return JsonResponse({'messages': messages})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_appraisal_chat_messages(request):
    unique_chat = request.GET.get('unique_chat')

    if request.method == 'GET':
        if not unique_chat:
            return JsonResponse({'error': 'unique_chat parameter is required.'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.message_id,
                    m.message,
                    m.timestamp,
                    m.sender_id,
                    m.receiver_id,
                    s.employee_name AS sender_name,
                    r.employee_name AS receiver_name,
                    m.strategic_goal,
                    m.kpi,
                    m.deliverable,
                    m.reply_to_id
                FROM perf_mgmt_appraisal_messages m
                LEFT JOIN perf_mgmt_user_creation_model s ON m.sender_id = s.employee_code
                LEFT JOIN perf_mgmt_user_creation_model r ON m.receiver_id = r.employee_code
                WHERE m.unique_chat = %s
                ORDER BY m.timestamp ASC
            """, [unique_chat])

            rows = cursor.fetchall()

            messages = []
            for row in rows:
                messages.append({
                    'message_id': row[0],
                    'message': row[1],
                    'timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else '',
                    'sender_id': row[3],
                    'receiver_id': row[4],
                    'sender_name': row[5] or 'Unknown',
                    'receiver_name': row[6] or 'Unknown',
                    'strategic_goal': row[7] or 'N/A',
                    'kpi': row[8] or 'N/A',
                    'deliverable': row[9] or 'N/A',
                    'reply_to_id': row[10]
                })

            # Group messages by reply_to_id
            grouped_messages = {}
            for message in messages:
                if message['reply_to_id'] not in grouped_messages:
                    grouped_messages[message['reply_to_id']] = []
                grouped_messages[message['reply_to_id']].append(message)

            return JsonResponse({'messages': grouped_messages})

    # ... rest of your code


def get_manager_info(request):
    employee_code = request.GET.get('employee_code')

    if not employee_code:
        return JsonResponse({'error': 'employee_code is required'}, status=400)

    with connection.cursor() as cursor:
        # Fetch the reports_to name for the employee
        cursor.execute("""
            SELECT employee_name, reports_to
            FROM perf_mgmt_user_creation_model
            WHERE employee_code = %s
        """, [employee_code])
        row = cursor.fetchone()

        if not row:
            return JsonResponse({'error': 'Employee not found'}, status=404)

        employee_name, manager_name = row

        # Get the manager's employee_code (if they exist)
        cursor.execute("""
            SELECT employee_code
            FROM perf_mgmt_user_creation_model
            WHERE employee_name = %s
            LIMIT 1
        """, [manager_name])
        manager_row = cursor.fetchone()
        manager_code = manager_row[0] if manager_row else None

    return JsonResponse({
        'employee_code': employee_code,
        'employee_name': employee_name,
        'reports_to': manager_name,
        'manager_employee_code': manager_code
    })


@require_GET
def get_mentees_by_reports_to_code(request):
    reports_to_code = request.GET.get('reports_to_code')

    if not reports_to_code:
        return JsonResponse({'error': 'Missing reports_to_code'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT employee_name, employee_code
            FROM perf_mgmt_user_creation_model
            WHERE reports_to_code = %s
        """, [reports_to_code])
        
        rows = cursor.fetchall()

    if rows:
        mentees = [{'employee_name': row[0], 'employee_code': row[1]} for row in rows]
        return JsonResponse({'mentees': mentees})
    else:
        return JsonResponse({'mentees': []})



def filter_by_employee_code(request):
    employee_code = request.GET.get('employee_code')

    if not employee_code:
        return JsonResponse({'status': 'error', 'message': 'No employee_code provided'})

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM perf_mgmt_assessment WHERE employee_code = %s", [employee_code])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    results = [dict(zip(columns, row)) for row in rows]

    return JsonResponse({'status': 'success', 'data': results})


def get_surbodinate_code(request):
    reports_to = request.GET.get('reports_to')
    company_code = request.GET.get('company_code')
    employee_name = request.GET.get('employee_name')

    if not all([reports_to, company_code, employee_name]):
        return JsonResponse({'status': 'error', 'message': 'Missing one or more required parameters'})

    query = """
        SELECT employee_code 
        FROM perf_mgmt_user_creation_model 
        WHERE reports_to = %s AND company_code = %s AND employee_name = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [reports_to, company_code, employee_name])
        result = cursor.fetchone()

    if result:
        return JsonResponse({'status': 'success', 'subordinate_code': result[0]})
    else:
        return JsonResponse({'status': 'not_found', 'message': 'No matching subordinate code found'})

def video_page(request):
    return render(request, 'link1.html')


def ai_recommendation_view(request, employee_code):
    try:
        # 1. Get latest assessment from perf_mgmt_assessment
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, strategic_goal, kpi, deliverable,
                       deliverable_self_score, deliverable_assessor_score
                FROM perf_mgmt_assessment
                WHERE UPPER(employee_code) = UPPER(%s)
                ORDER BY date_assessor_appraisal_completed DESC
                LIMIT 1
            """, [employee_code])
            assessment_row = cursor.fetchone()

        assessment_id = None
        if assessment_row:
            (assessment_id, strategic_goal, kpi, deliverable,
             self_score, assessor_score) = assessment_row
        else:
            # Handle missing assessment gracefully
            strategic_goal = kpi = deliverable = "Not available"
            self_score = assessor_score = None
            logger.warning(f"No assessment found for employee_code: {employee_code}")

        # 2. Get user details from perf_mgmt_user_creation_model
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT department, position, country, company_code, first_name, last_name, email
                FROM perf_mgmt_user_creation_model
                WHERE UPPER(employee_code) = UPPER(%s)
                LIMIT 1
            """, [employee_code])
            user_row = cursor.fetchone()

        if not user_row:
            logger.error(f"User not found for employee_code: {employee_code}")
            return JsonResponse({"error": f"Employee code {employee_code} not found in the system."}, status=404)

        department, position, country, company_code, first_name, last_name, email = user_row
        # Handle null or empty fields
        department = department or "Unknown"
        position = position or "Unknown"
        country = country or "Unknown"

        # 3. Check for existing recommendation
        recommendation = None
        if assessment_id:
            recommendation_obj = AIRecommendation.objects.filter(
                employee_code=employee_code,
                assessment_id=assessment_id
            ).order_by('-created_at').first()
            if recommendation_obj:
                recommendation = recommendation_obj.recommendation_text

        # 4. Generate new recommendation if none exists
        if not recommendation:
            context = {
                "employee_code": employee_code,
                "strategic_goal": strategic_goal,
                "kpi": kpi,
                "deliverable": deliverable,
                "self_score": self_score,
                "assessor_score": assessor_score,
                "department": department,
                "position": position,
                "country": country,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            }

            try:
                recommendation = get_ai_recommendation(context)
            except Exception as e:
                logger.error(f"Error generating AI recommendation for {employee_code}: {str(e)}")
                return JsonResponse({"error": "Failed to generate AI recommendation."}, status=500)

            # 5. Save recommendation if assessment exists
            if assessment_id:
                AIRecommendation.objects.create(
                    employee_code=employee_code,
                    assessment_id=assessment_id,
                    recommendation_text=recommendation
                )

        return JsonResponse({"recommendation": recommendation})

    except Exception as e:
        logger.error(f"Unexpected error in ai_recommendation_view for {employee_code}: {str(e)}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    


def get_config_values(request):
    """
    Fetches all records from the 'perf_mgmt_kpi_deli_doc' table directly using raw SQL.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM perf_mgmt_kpi_deli_doc")
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    return JsonResponse({'data': results}, safe=False)



@require_GET
def review_periods(request):
    try:
        company_code = request.GET.get('company_code')
        employee_code = request.GET.get('employee_code')

        # Resolve company_code from employee_code if needed
        if not company_code:
            if not employee_code:
                return JsonResponse({'error': 'Either company_code or employee_code is required.'}, status=400)
            try:
                user = UserCreationModel.objects.get(employee_code=employee_code)
                # Safely resolve string company_code
                company_code = (
                    user.company_code.company_code
                    if hasattr(user.company_code, 'company_code')
                    else user.company_code
                )
            except UserCreationModel.DoesNotExist:
                return JsonResponse({'error': 'No user found for the given employee_code.'}, status=404)

        # Query review periods using the resolved company_code
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    review,
                    TO_CHAR(period_start_date, 'YYYY-MM-DD') AS period_start_date,
                    TO_CHAR(period_end_date, 'YYYY-MM-DD') AS period_end_date
                FROM review_periods
                WHERE company_code = %s
                ORDER BY review ASC
                """,
                [company_code]
            )
            results = cursor.fetchall()

            if not results:
                return JsonResponse({'error': 'No review periods found for this company code.'}, status=404)

            response_data = [
                {
                    'review': row[0],
                    'period_start_date': row[1],
                    'period_end_date': row[2]
                }
                for row in results
            ]

            return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




def fetch_company_departments(request):
    company_code = request.GET.get('company_code')
    
    if not company_code:
        return JsonResponse({'error': 'company_code parameter is missing'}, status=400)

    # Get unique departments for this company_code
    departments = UserCreationModel.objects.filter(company_code=company_code).values_list('department', flat=True).distinct()
    
    return JsonResponse({'departments': list(departments)})


logger = logging.getLogger(__name__)

@csrf_exempt
def save_strategic_goals(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received data: {data}")

        goal_type = data.get('goal_type')
        strategic_goal = data.get('strategic_goal')
        weight = data.get('weight')
        due_date = data.get('due_date')
        departments = data.get('departments')
        username = data.get('username')
        region_branch = data.get('region_branch', '')  # optional
        company_code = data.get('company_code')
        branch_code = data.get('branch_code', '')      # optional
        employee_code = data.get('employee_code')

        # Validate required fields
        required_fields = {
            'goal_type': goal_type,
            'strategic_goal': strategic_goal,
            'employee_code': employee_code,
            'company_code': company_code,
            'username': username,
            'departments': departments,
        }
        missing_fields = [f for f, v in required_fields.items() if not v]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return JsonResponse({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)

        # Departments validation
        if not isinstance(departments, list) or not departments:
            logger.error("Departments must be a non-empty list")
            return JsonResponse({
                "status": "error",
                "message": "Departments must be a non-empty list"
            }, status=400)

        for dept in departments:
            if not dept or len(dept) > 255:
                logger.error(f"Invalid department '{dept}'")
                return JsonResponse({
                    "status": "error",
                    "message": f"Department '{dept}' is empty or exceeds 255 characters"
                }, status=400)

        # Company code length check
        if len(company_code) > 255:
            logger.error(f"Company code {company_code} exceeds 255 characters")
            return JsonResponse({
                "status": "error",
                "message": "Company code must be 255 characters or less"
            }, status=400)

        # Weight conversion
        try:
            if weight is not None and weight != '':
                weight = Decimal(weight)
                if weight < 0:
                    raise ValueError("Weight cannot be negative")
                weight = weight / 100  # percent to decimal
            else:
                weight = None
        except (ValueError, InvalidOperation) as e:
            logger.error(f"Invalid weight value: {str(e)}")
            return JsonResponse({"status": "error", "message": "Invalid weight value"}, status=400)

        # Due date parse
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        except (ValueError, TypeError):
            logger.error(f"Invalid due_date format: {due_date}")
            return JsonResponse({
                "status": "error",
                "message": "Invalid due_date format, expected YYYY-MM-DD"
            }, status=400)

        # Save StrategicGoals atomically for each department
        saved_goals = []
       

        with transaction.atomic():
            for dept in departments:
                sg_obj = StrategicGoals(
                    goal_type=goal_type,
                    strategic_goal=strategic_goal,
                    weight=weight,
                    due_date=due_date,
                    department=dept,
                    employee_code=employee_code,  # pass string directly, no FK instance
                    region_code=branch_code if branch_code else None,  # string or None
                    username=username,
                    region_branch=region_branch,
                    created_date=timezone.now(),
                    goal_activity='current',
                    company_code=company_code,
                )
                try:
                    sg_obj.full_clean()
                    sg_obj.save()
                    saved_goals.append(str(sg_obj.id))
                    logger.debug(f"Saved StrategicGoal id={sg_obj.id} for dept={dept}")
                except (ValidationError, IntegrityError, DatabaseError) as e:
                    logger.error(f"Save error for dept={dept}: {str(e)}")
                    raise

        return JsonResponse({
            "status": "success",
            "message": f"Strategic goals saved successfully for departments: {', '.join(departments)}",
            "saved_goal_ids": saved_goals,
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Unexpected error: {str(e)}"}, status=500)


@require_GET
def retrieve_strategic_goals(request):
    company_code = request.GET.get('company_code')
    if not company_code:
        return JsonResponse({'status': 'error', 'message': 'Company code is required.'}, status=400)

    goals = StrategicGoals.objects.filter(company_code=company_code).values(
        'id', 'goal_type', 'strategic_goal', 'weight', 'due_date',
        'department', 'employee_code', 'region_code',
        'username', 'region_branch', 'created_date'
    )

    return JsonResponse({'status': 'success', 'goals': list(goals)})


def get_manager_code(request):
    employee_code = request.GET.get('employee_code')
    
    if not employee_code:
        return JsonResponse({'error': 'employee_code parameter is required'}, status=400)

    try:
        # Fetch the employee by employee_code
        employee = UserCreationModel.objects.get(employee_code=employee_code)
        
        # Get the manager's employee_name (reports_to)
        manager_name = employee.reports_to

        # If no manager is assigned
        if not manager_name:
            return JsonResponse({'error': 'No manager assigned'}, status=404)

        # Fetch the manager based on employee_name (reports_to)
        manager = UserCreationModel.objects.get(employee_name=manager_name)

        # Return the response with aligned field names
        return JsonResponse({
            'success': True,
            'appraisor_code': manager.employee_code,  # The manager's employee_code
            'appraisor_name': manager.employee_name,  # The manager's name
        })

    except UserCreationModel.DoesNotExist:
        return JsonResponse({'error': 'Employee or manager not found'}, status=404)


@csrf_exempt
def send_appraisal_messages(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message')
        unique_chat = data.get('unique_chat')
        sender_code = data.get('sender_code')
        recipient_code = data.get('recipient_code')
        strategic_goal = data.get('strategic_goal', 'N/A')
        kpi = data.get('kpi', 'N/A')
        deliverable = data.get('deliverable', 'N/A')
        deliverable_number = data.get('deliverable_number', 'N/A')
        deliverable_id = data.get('deliverable_id')
        reply_to_id = data.get('reply_to_id')
        sender_name = data.get('sender_name')
        recipient_name = data.get('recipient_name')

        # Validate required fields
        if not all([message, sender_code, recipient_code, unique_chat]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Verify sender exists
        try:
            sender = UserCreationModel.objects.get(employee_code=sender_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Sender not found'}, status=404)

        # Verify receiver exists
        try:
            receiver = UserCreationModel.objects.get(employee_code=recipient_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Recipient not found'}, status=404)

        # Validate unique_chat
        expected_unique_chat = '_'.join(sorted([sender_code, recipient_code]))
        if unique_chat != expected_unique_chat:
            return JsonResponse({'error': 'Invalid unique_chat value'}, status=400)

        # Handle reply_to
        reply_to = None
        if reply_to_id:
            try:
                reply_to = AppraisalMessage.objects.get(id=reply_to_id, unique_chat=unique_chat)
            except AppraisalMessage.DoesNotExist:
                return JsonResponse({'error': 'Invalid reply_to message'}, status=400)

        # Create message
        chat_message = AppraisalMessage(
            sender=sender_code,
            receiver=receiver,
            message=message,
            chat_type='text',
            strategic_goal=strategic_goal,
            kpi=kpi,
            deliverable=deliverable,
            deliverable_number=deliverable_number,
            deliverable_id=deliverable_id,
            sender_name=sender_name or sender.employee_name,
            recipient_name=recipient_name or receiver.employee_name,
            reply_to=reply_to
        )
        chat_message.save()

        logger.info(f'Message saved: {unique_chat} from {sender_code} to {recipient_code}')
        return JsonResponse({'status': 'Message sent'}, status=201)
    except ValueError as ve:
        logger.error(f'Validation error in send_appraisal_messages: {str(ve)}', exc_info=True)
        return JsonResponse({'error': f'Validation error: {str(ve)}'}, status=400)
    except Exception as e:
        logger.error(f'Error in send_appraisal_messages: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Failed to send message: {str(e)}'}, status=500)
    


@csrf_exempt
def send_appraisee_message(request):
  if request.method != 'POST':
    return JsonResponse({'error': 'Invalid method'}, status=405)

  try:
    message = request.POST.get('message')
    sender_code = request.POST.get('sender_code')
    recipient_code = request.POST.get('recipient_code')
    strategic_goal = request.POST.get('strategic_goal', 'N/A')
    kpi = request.POST.get('kpi', 'N/A')
    deliverable = request.POST.get('deliverable', 'N/A')
    attachment = request.FILES.get('attachment')

    if not (message or attachment):
      return JsonResponse({'error': 'Message or attachment required'}, status=400)

    if not sender_code or not recipient_code:
      return JsonResponse({'error': 'Missing sender or recipient'}, status=400)

    sender = UserCreationModel.objects.filter(employee_code=sender_code).first()
    if not sender:
      return JsonResponse({'error': 'Sender not found'}, status=404)

    receiver = UserCreationModel.objects.filter(employee_code=recipient_code).first()
    if not receiver:
      return JsonResponse({'error': 'Recipient not found'}, status=404)

    chat_type = 'file' if attachment else 'text'

    chat_message = AppraisalMessage(
      sender=sender_code,
      receiver=receiver,
      message=message or '',
      chat_type=chat_message,
      strategic_goal=strategic_goal,
      kpi=kpi,
      deliverable=deliverable,
      sender_name=sender.employee_name,
      recipient_name=receiver.employee_name,
      deliverable_id=f"{strategic_goal} - {kpi} - {deliverable}",
    )

    if attachment:
      path = default_storage.save(f'attachments/{attachment.name}', attachment)
      chat_message.attachment_url = default_storage.url(path)

    existing_message = AppraisalMessage.objects.filter(
      strategic_goal=strategic_goal,
      kpi=kpi,
      deliverable=deliverable,
    ).first()

    if existing_message:
      chat_message.reply_to = existing_message
      chat_message.reply_to_id = existing_message.reply_to_id
    else:
      import uuid
      chat_message.reply_to_id = str(uuid.uuid4())

    chat_message.save()
    logger.info(f'Message saved from {sender_code} to {recipient_code}')
    return JsonResponse({'status': 'Message sent'})

  except Exception as e:
    logger.error(f'Error in send_appraisee_message: {str(e)}', exc_info=True)
    return JsonResponse({'error': f'Failed to send message: {str(e)}'}, status=500)

@csrf_exempt
def upload_attachment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        unique_chat = request.POST.get('unique_chat')
        sender_code = request.POST.get('sender_code')
        recipient_code = request.POST.get('recipient_code')
        message = request.POST.get('message', '')  # optional for attachment-only
        strategic_goal = request.POST.get('strategic_goal', 'N/A')
        kpi = request.POST.get('kpi', 'N/A')
        deliverable = request.POST.get('deliverable', 'N/A')
        file = request.FILES.get('file')

        if not all([unique_chat, sender_code, recipient_code, file]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Validate sender
        try:
            UserCreationModel.objects.get(employee_code=sender_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Sender not found'}, status=404)

        # Validate receiver
        try:
            receiver = UserCreationModel.objects.get(employee_code=recipient_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Recipient not found'}, status=404)

        # Save file to disk
        save_path = os.path.join(settings.MEDIA_ROOT, 'attachments')
        os.makedirs(save_path, exist_ok=True)
        file_name = file.name
        file_path = os.path.join(save_path, file_name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        attachment_url = f'{settings.MEDIA_URL}attachments/{file_name}'

        # Save message record
        chat_message = AppraisalMessage(
            sender=sender_code,
            receiver=receiver,
            message=message,
            chat_type='attachment',
            attachment_url=attachment_url,
            strategic_goal=strategic_goal,
            kpi=kpi,
            deliverable=deliverable
        )
        chat_message.save()

        logger.info(f'Attachment saved: {unique_chat} from {sender_code} to {recipient_code}')
        return JsonResponse({'status': 'Attachment sent'})
    
    except Exception as e:
        logger.error(f'Error in upload_attachment: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Failed to upload attachment: {str(e)}'}, status=500)

@csrf_exempt
def save_deliverable_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message')
        unique_chat = data.get('unique_chat')
        sender_code = data.get('sender_code')
        recipient_code = data.get('recipient_code')
        strategic_goal = data.get('strategic_goal')
        kpi = data.get('kpi')
        deliverable = data.get('deliverable')
        deliverable_id = data.get('deliverable_id')

        if not all([message, unique_chat, sender_code, recipient_code, deliverable_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Verify sender exists
        try:
            UserCreationModel.objects.get(employee_code=sender_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Sender not found'}, status=404)

        # Get receiver
        try:
            receiver = UserCreationModel.objects.get(employee_code=recipient_code)
        except UserCreationModel.DoesNotExist:
            return JsonResponse({'error': 'Recipient not found'}, status=404)

        # Create comment
        comment = AppraisalMessage(
            sender=sender_code,
            receiver=receiver,
            message=message,
            chat_type='text',
            strategic_goal=strategic_goal or '',
            kpi=kpi or '',
            deliverable=deliverable or '',
            deliverable_id=deliverable_id
        )
        comment.save()

        logger.info(f'Comment saved: {unique_chat} for deliverable {deliverable_id} from {sender_code} to {recipient_code}')
        return JsonResponse({'status': 'Comment saved'})
    except Exception as e:
        logger.error(f'Error in save_deliverable_comment: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Failed to save comment: {str(e)}'}, status=500)
    

def create_user(request):
    if request.method == 'POST':
        try:
            # Extract POST data
            data = request.POST

            # Validate required fields
            required_fields = [
                'first_name', 'last_name', 'phone_number', 'work_email',
                'select_name', 'employment_start_date', 'employment_status',
                'employee_status', 'team_or_division', 'departmentInputField',
                'positionInputField', 'is_employee_active'
            ]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return render(request, 'create_user.html', {'post_data': data})

            # Get company_code (assuming it's derived from a hidden field or user profile)
            company_code = data.get('company_code')  # Adjust based on how you provide this
            if not company_code:
                messages.error(request, "Company code is required.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate company_code exists in UserProfile
            try:
                company = UserProfile.objects.get(company_code=company_code)
            except UserProfile.DoesNotExist:
                messages.error(request, "Invalid company code.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate date fields
            date_of_birth = data.get('date_of_birth')
            if date_of_birth:
                try:
                    datetime.strptime(date_of_birth, '%Y-%m-%d')
                except ValueError:
                    messages.error(request, "Invalid date of birth format. Use YYYY-MM-DD.")
                    return render(request, 'create_user.html', {'post_data': data})

            employment_start_date = data.get('employment_start_date')
            try:
                datetime.strptime(employment_start_date, '%Y-%m-%d')
            except ValueError:
                messages.error(request, "Invalid employment start date format. Use YYYY-MM-DD.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate phone number
            phone_number = data.get('phone_number')
            phone_pattern = r'^\+?\d{1,3}[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}$'
            if not re.match(phone_pattern, phone_number):
                messages.error(request, "Invalid phone number format.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate email
            email = data.get('work_email')
            email_pattern = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$'
            if not re.match(email_pattern, email):
                messages.error(request, "Invalid email format.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate employee code (if provided)
            identity_number = data.get('identity_number')
            if identity_number:
                code_pattern = r'[A-Z]{2}-\d{6}'
                if not re.match(code_pattern, identity_number):
                    messages.error(request, "Invalid employee code format. Use AB-123456.")
                    return render(request, 'create_user.html', {'post_data': data})

            # Validate employment_type
            valid_employment_types = [choice[0] for choice in UserCreationModel.employment_type.field.choices]
            employment_type = data.get('employment_status')
            if employment_type not in valid_employment_types:
                messages.error(request, f"Invalid employment type. Must be one of: {', '.join(valid_employment_types)}")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate employee_status
            valid_employee_statuses = [choice[0] for choice in UserCreationModel.employee_status.field.choices]
            employee_status = data.get('employee_status')
            if employee_status not in valid_employee_statuses:
                messages.error(request, f"Invalid employee status. Must be one of: {', '.join(valid_employee_statuses)}")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate is_employee_active
            is_employee_active = data.get('is_employee_active')
            if is_employee_active not in ['Active', 'Inactive', 'Terminated']:
                messages.error(request, "Invalid activity status. Must be Active, Inactive, or Terminated.")
                return render(request, 'create_user.html', {'post_data': data})

            # Validate reason_for_inactivity
            reason_for_inactivity = data.get('reason_for_inactivity', '')
            if is_employee_active in ['Inactive', 'Terminated'] and not reason_for_inactivity:
                messages.error(request, "Reason for inactivity is required when status is Inactive or Terminated.")
                return render(request, 'create_user.html', {'post_data': data})

            # Handle 'other' reason for inactivity
            if reason_for_inactivity == 'other':
                other_reason = data.get('other_reason_text', '')
                if not other_reason:
                    messages.error(request, "Please specify the reason for inactivity.")
                    return render(request, 'create_user.html', {'post_data': data})
                reason_for_inactivity = other_reason

            # Create UserCreationModel instance
            user = UserCreationModel(
                company_code=company,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                employee_name=f"{data.get('first_name')} {data.get('last_name')}",
                date_of_birth=date_of_birth if date_of_birth else None,
                team_or_division=data.get('team_or_division'),
                employee_email=data.get('work_email'),
                phone_number=data.get('phone_number'),
                employee_gender=data.get('gender', ''),
                employment_type=employment_type,
                employee_status=employee_status,
                department=data.get('departmentInputField'),
                position=data.get('positionInputField'),
                is_employee_active=is_employee_active == 'Active',
                reason_for_inactivity=reason_for_inactivity,
                reports_to=data.get('select_name'),
                employment_start_date=employment_start_date,
                assign_admin_role=data.get('assign_admin_role', None),
                preexisting_employee_code=identity_number if identity_number else None,
                region_branch=data.get('region_branch', None),
            )

            # Save the instance (this will generate employee_code)
            user.save()

            # Success message
            messages.success(request, f"User {user.employee_name} created successfully!")
            return redirect('add_employee')

        except Exception as e:
            # Handle any unexpected errors
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'create_user.html', {'post_data': data})

    # GET request: Render the form
    return render(request, 'create_user.html')

@csrf_exempt
def create_multiple_questions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Assuming company_code is just a text field now, no additional validation
            company_code = data.get('company_code', '')  # Default to empty string if not provided
            branch_code = data.get('branch_code')
            competence_area = data.get('competence_area')
            questions = data.get('questions', [])

            saved_codes = []

            for q in questions:
                question_text = q.get('question')
                feedback_type = q.get('feedback_type')
                due_date_str = q.get('due_date')

                # Debugging the value of due_date
                print("Received Due Date:", due_date_str)  # Log to check the received due date

                if not due_date_str:
                    return JsonResponse({'status': 'error', 'message': 'Due Date is required.'}, status=400)

                # Parse the date using Django's parse_date utility
                due_date = parse_date(due_date_str)

                # Check if the date is valid (not None)
                if not due_date:
                    return JsonResponse({'status': 'error', 'message': 'Invalid Due Date format.'}, status=400)

                # Creating the question entry in the database
                obj = EvaluateYourMgtSetting.objects.create(
                    company_code=company_code,  # No validation, treated as normal text
                    branch_code=branch_code,
                    competence_area=competence_area,
                    question=question_text,
                    feedback_type=feedback_type,
                    due_date=due_date
                )
                saved_codes.append(obj.evaluation_code)

            # Return the saved evaluation codes as part of the success response
            return JsonResponse({'status': 'success', 'saved_codes': saved_codes})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

@csrf_exempt
def save_login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

    company = request.POST.get('company-name', '').strip()
    company_code = request.POST.get('company-code', '').strip()
    employee_name = request.POST.get('username', '').strip()
    employee_code = request.POST.get('employee-password', '').strip()
    region_branch = request.POST.get('region-branch', '').strip()
    headquarters = request.POST.get('country', '').strip()
    profile_photo = request.FILES.get('profile-photo') or request.FILES.get('file-input')

    if employee_code:
        try:
            # Get user and clean foreign key value
            user = UserCreationModel.objects.get(employee_code=employee_code)
            company_code_fk = user.company_code_id  # Get raw ID of the FK

            # Get the company profile
            user_profile = UserProfile.objects.get(company_code=company_code_fk)
            company = user_profile.company  # Clean name
            company_code = user_profile.company_code  # Clean code

            # Don't overwrite headquarters here — keep it as the country from the form

            # Get region
            region = Region.objects.filter(company_code=company_code_fk).first()
            region_branch = region.region_branch if region else None

            # Check if already logged in
            active_login = UserLogin.objects.filter(
                employee_code=employee_code,
                log_out__isnull=True
            ).order_by('-created_at').first()

            if active_login:
                return JsonResponse({'message': 'This employee is already logged in.'}, status=200)

            UserLogin.objects.create(
                username=user.employee_name,
                company=company,
                employee_code=employee_code,
                company_code=company_code,
                region_branch=region_branch,
                headquarters=headquarters,  # This is now correctly set to the form country
                profile_photo=profile_photo,
                region_code=region.region_code if region else None
            )

            # Store employee_code in session
            request.session['employee_code'] = employee_code
            logger.info(f"Session set for employee_code: {employee_code}")
            return JsonResponse({'message': 'Employee login successful.'}, status=200)

        except UserCreationModel.DoesNotExist:
            return JsonResponse({'message': 'Invalid employee credentials.'}, status=400)

        except UserProfile.DoesNotExist:
            return JsonResponse({'message': 'Company profile not found for this employee.'}, status=400)

    elif company_code and company:
        try:
            company_profile = UserProfile.objects.get(company_code=company_code)

            if company_profile.company.strip() != company:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Company code "{company_code}" does not match company name "{company}".'
                }, status=404)

        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Company code "{company_code}" not found.'}, status=404)

        active_login = CompanyLogin.objects.filter(
            company_code=company_code,
            log_out__isnull=True
        ).order_by('-created_at').first()

        if active_login:
            return JsonResponse({'status': 'error', 'message': 'This company is already logged in.'}, status=200)

        if not company_profile.is_multiple_branches:
            region_branch = None

        CompanyLogin.objects.create(
            company_code=company_code,
            company=company,
            region_branch=region_branch,
            headquarters=headquarters,  # Country value from the form
            profile_photo=profile_photo,
            created_at=now()
        )

        return JsonResponse({'status': 'success', 'message': 'Company login saved successfully.'}, status=201)

    return JsonResponse({'message': 'Missing login credentials.'}, status=400)



def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

def setting(request):
    return render(request, 'setting.html')

from .models import UserLogin


def get_active_user_login(request):
    employee_code = request.GET.get('employee_code')  # instead of session
    if not employee_code:
        return JsonResponse({'message': 'Employee code not provided.'}, status=400)
    
    try:
        active_login = UserLogin.objects.filter(
            employee_code=employee_code,
            log_out__isnull=True
        ).order_by('-created_at').first()
        
        if not active_login:
            return JsonResponse({'message': 'No active login found.'}, status=404)
        
        data = {
            'username': active_login.username,
            'employee_code': active_login.employee_code,
            'company_code': active_login.company_code,
            'region_branch': active_login.region_branch or '',
            'region_code': active_login.region_code or ''
        }
        return JsonResponse({'status': 'success', 'data': data}, status=200)
    except Exception as e:
        return JsonResponse({'message': f'Error retrieving login data: {str(e)}'}, status=500)



@csrf_exempt
@require_POST
def save_table_data(request):
    """
    Saves table data to UserCreationModel. Expects JSON with 'table_data' including company_code.
    Validates company_code against UserProfile, required fields, date formats, and assign_admin_role.
    Uses create() since employee_code is auto-generated by the model.
    """
    try:
        data = json.loads(request.body)
        table_data = data.get('table_data', [])
        if not table_data:
            return JsonResponse({'status': 'error', 'message': 'No table data provided.'}, status=400)

        valid_admin_roles = {'dpt', 'cpy', 'hra', 'gma', ''}
        date_fields = ['date_of_birth', 'employment_start_date']
        errors = []

        for row in table_data:
            try:
                with transaction.atomic():  # Each row wrapped in its own atomic block
                    # Validate company_code
                    company_code = row.get('company_code')
                    if not company_code:
                        errors.append('Company code is required.')
                        continue
                    try:
                        user_profile = UserProfile.objects.get(company_code=company_code)
                    except UserProfile.DoesNotExist:
                        errors.append(f'Invalid company code: {company_code}.')
                        continue

                    # Optional: Validate presence of reports_to_position only if required
                    reports_to_position = row.get('reports_to_position')  # Now optional

                    # Validate date fields
                    for date_field in date_fields:
                        date_value = row.get(date_field)
                        if date_value:
                            try:
                                datetime.strptime(date_value, '%Y-%m-%d')
                            except ValueError:
                                errors.append(
                                    f'Invalid {date_field} format: {date_value}. Must be YYYY-MM-DD.'
                                )
                                continue

                    # Validate assign_admin_role
                    assign_admin_role = row.get('assign_admin_role', '')
                    if assign_admin_role not in valid_admin_roles:
                        errors.append(
                            f'Invalid admin role: {assign_admin_role}. Must be one of {list(valid_admin_roles)}.'
                        )
                        continue

                    # Prepare data for creation
                    user_data = {
                        'company_code': user_profile,
                        'first_name': row.get('first_name') or None,
                        'last_name': row.get('last_name') or None,
                        'employee_name': row.get('employee_name') or None,
                        'date_of_birth': row.get('date_of_birth') or None,
                        'team_or_division': row.get('team_or_division') or None,
                        'employee_email': row.get('employee_email') or None,
                        'phone_number': row.get('phone_number') or None,
                        'employee_gender': row.get('employee_gender') or None,
                        'region_branch': row.get('region_branch') or None,
                        'employment_type': row.get('employment_type') or None,
                        'employee_status': row.get('employee_status') or None,
                        'department': row.get('department') or None,
                        'position': row.get('position') or None,
                        'is_employee_active': row.get('is_employee_active', True),
                        'reason_for_inactivity': row.get('reason_for_inactivity') or None,
                        'reports_to': row.get('reports_to') or None,
                        'reports_to_position': reports_to_position or None,
                        'employment_start_date': row.get('employment_start_date') or None,
                        'pre_existing_employee_code': row.get('pre_existing_employee_code') or None,
                        'last_login': row.get('last_login') or None,
                        'reports_to_code': row.get('reports_to_code') or None,
                        'assign_admin_role': assign_admin_role or None
                    }

                    logger.debug(f"Creating UserCreationModel with data: {user_data}")
                    UserCreationModel.objects.create(**user_data)

            except Exception as e:
                logger.error(f"Error processing row: {str(e)}")
                errors.append(f'Error creating user: {str(e)}')

        if errors:
            return JsonResponse({'status': 'error', 'message': errors}, status=400)

        return JsonResponse({'status': 'success', 'message': 'Table data saved successfully!'})

    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def get_admin_employees(request):
    company_code = request.GET.get('company_code')

    if not company_code:
        return JsonResponse({'error': 'Company code is required'}, status=400)

    try:
        admin_employees = UserCreationModel.objects.filter(
            company_code=company_code, 
            assign_admin_role__isnull=False
        ).exclude(assign_admin_role='').values('employee_name', 'position')

        return JsonResponse(list(admin_employees), safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No employees found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@require_POST
@csrf_exempt
def create_goal(request):
    try:
        data = json.loads(request.body)

        employee_code = data.get('employee_code')
        employee_name = data.get('employee_name')
        title = data.get('title')
        description = data.get('description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not all([employee_code, employee_name, title, description, start_date, end_date]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if end_date < start_date:
            return JsonResponse({'status': 'error', 'message': 'End date must be after start date.'}, status=400)

        goal = Goal(
            employee_code=employee_code,
            employee_name=employee_name,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        goal.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Goal created successfully.',
            'goal_id': goal.id,
            'duration': goal.duration
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)


@require_POST
@csrf_exempt
def register_course(request):
    try:
        data = json.loads(request.body)

        # Extract fields from request
        employee_code = data.get('employee_code')
        employee_name = data.get('employee_name')
        course_name = data.get('course_name')
        institution = data.get('institution')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        progress = data.get('progress', 0)

        # Check for required fields
        if not all([employee_code, employee_name, course_name, institution, start_date, end_date]):
            return JsonResponse({"error": "All fields are required."}, status=400)

        # Field length validation
        if len(course_name) > 255 or len(institution) > 255 or len(employee_name) > 255:
            return JsonResponse({"error": "One or more fields exceed length limits."}, status=400)

        # Progress must be within 0 to 100
        if not (0 <= progress <= 100):
            return JsonResponse({"error": "Progress must be between 0 and 100."}, status=400)

        # Validate and parse dates
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        if start_date_obj > end_date_obj:
            return JsonResponse({"error": "Start date must be before end date."}, status=400)

        # Recalculate duration (approximate months)
        delta_days = (end_date_obj - start_date_obj).days
        duration_months = max(delta_days // 30, 1)  # Minimum 1 month
        duration = f"{duration_months} months"

        # Prevent duplicate course entries for same employee
        if Course.objects.filter(employee_code=employee_code, course_name=course_name).exists():
            return JsonResponse({"error": "Course already registered."}, status=400)

        # Save course to database
        course = Course(
            employee_code=employee_code,
            employee_name=employee_name,
            course_name=course_name,
            institution=institution,
            start_date=start_date_obj,
            end_date=end_date_obj,
            progress=progress,
            duration=duration
        )
        course.save()

        return JsonResponse({
            "status": "Course registered successfully",
            "course_name": course.course_name,
            "duration": duration
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    
@require_GET
def get_goals_by_employee_code(request):
    employee_code = request.GET.get('employee_code')
    if not employee_code:
        return JsonResponse({'status': 'error', 'message': 'employee_code is required'}, status=400)

    goals = Goal.objects.filter(employee_code=employee_code).values(
        'id', 'title', 'description', 'start_date', 'end_date', 'duration', 'progress', 'is_active', 'created_at'
    )

    return JsonResponse({'status': 'success', 'goals': list(goals)}, status=200)


@require_GET
def get_courses_by_employee_code(request):
    employee_code = request.GET.get('employee_code')
    if not employee_code:
        return JsonResponse({'status': 'error', 'message': 'employee_code is required'}, status=400)

    courses = Course.objects.filter(employee_code=employee_code).values(
        'id', 'course_name', 'institution', 'duration', 'progress',
        'start_date', 'end_date', 'employee_name', 'is_active', 'created_at', 'updated_at'
    )

    return JsonResponse({'status': 'success', 'courses': list(courses)}, status=200)

@require_POST
@csrf_exempt
def save_regions(request):
    try:
        data = json.loads(request.body)
        company_code_str = data.get('company_code')
        regions = data.get('regions', [])

        if not company_code_str or not regions:
            return JsonResponse({'message': 'Missing company code or regions'}, status=400)

        try:
            user_profile = UserProfile.objects.get(company_code=company_code_str)
        except UserProfile.DoesNotExist:
            return JsonResponse({'message': 'Invalid company code'}, status=400)

        saved_regions = []

        for region_name in regions:
            region_name = region_name.strip()
            if not region_name:
                continue

            region, created = Region.objects.get_or_create(
                company_code=user_profile,
                region_branch=region_name,
                defaults={'user_select': 1}
            )
            if not created:
                region.user_select += 1
                region.save()

            saved_regions.append({
                'region_branch': region.region_branch,
                'region_code': region.region_code,
            })

        return JsonResponse({
            'status': 'success',
            'message': 'Regions saved',
            'company': user_profile.company,
            'company_code': user_profile.company_code,
            'regions': saved_regions,
        })

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)


@csrf_exempt
def populate_user_profiles(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body)

        # Required input fields
        start_date_str = data.get("start-date")
        end_date_str = data.get("end-date")

        if not start_date_str or not end_date_str:
            return JsonResponse({"error": "start-date and end-date are required"}, status=400)

        # Parse date fields
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Determine industry value
        industry = data.get("industry", "").strip()
        other_industry = data.get("otherIndustry", "").strip()
        industry_value = other_industry if industry.lower() == "other" else industry

        # Calculate user count
        selected_user_option = data.get("num-users", "").strip()
        custom_num_users = data.get("custom-num-users", "").strip()
        user_count = (
            int(custom_num_users)
            if selected_user_option.lower() == "custom" and custom_num_users
            else int(selected_user_option) if selected_user_option.isdigit()
            else 0
        )

        # Full address
        street = data.get("street-address", "").strip()
        city = data.get("city", "").strip()
        full_address = f"{street}, {city}".strip(", ")

        # Handle regions
        region_list = data.get("region", [])
        is_multiple = bool(data.get("region-input"))
        headquarters = region_list[0].strip() if not is_multiple and region_list else ""

        # Create and save profile
        profile = UserProfile(
            is_multiple_branches=is_multiple,
            company=data.get("company", "").strip(),
            country=data.get("country", "").strip(),
            headquarters=headquarters,
            start_date=start_date,
            end_date=end_date,
            review_cycle=data.get("review-cycle", "").strip(),
            payment_plan=data.get("payment-cycle", "").strip(),
            user_select=user_count,
            email=data.get("email", "").strip(),
            phone_number=data.get("phone", "").strip(),
            industry=industry_value,
            company_address=full_address,
            partner_code=data.get("partnerCode", "").strip(),
            activity_status="active",
            installment_amount=float(data.get("installment-amount", "").replace(",", "")) if data.get("installment-amount") else None,
            total_payable_amount=float(data.get("total-payable-amount", "").replace(",", "")) if data.get("total-payable-amount") else None,
            current_usd_exchange_rate=float(data.get("current-exchange-rate")) if data.get("current-exchange-rate") else None,
            review_number=int(data.get("total-reviews")) if data.get("total-reviews") else None,
            currency=data.get("currency", "").strip(),
        )

        profile.save()

        print(f"Profile created: Company Code={profile.company_code}")

        return JsonResponse({
            "status": "success",
            "message": f"Company profile created successfully for {profile.company}",
            "company_code": profile.company_code,
            "company": profile.company,
        })

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Exception occurred while creating company profile:")
        print(traceback_str)
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "trace": traceback_str
        }, status=500)



def get_regions_by_company(request):
    # Extract company_code_id from the request parameters (GET request)
    company_code_id = request.GET.get('company_code_id')

    if not company_code_id:
        return JsonResponse({'status': 'error', 'message': 'company_code_id is required.'}, status=400)

    try:
        # Filter regions by company_code_id
        regions = Region.objects.filter(company_code_id=company_code_id)

        # Create a list of dictionaries with region_code and region_branch
        region_list = [
            {'region_code': region.region_code, 'region_branch': region.region_branch}
            for region in regions
        ]

        # Return the list as a JSON response
        return JsonResponse({'status': 'success', 'regions': region_list})

    except Region.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No regions found for the given company_code_id.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)
    


def company_graph(request):
    # Default filter values
    default_start = (timezone.now() - timedelta(days=365)).date()
    default_end = timezone.now().date()

    # Get filter parameters
    company_filter = request.GET.get('company', 'all')
    region_filter = request.GET.get('region', 'all')
    raw_start = request.GET.get('start_date', '')
    raw_end = request.GET.get('end_date', '')  # Fixed syntax error here

    # Date parsing
    try:
        start_date = datetime.strptime(raw_start, '%Y-%m-%d').date() if raw_start else default_start
        end_date = datetime.strptime(raw_end, '%Y-%m-%d').date() if raw_end else default_end
    except ValueError:
        start_date, end_date = default_start, default_end

    if end_date < start_date:
        start_date, end_date = end_date, start_date

    # Base querysets
    companies = UserProfile.objects.filter(
        date_created__gte=start_date,
        date_created__lte=end_date
    )
    regions = Region.objects.all()
    users = UserCreationModel.objects.filter(
        date_created__gte=start_date,
        date_created__lte=end_date
    )

    # Apply filters
    if company_filter != 'all':
        companies = companies.filter(company=company_filter)
        regions = regions.filter(company_code__company=company_filter)
        users = users.filter(company_code__company=company_filter)
    
    if region_filter != 'all':
        regions = regions.filter(region_branch=region_filter)
        companies = companies.filter(company_code__in=regions.values('company_code'))
        users = users.filter(company_code__in=regions.values('company_code'))

    # Default chart data
    default_chart_data = {
        'total_companies': 0,
        'companies_with_regions': 0,
        'total_users': 0,
        'total_monthly_revenue': 0,
        'total_expected_revenue': 0,
        'avg_regions_per_company': 0,
        'trend_labels': [],
        'revenue_values': [],
        'company_growth': [],
        'peak_month': 'N/A',
        'peak_revenue': 0,
        'peak_percentage': 0,
        'region_dist_labels': ['No Regions', '1 Region', '2+ Regions'],
        'region_dist_values': [0, 0, 0],
        'payment_cycle_labels': [],
        'payment_cycle_values': [],
        'country_labels': [],
        'country_values': [],
        'continent_labels': [],
        'continent_values': [],
        'city_labels': [],
        'city_values': [],
        'industry_labels': [],
        'industry_values': [],
        'company_status_labels': [],
        'company_status_values': [],
        'company_details': [],
        'all_companies': [],
        'all_regions': [],
        'current_filters': {
            'company': company_filter,
            'region': region_filter,
            'start_date': start_date,
            'end_date': end_date
        }
    }

    try:
        # Key Metrics
        total_companies = companies.count()
        companies_with_regions = regions.values('company_code').distinct().count()
        total_users = users.count() if region_filter == 'all' else regions.aggregate(total=Sum('user_select'))['total'] or 0
        avg_regions_per_company = regions.values('company_code').annotate(
            region_count=Count('region_code')
        ).aggregate(avg=Avg('region_count'))['avg'] or 0

        # Financial Calculations
        zar_to_usd_rate = 0.055
        base_usd_amount = 50 * zar_to_usd_rate  # $2.75 per user per review
        total_monthly_revenue = 0
        total_expected_revenue = 0
        company_details = []

        if region_filter != 'all':
            # Region-specific metrics
            for region in regions:
                parent_company = region.company_code
                user_count = region.user_select or 0
                review_cycle = parent_company.review_cycle or 'monthly'
                start_date_company = parent_company.start_date
                end_date_company = parent_company.end_date
                if start_date_company and end_date_company and end_date_company >= start_date_company:
                    time_diff = (end_date_company - start_date_company).days
                    if review_cycle == 'monthly':
                        total_reviews = max(1, time_diff // 30)
                    elif review_cycle == 'quarterly':
                        total_reviews = max(1, time_diff // 90)
                    elif review_cycle == 'bi-annually':
                        total_reviews = max(1, time_diff // 180)
                    elif review_cycle == 'annually':
                        total_reviews = max(1, time_diff // 365)
                    else:
                        total_reviews = 1
                else:
                    total_reviews = 1

                currency_code = parent_company.currency or 'USD'
                exchange_rate = float(parent_company.current_usd_exchange_rate) if parent_company.current_usd_exchange_rate else 1.0
                if currency_code != 'USD' and not parent_company.current_usd_exchange_rate:
                    try:
                        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                        exchange_rate = response.json()['rates'].get(currency_code, 1.0)
                    except:
                        exchange_rate = 1.0

                amount_in_currency = base_usd_amount * exchange_rate
                total_payable = total_reviews * user_count * amount_in_currency
                if parent_company.payment_plan == 'monthly' and total_reviews > 0:
                    installment_amount = total_payable / total_reviews
                else:
                    installment_amount = total_payable

                total_payable_usd = total_payable / exchange_rate if exchange_rate != 0 else total_payable
                installment_usd = installment_amount / exchange_rate if exchange_rate != 0 else installment_amount

                total_expected_revenue += total_payable_usd
                total_monthly_revenue += installment_usd

                company_details.append({
                    'name': f"{parent_company.company} ({region.region_branch})",
                    'regions': [region.region_branch],
                    'users': user_count,
                    'total_payable': round(total_payable, 2),
                    'monthly_installment': round(installment_amount, 2),
                    'currency': currency_code
                })
        else:
            # Company-level metrics
            for company in companies:
                company_users = users.filter(company_code=company.company_code).count()
                user_count = company.user_select or company_users or 0
                review_cycle = company.review_cycle or 'monthly'
                start_date_company = company.start_date
                end_date_company = company.end_date
                if start_date_company and end_date_company and end_date_company >= start_date_company:
                    time_diff = (end_date_company - start_date_company).days
                    if review_cycle == 'monthly':
                        total_reviews = max(1, time_diff // 30)
                    elif review_cycle == 'quarterly':
                        total_reviews = max(1, time_diff // 90)
                    elif review_cycle == 'bi-annually':
                        total_reviews = max(1, time_diff // 180)
                    elif review_cycle == 'annually':
                        total_reviews = max(1, time_diff // 365)
                    else:
                        total_reviews = 1
                else:
                    total_reviews = 1

                currency_code = company.currency or 'USD'
                exchange_rate = float(company.current_usd_exchange_rate) if company.current_usd_exchange_rate else 1.0
                if currency_code != 'USD' and not company.current_usd_exchange_rate:
                    try:
                        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                        exchange_rate = response.json()['rates'].get(currency_code, 1.0)
                    except:
                        exchange_rate = 1.0

                amount_in_currency = base_usd_amount * exchange_rate
                total_payable = total_reviews * user_count * amount_in_currency
                if company.payment_plan == 'monthly' and total_reviews > 0:
                    installment_amount = total_payable / total_reviews
                else:
                    installment_amount = total_payable

                total_payable_usd = total_payable / exchange_rate if exchange_rate != 0 else total_payable
                installment_usd = installment_amount / exchange_rate if exchange_rate != 0 else installment_amount

                total_expected_revenue += total_payable_usd
                total_monthly_revenue += installment_usd

                company_regions = regions.filter(company_code=company.company_code).values_list('region_branch', flat=True)
                company_details.append({
                    'name': company.company,
                    'regions': list(company_regions),
                    'users': user_count,
                    'total_payable': round(total_payable, 2),
                    'monthly_installment': round(installment_amount, 2),
                    'currency': currency_code
                })

        # Trend Data
        trend_labels, revenue_values, company_growth = [], [], []
        current_date = start_date
        peak_revenue, peak_month, peak_percentage = 0, 'N/A', 0
        annual_revenue = total_monthly_revenue
        while current_date <= end_date:
            next_date = current_date + relativedelta(months=1)
            monthly_revenue = 0
            if region_filter != 'all':
                for region in regions.filter(
                    created_date__gte=current_date,
                    created_date__lt=next_date
                ):
                    user_count = region.user_select or 0
                    parent_company = region.company_code
                    exchange_rate = float(parent_company.current_usd_exchange_rate) if parent_company.current_usd_exchange_rate else 1.0
                    monthly_revenue += (base_usd_amount * user_count) / exchange_rate
            else:
                for company in companies.filter(
                    date_created__gte=current_date,
                    date_created__lt=next_date
                ):
                    company_users = users.filter(company_code=company.company_code).count()
                    user_count = company.user_select or company_users or 0
                    exchange_rate = float(company.current_usd_exchange_rate) if company.current_usd_exchange_rate else 1.0
                    monthly_revenue += (base_usd_amount * user_count) / exchange_rate
            company_count = companies.filter(
                date_created__gte=current_date,
                date_created__lt=next_date
            ).count()
            month_label = current_date.strftime('%b %Y')
            trend_labels.append(month_label)
            revenue_values.append(round(monthly_revenue, 2))
            company_growth.append(company_count)
            if monthly_revenue > peak_revenue:
                peak_revenue = monthly_revenue
                peak_month = month_label
                peak_percentage = round((monthly_revenue / annual_revenue * 100) if annual_revenue > 0 else 0, 1)
            current_date = next_date

        # Region Distribution
        region_counts = regions.values('company_code').annotate(
            region_count=Count('region_code')
        ).values('region_count')
        no_regions = companies.exclude(company_code__in=regions.values('company_code')).count()
        one_region = len([r for r in region_counts if r['region_count'] == 1])
        multi_regions = len([r for r in region_counts if r['region_count'] >= 2])
        region_dist_labels = ['No Regions', '1 Region', '2+ Regions']
        region_dist_values = [no_regions, one_region, multi_regions]

        # Payment Cycle Distribution
        payment_counts = companies.values('payment_plan').annotate(count=Count('company_code'))
        total_payment = sum(p['count'] for p in payment_counts)
        payment_cycle_labels = [p['payment_plan'].capitalize() or 'Unknown' for p in payment_counts]
        payment_cycle_values = [round((p['count'] / total_payment) * 100, 1) for p in payment_counts] if total_payment > 0 else []

        # Geographic Distribution
        # Country Distribution
        country_counts = companies.values('country').annotate(count=Count('company_code')).order_by('-count')
        country_labels = [c['country'] or 'Unknown' for c in country_counts]
        country_values = [c['count'] for c in country_counts]

        # Continent Distribution (mapped from country)
        continent_map = {
            'South Africa': 'Africa',
            'United Arab Emirates': 'Asia',
            'USA': 'North America',
            # Add more mappings as needed based on actual data
        }
        continent_counts = {}
        for company in companies:
            country = company.country or 'Unknown'
            continent = continent_map.get(country, 'Other')
            continent_counts[continent] = continent_counts.get(continent, 0) + 1
        continent_labels = list(continent_counts.keys())
        continent_values = list(continent_counts.values())

        # City Distribution (from regions)
        city_counts = regions.values('region_branch').annotate(count=Count('region_code')).order_by('-count')
        city_labels = [c['region_branch'] or 'Unknown' for c in city_counts]
        city_values = [c['count'] for c in city_counts]

        # Industry Distribution
        industry_counts = companies.values('industry').annotate(count=Count('company_code')).order_by('-count')
        industry_labels = [ind['industry'] or 'Unknown' for ind in industry_counts]
        industry_values = [ind['count'] for ind in industry_counts]

        # Company Activity Status
        status_counts = companies.values('activity_status').annotate(count=Count('company_code'))
        total_status = sum(status['count'] for status in status_counts)
        company_status_labels = [status['activity_status'].capitalize() for status in status_counts]
        company_status_values = [round((status['count'] / total_status) * 100, 1) for status in status_counts] if total_status > 0 else []

        # All regions for dropdown
        all_regions = [
            {'region_branch': r.region_branch, 'company': r.company_code.company}
            for r in Region.objects.all()
        ]

        chart_data = {
            'total_companies': total_companies,
            'companies_with_regions': companies_with_regions,
            'total_users': total_users,
            'total_monthly_revenue': round(total_monthly_revenue, 2),
            'total_expected_revenue': round(total_expected_revenue, 2),
            'avg_regions_per_company': round(avg_regions_per_company, 1),
            'trend_labels': trend_labels,
            'revenue_values': revenue_values,
            'company_growth': company_growth,
            'peak_month': peak_month,
            'peak_revenue': peak_revenue,
            'peak_percentage': peak_percentage,
            'region_dist_labels': region_dist_labels,
            'region_dist_values': region_dist_values,
            'payment_cycle_labels': payment_cycle_labels,
            'payment_cycle_values': payment_cycle_values,
            'country_labels': country_labels,
            'country_values': country_values,
            'continent_labels': continent_labels,
            'continent_values': continent_values,
            'city_labels': city_labels,
            'city_values': city_values,
            'industry_labels': industry_labels,
            'industry_values': industry_values,
            'company_status_labels': company_status_labels,
            'company_status_values': company_status_values,
            'company_details': company_details,
            'all_companies': list(companies.values_list('company', flat=True).distinct()),
            'all_regions': all_regions,
            'current_filters': {
                'company': company_filter,
                'region': region_filter,
                'start_date': start_date,
                'end_date': end_date
            }
        }
    except Exception as e:
        print(f"Error querying metrics: {e}")
        chart_data = default_chart_data

    return render(request, 'company_graph.html', chart_data)






@csrf_exempt
@require_POST
def generate_review_periods(request):
    try:
        data = json.loads(request.body)

        # Extract values from frontend
        company_code = data.get('company_code')
        company = data.get('company')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        review_count = int(data.get('review_number', 1))

        if not all([company_code, company, start_date_str, end_date_str]):
            return HttpResponseBadRequest("Missing one or more required fields.")

        # Parse date inputs
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        date_created = timezone.now()  # Timestamp generated at save time

        # Get UserProfile for FK
        user_profile = get_object_or_404(UserProfile, company_code=company_code)

        total_days = (end_date - start_date).days + 1
        days_per_review = total_days // review_count
        extra_days = total_days % review_count

        with transaction.atomic():
            current_start = start_date

            for i in range(1, review_count + 1):
                length = days_per_review + (1 if i <= extra_days else 0)
                cycle_start = current_start
                cycle_end = cycle_start + timedelta(days=length - 1)
                company_review_code = f"{company_code}-{i}"

                ReviewPeriod.objects.update_or_create(
                    company_code=user_profile,
                    review=i,
                    defaults={
                        'company': company,
                        'period_start_date': cycle_start,
                        'period_end_date': cycle_end,
                        'date_created': date_created,
                        'company_review_code': company_review_code,
                    }
                )

                current_start = cycle_end + timedelta(days=1)

        return JsonResponse({"message": "Review periods created successfully."}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def dash_staff(request):
    return render(request, 'dash_staff.html')


@csrf_exempt
def chat_message_view(request):
    if request.method == "POST":
        data = json.loads(request.body)

        session_id = data.get("session_id")
        message = data.get("message")
        sender = data.get("sender")  # "user" or "bot"

        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id)
        else:
            session, _ = ChatSession.objects.get_or_create(session_id=session_id)

        ChatMessage.objects.create(
            session=session,
            sender=sender,
            message=message,
            timestamp=timezone.now()
        )

        if sender == "user":
            reply = answer_question(message)
        else:
            reply = None

        return JsonResponse({
            "success": True,
            "session_id": session.session_id,
            "reply": reply
        })

    return JsonResponse({"error": "Invalid request"}, status=400)



@require_GET
def cascading_goals(request):
    company_code = request.GET.get('company_code')
    region_code = request.GET.get('region_code')

    if not company_code and not region_code:
        return JsonResponse({'error': 'Either company_code or region_code is required.'}, status=400)

    try:
        if company_code:
            goals = StrategicGoals.objects.filter(company_code=company_code, goal_activity='current')
        else:
            goals = StrategicGoals.objects.filter(region_code=region_code, goal_activity='current')

        goals_data = [
            {
                'id': goal.id,
                'company_code': goal.company_code,
                'goal_type': goal.goal_type,
                'strategic_goal': goal.strategic_goal,
                'created_date': goal.created_date.isoformat(),
                'region_code': goal.region_code,
                'goal_activity': goal.goal_activity,
                'department': goal.department,
                'due_date': goal.due_date.isoformat() if goal.due_date else None,
                'weight': float(goal.weight) if goal.weight else None,
                'username': goal.username,
                'region_branch': goal.region_branch,
                'strategy_code': goal.strategy_code
            }
            for goal in goals
        ]

        return JsonResponse({'results': goals_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


from .models import UoM

@require_GET
def get_uoms(request):
    uoms = UoM.objects.all()
    data = [
        {
            "id": uom.id,
            "name": uom.name,
            "symbol": uom.symbol,
            "description": uom.description,
            "category": uom.category
        }
        for uom in uoms
    ]
    return JsonResponse(data, safe=False)




@require_GET
def non_performance_reasons_view(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, reason_category, description, explanation, is_active
                FROM non_performance_reasons
                WHERE is_active = TRUE
                ORDER BY reason_category
            """)
            # Fetch column names
            columns = [col[0] for col in cursor.description]
            # Fetch all rows and convert to list of dicts
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
        
        return JsonResponse({
            'status': 'success',
            'data': results
        }, safe=True)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)



def management_hub_dashboard(request):
    """
    Company-specific manager dashboard view, displaying performance insights for direct reports.
    Uses session-stored employee_code from UserLogin to fetch manager data and populate employee name filter for Select2.
    Includes filters for department, review cycle, employee name, date, company code, branch, and region.
    """
    # Get employee_code from session
    employee_code = request.session.get('employee_code')
    if not employee_code:
        return render(request, 'dash_mgmt.html', {'error': 'No active session. Please log in.'})

    # Fetch manager's UserCreationModel data
    try:
        manager_data = UserCreationModel.objects.get(employee_code=employee_code)
    except UserCreationModel.DoesNotExist:
        return render(request, 'dash_mgmt.html', {'error': 'Manager not found in UserCreationModel'})

    company_code = manager_data.company_code.company_code
    manager_name = manager_data.employee_name

    # Verify active login in UserLogin
    try:
        active_login = UserLogin.objects.get(employee_code=employee_code, log_out__isnull=True)
    except UserLogin.DoesNotExist:
        return render(request, 'dash_mgmt.html', {'error': 'No active login session found.'})

    # Filter employees reporting to the manager
    employees = UserCreationModel.objects.filter(
        reports_to=manager_name,
        reports_to_code=employee_code,
        company_code=company_code,
        is_employee_active=True
    )

    # Get filter parameters from GET request (from form)
    department_filter = request.GET.get('department_name', '')
    review_cycle_filter = request.GET.get('review_cycle', '')
    employee_name_filter = request.GET.get('employee_name', '')
    start_date_filter = request.GET.get('start_date', '')
    end_date_filter = request.GET.get('end_date', '')
    company_code_filter = request.GET.get('company_code', company_code)  # Default to manager's company
    branch_code_filter = request.GET.get('branch_code', '')
    region_branch_filter = request.GET.get('region_branch', '')

    # Validate company code
    if company_code_filter != company_code:
        return render(request, 'dash_mgmt.html', {'error': 'Unauthorized company code'})

    # Apply filters to employees
    if department_filter:
        employees = employees.filter(department=department_filter)
    if employee_name_filter:
        employees = employees.filter(employee_name__icontains=employee_name_filter)
    if branch_code_filter:
        employees = employees.filter(team_or_division__icontains=branch_code_filter)
    if region_branch_filter:
        employees = employees.filter(region_branch__icontains=region_branch_filter)

    # Apply filters to assessments
    assessments = PerfMgmtAssessment.objects.filter(employee_code__in=[e.employee_code for e in employees])
    if review_cycle_filter:
        try:
            review_period = ReviewPeriod.objects.get(company_review_code=review_cycle_filter, company_code=company_code)
            assessments = assessments.filter(
                date_self_appraisal_completed__range=(
                    review_period.period_start_date,
                    review_period.period_end_date
                )
            )
        except ReviewPeriod.DoesNotExist:
            pass  # Ignore invalid review cycle
    if start_date_filter and end_date_filter:
        try:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()
            assessments = assessments.filter(
                date_self_appraisal_completed__range=(start_date, end_date)
            )
        except ValueError:
            pass  # Ignore invalid dates

    # Get filter options
    departments = employees.values('department').distinct()
    dept_names = [d['department'] for d in departments]
    review_periods = ReviewPeriod.objects.filter(company_code=company_code).order_by('period_start_date')
    review_cycles = [p.company_review_code for p in review_periods]
    employee_names = [e.employee_name for e in employees]
    branch_codes = employees.values('team_or_division').distinct()
    branch_codes = [b['team_or_division'] for b in branch_codes if b['team_or_division']]
    region_branches = employees.values('region_branch').distinct()
    region_branches = [r['region_branch'] for r in region_branches if r['region_branch']]

    # Get company name
    try:
        company = UserProfile.objects.get(company_code=company_code).company
    except UserProfile.DoesNotExist:
        company = 'Unknown Company'

    # 1. Employee Performance Insights
    appraisal_data = []
    for employee in employees:
        emp_assessments = assessments.filter(employee_code=employee.employee_code)
        self_avg = emp_assessments.aggregate(avg_self=Avg('deliverable_self_score'))['avg_self'] or 0
        assessor_avg = emp_assessments.aggregate(avg_assessor=Avg('deliverable_assessor_score'))['avg_assessor'] or 0
        appraisal_data.append({
            'employee_name': employee.employee_name,
            'employee_code': employee.employee_code,
            'department': employee.department,
            'position': employee.position,
            'self_score': round(self_avg, 1),
            'assessor_score': round(assessor_avg, 1),
            'gap': round(self_avg - assessor_avg, 1)
        })

    # Score Trends Over Time
    score_trends = []
    for employee in employees:
        emp_trends = []
        for period in review_periods:
            period_assessments = assessments.filter(
                employee_code=employee.employee_code,
                date_self_appraisal_completed__range=(
                    period.period_start_date, period.period_end_date
                )
            )
            avg_score = period_assessments.aggregate(
                avg_assessor=Avg('deliverable_assessor_score')
            )['avg_assessor'] or 0
            emp_trends.append({
                'review_code': period.company_review_code,
                'score': round(avg_score, 1)
            })
        score_trends.append({
            'employee_name': employee.employee_name,
            'trends': emp_trends
        })

    # Target vs. Actual Performance
    target_actual = []
    for kpi in assessments.values('kpi').distinct():
        kpi_assessments = assessments.filter(kpi=kpi['kpi'])
        short_term = kpi_assessments.aggregate(
            avg_actual=Avg('short_term_actual'),
            avg_target=Avg('short_term_target')
        )
        intermediate = kpi_assessments.aggregate(
            avg_actual=Avg('intermediate_term_actual'),
            avg_target=Avg('intermediate_term_target')
        )
        long_term = kpi_assessments.aggregate(
            avg_actual=Avg('long_term_actual'),
            avg_target=Avg('long_term_target')
        )
        target_actual.append({
            'kpi': kpi['kpi'],
            'short_term': {
                'actual': round(short_term['avg_actual'] or 0, 1),
                'target': round(short_term['avg_target'] or 0, 1)
            },
            'intermediate': {
                'actual': round(intermediate['avg_actual'] or 0, 1),
                'target': round(intermediate['avg_target'] or 0, 1)
            },
            'long_term': {
                'actual': round(long_term['avg_actual'] or 0, 1),
                'target': round(long_term['avg_target'] or 0, 1)
            }
        })

    # Weight vs. Score Alignment
    weight_score_alignment = []
    for deliverable in assessments.values('deliverable').distinct():
        del_assessments = assessments.filter(deliverable=deliverable['deliverable'])
        avg_weight = del_assessments.aggregate(avg_weight=Avg('deliverable_weight'))['avg_weight'] or 0
        avg_score = del_assessments.aggregate(avg_score=Avg('deliverable_assessor_score'))['avg_score'] or 0
        weight_score_alignment.append({
            'deliverable': deliverable['deliverable'],
            'weight': round(avg_weight, 1),
            'score': round(avg_score, 1),
            'impact': round(avg_weight * avg_score, 1)
        })

    # 2. Department-Level Insights
    dept_performance = []
    for dept in dept_names:
        dept_employees = employees.filter(department=dept)
        dept_codes = [e.employee_code for e in dept_employees]
        dept_assessments = assessments.filter(employee_code__in=dept_codes)
        avg_score = dept_assessments.aggregate(avg_score=Avg('deliverable_assessor_score'))['avg_score'] or 0
        dept_performance.append({
            'department': dept,
            'avg_score': round(avg_score, 1),
            'employee_count': len(dept_codes)
        })

    # Shared KPI Performance
    shared_kpi_performance = []
    for kpi in assessments.values('kpi').annotate(count=Count('employee_code')).filter(count__gt=1):
        kpi_assessments = assessments.filter(kpi=kpi['kpi'])
        for employee in employees:
            emp_kpi_assessments = kpi_assessments.filter(employee_code=employee.employee_code)
            if emp_kpi_assessments.exists():
                avg_score = emp_kpi_assessments.aggregate(
                    avg_score=Avg('deliverable_assessor_score')
                )['avg_score'] or 0
                shared_kpi_performance.append({
                    'kpi': kpi['kpi'],
                    'employee_name': employee.employee_name,
                    'department': employee.department,
                    'score': round(avg_score, 1)
                })

    # Skill Gaps
    development_needs = []
    low_score_deliverables = assessments.filter(
        Q(deliverable__icontains='training') | Q(deliverable__icontains='development'),
        deliverable_assessor_score__lte=2
    ).values('deliverable').annotate(
        avg_score=Avg('deliverable_assessor_score'),
        count=Count('id')
    )
    for item in low_score_deliverables:
        development_needs.append({
            'skill': item['deliverable'],
            'gap': round((5 - item['avg_score']) * 20, 1),
            'count': item['count']
        })

    # UoM Consistency
    uom_consistency = []
    for kpi in assessments.values('kpi').distinct():
        kpi_uoms = assessments.filter(kpi=kpi['kpi']).values('uom').distinct()
        uom_consistency.append({
            'kpi': kpi['kpi'],
            'uoms': [u['uom'] for u in kpi_uoms],
            'is_consistent': len(kpi_uoms) == 1
        })

    # 3. Strategic Goal & KPI Insights
    kpi_metrics = {
        'achievement_rate': 0,
        'on_track': 0,
        'gaps': 0,
        'progress_matrix': []
    }
    kpi_groups = assessments.values('kpi').annotate(
        avg_actual=Avg('short_term_actual'),
        avg_target=Avg('short_term_target')
    )
    total_kpis = len(kpi_groups)
    on_track_count = sum(1 for kpi in kpi_groups if kpi['avg_actual'] and kpi['avg_target'] and kpi['avg_actual'] >= kpi['avg_target'])
    kpi_metrics['achievement_rate'] = round((on_track_count / total_kpis * 100) if total_kpis else 0, 1)
    kpi_metrics['on_track'] = kpi_metrics['achievement_rate']
    kpi_metrics['gaps'] = round(100 - kpi_metrics['on_track'], 1)

    # Progress Matrix
    review_periods_list = review_periods.values('company_review_code').distinct()
    progress_matrix = [[0] * len(dept_names) for _ in review_periods_list]
    for i, period in enumerate(review_periods_list):
        for j, dept in enumerate(dept_names):
            dept_employees = employees.filter(department=dept)
            dept_codes = [e.employee_code for e in dept_employees]
            period_assessments = assessments.filter(
                employee_code__in=dept_codes,
                date_self_appraisal_completed__range=(
                    review_periods.get(company_review_code=period['company_review_code']).period_start_date,
                    review_periods.get(company_review_code=period['company_review_code']).period_end_date
                )
            )
            avg_score = period_assessments.aggregate(
                avg_score=Avg('deliverable_assessor_score')
            )['avg_score'] or 0
            progress_matrix[i][j] = round(avg_score, 1)
    kpi_metrics['progress_matrix'] = progress_matrix
    kpi_metrics['periods'] = [p['company_review_code'] for p in review_periods_list]

    # Strategic Goal Alignment
    strategic_alignment = []
    strategic_goals = ['Technological Advancement', 'Risk Mitigation', 'Operational Efficiency']
    for goal in strategic_goals:
        goal_assessments = assessments.filter(deliverable__icontains=goal.lower())
        avg_score = goal_assessments.aggregate(
            avg_score=Avg('deliverable_assessor_score')
        )['avg_score'] or 0
        strategic_alignment.append({
            'goal': goal,
            'score': round(avg_score, 1)
        })

    # Deliverable Completion vs. Impact
    deliverable_impact = []
    for deliverable in assessments.values('deliverable').distinct():
        del_assessments = assessments.filter(deliverable=deliverable['deliverable'])
        completed = del_assessments.filter(
            doc_evidence_assessor_confirmation=True
        ).count()
        total = del_assessments.count()
        avg_weight = del_assessments.aggregate(
            avg_weight=Avg('deliverable_weight')
        )['avg_weight'] or 0
        avg_score = del_assessments.aggregate(
            avg_score=Avg('deliverable_assessor_score')
        )['avg_score'] or 0
        deliverable_impact.append({
            'deliverable': deliverable['deliverable'],
            'completion_rate': round((completed / total * 100) if total else 0, 1),
            'impact': round(avg_weight * avg_score, 1)
        })

    # 4. Performance Appraisal Process Insights
    timeliness_data = []
    for dept in dept_names:
        dept_employees = employees.filter(department=dept)
        dept_codes = [e.employee_code for e in dept_employees]
        dept_assessments = assessments.filter(employee_code__in=dept_codes)
        avg_delay = dept_assessments.aggregate(
            avg_delay=Avg(
                ExpressionWrapper(
                    F('date_assessor_appraisal_completed') - F('date_self_appraisal_completed'),
                    output_field=fields.DurationField()
                )
            )
        )['avg_delay'] or timedelta(days=0)
        timeliness_data.append({
            'department': dept,
            'avg_delay_days': round(avg_delay.total_seconds() / 86400, 1)
        })

    # Evidence Confirmation Gaps
    evidence_gaps = []
    for dept in dept_names:
        dept_employees = employees.filter(department=dept)
        dept_codes = [e.employee_code for e in dept_employees]
        dept_assessments = assessments.filter(employee_code__in=dept_codes)
        mismatches = dept_assessments.filter(
            ~Q(doc_evidence_self_confirmation=F('doc_evidence_assessor_confirmation'))
        ).count()
        total = dept_assessments.count()
        evidence_gaps.append({
            'department': dept,
            'mismatch_rate': round((mismatches / total * 100) if total else 0, 1)
        })

    # Assessment Completion Rate
    completion_rates = []
    for dept in dept_names:
        dept_employees = employees.filter(department=dept)
        dept_codes = [e.employee_code for e in dept_employees]
        dept_assessments = assessments.filter(employee_code__in=dept_codes)
        complete = dept_assessments.filter(
            deliverable_assessor_score__isnull=False,
            doc_evidence_assessor_confirmation__isnull=False
        ).count()
        total = dept_assessments.count()
        completion_rates.append({
            'department': dept,
            'completion_rate': round((complete / total * 100) if total else 0, 1)
        })

    # 5. General Analytics
    top_bottom_performers = []
    for employee in employees:
        emp_assessments = assessments.filter(employee_code=employee.employee_code)
        weighted_score = emp_assessments.aggregate(
            weighted_score=Avg(
                ExpressionWrapper(
                    F('deliverable_assessor_score') * F('deliverable_weight'),
                    output_field=fields.FloatField()
                )
            )
        )['weighted_score'] or 0
        top_bottom_performers.append({
            'employee_name': employee.employee_name,
            'department': employee.department,
            'weighted_score': round(weighted_score, 1)
        })
    top_bottom_performers = sorted(top_bottom_performers, key=lambda x: x['weighted_score'], reverse=True)
    top_performers = top_bottom_performers[:5]
    bottom_performers = top_bottom_performers[-5:]

    # High-Impact Deliverables
    high_impact_deliverables = sorted(
        weight_score_alignment,
        key=lambda x: x['impact'],
        reverse=True
    )[:5]

    # Data Quality Check
    data_quality = []
    for kpi in assessments.values('kpi').distinct():
        kpi_assessments = assessments.filter(kpi=kpi['kpi'])
        missing_scores = kpi_assessments.filter(
            Q(deliverable_assessor_score__isnull=True) | Q(deliverable_self_score__isnull=True)
        ).count()
        missing_evidence = kpi_assessments.filter(
            Q(doc_evidence_self_confirmation__isnull=True) |
            Q(doc_evidence_assessor_confirmation__isnull=True)
        ).count()
        missing_targets = kpi_assessments.filter(
            Q(short_term_target__isnull=True) |
            Q(intermediate_term_target__isnull=True) |
            Q(long_term_target__isnull=True)
        ).count()
        data_quality.append({
            'kpi': kpi['kpi'],
            'missing_scores': missing_scores,
            'missing_evidence': missing_evidence,
            'missing_targets': missing_targets
        })

    # 6. Leadership Metrics
    leadership_metrics = {
        'score': 0,
        'improvement': 0,
        'competencies': []
    }
    leadership_deliverables = assessments.filter(
        Q(deliverable__icontains='leadership') | Q(deliverable__icontains='training')
    )
    leadership_avg = leadership_deliverables.aggregate(
        avg_score=Avg('deliverable_assessor_score')
    )['avg_score'] or 0
    leadership_metrics['score'] = round(leadership_avg, 1)
    leadership_metrics['improvement'] = 10  # Mocked
    leadership_metrics['competencies'] = [3.5, 4.0, 3.8, 4.2, 3.9]  # Mocked

    # 7. Skill Metrics
    skill_metrics = {
        'gap_index': 0,
        'trend': 0,
        'periods': [p['company_review_code'] for p in review_periods_list],
        'progression': []
    }
    skill_gaps = assessments.filter(
        Q(deliverable__icontains='training') | Q(deliverable__icontains='development')
    ).aggregate(
        avg_score=Avg('deliverable_assessor_score')
    )['avg_score'] or 0
    skill_metrics['gap_index'] = round((5 - skill_gaps) * 20, 1)
    skill_metrics['trend'] = 5  # Mocked
    skill_metrics['progression'] = [3.5, 3.7, 4.0, 4.2]  # Mocked

    # 8. Experience Metrics
    experience_metrics = {
        'score': 0,
        'improvement': 0
    }
    experience_avg = assessments.filter(
        Q(deliverable__icontains='training') | Q(deliverable__icontains='employee')
    ).aggregate(
        avg_score=Avg('deliverable_assessor_score')
    )['avg_score'] or 0
    experience_metrics['score'] = round(experience_avg * 2, 1)
    experience_metrics['improvement'] = 12  # Mocked

    # 9. Development Metrics
    development_metrics = {
        'roi': 0,
        'readiness': 0,
        'critical_roles': 0
    }
    training_assessments = assessments.filter(deliverable__icontains='training')
    development_metrics['roi'] = round(training_assessments.aggregate(
        avg_score=Avg('deliverable_assessor_score')
    )['avg_score'] or 0, 1)
    development_metrics['readiness'] = 75  # Mocked
    development_metrics['critical_roles'] = 80  # Mocked

    # 10. Chart Data
    appraisal_comparison_data = {
        'labels': [item['employee_name'] for item in appraisal_data],
        'self_scores': [item['self_score'] for item in appraisal_data],
        'assessor_scores': [item['assessor_score'] for item in appraisal_data]
    }
    alignment_sankey_data = {
        'labels': ['Strategic Goals', 'KPIs', 'Deliverables', 'Completed'],
        'source': [0, 0, 1, 1],
        'target': [1, 2, 2, 3],
        'value': [100, 80, 80, 60]
    }
    sentiment_heatmap_data = {
        'z': [[3.5, 4.0, 3.8], [4.0, 4.2, 4.1], [3.7, 3.9, 4.0], [4.2, 4.3, 4.5]],
        'x': ['Engagement', 'Satisfaction', 'Support'],
        'y': [p['company_review_code'] for p in review_periods_list[:4]]
    }
    top_performers_chart = {
        'labels': [p['employee_name'] for p in top_performers],
        'scores': [p['weighted_score'] for p in top_performers]
    }

    # Context for template
    context = {
        'company': company,
        'manager_name': manager_name,
        'company_code': company_code,
        'departments': dept_names,
        'review_cycles': review_cycles,
        'employee_names': employee_names,
        'branch_codes': branch_codes,
        'region_branches': region_branches,
        'leadership_metrics': leadership_metrics,
        'kpi_metrics': kpi_metrics,
        'skill_metrics': skill_metrics,
        'experience_metrics': experience_metrics,
        'development_metrics': development_metrics,
        'development_needs': development_needs,
        'appraisal_data': appraisal_data,
        'score_trends': score_trends,
        'target_actual': target_actual,
        'weight_score_alignment': weight_score_alignment,
        'dept_performance': dept_performance,
        'shared_kpi_performance': shared_kpi_performance,
        'uom_consistency': uom_consistency,
        'strategic_alignment': strategic_alignment,
        'deliverable_impact': deliverable_impact,
        'timeliness_data': timeliness_data,
        'evidence_gaps': evidence_gaps,
        'completion_rates': completion_rates,
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'high_impact_deliverables': high_impact_deliverables,
        'data_quality': data_quality,
        'appraisal_comparison_data': json.dumps(appraisal_comparison_data),
        'alignment_sankey_data': json.dumps(alignment_sankey_data),
        'sentiment_heatmap_data': json.dumps(sentiment_heatmap_data),
        'top_performers_chart': json.dumps(top_performers_chart),
        'departments_json': json.dumps(dept_names),
        'periods_json': json.dumps([p['company_review_code'] for p in review_periods_list])
    }

    return render(request, 'dash_mgmt.html', context)


def get_employee_fields(request):
    try:
        employee_code = request.GET.get('employee_code', '').strip()
        if not employee_code:
            return JsonResponse({'error': 'Employee code is required'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT company_code, region_branch
                FROM perf_mgmt_user_creation_model
                WHERE employee_code = %s
                LIMIT 1
            """, [employee_code])
            user_row = cursor.fetchone()

            if not user_row:
                return JsonResponse({'error': 'Employee not found'}, status=404)

            company_code, region_branch = user_row

            cursor.execute("""
                SELECT region_code
                FROM perf_mgmt_region
                WHERE company_code_id = %s AND region_branch = %s
                LIMIT 1
            """, [company_code, region_branch])
            region_row = cursor.fetchone()

            if not region_row and region_branch is None:
                cursor.execute("""
                    SELECT region_code
                    FROM perf_mgmt_region
                    WHERE company_code_id = %s AND region_branch IS NULL
                    LIMIT 1
                """, [company_code])
                region_row = cursor.fetchone()

            branch_code = region_row[0] if region_row else None

            return JsonResponse({
                'company_code': company_code,
                'branch_code': branch_code,
                'region_branch': region_branch
            })

    except OperationalError as oe:
        logger.critical(f"Database error: {str(oe)}")
        return JsonResponse({'error': 'Database error occurred'}, status=503)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'error': f'Internal error: {str(e)}'}, status=500)


def get_subordinates(request):
    try:
        employee_code = request.GET.get('employee_code', '').strip()
        if not employee_code:
            return JsonResponse({'error': 'Employee code is required'}, status=400)

        with connection.cursor() as cursor:
            # Step 1: Get supervisor's company_code
            cursor.execute("""
                SELECT company_code
                FROM perf_mgmt_user_creation_model
                WHERE employee_code = %s
                LIMIT 1
            """, [employee_code])
            supervisor_row = cursor.fetchone()

            if not supervisor_row:
                return JsonResponse({'error': 'Supervisor not found'}, status=404)

            supervisor_company_code = supervisor_row[0]

            # Step 2: Fetch subordinates with same company_code
            cursor.execute("""
                SELECT employee_code, position, department, employee_name, company_code
                FROM perf_mgmt_user_creation_model
                WHERE reports_to_code = %s AND company_code = %s
            """, [employee_code, supervisor_company_code])
            rows = cursor.fetchall()

            if not rows:
                return JsonResponse({'subordinates': [], 'message': 'No subordinates found'}, status=200)

            # ❗ Properly include company_code in response
            subordinates = [
                {
                    'employee_code': row[0],
                    'position': row[1] or 'N/A',
                    'department': row[2] or 'N/A',
                    'employee_name': row[3] or 'Unknown',
                    'company_code': row[4] or 'N/A'  # ✅ this line was missing before
                }
                for row in rows
            ]

            return JsonResponse({'subordinates': subordinates}, status=200)

    except OperationalError as oe:
        logger.critical(f"Database error: {str(oe)}")
        return JsonResponse({'error': 'Database error occurred'}, status=503)
    except Exception as e:
        logger.error(f"Error fetching subordinate fields: {str(e)}")
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)




def get_subordinates_by_reports_to(request):
    try:
        reports_to = request.GET.get('reports_to', '').strip()

        if not reports_to:
            return JsonResponse({'error': 'Reports to is required'}, status=400)

        with connection.cursor() as cursor:
            # Step 1: Get company_code for the reports_to
            cursor.execute("""
                SELECT company_code
                FROM perf_mgmt_user_creation_model
                WHERE employee_name = %s OR employee_code = %s
                LIMIT 1
            """, [reports_to, reports_to])
            supervisor_row = cursor.fetchone()

            if not supervisor_row:
                return JsonResponse({'error': 'Supervisor not found'}, status=404)

            supervisor_company_code = supervisor_row[0]

            # Step 2: Fetch subordinates with same company_code
            cursor.execute("""
                SELECT employee_code, position, department, employee_name, company_code
                FROM perf_mgmt_user_creation_model
                WHERE reports_to = %s AND company_code = %s
                OR reports_to_code = %s AND company_code = %s
            """, [reports_to, supervisor_company_code, reports_to, supervisor_company_code])

            rows = cursor.fetchall()

            if not rows:
                return JsonResponse({'subordinates': [], 'message': 'No subordinates found'}, status=200)

            subordinates = [
                {
                    'employee_code': row[0],
                    'position': row[1] or 'N/A',
                    'department': row[2] or 'N/A',
                    'employee_name': row[3] or 'Unknown',
                    'company_code': row[4] or 'N/A'
                }
                for row in rows
            ]

            return JsonResponse({'subordinates': subordinates}, status=200)

    except OperationalError as oe:
        logger.critical(f"Database error: {str(oe)}")
        return JsonResponse({'error': 'Database error occurred'}, status=503)
    except Exception as e:
        logger.error(f"Error fetching subordinate fields: {str(e)}")
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)



@csrf_exempt
def get_assessments_by_employee(request):
    if request.method == 'GET':
        try:
            assessor_code = request.GET.get('assessor_employee_code')
            if not assessor_code:
                return JsonResponse({'error': 'assessor_employee_code is required'}, status=400)

            # Fetch assessments with distinct deliverables per employee_code
            assessments = PerfMgmtAssessment.objects.filter(
                assessor_employee_code=assessor_code
            ).values(
                'employee_code',
                'assessor_employee_code',
                'date_self_appraisal_completed',
                'date_assessor_appraisal_completed',
                'strategic_goal',
                'kpi',
                'deliverable',
                'deliverable_self_score',
                'deliverable_assessor_score',
                'doc_evidence',
                'doc_evidence_self_confirmation',
                'doc_evidence_assessor_confirmation',
                'date_created',
                'date_updated',
                'attachment',
                'assessment_code',
                'strategic_goal_number',
                'kpi_number',
                'deliverable_number',
                'doc_evidence_number',
                'strategic_goal_weight',
                'kpi_weight',
                'deliverable_weight',
                'doc_evidence_weight',
                'short_term_target',
                'intermediate_term_target',
                'long_term_target',
                'uom',
                'short_term_actual',
                'intermediate_term_actual',
                'long_term_actual',
                'short_term_target_due_date',
                'intermediate_term_target_due_date',
                'long_term_target_due_date',
            ).distinct('employee_code', 'strategic_goal', 'kpi', 'deliverable')  # Ensure unique combinations

            # Track unique values across all employees for consolidated metrics
            global_unique_strategic_goals = set()
            global_unique_kpis = set()
            global_unique_deliverables = set()

            # Group assessments by employee_code, strategic_goal, kpi, and deliverable
            employee_metrics = {}
            for assessment in assessments:
                emp_code = assessment['employee_code']
                strategic_goal = assessment['strategic_goal'] or 'Unknown Goal'
                kpi = assessment['kpi'] or 'Unknown KPI'
                deliverable = assessment['deliverable'] or 'Unknown Deliverable'

                # Track global unique values
                global_unique_strategic_goals.add(strategic_goal)
                global_unique_kpis.add(kpi)
                global_unique_deliverables.add(deliverable)

                if emp_code not in employee_metrics:
                    employee_metrics[emp_code] = {
                        'strategic_goals': {},
                        'kpis': {},
                        'deliverables': {},
                        'assessments': [],
                        'total_assessments': 0,
                        'on_track_count': 0
                    }

                if strategic_goal not in employee_metrics[emp_code]['strategic_goals']:
                    employee_metrics[emp_code]['strategic_goals'][strategic_goal] = {
                        'total_diff': 0,
                        'count': 0
                    }

                if kpi not in employee_metrics[emp_code]['kpis']:
                    employee_metrics[emp_code]['kpis'][kpi] = {
                        'total_diff': 0,
                        'count': 0
                    }

                if deliverable not in employee_metrics[emp_code]['deliverables']:
                    employee_metrics[emp_code]['deliverables'][deliverable] = {
                        'total_diff': 0,
                        'count': 0
                    }

                employee_metrics[emp_code]['assessments'].append(assessment)
                employee_metrics[emp_code]['total_assessments'] += 1

                if assessment['deliverable_self_score'] is not None and assessment['deliverable_assessor_score'] is not None:
                    diff = abs(assessment['deliverable_self_score'] - assessment['deliverable_assessor_score'])
                    employee_metrics[emp_code]['strategic_goals'][strategic_goal]['total_diff'] += diff
                    employee_metrics[emp_code]['strategic_goals'][strategic_goal]['count'] += 1
                    employee_metrics[emp_code]['kpis'][kpi]['total_diff'] += diff
                    employee_metrics[emp_code]['kpis'][kpi]['count'] += 1
                    employee_metrics[emp_code]['deliverables'][deliverable]['total_diff'] += diff
                    employee_metrics[emp_code]['deliverables'][deliverable]['count'] += 1

                if assessment['doc_evidence_self_confirmation'] and assessment['doc_evidence_assessor_confirmation']:
                    employee_metrics[emp_code]['on_track_count'] += 1

            # Calculate metrics
            response_data = {'employees': {}, 'consolidated': {}}
            consolidated_metrics = {
                'strategic_goals': {sg: {'total_diff': 0, 'count': 0} for sg in global_unique_strategic_goals},
                'kpis': {kpi: {'total_diff': 0, 'count': 0} for kpi in global_unique_kpis},
                'deliverables': {deliv: {'total_diff': 0, 'count': 0} for deliv in global_unique_deliverables},
                'total_assessments': 0,
                'on_track_count': 0
            }

            for emp_code, emp_data in employee_metrics.items():
                response_data['employees'][emp_code] = {
                    'assessments': emp_data['assessments'],
                    'strategic_goals': {},
                    'kpis': {},
                    'deliverables': {},
                    'on_track': 0,
                    'gaps': 0
                }

                total_assessments = emp_data['total_assessments']
                if total_assessments > 0:
                    # Calculate strategic goal alignments
                    for sg, sg_data in emp_data['strategic_goals'].items():
                        if sg_data['count'] > 0:
                            misalignment = (sg_data['total_diff'] / (sg_data['count'] * 5.0)) * 100
                            alignment = 100 - misalignment
                            response_data['employees'][emp_code]['strategic_goals'][sg] = {
                                'alignment': round(alignment, 1),
                                'misalignment': round(misalignment, 1)
                            }
                            consolidated_metrics['strategic_goals'][sg]['total_diff'] += sg_data['total_diff']
                            consolidated_metrics['strategic_goals'][sg]['count'] += sg_data['count']

                    # Calculate KPI alignments
                    for kpi, kpi_data in emp_data['kpis'].items():
                        if kpi_data['count'] > 0:
                            misalignment = (kpi_data['total_diff'] / (kpi_data['count'] * 5.0)) * 100
                            alignment = 100 - misalignment
                            response_data['employees'][emp_code]['kpis'][kpi] = {
                                'alignment': round(alignment, 1),
                                'misalignment': round(misalignment, 1)
                            }
                            consolidated_metrics['kpis'][kpi]['total_diff'] += kpi_data['total_diff']
                            consolidated_metrics['kpis'][kpi]['count'] += kpi_data['count']

                    # Calculate deliverable alignments
                    for deliverable, del_data in emp_data['deliverables'].items():
                        if del_data['count'] > 0:
                            misalignment = (del_data['total_diff'] / (del_data['count'] * 5.0)) * 100
                            alignment = 100 - misalignment
                            response_data['employees'][emp_code]['deliverables'][deliverable] = {
                                'alignment': round(alignment, 1),
                                'misalignment': round(misalignment, 1)
                            }
                            consolidated_metrics['deliverables'][deliverable]['total_diff'] += del_data['total_diff']
                            consolidated_metrics['deliverables'][deliverable]['count'] += del_data['count']

                    # Calculate on-track and gaps
                    on_track = (emp_data['on_track_count'] / total_assessments * 100)
                    response_data['employees'][emp_code]['on_track'] = round(on_track, 1)
                    response_data['employees'][emp_code]['gaps'] = round(100 - on_track, 1)

                    consolidated_metrics['total_assessments'] += total_assessments
                    consolidated_metrics['on_track_count'] += emp_data['on_track_count']

            # Calculate consolidated metrics
            consolidated_data = {
                'strategic_goals': {},
                'kpis': {},
                'deliverables': {},
                'on_track': 0,
                'gaps': 0
            }

            if consolidated_metrics['total_assessments'] > 0:
                # Consolidated strategic goals
                for sg, sg_data in consolidated_metrics['strategic_goals'].items():
                    if sg_data['count'] > 0:
                        misalignment = (sg_data['total_diff'] / (sg_data['count'] * 5.0)) * 100
                        alignment = 100 - misalignment
                        consolidated_data['strategic_goals'][sg] = {
                            'alignment': round(alignment, 1),
                            'misalignment': round(misalignment, 1)
                        }

                # Consolidated KPIs
                for kpi, kpi_data in consolidated_metrics['kpis'].items():
                    if kpi_data['count'] > 0:
                        misalignment = (kpi_data['total_diff'] / (kpi_data['count'] * 5.0)) * 100
                        alignment = 100 - misalignment
                        consolidated_data['kpis'][kpi] = {
                            'alignment': round(alignment, 1),
                            'misalignment': round(misalignment, 1)
                        }

                # Consolidated deliverables
                for deliverable, del_data in consolidated_metrics['deliverables'].items():
                    if del_data['count'] > 0:
                        misalignment = (del_data['total_diff'] / (del_data['count'] * 5.0)) * 100
                        alignment = 100 - misalignment
                        consolidated_data['deliverables'][deliverable] = {
                            'alignment': round(alignment, 1),
                            'misalignment': round(misalignment, 1)
                        }

                # Consolidated on-track and gaps
                consolidated_on_track = (consolidated_metrics['on_track_count'] / consolidated_metrics['total_assessments'] * 100)
                consolidated_data['on_track'] = round(consolidated_on_track, 1)
                consolidated_data['gaps'] = round(100 - consolidated_on_track, 1)

            response_data['consolidated'] = consolidated_data

            return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def management_dashboard(request):
    # Get filter options
    departments = UserCreationModel.objects.filter(
        company_code=request.user.company_code,
        reports_to_code=request.user.employee_code
    ).values_list('department', flat=True).distinct()
    
    review_cycles = ReviewPeriod.objects.filter(
        company_code=request.user.company_code
    ).values_list('review', flat=True).distinct()
    
    regions = Region.objects.filter(
        company_code=request.user.company_code
    ).values_list('region_branch', flat=True).distinct()

    # Mock development needs and metrics (replace with real data as needed)
    development_needs = [
        {'skill': 'Leadership Training', 'gap': 20},
        {'skill': 'System Uptime', 'gap': 15},
        {'skill': 'User Engagement', 'gap': 10},
    ]
    kpi_metrics = {'achievement_rate': 75, 'on_track': 17.4}
    development_metrics = {'roi': 2.5, 'critical_roles': 85}

    context = {
        'departments': departments,
        'review_cycles': review_cycles,
        'regions': regions,
        'development_needs': development_needs,
        'kpi_metrics': kpi_metrics,
        'development_metrics': development_metrics,
    }
    return render(request, 'perf_mgmt/management_dashboard.html', context)


class AssessmentsByEmployeeAPIView(APIView):
    def get(self, request):
        assessor_code = request.query_params.get('assessor_employee_code')
        department = request.query_params.get('department')
        review_cycle = request.query_params.get('review_cycle')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        region_branch = request.query_params.get('region_branch')

        # Get employees reporting to the assessor
        employees = UserCreationModel.objects.filter(
            reports_to_code=assessor_code
        )
        
        if department:
            employees = employees.filter(department=department)
        if region_branch:
            employees = employees.filter(region_branch=region_branch)

        employee_codes = employees.values_list('employee_code', flat=True)

        # Filter assessments
        assessments = PerfMgmtAssessment.objects.filter(
            employee_code__in=employee_codes
        )
        
        if review_cycle:
            assessments = assessments.filter(
                Q(date_self_appraisal_completed__year=review_cycle) |
                Q(date_assessor_appraisal_completed__year=review_cycle)
            )
        if start_date:
            assessments = assessments.filter(date_self_appraisal_completed__gte=start_date)
        if end_date:
            assessments = assessments.filter(date_self_appraisal_completed__lte=end_date)

        # Aggregate data (mocked for brevity; replace with real logic)
        response_data = {
            'employees': {},
            'consolidated': {
                'strategic_goals': {
                    'Capability Building': {'misalignment': 20},
                    'General Improvement': {'misalignment': 6.7},
                    '% grant-eligible citizens covered': {'misalignment': 0}
                },
                'kpis': {
                    'User Training Programs': {'misalignment': 20},
                    'System Uptime': {'misalignment': 10},
                    'Certification Achievement': {'misalignment': 0}
                },
                'on_track': 17.4,
                'gaps': 82.6
            }
        }

        for emp_code in employee_codes:
            emp_assessments = assessments.filter(employee_code=emp_code)
            # Mocked employee data (replace with real aggregation)
            response_data['employees'][emp_code] = {
                'strategic_goals': {
                    'Capability Building': {'misalignment': 20 if emp_code == 'EMP22334NG' else 0},
                    'General Improvement': {'misalignment': 6.7 if emp_code == 'EMP22334NG' else 0},
                    '% grant-eligible citizens covered': {'misalignment': 0}
                },
                'on_track': 0 if emp_code == 'EMP22334NG' else 50,
                'gaps': 100 if emp_code == 'EMP22334NG' else 50
            }

        return Response(response_data, status=status.HTTP_200_OK)
    

@csrf_exempt
def dash_staff(request):
    if request.method not in ('POST', 'GET'):
        return render(request, 'error.html', {'message': 'Invalid request method.'}, status=405)

    get_data = request.POST if request.method == 'POST' else request.GET
    username = get_data.get('username')
    employee_password = get_data.get('employee_password')
    region_code = get_data.get('region_code')

    if not username or not employee_password:
        return render(request, 'error.html', {'message': 'Username and employee code are required.'}, status=400)

    # Authenticate employee
    try:
        employee = UserCreationModel.objects.get(
            employee_name=username,
            employee_code=employee_password,
            is_employee_active=True
        )
    except UserCreationModel.DoesNotExist:
        return render(request, 'error.html', {'message': 'Invalid employee credentials. Please try again.'}, status=403)

    employee_code = employee.employee_code
    employee_name = employee.employee_name
    employee_role = employee.position
    employee_department = employee.department
    company_code = employee.company_code.company_code
    tenure_days = (date.today() - employee.employment_start_date).days
    tenure = f"{tenure_days // 365} years" if tenure_days >= 365 else f"{tenure_days} days"

    # Company details
    try:
        company = UserProfile.objects.get(company_code=company_code, activity_status='active')
    except UserProfile.DoesNotExist:
        return render(request, 'error.html', {'message': f'No active company found for code {company_code}'}, status=404)

    company_name = company.company
    company_details = {
        'company': company.company,
        'country': company.country,
        'headquarters': company.headquarters,
        'email': company.email
    }

    # Region validation
    region_branch = region_name = None
    if region_code:
        try:
            region = Region.objects.get(region_code=region_code)
            if region.company_code.company_code != company_code:
                return render(request, 'error.html', {'message': f'Region {region_code} does not belong to company {company_code}'}, status=404)
            if employee.region_code and employee.region_code.region_code != region_code:
                return render(request, 'error.html', {'message': f'Employee not in region {region_code}'}, status=403)
            region_branch = region.region_branch
            region_name = region.region_name
        except Region.DoesNotExist:
            return render(request, 'error.html', {'message': f'Invalid region code: {region_code}'}, status=404)

    # Performance assessments
    current_date = date.today()
    try:
        review_period = ReviewPeriod.objects.filter(
            company_code=company_code,
            period_start_date__lte=current_date,
            period_end_date__gte=current_date
        ).latest('date_created')
        assessments = PerfMgmtAssessment.objects.filter(
            employee_code=employee_code,
            date_self_appraisal_completed__range=(review_period.period_start_date, review_period.period_end_date)
        )
    except ReviewPeriod.DoesNotExist:
        assessments = PerfMgmtAssessment.objects.filter(employee_code=employee_code)

    self_appraisal, assessor_appraisal = [], []
    for assessment in assessments:
        category = assessment.strategic_goal
        self_score = assessment.deliverable_self_score
        assessor_score = assessment.deliverable_assessor_score or 0
        self_appraisal.append({'name': category, 'score': self_score})
        assessor_appraisal.append({'name': category, 'score': assessor_score})

    def aggregate_scores(appraisals):
        aggregated = {}
        for item in appraisals:
            name, score = item['name'], item['score']
            if name in aggregated:
                a = aggregated[name]
                a['score'] = (a['score'] * a['count'] + score) / (a['count'] + 1)
                a['count'] += 1
            else:
                aggregated[name] = {'name': name, 'score': score, 'count': 1}
        return [{'name': k, 'score': v['score']} for k, v in aggregated.items()]

    self_appraisal = aggregate_scores(self_appraisal)
    assessor_appraisal = aggregate_scores(assessor_appraisal)
    categories = set(item['name'] for item in self_appraisal) & set(item['name'] for item in assessor_appraisal)
    self_appraisal = sorted([i for i in self_appraisal if i['name'] in categories], key=lambda x: x['name'])
    assessor_appraisal = sorted([i for i in assessor_appraisal if i['name'] in categories], key=lambda x: x['name'])

    self_appraisal_avg = sum(i['score'] for i in self_appraisal) / len(self_appraisal) if self_appraisal else 0
    assessor_appraisal_avg = sum(i['score'] for i in assessor_appraisal) / len(assessor_appraisal) if assessor_appraisal else 0
    score_differences = [s['score'] - a['score'] for s, a in zip(self_appraisal, assessor_appraisal)]
    colors = ['rgb(37, 99, 235)' if d > 0 else 'rgb(34, 197, 94)' for d in score_differences]
    categories = [i['name'] for i in self_appraisal]

    # Feedback: 360° and Experience
    peer_results = EvaluateYourPeerResults.objects.filter(employee_code=employee_code)
    feedback_categories = list(set(result.factor_type for result in peer_results))
    feedback_self_scores, feedback_peer_avg = [], []
    for cat in feedback_categories:
        self_score = ManagerSelfEvaluationResults.objects.filter(company_code=company_code, description__icontains=cat).aggregate(Avg('description'))['description__avg'] or 0
        peer_avg = peer_results.filter(factor_type=cat).aggregate(Avg('response'))['response__avg'] or 0
        feedback_self_scores.append(self_score)
        feedback_peer_avg.append(peer_avg)

    ex_results = EmpExFactorResults.objects.filter(employee_code=employee_code)
    experience_score = ex_results.aggregate(Avg('response'))['response__avg'] or 0
    top_themes = list(set(r.factor_type for r in ex_results))[:3]
    department_avg = EmpExFactorResults.objects.exclude(employee_code=employee_code).aggregate(Avg('response'))['response__avg'] or 0

    # Placeholder data
    skills = {'months': [], 'categories': [], 'proficiency_levels': [], 'names': [], 'scores': [], 'department_avg_scores': [], 'completed_goals': 0, 'department_avg_goals': 0, 'growth_rate': 0, 'department_growth_rate': 0, 'readiness': 0, 'department_readiness': 0}
    goals = {'start_dates': [], 'titles': [], 'durations': [], 'status_colors': [], 'descriptions': [], 'ids': []}
    leadership = {'scores': [], 'categories': [], 'department_avg_scores': [], 'decision_making': 0, 'decision_making_percentile': 0}
    development = {'timeline_dates': [], 'timeline_scores': [], 'department_avg_scores': []}
    milestones = {'dates': [], 'titles': [], 'status_colors': [], 'descriptions': []}
    kpis = []

    all_ex_scores = EmpExFactorResults.objects.filter(
        employee_code__in=UserCreationModel.objects.filter(
            company_code=company_code,
            department=employee_department,
            is_employee_active=True
        ).values_list('employee_code', flat=True)
    ).values('employee_code').annotate(avg_score=Avg('response')).order_by('-avg_score')

    rank = next((i + 1 for i, r in enumerate(all_ex_scores) if r['employee_code'] == employee_code), 1)
    department_size = all_ex_scores.count()

    employee_context = {
        'name': employee_name,
        'role': employee_role,
        'department': employee_department,
        'tenure': tenure,
        'rank': rank,
        'performance_score': round(experience_score, 1),
        'department_avg_score': round(department_avg, 1),
        'self_appraisal': self_appraisal,
        'assessor_appraisal': assessor_appraisal,
        'self_appraisal_avg': round(self_appraisal_avg, 1),
        'assessor_appraisal_avg': round(assessor_appraisal_avg, 1),
        'feedback': {
            'self_scores': feedback_self_scores,
            'peer_avg': feedback_peer_avg,
            'categories': feedback_categories
        },
        'experience': {
            'score': round(experience_score, 1),
            'department_avg': round(department_avg, 1),
            'top_themes': top_themes
        },
        'skills': skills,
        'goals': goals,
        'leadership': leadership,
        'development': development,
        'milestones': milestones,
        'kpis': kpis
    }

    context = {
        'employee': employee_context,
        'score_differences': score_differences,
        'categories': categories,
        'colors': colors,
        'department_size': department_size,
        'company_name': company_name,
        'region_branch': region_branch,
        'company_details': company_details,
        'region_name': region_name
    }

    return render(request, 'dash_staff.html', context)



from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import PerfMgmtAssessment
import json

@require_http_methods(["POST"])
def create_perf_mgmt_assessment(request):
    try:
        data = json.loads(request.body)
        perf_mgmt_assessment = PerfMgmtAssessment(
            employee_code=data.get('employee_code'),
            assessor_employee_code=data.get('assessor_employee_code'),
            strategic_goal=data.get('strategic_goal'),
            kpi=data.get('kpi'),
            deliverable=data.get('deliverable'),
            deliverable_self_score=data.get('deliverable_self_score'),
            doc_evidence=data.get('doc_evidence'),
            doc_evidence_self_confirmation=data.get('doc_evidence_self_confirmation'),
            strategic_goal_number=data.get('strategic_goal_number'),
            kpi_number=data.get('kpi_number'),
            deliverable_number=data.get('deliverable_number'),
            doc_evidence_number=data.get('doc_evidence_number'),
            short_term_target=data.get('short_term_target'),
            intermediate_term_target=data.get('intermediate_term_target'),
            long_term_target=data.get('long_term_target'),
            uom=data.get('uom'),
            short_term_actual=data.get('short_term_actual'),
            intermediate_term_actual=data.get('intermediate_term_actual'),
            long_term_actual=data.get('long_term_actual'),
        )
        perf_mgmt_assessment.save()
        return JsonResponse({'message': 'Perf Mgmt Assessment created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    



from .models import EmployeeExperienceFactor

def get_factor_descriptions(request):
    factor_type = request.GET.get('factor_type')
    if factor_type:
        descriptions = EmployeeExperienceFactor.objects.filter(factor_type=factor_type).values_list('description', flat=True)
        return JsonResponse({'descriptions': list(descriptions)})
    else:
        return JsonResponse({'error': 'factor_type is required'}, status=400)


def performa360_settings(request):
    """
    View to render the Performa360 settings page.
    """
    return render(request, 'setting_applicaion_exp.html')

# In perf_mgmt/views.py (or wherever your views are)
def performa360_main(request):
    return render(request, 'main_application.html')

def staff_dashboard(request):
    return render(request, 'staff_dash.html')

def view_settings_culture(request):
    return render(request, 'settings_culture.html')


def policies_admin(request):
    return render(request, 'policies_admin.html')

def leave_policy(request):
    return render(request, 'leave_policy.html')
