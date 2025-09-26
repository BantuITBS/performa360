import os
import phonenumbers
import re
import random
import string
import uuid
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import F, Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now
from django.db import models, connection
from django.db.models import CheckConstraint, Q
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q, F
from django.db import models
from datetime import datetime

# Define the validator for phone numbers
validate_phone_number = RegexValidator(
    regex=r'^\d{10,15}$',
    message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed."
)

def validate_phone_number(value):
    try:
        phone_number = phonenumbers.parse(str(value), None)  # None will use the default country
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError(f"{value} is not a valid phone number.")
    except phonenumbers.NumberParseException:
        raise ValidationError(f"{value} is not a valid phone number.")

def generate_unique_password():
    """Generate a random unique password."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

class UserCreationModel(models.Model):
    ADMIN_ROLE_CHOICES = [
        ('dpt', 'Department Admin'),
        ('cpy', 'Company Admin'),
        ('hra', 'HR Admin'),
        ('gma', 'General Manager Admin'),
        ('', 'n/a'),  # Default as blank value
    ]

    company_code = models.ForeignKey(
        'UserProfile',
        to_field='company_code',
        on_delete=models.CASCADE,
        db_column='company_code',
        related_name='user_creation_models'
    )
    region_code = models.ForeignKey(
        'Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='region_code'
    )
    employee_code = models.CharField(max_length=14, primary_key=True)  # Auto-generated
    pre_existing_employee_code = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    employee_name = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    team_or_division = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    time_created = models.TimeField(auto_now_add=True)
    employee_email = models.EmailField()
    phone_number = models.TextField()
    employee_gender = models.TextField()
    region_branch = models.TextField(null=True, blank=True)

    employment_type = models.CharField(
        max_length=50,
        choices=[
            ('Permanent', 'Permanent'),
            ('Contract', 'Contract'),
            ('Intern', 'Intern'),
            ('Part-Time', 'Part-Time')
        ],
        null=True,
        blank=True
    )

    employee_status = models.CharField(
        max_length=50,
        choices=[
            ('HR Manager', 'HR Manager'),
            ('International Executive', 'International Executive'),
            ('Staff', 'Staff'),
            ('Department Manager', 'Department Manager'),
            ('General Manager', 'General Manager'),
            ('Company Executive', 'Company Executive'),
            ('Region Executive', 'Region Executive'),
            ('Country Executive', 'Country Executive')
        ],
        null=True,
        blank=True
    )

    department = models.TextField()
    position = models.TextField()
    reports_to_position = models.TextField()
    is_employee_active = models.BooleanField(default=True)
    reason_for_inactivity = models.TextField(default='n/a')
    reports_to = models.TextField()
    employment_start_date = models.DateField()
    last_login = models.DateTimeField(null=True, blank=True)

    reports_to_code = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        editable=False
    )

    assign_admin_role = models.CharField(
        max_length=3,
        choices=ADMIN_ROLE_CHOICES,
        null=True,
        blank=True,
        default='n/a'
    )

    USERNAME_FIELD = 'employee_code'
    REQUIRED_FIELDS = [
        'company_code',
        'first_name',
        'last_name',
        'employee_name',
        'date_of_birth',
        'team_or_division',
        'employee_email',
        'phone_number',
        'employee_gender',
        'employment_type',
        'employee_status',
        'department',
        'position',
        'is_employee_active',
        'reason_for_inactivity',
        'reports_to',
        'employment_start_date',
    ]

    def generate_employee_code(self):
        # Use assign_admin_role as suffix (dpt, cpy, hra, gma, or 'n/a')
        suffix = self.assign_admin_role or ''  # If empty, suffix is blank

        code_parts = ['EMP']

        if suffix.lower() not in ['n/a', '']:
            letters = ['a', 'd', 'm']
            random.shuffle(letters)
            code_parts.extend(letters)

            digits = [str(random.randint(0, 9)) for _ in range(5)]
            code_parts.extend(digits)

            random.shuffle(code_parts)
        else:
            digits = [str(random.randint(0, 9)) for _ in range(6)]
            code_parts.extend(digits)

        return "".join(code_parts) + suffix

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self.generate_employee_code()

        if self.reports_to:
            try:
                reports_to_user = UserCreationModel.objects.get(employee_name=self.reports_to)
                self.reports_to_code = reports_to_user.employee_code
            except (UserCreationModel.MultipleObjectsReturned, UserCreationModel.DoesNotExist):
                self.reports_to_code = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_name} ({self.employee_code})"

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return False

    class Meta:
        db_table = 'perf_mgmt_user_creation_model'



class UserProfile(models.Model):
    ACTIVITY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    company_code = models.CharField(max_length=20, primary_key=True)
    is_multiple_branches = models.BooleanField(default=False)
    company = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    headquarters = models.CharField(max_length=255)
    
    # Timestamps for tracking
    date_created = models.DateField(auto_now_add=True)
    time_created = models.TimeField(auto_now_add=True)
    
    # Activity status with options for 'active' or 'inactive'
    activity_status = models.CharField(
        max_length=8,
        choices=ACTIVITY_STATUS_CHOICES,
        default='active'
    )
    
    # Other business logic fields
    user_select = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(default=date(2025, 2, 12))
    end_date = models.DateField(default=date(2025, 2, 12))
    review_cycle = models.CharField(max_length=50, blank=True, null=True)
    review_number = models.IntegerField(blank=True, null=True)
    payment_plan = models.CharField(max_length=50, blank=True, null=True)
    current_usd_exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    
    # Contact and address information
    email = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True, default='n/a')
    partner_code = models.CharField(max_length=8, blank=True, null=True)

    total_payable_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'perf_mgmt_userprofile'

    def __str__(self):
        return f"UserProfile: {self.company_code}"

    def save(self, *args, **kwargs):
        if not self.company_code:
            self.company_code = self.generate_unique_company_code()

        months = self.calculate_months()

        # Calculate metrics if `total_cost` is provided
        if self.total_payable_amount:
            self.total_payable_amount = self.total_payable_amount
            self.installment_amount = self.total_payable_amount / months if months else 0
            self.installment_amount = self.installment_amount

        # Save the object after calculating fields
        super(UserProfile, self).save(*args, **kwargs)

    def calculate_months(self):
        """Calculate the number of months between the start and end dates."""
        if self.start_date and self.end_date and self.end_date >= self.start_date:
            delta = relativedelta(self.end_date, self.start_date)
            months = delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
            return max(months, 1)
        return 1

    @staticmethod
    def generate_company_code():
        random_numbers = str(random.randint(10000, 99999))
        company_code = f"CMP{random_numbers}"
        return company_code

    @classmethod
    def generate_unique_company_code(cls):
        company_code = cls.generate_company_code()
        while cls.objects.filter(company_code=company_code).exists():
            company_code = cls.generate_company_code()
        return company_code




class ReviewPeriod(models.Model):
    company = models.CharField(max_length=255)

    company_code = models.ForeignKey(
        'UserProfile',          # No app prefix needed if same app
        to_field='company_code',
        db_column='company_code',
        on_delete=models.CASCADE
    )

    review = models.IntegerField()
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    date_created = models.DateTimeField()  # Set manually in view

    company_review_code = models.CharField(max_length=20, primary_key=True)

    class Meta:
        db_table = 'review_periods'
        unique_together = (('company_code', 'review'),)

    def __str__(self):
        return self.company_review_code

class PersonalDevelopmentPlan(models.Model):
    course_programme = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    employee_code = models.CharField(max_length=50, unique=True)  # No blank or null allowed
    completion_status = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Completion percentage (0 to 100)"
    )
    institution = models.CharField(max_length=255, blank=True, null=True)
    appraisal_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate employee_code if it's not set
        if not self.employee_code:
            self.employee_code = self.generate_employee_code()
        super().save(*args, **kwargs)

    def generate_employee_code(self):
        """Generate a unique employee code (e.g., EMP12345)."""
        base_code = "EMP" + str(uuid.uuid4().int)[:5]  # Generate a short unique identifier
        return base_code

    def __str__(self):
        return f"{self.employee_code} - {self.course_programme}"

    class Meta:
        db_table = "perf_mgmt_pdp"
        verbose_name = "Personal Development Plan"
        verbose_name_plural = "Personal Development Plans"


class PerfMgmtKpiDeliDoc(models.Model):
    strategy_code = models.CharField(max_length=255, primary_key=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    kpi = models.TextField(blank=True, null=True)
    deliverable = models.CharField(max_length=255, blank=True, null=True)
    doc_evidence = models.CharField(max_length=255, blank=True, null=True)
    strategic_goal = models.CharField(max_length=255, blank=True, null=True)
    goal_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'perf_mgmt_kpi_deli_doc'  # Specify the existing table name
        managed = False  # Prevent Django from creating or altering the table

    def __str__(self):
        return f"{self.department} - {self.kpi} - {self.deliverable} - {self.strategic_goal}"

class Role(models.Model):
    department_name = models.CharField(max_length=255)  # Store the department name directly in this table
    role_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)  # Store the department name directly in this table
    role_code = models.CharField(max_length=1024, unique=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-populate role_code before saving."""
        self.role_code = "__".join([
            self.department_name or '',
            self.role_name or '',
            self.industry or ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_role"


class SGSKPIsDelDev(models.Model):
    strategy_code_results = models.CharField(max_length=2255, primary_key=True)

    # Changed from ForeignKey to CharField
    employee_code = models.CharField(max_length=14)

    date_created = models.DateTimeField(auto_now_add=True)

    kpi = models.TextField()
    deliverable = models.TextField()
    doc_evidence = models.TextField(blank=True, null=True)
    strategic_goal = models.TextField(blank=True, null=True)
    date_modified = models.DateField(auto_now=True)
    strategic_goal_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    strategic_goal_due_date = models.DateField(blank=True, null=True)
    kpi_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kpi_due_date = models.DateField(blank=True, null=True)
    deliverable_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    deliverable_due_date = models.DateField(blank=True, null=True)
    doc_evidence_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    doc_evidence_due_date = models.DateField(blank=True, null=True)

    strategic_goal_number = models.CharField(max_length=50, blank=True, null=True)
    kpi_number = models.CharField(max_length=50, blank=True, null=True)
    deliverable_number = models.CharField(max_length=50, blank=True, null=True)
    doc_evidence_number = models.CharField(max_length=50, blank=True, null=True)

    goal_type = models.TextField(blank=True, null=True)
    goal_type_number = models.IntegerField(blank=True, null=True)
    review_cycle_number = models.CharField(max_length=100, blank=True, null=True)

    short_term_target = models.FloatField(blank=True, null=True)
    intermediate_term_target = models.FloatField(blank=True, null=True)
    long_term_target = models.FloatField(blank=True, null=True)

    uom = models.CharField(max_length=50, blank=True, null=True)  # Units of Measure
    short_term_actual = models.FloatField(blank=True, null=True)
    intermediate_term_actual = models.FloatField(blank=True, null=True)
    long_term_actual = models.FloatField(blank=True, null=True)


    short_term_target_due_date = models.DateField(null=True, blank=True)
    intermediate_term_target_due_date = models.DateField(null=True, blank=True)
    long_term_target_due_date = models.DateField(null=True, blank=True)

    long_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    medium_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    short_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)

    high_priority = models.TextField(blank=True, null=True)
    low_priority = models.TextField(blank=True, null=True)
    lowest_priority = models.TextField(blank=True, null=True)
    secondary_department = models.TextField(blank=True, null=True)


    def save(self, *args, **kwargs):
        # Determine review cycle number
        today = date.today()
        review_period = ReviewPeriod.objects.filter(
            period_start_date__lte=today,
            period_end_date__gte=today
        ).first()
        if review_period:
            self.review_cycle_number = review_period.review
        else:
            self.review_cycle_number = None

        # Construct strategy_code_results using concatenation
        self.strategy_code_results = "__".join(filter(None, [
            self.employee_code,
            self.goal_type,
            self.strategic_goal,
            self.kpi,
            self.deliverable,
            self.doc_evidence,
            self.doc_evidence_number,
            self.review_cycle_number
        ]))

        # Other ID auto-increment logic
        if not self.strategic_goal_number:
            count = SGSKPIsDelDev.objects.filter(
                employee_code=self.employee_code,
                strategic_goal__isnull=False
            ).values('strategic_goal').distinct().count()
            self.strategic_goal_number = str(count + 1)

        if not self.kpi_number:
            kpi_count = SGSKPIsDelDev.objects.filter(
                employee_code=self.employee_code,
                strategic_goal=self.strategic_goal,
                kpi__isnull=False
            ).values('kpi').distinct().count()
            self.kpi_number = f"{self.strategic_goal_number}.{kpi_count + 1}"

        if not self.deliverable_number:
            del_count = SGSKPIsDelDev.objects.filter(
                employee_code=self.employee_code,
                strategic_goal=self.strategic_goal,
                kpi=self.kpi,
                deliverable__isnull=False
            ).values('deliverable').distinct().count()
            self.deliverable_number = f"{self.kpi_number}.{del_count + 1}"

        if not self.doc_evidence_number:
            doc_count = SGSKPIsDelDev.objects.filter(
                employee_code=self.employee_code,
                strategic_goal=self.strategic_goal,
                kpi=self.kpi,
                deliverable=self.deliverable,
                doc_evidence__isnull=False
            ).values('doc_evidence').distinct().count()
            self.doc_evidence_number = f"{self.deliverable_number}.{doc_count + 1}"

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'perf_mgmt_sgs_kpis_del_dev'

class PerfMgmtAssessment(models.Model):
    employee_code = models.CharField(max_length=150)
    assessor_employee_code = models.CharField(max_length=150)
    date_self_appraisal_completed = models.DateTimeField()
    date_assessor_appraisal_completed = models.DateTimeField()
    strategic_goal = models.CharField(max_length=255)
    kpi = models.CharField(max_length=255)
    deliverable = models.CharField(max_length=255)
    deliverable_self_score = models.IntegerField()
    deliverable_assessor_score = models.IntegerField(null=True)
    doc_evidence = models.CharField(max_length=255)
    doc_evidence_self_confirmation = models.BooleanField()
    doc_evidence_assessor_confirmation = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    # Attachment URL field (UPDATED)
    attachment_url = models.CharField(max_length=512, null=True, blank=True)

    # Auto-generated assessment_code (unique constraint)
    assessment_code = models.CharField(max_length=1024, blank=True, null=True)

    # Numbering fields from SGSKPIsDelDev
    strategic_goal_number = models.CharField(max_length=50, blank=True, null=True)
    kpi_number = models.CharField(max_length=50, blank=True, null=True)
    deliverable_number = models.CharField(max_length=50, blank=True, null=True)
    doc_evidence_number = models.CharField(max_length=50, blank=True, null=True)

    # Weight fields from SGSKPIsDelDev
    strategic_goal_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kpi_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    deliverable_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    doc_evidence_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    short_term_target = models.FloatField(blank=True, null=True)
    intermediate_term_target = models.FloatField(blank=True, null=True)
    long_term_target = models.FloatField(blank=True, null=True)

    uom = models.CharField(max_length=50, blank=True, null=True)
    short_term_actual = models.FloatField(blank=True, null=True)
    intermediate_term_actual = models.FloatField(blank=True, null=True)
    long_term_actual = models.FloatField(blank=True, null=True)

    short_term_target_due_date = models.DateField(null=True, blank=True)
    intermediate_term_target_due_date = models.DateField(null=True, blank=True)
    long_term_target_due_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Auto-generate the assessment_code before saving."""
        date_part = self.date_self_appraisal_completed.strftime('%Y-%m') if self.date_self_appraisal_completed else datetime.now().strftime('%Y-%m')
        self.assessment_code = f"{self.employee_code}__{self.strategic_goal}__{self.kpi}__{self.deliverable}__{date_part}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_assessment"


class EvaluateYourManager(models.Model):
    """Model to represent assessor appraisal factors."""
    evaluateyourmanager_code = models.CharField(max_length=1024, unique=True, primary_key=True, editable=False)
    
    factor_type = models.CharField(
        max_length=1550,
        help_text="Type of assessor appraisal factor"
    )
    description = models.TextField(blank=True, help_text="Detailed description of the factor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def factor_type_string(self):
        return f"{self.get_factor_type_display()}"
    
        
    def save(self, *args, **kwargs):
        """Auto-populate evaluateyourmanager_code before saving."""
        self.evaluateyourmanager_code = "__".join([
            self.description or '',
            self.factor_type or ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_evaluateyourmanager"


class EvaluateYourPeer(models.Model):
    """Model to represent assessor appraisal factors."""
    factor_type = models.CharField(
    max_length=1550,
    help_text="Type of assessor appraisal factor"
    )
    description = models.TextField(blank=True, help_text="Detailed description of the factor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    evaluateyourpeer_code = models.CharField(max_length=1024, primary_key=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        """Auto-populate evaluateyourpeer_code before saving."""
        self.evaluateyourpeer_code = "__".join([
            self.description or '',
            ''  # Removed factor_type since it's not defined
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_evaluateyourpeer"

class EvaluateYourPeerSetting(models.Model):
    """
    Model to represent evaluate your peer settings.
    """
    company_code = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    evaluation_code = models.CharField(max_length=1024, primary_key=True, editable=False)  # Primary key

    def save(self, *args, **kwargs):
        # Generate evaluation_code by concatenating company_code, factor_type, and description
        self.evaluation_code = "__".join([
            self.company_code or '',
            self.factor_type or '',
            self.description or ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_evaluateyourpeersetting"

    def __str__(self):
        return self.evaluation_code
    


class EvaluateYourPeerResults(models.Model):
    """
    Model to represent evaluate your manager results.
    """
    employee_code = models.CharField(max_length=255)  # Note: storing passwords in plain text is not recommended
    peer_name= models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    response = models.IntegerField()
    evaluate_code = models.CharField(max_length=1024, editable=False)
    evaluate_results_code = models.CharField(max_length=1024, primary_key=True, editable=False)  # Primary key
    
    def save(self, *args, **kwargs):
        # Generate evaluate_code by concatenating relevant fields
        self.evaluate_code = "__".join([
            self.employee_code or '',
            self.factor_type or '',
            self.description or '',
            str(self.response) if self.response is not None else ''
        ])
        
        # Generate evaluate_results_code by adding the formatted date_created
        date_part = self.date_created.strftime('%Y_%m') if self.date_created else datetime.now().strftime('%Y_%m')
        self.evaluate_results_code = f"{self.evaluate_code}__{date_part}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "perf_mgmt_evaluateyourpeerresults"

    def __str__(self):
        return self.evaluate_results_code
        
class EmployeeExperienceFactor(models.Model):
    """Model to represent employee experience factors as long text with a factor type."""
    
    factor_type = models.CharField(
        max_length=1550,
        help_text="Type of employee experience factor"
    )
    description = models.TextField(help_text="Detailed description of the experience factor")
    experiencefactor_code = models.CharField(max_length=1024, unique=True, primary_key=True, editable=False)
    def save(self, *args, **kwargs):
        """Auto-populate experiencefactor_code before saving."""
        self.experiencefactor_code = "__".join([
            self.description or '',
            self.factor_type or ''
        ])
        super().save(*args, **kwargs)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_factor_type_display()}"


    class Meta:
        db_table = "perf_mgmt_employee_experience_factor"
        verbose_name = "Employee Experience Factor"
        verbose_name_plural = "Employee Experience Factors"


class EmpExFactorSetting(models.Model):
    """
    Model to represent employee experience factor settings.
    """
    id = models.AutoField(primary_key=True)
    company_code= models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    experience_code = models.CharField(max_length=1024, unique=True, editable=False)

    def save(self, *args, **kwargs):
        """Auto-generate experience_code before saving."""
        self.experience_code = "__".join([
            self.company_code or '',
            self.factor_type or '',
            self.description or ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_empexfactorsetting"
        verbose_name = "Employee Experience Factor Setting"
        verbose_name_plural = "Employee Experience Factor Settings"

    def __str__(self):
        return f"{self.experience_code}"
    

class EmpExFactorResults(models.Model):
    """
    Model to represent employee experience factor results.
    """
    id = models.AutoField(primary_key=True)
    employee_code= models.CharField(max_length=255)  # Note: storing passwords in plain text is not recommended
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    response = models.IntegerField()
    experience_code = models.CharField(max_length=1024, editable=False, unique=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate experience_code by concatenating employee_code, factor_type, 
        description, and response separated by '__' before saving.
        """
        self.experience_code = "__".join([
            self.employee_code or '',
            self.factor_type or '',
            self.description or '',
            str(self.response) if self.response is not None else ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_empexfactorresults"
        verbose_name = "Employee Experience Factor Result"
        verbose_name_plural = "Employee Experience Factor Results"

    def __str__(self):
        return self.experience_code
    

class EvaluateYourMgtSetting(models.Model):
    """
    Model to represent evaluate your manager settings.
    """
    company_code = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    feedback_type = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    change_status = models.CharField(max_length=255, null=True, blank=True)  # ✅ New nullable field
    evaluation_code = models.CharField(max_length=1024, primary_key=True, editable=False)

    def save(self, *args, **kwargs):
        # Generate evaluation_code by concatenating required fields
        parts = [
            self.company_code or '',
            self.factor_type or '',
            self.description or ''
        ]
        if self.change_status:  # ✅ Append only if value exists
            parts.append(self.change_status)
        self.evaluation_code = "__".join(parts)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "perf_mgmt_evaluateyourmgtsetting"

    def __str__(self):
        return self.evaluation_code


class EvaluateYourMgtResults(models.Model):
    """
    Model to represent evaluate your manager results.
    """
    employee_code = models.CharField(max_length=255)  # Note: storing passwords in plain text is not recommended
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    factor_type = models.CharField(max_length=255)
    description = models.TextField()
    response = models.IntegerField()
    evaluate_code = models.CharField(max_length=1024, editable=False)
    evaluate_results_code = models.CharField(max_length=1024, primary_key=True, editable=False)  # Primary key
    
    def save(self, *args, **kwargs):
        # Generate evaluate_code by concatenating relevant fields
        self.evaluate_code = "__".join([
            self.employee_code or '',
            self.factor_type or '',
            self.description or '',
            str(self.response) if self.response is not None else ''
        ])
        
        # Generate evaluate_results_code by adding the formatted date_created
        date_part = self.date_created.strftime('%Y_%m') if self.date_created else datetime.now().strftime('%Y_%m')
        self.evaluate_results_code = f"{self.evaluate_code}__{date_part}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "perf_mgmt_evaluateyourmgtresults"

    def __str__(self):
        return self.evaluate_results_code


class ManagerSelfEvaluation(models.Model):
    id = models.BigAutoField(primary_key=True)
    factor_type = models.CharField(max_length=50, null=False)
    description = models.TextField(null=False)
    created_at = models.DateTimeField(default=now, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    self_evaluation_code = models.CharField(max_length=1024, editable=False)

    def save(self, *args, **kwargs):
        self.self_evaluation_code = f"{self.factor_type}__{self.description}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.self_evaluation_code

class ManagerSelfEvaluationSetting(models.Model):
    company_code = models.CharField(max_length=255, null=False)
    date_created = models.DateTimeField(default=now, null=False)
    date_modified = models.DateTimeField(auto_now=True, null=False)
    factor_type = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    self_evaluation_setting_code = models.CharField(max_length=1024, editable=False)

    def save(self, *args, **kwargs):
        self.self_evaluation_setting_code = f"{self.company_code}__{self.factor_type}__{self.description}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.self_evaluation_setting_code

    class Meta:
        db_table = 'perf_mgmt_managerselfevaluationsetting'
    

class ManagerSelfEvaluationResults(models.Model):
    company_code = models.CharField(max_length=255, null=False)
    date_created = models.DateTimeField(default=now, null=False)
    date_modified = models.DateTimeField(auto_now=True, null=False)
    factor_type = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    self_evaluation_setting_code = models.CharField(max_length=1024, editable=False)
    description = models.IntegerField(null=False)

    def save(self, *args, **kwargs):
        month_year = self.date_created.strftime("%m-%Y")  # Extracts Month-Year (e.g., 08-2024)
        self.self_evaluation_setting_code = f"{self.company_code}__{self.factor_type}__{self.description}"
        self.self_evaluation_results_code = f"{self.company_code}__{self.factor_type}__{self.description}__{month_year}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.self_evaluation_results_code

class Region(models.Model):
    region_code = models.CharField(max_length=255, unique=True, primary_key=True)
    company_code = models.ForeignKey(UserProfile, to_field="company_code", on_delete=models.CASCADE)  
    region_branch = models.TextField()
    user_select = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if not self.region_code:
            self.region_code = self.generate_region_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_region_code():
        return "CMPRGN" + "".join(random.choices(string.digits, k=5))

    def __str__(self):
        return f"{self.region_code} - {self.region_branch} - {self.user_select}"

class ChatMessage(models.Model):
    sender = models.CharField(
        max_length=32,
        db_column='sender_id'
    )
    receiver = models.ForeignKey(
        'perf_mgmt.UserCreationModel',
        related_name='received_messages',
        on_delete=models.CASCADE,
        db_column='receiver_id',
        to_field='employee_code'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    unique_chat = models.CharField(max_length=32, editable=False, db_index=True)
    chat_type = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        sender_code = self.sender
        receiver_code = self.receiver.employee_code
        self.unique_chat = '_'.join(sorted([sender_code, receiver_code]))
        super().save(*args, **kwargs)

    def __str__(self):
        # Use sender directly (employee_code)
        sender_name = self.sender
        receiver_name = getattr(self.receiver, 'employee_name', 'Unknown')
        message_preview = self.message[:30] + ('...' if len(self.message) > 30 else '')
        return f'{sender_name} ➜ {receiver_name}: {message_preview}'

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'sender']),
            models.Index(fields=['unique_chat']),
        ]
        constraints = [
            CheckConstraint(
                check=~Q(sender=F('receiver_id')),
                name='prevent_self_messaging'
            )
        ]

class AIRecommendation(models.Model):
    employee_code = models.CharField(max_length=50)
    assessment = models.ForeignKey('PerfMgmtAssessment', on_delete=models.CASCADE)

    performance_recommendation = models.TextField()
    upskilling_recommendation = models.TextField()
    engagement_recommendation = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Recommendation for {self.employee_code} on {self.created_at.strftime('%Y-%m-%d')}"

class UserLogin(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.TextField()
    company = models.TextField()
    employee_code = models.CharField(max_length=100)
    region_branch = models.TextField(blank=True, null=True)
    headquarters = models.TextField()
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    company_code = models.TextField()
    region_code = models.TextField(blank=True, null=True)
    log_out = models.DateTimeField(blank=True, null=True)  # 👈 New field added

    class Meta:
        db_table = 'perf_mgmt_user_login'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} @ {self.headquarters}"


class CompanyLogin(models.Model):
    id = models.AutoField(primary_key=True)

    # Use CharField instead of ForeignKey
    company_code = models.CharField(max_length=20)
    company = models.TextField()  # Name of the company
    region_branch = models.TextField(null=True, blank=True)  # Branch or region
    headquarters = models.TextField()  # HQ location
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    log_out = models.DateTimeField(null=True, blank=True)  # Nullable log_out column

    class Meta:
        db_table = 'perf_mgmt_company_user_login'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company} @ {self.headquarters}"

class AppraisalMessage(models.Model):
    sender = models.CharField(max_length=32, db_column='sender_id')
    receiver = models.ForeignKey(
        'perf_mgmt.UserCreationModel',
        related_name='received_appraisal_messages',
        on_delete=models.CASCADE,
        db_column='receiver_id',
        to_field='employee_code'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    unique_chat = models.CharField(max_length=132, editable=False, db_index=True)
    chat_type = models.CharField(max_length=2255, null=True, blank=True, default='text')
    attachment_url = models.URLField(null=True, blank=True)
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    recipient_name = models.CharField(max_length=1255, null=True, blank=True)
    strategic_goal = models.CharField(max_length=1255, null=True, blank=True, default='N/A')
    kpi = models.CharField(max_length=2255, null=True, blank=True, default='N/A')
    deliverable = models.CharField(max_length=2255, null=True, blank=True, default='N/A')
    deliverable_number = models.CharField(max_length=50, null=True, blank=True, default='N/A')
    deliverable_id = models.CharField(max_length=2255, null=True, blank=True)
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies',
        db_column='reply_to_id'
    )
    message_id = models.CharField(max_length=255, editable=False, unique=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        sender_code = str(self.sender).strip()
        receiver_code = str(self.receiver.employee_code).strip()
        self.unique_chat = '_'.join(sorted([sender_code, receiver_code]))

        if not self.timestamp:
            self.timestamp = timezone.now()
        
        ts_str = self.timestamp.strftime('%Y%m%d%H%M%S%f')
        self.message_id = f"{self.unique_chat}__{ts_str}"

        if self.reply_to and self.reply_to.unique_chat != self.unique_chat:
            raise ValueError("Reply must belong to the same chat.")

        if not self.id:
            super().save(*args, **kwargs)

        if not self.reply_to_id:
            existing_message = AppraisalMessage.objects.filter(
                unique_chat=self.unique_chat,
                strategic_goal=self.strategic_goal,
                kpi=self.kpi,
                deliverable=self.deliverable,
            ).exclude(id=self.id).order_by('id').first()
            if existing_message:
                self.reply_to_id = existing_message.id
            else:
                self.reply_to_id = self.id
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        sender_name = self.sender_name or self.sender
        receiver_name = self.recipient_name or getattr(self.receiver, 'employee_name', 'Unknown')
        message_preview = self.message[:30] + ('...' if len(self.message) > 30 else '')
        return f'{sender_name} ➜ {receiver_name}: {message_preview} at {self.timestamp}'

    class Meta:
        db_table = 'perf_mgmt_appraisal_messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'sender']),
            models.Index(fields=['unique_chat']),
            models.Index(fields=['reply_to']),  
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(sender=F('receiver_id')),
                name='prevent_self_messaging_appraisal'
            )
        ]
        
