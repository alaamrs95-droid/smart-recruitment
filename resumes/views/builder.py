# resumes/views/builder.py
# تم إنشاء هذا الملف لدعم نظام بناء السيرة الذاتية داخل المنصة
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from ..models.builder import (
    BuiltResume, PersonalInfo, Experience, Education, 
    Skill, Language, Project, Certification
)
from ..forms.builder import (
    BuiltResumeForm, PersonalInfoForm, ExperienceForm, 
    EducationForm, SkillForm, LanguageForm, ProjectForm, CertificationForm
)

class ResumeBuilderView(LoginRequiredMixin, ListView):
    """
    عرض قائمة السير الذاتية المبنية للمستخدم
    """
    model = BuiltResume
    template_name = 'resumes/builder/resume_list.html'
    context_object_name = 'resumes'
    
    def get_queryset(self):
        return BuiltResume.objects.filter(candidate=self.request.user, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_resumes'] = self.get_queryset().exists()
        return context

class CreateResumeView(LoginRequiredMixin, CreateView):
    """
    إنشاء سيرة ذاتية جديدة
    """
    model = BuiltResume
    form_class = BuiltResumeForm
    template_name = 'resumes/builder/resume_create.html'
    success_url = reverse_lazy('resumes_builder:resume_list')
    
    def form_valid(self, form):
        form.instance.candidate = self.request.user
        messages.success(self.request, _('Resume created successfully!'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create New Resume')
        return context

class EditResumeView(LoginRequiredMixin, UpdateView):
    """
    تعديل السيرة الذاتية
    """
    model = BuiltResume
    form_class = BuiltResumeForm
    template_name = 'resumes/builder/resume_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('resumes_builder:resume_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Resume updated successfully!'))
        return super().form_valid(form)
    
    def get_queryset(self):
        return BuiltResume.objects.filter(candidate=self.request.user, is_active=True)

class ResumeDetailView(LoginRequiredMixin, DetailView):
    """
    عرض تفاصيل السيرة الذاتية المبنية
    """
    model = BuiltResume
    template_name = 'resumes/builder/resume_detail.html'
    context_object_name = 'resume'
    
    def get_queryset(self):
        # السماح للمرشحين برؤية سيرهم الذاتية فقط
        # السماح لأصحاب العمل برؤية جميع السير الذاتية للمطابقة
        if self.request.user.role == 'candidate':
            return BuiltResume.objects.filter(candidate=self.request.user, is_active=True)
        elif self.request.user.role == 'employer':
            return BuiltResume.objects.filter(is_active=True)
        else:
            return BuiltResume.objects.none()
    
    def get_object(self, queryset=None):
        return super().get_object(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resume = self.get_object()
        
        # إضافة معلومات عن نوع المستخدم
        context['user_role'] = self.request.user.role
        context['is_owner'] = (self.request.user.role == 'candidate' and resume.candidate == self.request.user)
        
        # الحصول على جميع الأقسام
        context['personal_info'] = getattr(resume, 'personal_info', None)
        context['experiences'] = resume.experiences.all()
        context['education'] = resume.education.all()
        context['skills'] = resume.skills.all()
        context['languages'] = resume.languages.all()
        context['projects'] = resume.projects.all()
        context['certifications'] = resume.certifications.all()
        
        return context

# === Views للأقسام المختلفة ===

@login_required
def edit_personal_info(request, resume_id):
    """
    تعديل المعلومات الشخصية
    """
    resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
    
    try:
        personal_info = resume.personal_info
    except PersonalInfo.DoesNotExist:
        personal_info = PersonalInfo(resume=resume)
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=personal_info)
        if form.is_valid():
            form.save()
            messages.success(request, _('Personal information updated successfully!'))
            return redirect('resumes_builder:resume_detail', pk=resume_id)
    else:
        form = PersonalInfoForm(instance=personal_info)
    
    return render(request, 'resumes/builder/edit_personal_info.html', {
        'form': form,
        'resume': resume,
        'title': _('Edit Personal Information')
    })

@login_required
def add_experience(request, resume_id):
    """
    إضافة خبرة عمل جديدة
    """
    resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.resume = resume
            experience.save()
            messages.success(request, _('Experience added successfully!'))
            return redirect('resumes_builder:resume_detail', pk=resume_id)
    else:
        form = ExperienceForm()
    
    return render(request, 'resumes/builder/add_experience.html', {
        'form': form,
        'resume': resume,
        'title': _('Add Work Experience')
    })

@login_required
def edit_experience(request, resume_id, experience_id):
    """
    تعديل خبرة عمل
    """
    resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
    experience = get_object_or_404(Experience, id=experience_id, resume=resume)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, _('Experience updated successfully!'))
            return redirect('resumes_builder:resume_detail', pk=resume_id)
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'resumes/builder/edit_experience.html', {
        'form': form,
        'resume': resume,
        'experience': experience,
        'title': _('Edit Work Experience')
    })

@login_required
def delete_experience(request, resume_id, experience_id):
    """
    حذف خبرة عمل
    """
    resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
    experience = get_object_or_404(Experience, id=experience_id, resume=resume)
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, _('Experience deleted successfully!'))
        return redirect('resumes_builder:resume_detail', pk=resume_id)
    
    return render(request, 'resumes/builder/delete_confirm.html', {
        'object': experience,
        'resume': resume,
        'title': _('Delete Work Experience'),
        'cancel_url': reverse_lazy('resumes_builder:resume_detail', kwargs={'pk': resume_id})
    })

