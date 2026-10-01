from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views import View
from jobs.models import Job

def _public_jobs():
    return Job.objects.filter(status="active").select_related("company").prefetch_related("job_skills__skill").order_by("-created_at")

class JobSeoListView(View):
    def get(self, request):
        return render(request,"jobs/seo_list.html",{"jobs":_public_jobs()[:50],"site_url":settings.SITE_URL.rstrip("/")})

class JobSeoDetailView(View):
    def get(self, request, slug):
        job=_public_jobs().filter(slug=slug).first()
        if not job: raise Http404("Job not found")
        return render(request,"jobs/seo_detail.html",{"job":job,"site_url":settings.SITE_URL.rstrip("/")})

def sitemap_xml(request):
    base=settings.SITE_URL.rstrip("/")
    urls=[f"{base}/seo/jobs/"]+[f"{base}/seo/jobs/{j.slug}/" for j in _public_jobs()[:500]]
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls)+"</urlset>"
    return HttpResponse(xml,content_type="application/xml")

def robots_txt(request):
    base=settings.SITE_URL.rstrip("/")
    return HttpResponse("User-agent: *\nAllow: /seo/jobs/\nDisallow: /api/\nDisallow: /admin/\n\n"+f"Sitemap: {base}/sitemap.xml\n",content_type="text/plain")