class StrategicGoals(models.Model):
    GOAL_ACTIVITY_CHOICES = [
        ('current', 'Current'),
        ('outdated', 'Outdated'),
    ]

    id = models.AutoField(primary_key=True)
    company_code = models.CharField(max_length=255)  # company code string
    goal_type = models.CharField(max_length=100)
    strategic_goal = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    employee_code = models.CharField(max_length=50)  # Changed from ForeignKey to CharField
    region_code = models.CharField(max_length=50, blank=True, null=True)  # Changed from ForeignKey to CharField

    goal_activity = models.CharField(max_length=10, choices=GOAL_ACTIVITY_CHOICES, default='current')
    department = models.CharField(max_length=255, blank=True, null=True)
    lead_department = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    short_term_target = models.FloatField(blank=True, null=True)
    intermediate_term_target = models.FloatField(blank=True, null=True)
    long_term_target = models.FloatField(blank=True, null=True)

    uom = models.CharField(max_length=50, blank=True, null=True)  # Units of Measure
    short_term_target_due_date = models.DateField(null=True, blank=True)
    intermediate_term_target_due_date = models.DateField(null=True, blank=True)
    long_term_target_due_date = models.DateField(null=True, blank=True)

    due_date = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    region_branch = models.CharField(max_length=255, blank=True, null=True)
    strategy_code = models.CharField(max_length=1024, editable=False, unique=True)

    long_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    medium_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    short_term_required_budget = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)

    priority_level = models.TextField(blank=True, null=True)
    secondary_department = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.strategy_code = "__".join([
            self.company_code or '',
            self.goal_type or '',
            self.strategic_goal or '',
            self.department or ''
        ])
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'perf_mgmt_strategic_goals'
        constraints = [
            models.UniqueConstraint(
                fields=['company_code', 'goal_type', 'strategic_goal', 'department'],
                name='unique_strategy_code'
            )
        ]