# === دوال مساعدة للأقسام الأخرى ===

def handle_section_crud(request, resume_id, model_class, form_class, section_name):
    """
    دالة عامة للتعامل مع CRUD للأقسام المختلفة
    """
    resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.resume = resume
            obj.save()
            messages.success(request, _(f'{section_name} added successfully!'))
            return redirect('resumes_builder:resume_detail', pk=resume_id)
    else:
        form = form_class()
    
    return render(request, f'resumes/builder/add_{section_name.lower().replace(" ", "_")}.html', {
        'form': form,
        'resume': resume,
        'title': _(f'Add {section_name}')
    })

@login_required
def add_education(request, resume_id):
    """إضافة تعليم"""
    return handle_section_crud(request, resume_id, Education, EducationForm, 'Education')

@login_required
def add_skill(request, resume_id):
    """إضافة مهارة"""
    return handle_section_crud(request, resume_id, Skill, SkillForm, 'Skill')

@login_required
def add_language(request, resume_id):
    """إضافة لغة"""
    return handle_section_crud(request, resume_id, Language, LanguageForm, 'Language')

@login_required
def add_project(request, resume_id):
    """إضافة مشروع"""
    return handle_section_crud(request, resume_id, Project, ProjectForm, 'Project')

@login_required
def add_certification(request, resume_id):
    """إضافة شهادة"""
    return handle_section_crud(request, resume_id, Certification, CertificationForm, 'Certification')

# === API Views للتعامل مع AJAX ===

@login_required
def set_default_resume(request, resume_id):
    """
    تعيين السيرة الذاتية كافتراضية
    """
    if request.method == 'POST':
        resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
        
        # إلغاء جميع السير الافتراضية الأخرى
        BuiltResume.objects.filter(candidate=request.user).update(is_default=False)
        
        # تعيين السيرة الحالية كافتراضية
        resume.is_default = True
        resume.save()
        
        return JsonResponse({'success': True, 'message': _('Default resume updated!')})
    
    return JsonResponse({'success': False, 'message': _('Invalid request!')})

@login_required
def delete_resume(request, resume_id):
    """
    حذف السيرة الذاتية
    """
    if request.method == 'POST':
        resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
        resume.is_active = False
        resume.save()
        
        return JsonResponse({'success': True, 'message': _('Resume deleted successfully!')})
    
    return JsonResponse({'success': False, 'message': _('Invalid request!')})

@login_required
def duplicate_resume(request, resume_id):
    """
    نسخ السيرة الذاتية
    """
    if request.method == 'POST':
        original_resume = get_object_or_404(BuiltResume, id=resume_id, candidate=request.user)
        
        # إنشاء نسخة جديدة
        new_resume = BuiltResume.objects.create(
            candidate=request.user,
            title=f"{original_resume.title} (Copy)",
            summary=original_resume.summary
        )
        
        # نسخ المعلومات الشخصية
        if hasattr(original_resume, 'personal_info'):
            old_info = original_resume.personal_info
            PersonalInfo.objects.create(
                resume=new_resume,
                first_name=old_info.first_name,
                last_name=old_info.last_name,
                email=old_info.email,
                phone=old_info.phone,
                location=old_info.location,
                linkedin=old_info.linkedin,
                github=old_info.github,
                website=old_info.website
            )
        
        # نسخ الأقسام الأخرى
        for model_class in [Experience, Education, Skill, Language, Project, Certification]:
            for item in model_class.objects.filter(resume=original_resume):
                item.pk = None
                item.resume = new_resume
                item.save()
        
        return JsonResponse({
            'success': True, 
            'message': _('Resume duplicated successfully!'),
            'new_resume_id': new_resume.id
        })
    
    return JsonResponse({'success': False, 'message': _('Invalid request!')})
