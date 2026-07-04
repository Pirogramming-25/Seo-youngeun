from django.shortcuts import render, redirect, get_object_or_404
from .models import Idea, DevTool, IdeaStar
from .forms import IdeaForm, DevToolForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count

#아이디어 리스트
def idea_list(request):
    sort = request.GET.get('sort', 'latest')

    ideas = Idea.objects.annotate(star_total=Count('stars'))

    if sort == 'star':
        ideas = ideas.order_by('-star_total')
    elif sort == 'name':
        ideas = ideas.order_by('title')
    elif sort == 'interest':
        ideas = ideas.order_by('-interest')
    elif sort == 'old':
        ideas = ideas.order_by('created_at')
    else:
        ideas = ideas.order_by('-created_at')

    starred_idea_ids = []

    if request.user.is_authenticated:
        starred_idea_ids = IdeaStar.objects.filter(
            user=request.user
        ).values_list('idea_id', flat=True)

    return render(request, 'idea_site/idea_list.html', {
        'ideas': ideas,
        'sort': sort,
        'starred_idea_ids': starred_idea_ids,
    })


#아이디어 등록
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)

        if form.is_valid():
            idea = form.save()
            return redirect('idea_site:idea_detail', idea.pk)
    else:
        form = IdeaForm()

    return render(request, 'idea_site/idea_form.html', {
        'form': form,
    })
#아이디어 디테일
def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    is_starred = False

    if request.user.is_authenticated:
        is_starred = IdeaStar.objects.filter(
            user=request.user,
            idea=idea,
        ).exists()

    return render(request, 'idea_site/idea_detail.html', {
        'idea': idea,
        'is_starred': is_starred,
    })

#아이디어 수정
def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)

        if form.is_valid():
            idea = form.save()
            return redirect('idea_site:idea_detail', idea.pk)
    else:
        form = IdeaForm(instance=idea)

    return render(request, 'idea_site/idea_form.html', {
        'form': form,
        'idea': idea,
    })

#아이디어 삭제
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        idea.delete()
        return redirect('idea_site:idea_list')

    return redirect('idea_site:idea_detail', idea.pk)

#관심도 조절
def idea_interest(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'plus':
            idea.interest += 1
        elif action == 'minus':
            idea.interest -= 1

        idea.save()

        return JsonResponse({
            'interest': idea.interest,
        })

    return JsonResponse({
        'error': '잘못된 요청입니다.',
    }, status=400)

#찜하기
@login_required
def idea_star(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        star, created = IdeaStar.objects.get_or_create(
            user=request.user,
            idea=idea,
        )

        if created:
            is_starred = True
        else:
            star.delete()
            is_starred = False

        return JsonResponse({
            'is_starred': is_starred,
            'star_count': idea.stars.count(),
        })

    return JsonResponse({
        'error': '잘못된 요청입니다.',
    }, status=400)

#개발툴 리스트
def devtool_list(request):
    devtools = DevTool.objects.all().order_by('name')

    return render(request, 'idea_site/devtool_list.html', {
        'devtools': devtools,
    })

#개발툴 수정
def devtool_create(request):
    if request.method == 'POST':
        form = DevToolForm(request.POST)

        if form.is_valid():
            devtool = form.save()
            return redirect('idea_site:devtool_detail', devtool.pk)
    else:
        form = DevToolForm()

    return render(request, 'idea_site/devtool_form.html', {
        'form': form,
    })

#개발툴 디테일
def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    return render(request, 'idea_site/devtool_detail.html', {
        'devtool': devtool,
    })

def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        form = DevToolForm(request.POST, instance=devtool)

        if form.is_valid():
            devtool = form.save()
            return redirect('idea_site:devtool_detail', devtool.pk)
    else:
        form = DevToolForm(instance=devtool)

    return render(request, 'idea_site/devtool_form.html', {
        'form': form,
        'devtool': devtool,
    })

#개발툴 삭제
def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == 'POST':
        devtool.delete()
        return redirect('idea_site:devtool_list')

    return redirect('idea_site:devtool_detail', devtool.pk)
    