class Goal(models.Model):
    employee_code = models.CharField(max_length=50)  # Changed from ForeignKey
    employee_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=20, blank=True)  # Auto-calculated
    progress = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.end_date >= self.start_date:
            days = (self.end_date - self.start_date).days
            months = max(days // 30, 1)
            self.duration = f"{months} months"
        else:
            self.duration = ""
        super().save(*args, **kwargs)


class Course(models.Model):
    employee_code = models.CharField(max_length=100)
    employee_name = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=50, blank=True)
    progress = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Validate progress range
        if not (0 <= self.progress <= 100):
            raise ValueError("Progress must be between 0 and 100")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_name} ({self.employee_name})"

    class Meta:
        unique_together = ('employee_code', 'course_name')  # Updated constraint




class ChatSession(models.Model):
    """Represents a unique chat session."""
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Session {self.session_id} ({self.created_at})"

    class Meta:
        db_table = 'custom_chat_sessions'  # <-- new table name here


class ChatMessage(models.Model):
    """Stores individual messages within a chat session."""
    USER = 'user'
    BOT = 'bot'
    MESSAGE_SENDER_CHOICES = [
        (USER, 'User'),
        (BOT, 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=50, choices=MESSAGE_SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.sender.upper()}] {self.message[:30]}"

    class Meta:
        db_table = 'custom_chat_messages'  # <-- new table name here



class UoM(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=255)  # e.g., length, mass, time, etc.

    def __str__(self):
        return f"{self.name} ({self.symbol})"

