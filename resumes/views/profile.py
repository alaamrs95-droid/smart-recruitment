# resumes/views/profile.py
# تم إنشاء هذا الملف لإدارة ملفات تعريف السير الذاتية
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from ..models.profile import CandidateResumeProfile

@login_required
def resume_profile_view(request):
    """
    عرض وإدارة ملف تعريف السيرة الذاتية للمرشح
    """
    if request.user.role != 'candidate':
        messages.error(request, _("This page is only available for candidates."))
        return redirect('home')
    
    # الحصول على أو إنشاء ملف التعريف
    profile, created = CandidateResumeProfile.objects.get_or_create(
        candidate=request.user
    )
    
    # الحصول على جميع السير الذاتية
    all_resumes = profile.get_all_resumes()
    
    context = {
        'profile': profile,
        'all_resumes': all_resumes,
        'has_resume': profile.has_resume(),
        'has_both_resumes': profile.has_both_resumes(),
    }
    
    return render(request, 'resumes/profile.html', context)

@login_required
def set_primary_resume(request, resume_type):
    """
    تعيين السيرة الذاتية الرئيسية
    """
    if request.user.role != 'candidate':
        return JsonResponse({'error': _('Access denied')}, status=403)
    
    if resume_type not in ['uploaded', 'built', 'both']:
        return JsonResponse({'error': _('Invalid resume type')}, status=400)
    
    try:
        profile = CandidateResumeProfile.objects.get(candidate=request.user)
        
        if resume_type == 'uploaded':
            # البحث عن آخر سيرة مرفوعة معالجة
            from ..models.uploaded import Resume
            resume = Resume.objects.filter(
                candidate=request.user, 
                is_processed=True
            ).first()
            
            if not resume:
                return JsonResponse({'error': _('No processed uploaded resume found')}, status=404)
            
            profile.set_primary_resume('uploaded', resume)
            
        elif resume_type == 'built':
            # البحث عن آخر سيرة مبنية
            from ..models.builder import BuiltResume
            resume = BuiltResume.objects.filter(
                candidate=request.user,
                is_active=True
            ).first()
            
            if not resume:
                return JsonResponse({'error': _('No built resume found')}, status=404)
            
            profile.set_primary_resume('built', resume)
            
        elif resume_type == 'both':
            profile.set_primary_resume('both')
        
        return JsonResponse({
            'success': True,
            'message': _('Primary resume updated successfully'),
            'primary_type': profile.primary_resume_type
        })
        
    except CandidateResumeProfile.DoesNotExist:
        return JsonResponse({'error': _('Profile not found')}, status=404)

@login_required
def toggle_matching_status(request):
    """
    تشغيل/إيقاف المطابقة للملف الشخصي
    """
    if request.user.role != 'candidate':
        return JsonResponse({'error': _('Access denied')}, status=403)
    
    if request.method == 'POST':
        try:
            profile = CandidateResumeProfile.objects.get(candidate=request.user)
            profile.is_active_for_matching = not profile.is_active_for_matching
            profile.save()
            
            return JsonResponse({
                'success': True,
                'is_active': profile.is_active_for_matching,
                'message': _('Matching status updated successfully')
            })
            
        except CandidateResumeProfile.DoesNotExist:
            return JsonResponse({'error': _('Profile not found')}, status=404)
    
    return JsonResponse({'error': _('Invalid request method')}, status=405)
